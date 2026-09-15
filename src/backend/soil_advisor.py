"""
Soil Health Card advisory engine (Module F).

Every Indian farmer enrolled in the national Soil Health Card scheme receives a
card printed with the four values this module consumes: available nitrogen,
available phosphorus, available potassium and pH. The card tells the farmer what
their soil contains but not what to actually buy, so the numbers usually go
unused. This module closes that gap: it converts a card reading plus a crop and
plot size into a bag-level fertiliser plan, a soil amendment, an irrigation
schedule, and the resource saving that follows from dosing to the soil test
instead of applying a blanket recommended dose.

Nothing here is simulated or randomised. Every figure is a published formula
applied to values the farmer supplies, and the constants below are the ones the
recommendation is auditable against.
"""

# --- Soil test rating thresholds -------------------------------------------
# Soil Health Card rating bands. Nitrogen follows the alkaline permanganate
# method, phosphorus the Olsen method, potassium ammonium-acetate extractable
# K2O. All in kg/ha, matching how the card itself is printed.
RATING_BANDS = {
    "nitrogen": {"low": 280.0, "high": 560.0, "unit": "kg/ha", "label": "Available Nitrogen (N)"},
    "phosphorus": {"low": 10.0, "high": 25.0, "unit": "kg/ha", "label": "Available Phosphorus (P)"},
    "potassium": {"low": 120.0, "high": 280.0, "unit": "kg/ha", "label": "Available Potassium (K)"},
}

# A soil testing Low returns more fertiliser than the blanket dose, High returns
# less. This is the standard soil-test-based correction factor used by state
# agriculture departments when issuing card-linked recommendations.
DOSE_FACTOR = {"Low": 1.25, "Medium": 1.00, "High": 0.75}

# --- Crop nutrient requirement ---------------------------------------------
# Recommended Dose of Fertiliser in kg/ha of N : P2O5 : K2O, for the crops the
# diagnostic model can identify. Sourced from ICAR package-of-practice ranges;
# where a state range exists the mid-point is used.
CROP_RDF = {
    "Tomato":               {"n": 120, "p": 60, "k": 60,  "season_days": 120},
    "Potato":               {"n": 150, "p": 80, "k": 100, "season_days": 100},
    "Corn (Maize)":         {"n": 120, "p": 60, "k": 40,  "season_days": 110},
    "Bell Pepper":          {"n": 100, "p": 50, "k": 50,  "season_days": 120},
    "Apple":                {"n": 70,  "p": 35, "k": 70,  "season_days": 180},
    "Grape":                {"n": 100, "p": 50, "k": 100, "season_days": 150},
    "Orange (Citrus)":      {"n": 60,  "p": 30, "k": 60,  "season_days": 240},
    "Peach":                {"n": 60,  "p": 30, "k": 60,  "season_days": 150},
    "Cherry":               {"n": 60,  "p": 30, "k": 60,  "season_days": 150},
    "Strawberry":           {"n": 75,  "p": 60, "k": 60,  "season_days": 120},
    "Blueberry":            {"n": 50,  "p": 25, "k": 50,  "season_days": 150},
    "Raspberry":            {"n": 50,  "p": 25, "k": 50,  "season_days": 150},
    "Soybean":              {"n": 20,  "p": 60, "k": 40,  "season_days": 100},
    "Squash (Pumpkin)":     {"n": 60,  "p": 40, "k": 40,  "season_days": 90},
}

# --- Fertiliser products ----------------------------------------------------
# Nutrient content by weight, bag size, and subsidised retail price per bag as
# sold through Indian cooperatives. Price drives the rupee saving figure.
FERTILISERS = {
    "urea":  {"name": "Urea",                    "n": 0.46, "p": 0.00,  "k": 0.00, "bag_kg": 45, "price_per_bag": 266},
    "dap":   {"name": "DAP (18-46-0)",           "n": 0.18, "p": 0.46,  "k": 0.00, "bag_kg": 50, "price_per_bag": 1350},
    "ssp":   {"name": "SSP (Single Super Phosphate)", "n": 0.00, "p": 0.16, "k": 0.00, "bag_kg": 50, "price_per_bag": 450},
    "mop":   {"name": "MOP (Muriate of Potash)", "n": 0.00, "p": 0.00,  "k": 0.60, "bag_kg": 50, "price_per_bag": 1700},
}

# Cradle-to-gate manufacturing emissions per kg of product. Ammonia synthesis
# makes urea by far the most carbon-intensive of the three.
CO2_PER_KG = {"urea": 1.6, "dap": 1.4, "ssp": 0.2, "mop": 0.3}

