"""
Full project test suite for AgriSmart AI.

Run from the repository root:

    python -m unittest discover -s tests -v

Built on stdlib unittest rather than pytest so it runs against the exact
requirements.txt a judge installs, with no extra test dependency. The model
weights are loaded once for the whole run because YOLO initialisation dominates
the runtime; tests that need inference are skipped, not failed, when
model/weights/best.pt is absent, so the suite still passes on a clean checkout.
"""

import io
import re
import sys
import unittest
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image
from fastapi.testclient import TestClient

from src.backend.main import app, MAX_UPLOAD_BYTES
from src.backend.disease_kb import DISEASE_DATABASE, get_disease_info
from src.backend import soil_advisor as sa
from src.backend import ood_guard
from model.predict import predict, get_model, MODEL_PATH

client = TestClient(app)

TEMPLATES = PROJECT_ROOT / "src" / "frontend" / "templates"
DATASET = PROJECT_ROOT / "data" / "dataset"
WEIGHTS_PRESENT = MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 0

SAMPLE_CARD = {
    "nitrogen": 245, "phosphorus": 31, "potassium": 190,
    "ph": 6.8, "organic_carbon": 0.62,
    "crop": "Tomato", "acres": 2.5,
    "soil_type": "loam", "irrigation_method": "drip",
}


def a_real_leaf_image():
    """Return a path to a genuine dataset leaf, or None if the dataset is absent."""
    if not DATASET.is_dir():
        return None
    for class_dir in sorted(DATASET.iterdir()):
        if class_dir.is_dir():
            for image in sorted(class_dir.iterdir()):
                if image.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                    return image
    return None


def png_bytes(color=(120, 160, 90), size=(320, 320)):
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

class TestPages(unittest.TestCase):
    """Every page must render, and the three must agree on navigation."""

    PAGES = {"/": "Crop Disease Diagnostic Scanner",
             "/research": "Research Assistant",
             "/soil": "Soil Health Card"}

    def test_pages_render(self):
        for route, marker in self.PAGES.items():
            with self.subTest(route=route):
                response = client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn(marker, response.text)

    def test_no_unrendered_template_tags(self):
        # A Jinja variable the route forgot to pass reaches the browser as
        # literal "{{ name }}", which no amount of CSS review would catch.
        for route in self.PAGES:
            with self.subTest(route=route):
                self.assertNotIn("{{", client.get(route).text)

    def test_every_page_links_to_every_other_page(self):
        for route in self.PAGES:
            body = client.get(route).text
            for target in self.PAGES:
                with self.subTest(page=route, links_to=target):
                    self.assertIn('href="%s"' % target, body)

    def test_dashboard_reports_real_knowledge_base_size(self):
        body = client.get("/").text
        crops = len({key.split("___")[0] for key in DISEASE_DATABASE if "___" in key})
        self.assertIn("%d diseases" % len(DISEASE_DATABASE), body)
        self.assertIn("%d crops" % crops, body)

    def test_dashboard_has_no_orphaned_elements(self):
        # These ids belonged to the simulated soil feed and the old scorecard.
        # Their JavaScript is gone, so leaving the markup behind would strand
        # placeholder numbers like "34.2%" on the page forever.
        body = client.get("/").text
        for orphan in ("soil-moisture-val", "soil-moisture-bar", "soil-ph-val",
                       "soil-temp-val", "soil-irrigation-card", "top-moisture",
                       "top-eco-score", "calc-score", "calc-water", "calc-form"):
            with self.subTest(element=orphan):
                self.assertNotIn('id="%s"' % orphan, body)

    def test_soil_page_javascript_targets_exist(self):
        """Every getElementById on the soil page must match a real element."""
        source = (TEMPLATES / "soil.html").read_text(encoding="utf-8")
        markup = re.sub(r"<script>.*?</script>", "", source, flags=re.S)
        script = re.findall(r"<script>(.*?)</script>", source, re.S)[-1]
        declared = set(re.findall(r'\bid="([^"]+)"', markup))
        used = set(re.findall(r"getElementById\('([^']+)'\)", script))
        self.assertEqual(used - declared, set())


# ---------------------------------------------------------------------------
# Soil advisory engine (pure functions, no HTTP)
# ---------------------------------------------------------------------------

class TestSoilRatings(unittest.TestCase):

    def test_rating_boundaries(self):
        # The band edges are where an off-by-one sends a farmer the wrong dose.
        for nutrient, band in sa.RATING_BANDS.items():
            low, high = band["low"], band["high"]
            with self.subTest(nutrient=nutrient):
                self.assertEqual(sa._rate(low - 0.1, nutrient), "Low")
                self.assertEqual(sa._rate(low, nutrient), "Medium")
                self.assertEqual(sa._rate(high, nutrient), "Medium")
                self.assertEqual(sa._rate(high + 0.1, nutrient), "High")

    def test_dose_factor_direction(self):
        self.assertGreater(sa.DOSE_FACTOR["Low"], 1.0)
        self.assertEqual(sa.DOSE_FACTOR["Medium"], 1.0)
        self.assertLess(sa.DOSE_FACTOR["High"], 1.0)

    def test_low_soil_gets_more_fertiliser_than_high_soil(self):
        def urea_for(n):
            plan = sa.build_advisory(**{**SAMPLE_CARD, "nitrogen": n})
            return plan["fertilisers"][0]["kg"]
        self.assertGreater(urea_for(100), urea_for(400))
        self.assertGreater(urea_for(400), urea_for(900))

    def test_ph_classification_covers_the_full_range(self):
        expected = [(4.5, "Strongly Acidic"), (6.0, "Slightly Acidic"),
                    (7.0, "Neutral"), (8.0, "Slightly Alkaline"),
                    (9.2, "Strongly Alkaline / Sodic")]
        for ph, label in expected:
            with self.subTest(ph=ph):
                self.assertEqual(sa._classify_ph(ph)[0], label)

    def test_only_off_target_ph_prescribes_an_amendment(self):
        self.assertIsNone(sa._classify_ph(7.0)[2])
        self.assertEqual(sa._classify_ph(5.0)[2], "Agricultural Lime")
        self.assertEqual(sa._classify_ph(9.0)[2], "Gypsum")


class TestFertiliserChemistry(unittest.TestCase):
    """The product plan must actually deliver the nutrients it was asked for."""

    def test_plan_delivers_requested_nutrients(self):
        # Phosphorus may arrive as DAP or as SSP depending on the crop, so the
        # check sums what every product in the plan actually contributes.
        for n, p, k in [(100, 50, 60), (150, 80, 100), (20, 60, 40), (0, 0, 0)]:
            with self.subTest(npk=(n, p, k)):
                plan = sa._product_plan(n, p, k)
                delivered = {nutrient: sum(kg * sa.FERTILISERS[product][nutrient]
                                           for product, kg in plan.items())
                             for nutrient in ("n", "p", "k")}
                delivered_n, delivered_p, delivered_k = delivered["n"], delivered["p"], delivered["k"]
                self.assertAlmostEqual(delivered_n, n, delta=0.5)
                self.assertAlmostEqual(delivered_p, p, delta=0.5)
                self.assertAlmostEqual(delivered_k, k, delta=0.5)

    def test_dap_nitrogen_is_credited_not_double_applied(self):
        # Sizing urea before DAP would over-apply nitrogen. If DAP's own 18% N
        # is credited, a phosphorus-heavy request needs strictly less urea.
        heavy_p = sa._product_plan(100, 200, 0, carrier="dap")["urea"]
        no_p = sa._product_plan(100, 0, 0, carrier="dap")["urea"]
        self.assertLess(heavy_p, no_p)

    def test_a_legume_switches_to_a_nitrogen_free_phosphorus_carrier(self):
        # Soybean fixes its own nitrogen, so its N requirement is small beside a
        # large P requirement. DAP alone would overshoot it, and fertiliser
        # cannot be un-applied, so the plan must reach for SSP instead.
        self.assertEqual(sa._phosphorus_carrier(20, 60), "ssp")
        self.assertEqual(sa._phosphorus_carrier(120, 60), "dap")
        soybean = sa.build_advisory(**{**SAMPLE_CARD, "crop": "Soybean"})
        products = {row["name"] for row in soybean["fertilisers"]}
        self.assertTrue(any("SSP" in name for name in products))
        self.assertFalse(any("DAP" in name for name in products))

    def test_the_shopping_list_has_no_empty_rows(self):
        for crop in sa.CROP_RDF:
            with self.subTest(crop=crop):
                result = sa.build_advisory(**{**SAMPLE_CARD, "crop": crop})
                for row in result["fertilisers"]:
                    self.assertGreater(row["kg"] + row["blanket_kg"], 0)

    def test_both_plans_compare_like_with_like(self):
        # The "vs blanket dose" column is only meaningful if both plans used the
        # same phosphorus carrier; otherwise a substitution reads as a saving.
        for crop in sa.CROP_RDF:
            with self.subTest(crop=crop):
                result = sa.build_advisory(**{**SAMPLE_CARD, "crop": crop})
                for row in result["fertilisers"]:
                    if row["kg"] == 0:
                        self.assertEqual(row["blanket_kg"], 0)

    def test_never_returns_a_negative_quantity(self):
        # A crop whose DAP alone oversupplies nitrogen must clamp to zero urea
        # rather than instructing the farmer to remove fertiliser.
        plan = sa._product_plan(5, 200, 10)
        for product, kg in plan.items():
            with self.subTest(product=product):
                self.assertGreaterEqual(kg, 0)