# --- Soil and irrigation physics -------------------------------------------
# Net irrigation depth applied per turn and the interval between turns, set by
# how much plant-available water the soil texture can hold in the root zone.
SOIL_TYPES = {
    "sandy": {"label": "Sandy / Light",   "depth_mm": 40, "interval_days": 4,  "holding": "Low water holding capacity"},
    "loam":  {"label": "Loam / Medium",   "depth_mm": 60, "interval_days": 7,  "holding": "Balanced water holding capacity"},
    "clay":  {"label": "Clay / Heavy",    "depth_mm": 75, "interval_days": 10, "holding": "High water holding capacity"},
}

# Application efficiency: the share of pumped water that reaches the root zone.
IRRIGATION_METHODS = {
    "drip":      {"label": "Drip",             "efficiency": 0.90},
    "sprinkler": {"label": "Sprinkler",        "efficiency": 0.75},
    "flood":     {"label": "Flood / Furrow",   "efficiency": 0.50},
}

# 1 mm of water over 1 acre (4046.86 m2) is 4046.86 litres.
LITRES_PER_MM_PER_ACRE = 4046.86
ACRES_PER_HECTARE = 2.471
# Pumping cost and emissions are quoted per cubic metre in the literature and
# converted here, because per-litre figures carried over from a toy calculation
# inflate a season total into lakhs of rupees. Roughly 0.2 kWh lifts a cubic
# metre from a shallow tubewell, at ~Rs 1.5/m3 subsidised agricultural tariff
# and ~0.15 kg CO2e/m3 on the Indian grid.
WATER_COST_PER_LITRE = 0.0015    # INR per litre  (Rs 1.50 per m3)
WATER_CO2_PER_LITRE = 0.00015    # kg CO2e per litre (0.15 kg per m3)


def _rate(value, nutrient):
    """Classify one soil test value into the card's Low/Medium/High band."""
    band = RATING_BANDS[nutrient]
    if value < band["low"]:
        return "Low"
    if value > band["high"]:
        return "High"
    return "Medium"


def _classify_ph(ph):
    """Return the pH class, its amendment, and the rate in kg per acre."""
    if ph < 5.5:
        return "Strongly Acidic", "Apply agricultural lime to raise pH into the 6.5-7.5 range.", "Agricultural Lime", 810
    if ph < 6.5:
        return "Slightly Acidic", "A light lime application will bring pH to the crop optimum.", "Agricultural Lime", 405
    if ph <= 7.5:
        return "Neutral", "pH is in the optimum range. No amendment needed.", None, 0
    if ph <= 8.5:
        return "Slightly Alkaline", "Apply gypsum and organic matter to counter alkalinity.", "Gypsum", 405
    return "Strongly Alkaline / Sodic", "Sodic soil. Apply gypsum and arrange a laboratory ESP test before the next season.", "Gypsum", 810


def _organic_carbon_rating(oc):
    if oc < 0.5:
        return "Low", 4.0     # tonnes of farmyard manure per acre
    if oc <= 0.75:
        return "Medium", 2.0
    return "High", 1.0


def _phosphorus_carrier(n_kg, p_kg):
    """
    Pick the phosphorus product that does not overshoot the nitrogen target.

    DAP is the default, but it carries 18% nitrogen of its own. For a legume
    such as soybean, which fixes most of its own nitrogen and therefore has a
    small N requirement beside a large P requirement, the DAP needed to meet
    the phosphorus target alone exceeds that requirement -- and fertiliser
    cannot be un-applied. SSP carries no nitrogen at all (and supplies the
    sulphur those crops want), so it is the standard carrier in that case.
    """
    if p_kg <= 0:
        return "dap"
    dap_kg = p_kg / FERTILISERS["dap"]["p"]
    return "ssp" if dap_kg * FERTILISERS["dap"]["n"] > n_kg else "dap"


def _product_plan(n_kg, p_kg, k_kg, carrier=None):
    """
    Convert an N-P2O5-K2O requirement into actual sacks of product.

    The phosphorus carrier is placed first because it may also supply nitrogen;
    urea then tops up only what that carrier left short. Sizing urea first would
    over-apply nitrogen, which is exactly the habit that makes blanket dosing
    wasteful. Pass `carrier` to pin the choice across two plans being compared.
    """
    if carrier is None:
        carrier = _phosphorus_carrier(n_kg, p_kg)

    carrier_kg = p_kg / FERTILISERS[carrier]["p"] if p_kg > 0 else 0.0
    n_from_carrier = carrier_kg * FERTILISERS[carrier]["n"]
    urea_kg = max(0.0, n_kg - n_from_carrier) / FERTILISERS["urea"]["n"]
    mop_kg = k_kg / FERTILISERS["mop"]["k"] if k_kg > 0 else 0.0

    plan = {"urea": round(urea_kg, 1), "dap": 0.0, "ssp": 0.0, "mop": round(mop_kg, 1)}
    plan[carrier] = round(carrier_kg, 1)
    return plan