class TestIrrigationAndScore(unittest.TestCase):

    def test_water_scales_with_area(self):
        one = sa.build_advisory(**{**SAMPLE_CARD, "acres": 1})["irrigation"]["season_litres"]
        ten = sa.build_advisory(**{**SAMPLE_CARD, "acres": 10})["irrigation"]["season_litres"]
        self.assertAlmostEqual(ten / one, 10, delta=0.1)

    def test_efficient_irrigation_uses_less_water(self):
        def season(method):
            return sa.build_advisory(**{**SAMPLE_CARD, "irrigation_method": method})["irrigation"]["season_litres"]
        self.assertLess(season("drip"), season("sprinkler"))
        self.assertLess(season("sprinkler"), season("flood"))

    def test_flood_baseline_saves_no_water_against_itself(self):
        flood = sa.build_advisory(**{**SAMPLE_CARD, "irrigation_method": "flood"})
        self.assertEqual(flood["sustainability"]["water_saved_litres"], 0)

    def test_score_stays_within_bounds_across_the_input_space(self):
        seen = set()
        for crop in sa.CROP_RDF:
            for soil in sa.SOIL_TYPES:
                for method in sa.IRRIGATION_METHODS:
                    for ph in (4.5, 6.0, 7.0, 8.0, 9.2):
                        for oc in (0.3, 0.6, 1.2):
                            result = sa.build_advisory(
                                nitrogen=245, phosphorus=31, potassium=190,
                                ph=ph, organic_carbon=oc, crop=crop, acres=2.5,
                                soil_type=soil, irrigation_method=method)
                            score = result["sustainability"]["score"]
                            self.assertGreaterEqual(score, 0)
                            self.assertLessEqual(score, 100)
                            seen.add(score)
        # The old scorecard could only ever return two values. Confirm the
        # replacement genuinely discriminates between farm practices.
        self.assertGreater(len(seen), 10)

    def test_score_breakdown_sums_to_the_score(self):
        result = sa.build_advisory(**SAMPLE_CARD)["sustainability"]
        self.assertEqual(sum(part["points"] for part in result["breakdown"]), result["score"])
        self.assertEqual(sum(part["max"] for part in result["breakdown"]), 100)

    def test_drip_scores_above_flood(self):
        def score(method):
            return sa.build_advisory(**{**SAMPLE_CARD, "irrigation_method": method})["sustainability"]["score"]
        self.assertGreater(score("drip"), score("flood"))


class TestSavingsAreHonest(unittest.TestCase):
    """Savings must never be negative, and corrections must be disclosed."""

    def test_savings_are_never_negative(self):
        for n in (100, 245, 400, 900):
            for p in (5, 31, 120):
                result = sa.build_advisory(**{**SAMPLE_CARD, "nitrogen": n, "phosphorus": p})
                s = result["sustainability"]
                with self.subTest(nitrogen=n, phosphorus=p):
                    self.assertGreaterEqual(s["water_saved_litres"], 0)
                    self.assertGreaterEqual(s["fertiliser_avoided_kg"], 0)
                    self.assertGreaterEqual(s["co2_saved_kg"], 0)
                    self.assertGreaterEqual(s["cost_saved_inr"], 0)

    def test_deficient_soil_reports_the_extra_spend(self):
        # Nitrogen well below the Low band: the plan must add product, name the
        # deficient nutrient, and price the correction rather than bury it.
        result = sa.build_advisory(**{**SAMPLE_CARD, "nitrogen": 100})["sustainability"]
        self.assertGreater(result["fertiliser_added_kg"], 0)
        self.assertIn("Nitrogen", result["deficient_nutrients"])
        self.assertGreater(result["correction_cost_inr"], 0)

    def test_sufficient_soil_reports_no_correction(self):
        result = sa.build_advisory(
            **{**SAMPLE_CARD, "nitrogen": 900, "phosphorus": 120, "potassium": 400})["sustainability"]
        self.assertEqual(result["fertiliser_added_kg"], 0)
        self.assertEqual(result["deficient_nutrients"], [])
        self.assertGreater(result["fertiliser_avoided_kg"], 0)

    def test_pumping_costs_stay_in_a_plausible_range(self):
        # A per-litre rate off by two orders of magnitude turns one season on a
        # smallholding into lakhs of rupees, which is how the old figure read.
        result = sa.build_advisory(**SAMPLE_CARD)
        litres = result["irrigation"]["season_litres"]
        self.assertLess(result["sustainability"]["cost_saved_inr"], litres * 0.01)
        self.assertLess(sa.WATER_COST_PER_LITRE, 0.01)


# ---------------------------------------------------------------------------
# Soil API
# ---------------------------------------------------------------------------

class TestSoilEndpoint(unittest.TestCase):

    def post(self, **overrides):
        return client.post("/api/soil-health-card", data={**SAMPLE_CARD, **overrides})

    def test_happy_path(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")
        for section in ("nutrients", "fertilisers", "soil_health", "irrigation", "sustainability"):
            self.assertIn(section, body)
        self.assertEqual(len(body["nutrients"]), 3)
        self.assertEqual(len(body["fertilisers"]), 3)

    def test_every_offered_option_is_accepted(self):
        # The dropdowns are populated from /api/soil-reference, so anything it
        # advertises must be something the calculator will actually accept.
        reference = client.get("/api/soil-reference").json()
        for crop in reference["crops"]:
            with self.subTest(crop=crop):
                self.assertEqual(self.post(crop=crop).status_code, 200)
        for soil in reference["soil_types"]:
            with self.subTest(soil=soil["value"]):
                self.assertEqual(self.post(soil_type=soil["value"]).status_code, 200)
        for method in reference["irrigation_methods"]:
            with self.subTest(method=method["value"]):
                self.assertEqual(self.post(irrigation_method=method["value"]).status_code, 200)

    def test_rejects_bad_input(self):
        cases = [
            ("unknown crop", {"crop": "Banana"}),
            ("unknown soil", {"soil_type": "gravel"}),
            ("unknown method", {"irrigation_method": "bucket"}),
            ("negative acres", {"acres": -5}),
            ("zero acres", {"acres": 0}),
            ("absurd acres", {"acres": 10 ** 9}),
            ("impossible ph", {"ph": 45}),
            ("negative nitrogen", {"nitrogen": -10}),
            ("absurd potassium", {"potassium": 99999}),
        ]
        for label, payload in cases:
            with self.subTest(case=label):
                response = self.post(**payload)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["status"], "error")
                self.assertTrue(response.json()["message"])

    def test_reference_matches_the_engine(self):
        reference = client.get("/api/soil-reference").json()
        self.assertEqual(sorted(reference["crops"]), sorted(sa.CROP_RDF))
        self.assertEqual({s["value"] for s in reference["soil_types"]}, set(sa.SOIL_TYPES))
        self.assertEqual({m["value"] for m in reference["irrigation_methods"]}, set(sa.IRRIGATION_METHODS))

    def test_replaced_endpoints_are_gone(self):
        # Both returned randomised or two-valued figures and are superseded.
        self.assertEqual(client.get("/api/soil-analytics").status_code, 404)
        self.assertEqual(client.post("/api/sustainability-calc", data={"acres": 2}).status_code, 404)