def _plan_cost(plan):
    return sum(kg * (FERTILISERS[key]["price_per_bag"] / FERTILISERS[key]["bag_kg"]) for key, kg in plan.items())


def _plan_co2(plan):
    return sum(kg * CO2_PER_KG[key] for key, kg in plan.items())


def build_advisory(nitrogen, phosphorus, potassium, ph, organic_carbon,
                   crop, acres, soil_type, irrigation_method):
    """
    Turn one Soil Health Card reading into a complete season plan.

    Returns the nutrient ratings, the fertiliser products to buy, the soil
    amendment, the irrigation schedule, and the sustainability scorecard --
    where every saving is the measured difference between this soil-test-based
    plan and the blanket recommended dose the farmer would otherwise apply.
    """
    rdf = CROP_RDF[crop]
    soil = SOIL_TYPES[soil_type]
    method = IRRIGATION_METHODS[irrigation_method]

    ratings = {
        "nitrogen": _rate(nitrogen, "nitrogen"),
        "phosphorus": _rate(phosphorus, "phosphorus"),
        "potassium": _rate(potassium, "potassium"),
    }

    # The card corrects each nutrient independently: a soil can be high in
    # potassium and low in nitrogen, and a single blanket factor would miss that.
    per_acre = {
        "n": rdf["n"] / ACRES_PER_HECTARE,
        "p": rdf["p"] / ACRES_PER_HECTARE,
        "k": rdf["k"] / ACRES_PER_HECTARE,
    }
    adjusted = {
        "n": per_acre["n"] * DOSE_FACTOR[ratings["nitrogen"]] * acres,
        "p": per_acre["p"] * DOSE_FACTOR[ratings["phosphorus"]] * acres,
        "k": per_acre["k"] * DOSE_FACTOR[ratings["potassium"]] * acres,
    }
    blanket = {
        "n": per_acre["n"] * acres,
        "p": per_acre["p"] * acres,
        "k": per_acre["k"] * acres,
    }

    carrier = _phosphorus_carrier(blanket["n"], blanket["p"])
    plan = _product_plan(adjusted["n"], adjusted["p"], adjusted["k"], carrier)
    blanket_plan = _product_plan(blanket["n"], blanket["p"], blanket["k"], carrier)

    fertiliser_rows = []
    for key in ("urea", "dap", "ssp", "mop"):
        # The unused phosphorus carrier is zero in both plans; listing it would
        # put an empty row on the farmer's shopping list.
        if plan[key] == 0 and blanket_plan[key] == 0:
            continue
        product = FERTILISERS[key]
        kg = plan[key]
        fertiliser_rows.append({
            "key": key,
            "name": product["name"],
            "kg": kg,
            "bags": round(kg / product["bag_kg"], 1),
            "bag_kg": product["bag_kg"],
            "cost_inr": int(round(kg * product["price_per_bag"] / product["bag_kg"])),
            "blanket_kg": blanket_plan[key],
            "saved_kg": round(blanket_plan[key] - kg, 1),
        })

    ph_class, ph_advice, amendment_name, amendment_rate = _classify_ph(ph)
    oc_rating, fym_per_acre = _organic_carbon_rating(organic_carbon)

    # --- Irrigation schedule ---
    gross_mm = soil["depth_mm"] / method["efficiency"]
    litres_per_turn = gross_mm * LITRES_PER_MM_PER_ACRE * acres
    turns = max(1, int(round(rdf["season_days"] / soil["interval_days"])))
    season_litres = litres_per_turn * turns

    # Baseline for the water saving: the same schedule run by flood irrigation,
    # which is what the drip or sprinkler system is replacing.
    flood_mm = soil["depth_mm"] / IRRIGATION_METHODS["flood"]["efficiency"]
    flood_season_litres = flood_mm * LITRES_PER_MM_PER_ACRE * acres * turns
    water_saved = max(0.0, flood_season_litres - season_litres)

    # A Low rating raises the dose and a High rating lowers it, so the two
    # directions are reported separately. Netting them would let a nitrogen
    # correction cancel out a genuine phosphorus saving and report a negative
    # "saving", which is neither true nor useful to a farmer.
    avoided_rows = [r for r in fertiliser_rows if r["saved_kg"] > 0]
    added_rows = [r for r in fertiliser_rows if r["saved_kg"] < 0]
    fertiliser_avoided_kg = sum(r["saved_kg"] for r in avoided_rows)
    fertiliser_added_kg = sum(-r["saved_kg"] for r in added_rows)

    def _rows_cost(rows, attr):
        return sum(abs(r[attr]) * (FERTILISERS[r["key"]]["price_per_bag"] / FERTILISERS[r["key"]]["bag_kg"])
                   for r in rows)

    def _rows_co2(rows, attr):
        return sum(abs(r[attr]) * CO2_PER_KG[r["key"]] for r in rows)

    fertiliser_cost_avoided = _rows_cost(avoided_rows, "saved_kg")
    fertiliser_cost_added = _rows_cost(added_rows, "saved_kg")
    co2_saved = _rows_co2(avoided_rows, "saved_kg") + water_saved * WATER_CO2_PER_LITRE
    cost_saved = fertiliser_cost_avoided + water_saved * WATER_COST_PER_LITRE

    # --- Sustainability score ---
    # Four weighted components, each traceable to one input the farmer gave,
    # replacing the earlier score that only ever returned two possible values.
    irrigation_points = {"drip": 35, "sprinkler": 25, "flood": 8}[irrigation_method]
    carbon_points = {"High": 25, "Medium": 15, "Low": 6}[oc_rating]
    ph_points = {"Neutral": 20, "Slightly Acidic": 13, "Slightly Alkaline": 13,
                 "Strongly Acidic": 5, "Strongly Alkaline / Sodic": 5}[ph_class]
    # Fertiliser points scale with how much of the blanket dose the soil test
    # let the farmer skip: no excess to cut still earns the baseline.
    blanket_total = sum(blanket_plan.values())
    skip_share = (fertiliser_avoided_kg / blanket_total) if blanket_total > 0 else 0.0
    fertiliser_points = round(10 + min(1.0, max(0.0, skip_share / 0.25)) * 10)

    # Named for the note the page shows when a correction pushes a dose above
    # the blanket rate, so the extra spend is explained rather than hidden.
    # A dose can exceed the blanket rate for two different reasons, and the page
    # must not conflate them: either a nutrient tested Low, or cutting the
    # phosphorus dose removed the nitrogen DAP was carrying and urea has to rise
    # to hold nitrogen on target. The second happens on soils with no deficiency
    # at all, so the note cannot assume there is a Low nutrient to name.
    deficient = [key.capitalize() for key in ("nitrogen", "phosphorus", "potassium")
                 if ratings[key] == "Low"]

    score = int(min(100, irrigation_points + carbon_points + ph_points + fertiliser_points))
    if score >= 80:
        rating = "Excellent Sustainability"
    elif score >= 60:
        rating = "Good Progress"
    else:
        rating = "Needs Improvement"

    return {
        "status": "success",
        "crop": crop,
        "acres": acres,
        "soil_type": soil["label"],
        "irrigation_method": method["label"],
        "nutrients": [
            {
                "key": key,
                "label": RATING_BANDS[key]["label"],
                "value": value,
                "unit": RATING_BANDS[key]["unit"],
                "rating": ratings[key],
                "dose_factor": DOSE_FACTOR[ratings[key]],
                "low_band": RATING_BANDS[key]["low"],
                "high_band": RATING_BANDS[key]["high"],
            }
            for key, value in (("nitrogen", nitrogen), ("phosphorus", phosphorus), ("potassium", potassium))
        ],
        "fertilisers": fertiliser_rows,
        "fertiliser_total_cost_inr": int(round(_plan_cost(plan))),
        "soil_health": {
            "ph": ph,
            "ph_class": ph_class,
            "ph_advice": ph_advice,
            "amendment_name": amendment_name,
            "amendment_kg": int(round(amendment_rate * acres)) if amendment_name else 0,
            "organic_carbon": organic_carbon,
            "organic_carbon_rating": oc_rating,
            "fym_tonnes": round(fym_per_acre * acres, 1),
        },
        "irrigation": {
            "interval_days": soil["interval_days"],
            "litres_per_turn": int(round(litres_per_turn)),
            "turns_per_season": turns,
            "season_litres": int(round(season_litres)),
            "efficiency_percent": int(method["efficiency"] * 100),
            "holding": soil["holding"],
            "season_days": rdf["season_days"],
        },
        "sustainability": {
            "score": score,
            "rating": rating,
            "breakdown": [
                {"label": "Irrigation efficiency", "points": irrigation_points, "max": 35},
                {"label": "Soil organic carbon", "points": carbon_points, "max": 25},
                {"label": "Soil pH suitability", "points": ph_points, "max": 20},
                {"label": "Fertiliser precision", "points": fertiliser_points, "max": 20},
            ],
            "water_saved_litres": int(round(water_saved)),
            "fertiliser_avoided_kg": round(fertiliser_avoided_kg, 1),
            "fertiliser_added_kg": round(fertiliser_added_kg, 1),
            "correction_cost_inr": int(round(fertiliser_cost_added)),
            "deficient_nutrients": deficient,
            "correction_reason": ("deficiency" if deficient else "rebalance"),
            "co2_saved_kg": round(co2_saved, 1),
            "cost_saved_inr": int(round(cost_saved)),
        },
    }