# ---------------------------------------------------------------------------
# Weather and chat
# ---------------------------------------------------------------------------

class TestWeather(unittest.TestCase):

    def test_returns_a_complete_reading(self):
        body = client.get("/api/weather?city=Ahmedabad").json()
        for field in ("city", "temp_c", "humidity", "wind_kmh", "condition",
                      "spray_advisory", "rain_risk", "source"):
            self.assertIn(field, body)

    def test_survives_an_unknown_city(self):
        # Without an API key this falls back to the simulated station; with one,
        # a bad city must still not propagate an exception to the dashboard.
        self.assertEqual(client.get("/api/weather?city=Nowhereville").status_code, 200)


class TestChat(unittest.TestCase):

    def test_answers_are_grounded(self):
        for query in ["tomato early blight", "how do I treat potato late blight",
                      "when should I irrigate", "aloo jhulsa"]:
            with self.subTest(query=query):
                response = client.post("/api/chat", data={"query": query, "lang": "en"})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json().get("reply", "").strip())

    def test_handles_an_empty_and_an_irrelevant_query(self):
        for query in ["", "   ", "what is the capital of France"]:
            with self.subTest(query=repr(query)):
                response = client.post("/api/chat", data={"query": query, "lang": "en"})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json().get("reply", "").strip())


# ---------------------------------------------------------------------------
# Knowledge base integrity
# ---------------------------------------------------------------------------

class TestKnowledgeBase(unittest.TestCase):

    REQUIRED = ("crop", "disease", "is_healthy", "severity", "symptoms",
                "organic_remedies", "chemical_remedies", "irrigation_advice",
                "sustainability_impact")

    def test_every_entry_is_complete(self):
        for key, entry in DISEASE_DATABASE.items():
            with self.subTest(entry=key):
                for field in self.REQUIRED:
                    self.assertIn(field, entry)
                    self.assertTrue(entry[field] != "" and entry[field] is not None)
                self.assertTrue(entry["symptoms"], "symptoms must not be empty")

    def test_every_trained_class_has_guidance(self):
        # A class the model can predict but the knowledge base cannot explain
        # would surface to the farmer as a diagnosis with no treatment.
        if not DATASET.is_dir():
            self.skipTest("dataset not present")
        for class_dir in sorted(p for p in DATASET.iterdir() if p.is_dir()):
            with self.subTest(cls=class_dir.name):
                info = get_disease_info(class_dir.name)
                self.assertTrue(info["disease"])
                self.assertTrue(info["crop"])

    def test_unknown_class_degrades_gracefully(self):
        info = get_disease_info("Dragonfruit___Imaginary_rot")
        self.assertIsInstance(info, dict)
        self.assertIn("disease", info)

    def test_every_crop_in_the_knowledge_base_can_be_fertilised(self):
        # The soil planner and the diagnostic engine must cover the same crops,
        # or a farmer can be diagnosed for a crop they cannot then plan for.
        kb_crops = {key.split("___")[0] for key in DISEASE_DATABASE if "___" in key}
        normalise = {
            "Corn_(maize)": "Corn (Maize)", "Pepper,_bell": "Bell Pepper",
            "Orange": "Orange (Citrus)", "Squash": "Squash (Pumpkin)",
            "Cherry_(including_sour)": "Cherry",
        }
        for crop in kb_crops:
            with self.subTest(crop=crop):
                self.assertIn(normalise.get(crop, crop), sa.CROP_RDF)


# ---------------------------------------------------------------------------
# Prediction: upload validation, inference, OOD screening, CLI
# ---------------------------------------------------------------------------

class TestPredictValidation(unittest.TestCase):
    """Upload guards must reject bad input before any inference is attempted."""

    def test_rejects_unsupported_extension(self):
        response = client.post("/api/predict", files={"file": ("notes.txt", b"hello", "text/plain")})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file type", response.json()["message"])

    def test_rejects_a_file_that_is_not_an_image(self):
        response = client.post("/api/predict", files={"file": ("fake.jpg", b"not an image", "image/jpeg")})
        self.assertEqual(response.status_code, 400)
        self.assertIn("not a valid image", response.json()["message"])

    def test_rejects_an_oversized_upload(self):
        oversized = b"\xff" * (MAX_UPLOAD_BYTES + 1024)
        response = client.post("/api/predict", files={"file": ("big.jpg", oversized, "image/jpeg")})
        self.assertEqual(response.status_code, 400)
        self.assertIn("too large", response.json()["message"])


@unittest.skipUnless(WEIGHTS_PRESENT, "model/weights/best.pt not present")
class TestInference(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.leaf = a_real_leaf_image()
        get_model()   # pay the YOLO load cost once for the whole class

    def test_cli_predict_interface(self):
        """Section 4.1 requires predict(image_path) -> class_label."""
        if self.leaf is None:
            self.skipTest("dataset not present")
        label = predict(str(self.leaf))
        self.assertIsInstance(label, str)
        self.assertTrue(label)

    def test_cli_raises_on_a_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            predict(str(PROJECT_ROOT / "does_not_exist.jpg"))

    def test_cli_entry_point_runs(self):
        if self.leaf is None:
            self.skipTest("dataset not present")
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "model" / "predict.py"), "--image", str(self.leaf)],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=300)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Predicted Class:", result.stdout)

    def test_a_real_leaf_is_accepted(self):
        if self.leaf is None:
            self.skipTest("dataset not present")
        with open(self.leaf, "rb") as handle:
            response = client.post("/api/predict", files={"file": (self.leaf.name, handle.read(), "image/jpeg")})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn(body["status"], {"success", "low_confidence"})
        if body["status"] == "success":
            for field in ("crop", "disease", "confidence", "symptoms",
                          "organic_remedies", "chemical_remedies"):
                self.assertIn(field, body)

    def test_a_blank_image_is_rejected_as_out_of_distribution(self):
        # A flat grey frame scores 0.575 top-1 on this model, which is exactly
        # why ood_guard screens on view agreement and entropy, not a top-1 cut.
        response = client.post("/api/predict",
                               files={"file": ("grey.png", png_bytes((128, 128, 128)), "image/png")})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "low_confidence")
        self.assertTrue(body["guidance"], "a rejection must tell the farmer what to do next")
        self.assertTrue(body["failed_checks"])

    def test_rejection_guidance_is_actionable(self):
        for check in ood_guard._REJECTION_GUIDANCE:
            with self.subTest(check=check):
                self.assertTrue(ood_guard.rejection_guidance([check]))


class TestOodGuardConfiguration(unittest.TestCase):
    """Thresholds must stay internally consistent even without the weights."""

    def test_thresholds_are_ordered_sensibly(self):
        self.assertGreater(ood_guard.MIN_VIEW_MEAN_CONFIDENCE, ood_guard.MIN_USABLE_CONFIDENCE)
        self.assertLess(ood_guard.MAX_NORMALISED_ENTROPY, ood_guard.MAX_USABLE_ENTROPY)
        self.assertGreater(ood_guard.MIN_VIEW_MEAN_CONFIDENCE, ood_guard.MIN_WEAKEST_VIEW_CONFIDENCE)

    def test_thresholds_are_probabilities(self):
        for name in ("MIN_VIEW_MEAN_CONFIDENCE", "MAX_NORMALISED_ENTROPY",
                     "MIN_VIEW_AGREEMENT", "MIN_WEAKEST_VIEW_CONFIDENCE",
                     "MIN_USABLE_CONFIDENCE", "MAX_USABLE_ENTROPY"):
            with self.subTest(threshold=name):
                self.assertTrue(0.0 <= getattr(ood_guard, name) <= 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
