# Comprehensive Agricultural Disease Knowledge Base & Precautionary Guidance
# Strictly satisfying Section 3.1 & 4.1 of the Hackathon requirements
#
# Every key below matches a class label emitted by the trained PlantVillage model
# exactly, so get_disease_info() resolves without falling back to generic advice.

DISEASE_DATABASE = {

    # ---------------------------------------------------------------- APPLE
    "Apple___Apple_scab": {
        "crop": "Apple",
        "disease": "Apple Scab (Venturia inaequalis)",
        "is_healthy": False,
        "severity": "Moderate to High",
        "symptoms": [
            "Olive-green to velvety brown lesions on leaves and young fruit",
            "Lesions darken and the leaf puckers or twists around them",
            "Severely affected fruit becomes deformed, cracked, and unmarketable"
        ],
        "organic_remedies": [
            "Rake and destroy all fallen leaves in winter to remove the overwintering inoculum",
            "Apply lime sulphur or wettable sulphur at green-tip and pink-bud stages",
            "Prune the canopy open so leaves dry quickly after rain"
        ],
        "chemical_remedies": [
            "Dodine 65% WP @ 0.75g per litre at green-tip stage",
            "Mancozeb 75% WP @ 2.5g per litre repeated at 10-12 day intervals during wet spells"
        ],
        "irrigation_advice": "Use basin or drip irrigation. Never wet the canopy, as scab needs several hours of leaf wetness to infect.",
        "sustainability_impact": "Winter sanitation removes the primary inoculum and can cut the season's spray count by half."
    },
    "Apple___Black_rot": {
        "crop": "Apple",
        "disease": "Black Rot (Botryosphaeria obtusa)",
        "is_healthy": False,
        "severity": "Moderate to High",
        "symptoms": [
            "Purple-bordered 'frog-eye' leaf spots with tan centres",
            "Firm, dark, concentrically zoned rot on the fruit, often starting at the calyx",
            "Sunken reddish-brown cankers on branches that crack and kill the limb"
        ],
        "organic_remedies": [
            "Prune out cankered wood 20-30cm below the visible margin and burn it",
            "Remove all mummified fruit left hanging in the tree",
            "Apply copper oxychloride at bud swell as a protectant"
        ],
        "chemical_remedies": [
            "Captan 50% WP @ 2g per litre during fruit development",
            "Thiophanate-methyl 70% WP @ 1g per litre for canker management"
        ],
        "irrigation_advice": "Avoid water stress, which predisposes limbs to canker. Maintain steady soil moisture through drip.",
        "sustainability_impact": "Removing cankers and mummies is a one-time labour cost that eliminates the inoculum source for several seasons."
    },
    "Apple___Cedar_apple_rust": {
        "crop": "Apple",
        "disease": "Cedar Apple Rust (Gymnosporangium juniperi-virginianae)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "Bright yellow-orange spots on the upper leaf surface, often with a red border",
            "Tube-like or hair-like fungal structures on the underside beneath each spot",
            "Premature leaf drop and distorted, blemished fruit in heavy infections"
        ],
        "organic_remedies": [
            "Remove nearby juniper or cedar hosts within a few hundred metres if possible",
            "Cut galls out of juniper hosts in winter before they release spores",
            "Apply sulphur sprays from pink bud through to early fruit set"
        ],
        "chemical_remedies": [
            "Myclobutanil 10% WP @ 1g per litre at pink bud",
            "Propiconazole 25% EC @ 1ml per litre during the spring spore-release period"
        ],
        "irrigation_advice": "Keep foliage dry in spring. Spores germinate only in prolonged leaf wetness during warm rain.",
        "sustainability_impact": "This rust cannot complete its life cycle without a juniper host, so host removal replaces fungicide entirely."
    },
    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Uniform deep-green leaves, no lesions, spotting, rust pustules, or premature drop"],
        "organic_remedies": [
            "Maintain annual compost or farmyard manure application around the drip line",
            "Prune for an open canopy each dormant season to sustain airflow"
        ],
        "chemical_remedies": ["None required. Avoid unnecessary prophylactic chemical sprays."],
        "irrigation_advice": "Maintain soil moisture with organic wood-chip mulching.",
        "sustainability_impact": "Mulching conserves 30% orchard water consumption."
    },

    # ------------------------------------------------------------ BLUEBERRY
    "Blueberry___healthy": {
        "crop": "Blueberry",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Glossy green leaves with no spotting, mottling, or marginal scorch"],
        "organic_remedies": [
            "Maintain acidic soil pH between 4.5 and 5.5 using pine-needle or sawdust mulch",
            "Top-dress with well-rotted organic matter before flowering"
        ],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Blueberries are shallow-rooted. Keep the top 30cm consistently moist with drip irrigation.",
        "sustainability_impact": "Organic mulch maintains soil acidity naturally, avoiding repeated acidifier applications."
    },

    # --------------------------------------------------------------- CHERRY
    "Cherry_(including_sour)___Powdery_mildew": {
        "crop": "Cherry",
        "disease": "Powdery Mildew (Podosphaera clandestina)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "White powdery fungal patches on young leaves and shoot tips",
            "Leaves curl, blister, and become distorted as they expand",
            "Light-coloured russeting or webbing on the fruit surface near harvest"
        ],
        "organic_remedies": [
            "Spray potassium bicarbonate (5g/L) with a wetting agent at first appearance",
            "Apply wettable sulphur, avoiding application above 30C to prevent leaf burn",
            "Prune out water sprouts, which are the most susceptible tissue"
        ],
        "chemical_remedies": [
            "Myclobutanil 10% WP @ 1g per litre",
            "Trifloxystrobin 25% WG @ 0.4g per litre, rotating actives to avoid resistance"
        ],
        "irrigation_advice": "Unlike most fungi, powdery mildew does not need leaf wetness. Focus on canopy airflow rather than dryness.",
        "sustainability_impact": "Bicarbonate and sulphur are low-toxicity and permitted in organic certification, protecting pollinators."
    },
    "Cherry_(including_sour)___healthy": {
        "crop": "Cherry",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Clean green foliage with no powdery coating, curling, or leaf spotting"],
        "organic_remedies": [
            "Maintain an open canopy through dormant pruning",
            "Apply balanced compost in early spring"
        ],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Irrigate deeply but infrequently. Avoid waterlogging, which cherries tolerate poorly.",
        "sustainability_impact": "Healthy pruned canopies need fewer fungicide rounds across the season."
    },

    # ----------------------------------------------------------------- CORN
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "crop": "Corn (Maize)",
        "disease": "Gray Leaf Spot (Cercospora zeae-maydis)",
        "is_healthy": False,
        "severity": "High",
        "symptoms": [
            "Narrow rectangular grey to tan lesions running parallel to the leaf veins",
            "Lesions have sharply squared-off edges because the veins confine them",
            "Heavy infection merges lesions, blighting the whole leaf and weakening the stalk"
        ],
        "organic_remedies": [
            "Rotate out of maize for at least one season; the fungus survives on maize residue",
            "Plough or remove infected stubble rather than leaving it on the surface",
            "Sow resistant hybrids where available and widen row spacing for airflow"
        ],
        "chemical_remedies": [
            "Azoxystrobin 23% SC @ 1ml per litre at early tasselling",
            "Pyraclostrobin + Epoxiconazole applied between tasselling and silking"
        ],
        "irrigation_advice": "Irrigate at the base in the early morning. Extended humidity in a dense canopy drives this disease.",
        "sustainability_impact": "Crop rotation and residue management control this disease without any fungicide input."
    },
    "Corn_(maize)___Common_rust_": {
        "crop": "Corn (Maize)",
        "disease": "Common Rust (Puccinia sorghi)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "Small cinnamon-brown powdery pustules scattered on both leaf surfaces",
            "Pustules rupture the leaf surface and darken to brownish-black as the crop matures",
            "Severe infection yellows the leaf and reduces grain filling"
        ],
        "organic_remedies": [
            "Sow resistant hybrids, which is the single most effective measure",
            "Avoid staggered or very late sowing that exposes young plants to heavy spore loads",
            "Maintain balanced potassium nutrition to strengthen leaf tissue"
        ],
        "chemical_remedies": [
            "Mancozeb 75% WP @ 2.5g per litre at first pustule appearance",
            "Propiconazole 25% EC @ 1ml per litre if infection reaches the ear leaf before silking"
        ],
        "irrigation_advice": "Irrigate in the early morning so leaves dry quickly in sunlight.",
        "sustainability_impact": "Resistant hybrid selection removes the need for rust fungicide in most seasons."
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "crop": "Corn (Maize)",
        "disease": "Northern Leaf Blight (Exserohilum turcicum)",
        "is_healthy": False,
        "severity": "High",
        "symptoms": [
            "Long cigar-shaped or elliptical grey-green lesions, often 3-15cm long",
            "Lesions turn tan and may show dark zones of spore production in humid weather",
            "Infection starts on lower leaves and moves upward toward the ear leaf"
        ],
        "organic_remedies": [
            "Rotate with a non-host crop such as pulses for at least one season",
            "Bury infected residue by deep ploughing to break the disease cycle",
            "Choose hybrids carrying Ht resistance genes"
        ],
        "chemical_remedies": [
            "Mancozeb 75% WP @ 2.5g per litre on appearance of the first lesions",
            "Azoxystrobin + Difenoconazole @ 1ml per litre before the disease reaches the ear leaf"
        ],
        "irrigation_advice": "Avoid overhead irrigation. This fungus requires 6-18 hours of continuous leaf wetness to infect.",
        "sustainability_impact": "Protecting the ear leaf alone preserves most of the yield, so a single well-timed spray beats repeated blanket cover."
    },
    "Corn_(maize)___healthy": {
        "crop": "Corn (Maize)",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Upright deep-green leaves with no pustules, streaks, or elongated lesions"],
        "organic_remedies": [
            "Maintain crop rotation with legumes to sustain soil nitrogen",
            "Incorporate farmyard manure before sowing"
        ],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Maintain adequate moisture at the critical tasselling and silking stages.",
        "sustainability_impact": "Legume rotation fixes soil nitrogen and reduces urea requirement in the following season."
    },

    # ---------------------------------------------------------------- GRAPE
    "Grape___Black_rot": {
        "crop": "Grape",
        "disease": "Black Rot (Guignardia bidwellii)",
        "is_healthy": False,
        "severity": "High",
        "symptoms": [
            "Circular tan leaf spots with a dark brown margin and tiny black dots inside",
            "Berries develop a pale spot, then rot, shrivel, and harden into black mummies",
            "Elongated dark lesions on shoots and tendrils"
        ],
        "organic_remedies": [
            "Remove every mummified berry from the vine and the ground during dormancy",
            "Prune for an open canopy so that clusters dry rapidly after rain",
            "Apply copper-based protectant sprays before predicted rain events"
        ],
        "chemical_remedies": [
            "Mancozeb 75% WP @ 2g per litre from bud break to fruit set",
            "Myclobutanil 10% WP @ 1g per litre during the critical bloom period"
        ],
        "irrigation_advice": "Use drip irrigation exclusively. Berries are most susceptible from bloom until about four weeks after fruit set.",
        "sustainability_impact": "Dormant-season mummy removal is the highest-value non-chemical intervention in the vineyard."
    },
    "Grape___Esca_(Black_Measles)": {
        "crop": "Grape",
        "disease": "Esca / Black Measles (Phaeomoniella chlamydospora)",
        "is_healthy": False,
        "severity": "Severe",
        "symptoms": [
            "Tiger-stripe pattern of yellow or red bands between the veins on leaves",
            "Small dark spots or 'measles' on the berry skin, which may crack",
            "Sudden collapse (apoplexy) of an entire vine arm in hot weather"
        ],
        "organic_remedies": [
            "Prune late in the dormant season when infection pressure is lowest",
            "Seal large pruning wounds immediately with a protective paste",
            "Remove and burn vines showing apoplexy; the trunk wood is colonised"
        ],
        "chemical_remedies": [
            "No curative chemical treatment exists for established infections",
            "Apply a wound protectant such as thiophanate-methyl paste after pruning"
        ],
        "irrigation_advice": "Avoid water stress, which triggers the sudden apoplectic collapse in established infections.",
        "sustainability_impact": "Because no cure exists, pruning-wound hygiene is the only durable control and costs nothing but timing."
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": "Grape",
        "disease": "Isariopsis Leaf Spot (Pseudocercospora vitis)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "Irregular dark brown to blackish angular spots on mature leaves",
            "Spots enlarge and merge, giving a scorched appearance",
            "Heavy defoliation late in the season reduces sugar accumulation in the fruit"
        ],
        "organic_remedies": [
            "Collect and destroy fallen leaves that carry the fungus over winter",
            "Improve canopy ventilation through summer pruning",
            "Apply Bordeaux mixture (1%) after the monsoon sets in"
        ],
        "chemical_remedies": [
            "Mancozeb 75% WP @ 2g per litre",
            "Copper oxychloride 50% WP @ 3g per litre at 15 day intervals in wet weather"
        ],
        "irrigation_advice": "Keep foliage dry. This disease intensifies during prolonged monsoon humidity.",
        "sustainability_impact": "Protecting late-season leaves preserves sugar accumulation and fruit quality without extra inputs."
    },
    "Grape___healthy": {
        "crop": "Grape",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Uniform green leaves, no interveinal striping, angular spots, or berry lesions"],
        "organic_remedies": [
            "Maintain canopy management and leaf removal around fruit zones",
            "Apply compost and maintain balanced potassium nutrition"
        ],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Use regulated deficit irrigation after veraison to concentrate fruit sugars.",
        "sustainability_impact": "Deficit irrigation at the right stage saves water while improving fruit quality."
    },

    # --------------------------------------------------------------- ORANGE
    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": "Orange",
        "disease": "Huanglongbing / Citrus Greening (Candidatus Liberibacter asiaticus)",
        "is_healthy": False,
        "severity": "Critical",
        "symptoms": [
            "Blotchy asymmetric yellow mottling that does not mirror across the leaf midrib",
            "Yellow shoots on an otherwise green tree, and corky enlarged leaf veins",
            "Small lopsided fruit that stays green at the bottom, with bitter juice and aborted seeds"
        ],
        "organic_remedies": [
            "Remove and destroy infected trees promptly; they act as a reservoir for the vector",
            "Control the Asian citrus psyllid vector using yellow sticky traps and neem oil sprays",
            "Plant only certified disease-free nursery stock"
        ],
        "chemical_remedies": [
            "No cure exists. Management targets the psyllid vector",
            "Imidacloprid 17.8% SL @ 0.3ml per litre as a soil drench against psyllid nymphs"
        ],
        "irrigation_advice": "Maintain steady irrigation and nutrition to prolong the productive life of infected trees.",
        "sustainability_impact": "Vector control and certified planting material are the only durable defences; early tree removal protects the whole orchard."
    },

    # ---------------------------------------------------------------- PEACH
    "Peach___Bacterial_spot": {
        "crop": "Peach",
        "disease": "Bacterial Spot (Xanthomonas arboricola pv. pruni)",
        "is_healthy": False,
        "severity": "Moderate to High",
        "symptoms": [
            "Small angular purple-black leaf spots whose centres fall out, giving a shot-hole look",
            "Sunken dark pits and cracks on the fruit surface",
            "Premature yellowing and heavy leaf drop in wet, windy seasons"
        ],
        "organic_remedies": [
            "Plant tolerant cultivars, as bacterial diseases resist curative treatment",
            "Establish windbreaks; wind-driven rain and sand abrasion spread the bacterium",
            "Apply copper sprays at low rates during dormancy"
        ],
        "chemical_remedies": [
            "Copper oxychloride at dormancy; use reduced rates in season to avoid phytotoxicity",
            "Streptomycin-based bactericide where locally approved for use"
        ],
        "irrigation_advice": "Avoid overhead irrigation entirely. Splashing water is the primary means of bacterial spread.",
        "sustainability_impact": "Windbreaks reduce both disease spread and orchard water loss through evaporation."
    },
    "Peach___healthy": {
        "crop": "Peach",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Long narrow green leaves with no shot-holes, spotting, or marginal necrosis"],
        "organic_remedies": [
            "Apply balanced compost in early spring",
            "Thin fruit appropriately to avoid limb stress"
        ],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Maintain consistent moisture during fruit swell; drought at this stage reduces fruit size sharply.",
        "sustainability_impact": "Correct fruit thinning improves size and market value without additional inputs."
    },

    # ----------------------------------------------------------- BELL PEPPER
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper",
        "disease": "Bacterial Spot (Xanthomonas campestris pv. vesicatoria)",
        "is_healthy": False,
        "severity": "High",
        "symptoms": [
            "Small water-soaked spots that become brown and angular, bounded by leaf veins",
            "Yellow halo around older spots, followed by heavy leaf drop",
            "Raised scabby or corky lesions on the fruit that destroy market value"
        ],
        "organic_remedies": [
            "Use certified disease-free seed, or treat seed in hot water at 50C for 25 minutes",
            "Rotate away from peppers and tomatoes for two to three years",
            "Apply copper hydroxide tank-mixed with mancozeb as a protectant"
        ],
        "chemical_remedies": [
            "Copper oxychloride 50% WP @ 3g per litre at 7-10 day intervals",
            "Streptocycline @ 0.5g per 10 litres combined with copper where locally approved"
        ],
        "irrigation_advice": "Switch to drip irrigation. Never work among wet plants, as handling spreads the bacterium directly.",
        "sustainability_impact": "Hot-water seed treatment costs almost nothing and prevents introducing the pathogen to a clean field."
    },
    "Pepper,_bell___healthy": {
        "crop": "Bell Pepper",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Broad glossy dark-green leaves with no angular spotting or fruit lesions"],
        "organic_remedies": [
            "Apply vermicompost at transplanting and again before flowering",
            "Mulch to stabilise soil moisture and suppress weeds"
        ],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Keep moisture even. Fluctuation between dry and wet triggers blossom-end rot in the fruit.",
        "sustainability_impact": "Mulching reduces irrigation frequency by roughly a third and suppresses weed competition."
    },

    # --------------------------------------------------------------- POTATO
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight (Alternaria solani)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "Small circular brown spots expanding into concentric rings on lower leaves",
            "Yellowing around lesions and premature senescence of the lower canopy",
            "Dark sunken dry lesions on tubers with a distinct raised margin"
        ],
        "organic_remedies": [
            "Rotate with non-solanaceous crops such as maize or beans for at least two seasons",
            "Spray Trichoderma viride bio-fungicide @ 5g per litre as a preventive foliar drench",
            "Remove and destroy infected lower leaves early in the epidemic"
        ],
        "chemical_remedies": [
            "Azoxystrobin 23% SC @ 1ml per litre",
            "Difenoconazole 25% EC @ 0.5ml per litre at 10-14 day intervals"
        ],
        "irrigation_advice": "Avoid overhead watering during cloudy or humid weather. Irrigate early so foliage dries by evening.",
        "sustainability_impact": "Maintaining adequate nitrogen delays early blight naturally, since stressed plants are colonised first."
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight (Phytophthora infestans)",
        "is_healthy": False,
        "severity": "Critical",
        "symptoms": [
            "Water-soaked grey-green blotches spreading rapidly from the leaf margins",
            "White downy fungal growth on the leaf underside in humid mornings",
            "Reddish-brown granular dry rot spreading inward from the tuber surface"
        ],
        "organic_remedies": [
            "Destroy all volunteer potato plants and cull piles, which harbour the pathogen",
            "Apply Bordeaux mixture (1%) preventively before forecast rain",
            "Earth up ridges well so spores cannot wash down onto developing tubers"
        ],
        "chemical_remedies": [
            "Metalaxyl + Mancozeb @ 2.5g per litre at the first sign of infection",
            "Cymoxanil + Mancozeb @ 3g per litre, repeated at 7 day intervals in an active epidemic"
        ],
        "irrigation_advice": "Stop all overhead irrigation immediately. Under cool, wet conditions this disease can destroy a field within days.",
        "sustainability_impact": "Acting within 48 hours of first detection is the difference between a single spray and total crop loss."
    },
    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Uniform green compound leaves with no blotching, downy growth, or marginal necrosis"],
        "organic_remedies": [
            "Maintain crop rotation and add well-rotted farmyard manure before planting",
            "Earth up regularly to protect developing tubers from light and spores"
        ],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Maintain standard soil moisture between 60-70% field capacity.",
        "sustainability_impact": "Proper earthing up prevents tuber greening and spoilage, reducing post-harvest waste."
    },

    # ------------------------------------------------------------- RASPBERRY
    "Raspberry___healthy": {
        "crop": "Raspberry",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Clean compound green leaves with no rust pustules, spotting, or cane lesions"],
        "organic_remedies": [
            "Thin canes annually to maintain airflow through the row",
            "Mulch with straw to conserve moisture and suppress weeds"
        ],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Raspberries are shallow-rooted and need consistent moisture; drip irrigation is strongly preferred.",
        "sustainability_impact": "Annual cane thinning reduces disease pressure and removes the need for preventive fungicide."
    },

    # --------------------------------------------------------------- SOYBEAN
    "Soybean___healthy": {
        "crop": "Soybean",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Uniform green trifoliate leaves with no mosaic, pustules, or lesions"],
        "organic_remedies": [
            "Inoculate seed with Rhizobium to maximise biological nitrogen fixation",
            "Maintain rotation with cereals to break pest and disease cycles"
        ],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Ensure adequate moisture at flowering and pod fill, the two most yield-sensitive stages.",
        "sustainability_impact": "Rhizobium inoculation fixes atmospheric nitrogen and enriches the soil for the following cereal crop."
    },

    # ---------------------------------------------------------------- SQUASH
    "Squash___Powdery_mildew": {
        "crop": "Squash",
        "disease": "Powdery Mildew (Podosphaera xanthii)",
        "is_healthy": False,
        "severity": "Moderate to High",
        "symptoms": [
            "White talcum-like powdery patches on the upper leaf surface and stems",
            "Patches merge until the leaf yellows, browns, and dies back",
            "Exposed fruit suffers sunscald once the protective canopy collapses"
        ],
        "organic_remedies": [
            "Spray milk solution (1 part milk to 9 parts water) or potassium bicarbonate at 5g/L weekly",
            "Apply neem oil at 5ml per litre in the early morning or late evening",
            "Space plants generously and remove the oldest infected leaves"
        ],
        "chemical_remedies": [
            "Wettable sulphur 80% WP @ 2g per litre, avoiding application above 32C",
            "Hexaconazole 5% EC @ 1ml per litre, rotating actives to prevent resistance"
        ],
        "irrigation_advice": "Powdery mildew does not require leaf wetness. Prioritise plant spacing and airflow over keeping leaves dry.",
        "sustainability_impact": "Milk and bicarbonate sprays are food-safe, cost almost nothing, and leave no residue on harvested fruit."
    },

    # ------------------------------------------------------------ STRAWBERRY
    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry",
        "disease": "Leaf Scorch (Diplocarpon earlianum)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "Numerous small irregular dark purple spots scattered across the leaf",
            "Spots merge until the leaf looks scorched, dry, and reddish-brown",
            "Lesions also appear on petioles and runners, weakening the plant"
        ],
        "organic_remedies": [
            "Renovate beds after harvest by mowing off and removing old foliage",
            "Space plants for airflow and control weeds that trap humidity",
            "Apply copper-based fungicide during periods of prolonged wet weather"
        ],
        "chemical_remedies": [
            "Captan 50% WP @ 2g per litre",
            "Myclobutanil 10% WP @ 1g per litre applied after bed renovation"
        ],
        "irrigation_advice": "Use drip irrigation under plastic mulch. Overhead watering greatly worsens all strawberry leaf diseases.",
        "sustainability_impact": "Post-harvest renovation removes the inoculum mechanically and typically eliminates one full spray round."
    },
    "Strawberry___healthy": {
        "crop": "Strawberry",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Bright green trifoliate leaves with no purple spotting or scorched margins"],
        "organic_remedies": [
            "Mulch with straw to keep fruit off the soil and reduce rot",
            "Renovate beds annually after harvest"
        ],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Keep the shallow root zone evenly moist through drip lines; strawberries are sensitive to both drought and waterlogging.",
        "sustainability_impact": "Straw mulch reduces fruit rot losses and conserves soil moisture simultaneously."
    },

    # ---------------------------------------------------------------- TOMATO
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot (Xanthomonas spp.)",
        "is_healthy": False,
        "severity": "High",
        "symptoms": [
            "Small dark water-soaked spots on leaves, often with a narrow yellow halo",
            "Spots become angular and greasy-looking, and leaves drop prematurely",
            "Raised scabby spots on green fruit that make it unmarketable"
        ],
        "organic_remedies": [
            "Treat seed in hot water at 50C for 25 minutes before sowing",
            "Rotate away from tomato and pepper for two to three years",
            "Apply copper hydroxide preventively, tank-mixed with mancozeb"
        ],
        "chemical_remedies": [
            "Copper oxychloride 50% WP @ 3g per litre at 7-10 day intervals",
            "Streptocycline @ 0.5g per 10 litres with copper, where locally approved"
        ],
        "irrigation_advice": "Use drip irrigation only, and never handle plants while the foliage is wet.",
        "sustainability_impact": "Seed treatment and rotation prevent introduction entirely, which is far cheaper than season-long copper sprays."
    },
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight (Alternaria solani)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "Dark brown to black spots with concentric rings (target-like pattern) on older leaves",
            "Yellowing (chlorosis) of leaf tissue surrounding the spots",
            "Stem lesions near the soil line and fruit rot near the stem end"
        ],
        "organic_remedies": [
            "Prune and safely destroy lower infected leaves to improve air circulation",
            "Apply cold-pressed Neem Oil (5ml/L) or Copper oxychloride organically certified spray",
            "Mulch the soil surface around plants to prevent fungal spores from splashing onto leaves"
        ],
        "chemical_remedies": [
            "Mancozeb 75% WP @ 2.5g per litre of water",
            "Chlorothalonil @ 2g per litre of water at 7-10 day intervals"
        ],
        "irrigation_advice": "Switch to drip irrigation immediately. Keep foliage completely dry during morning and evening.",
        "sustainability_impact": "Targeted spot treatment saves 40% fungicide compared to blanket prophylactic spraying."
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight (Phytophthora infestans)",
        "is_healthy": False,
        "severity": "Severe",
        "symptoms": [
            "Large, irregular water-soaked greasy lesions turning dark brown to purplish-black",
            "White cottony fungal growth on the undersides of leaves in humid conditions",
            "Rapid collapse of foliage and dark sunken blotches on green or ripe tomatoes"
        ],
        "organic_remedies": [
            "Immediately remove and deeply bury or burn severely diseased plants",
            "Apply preventive Bordeaux mixture (1%) or copper hydroxide spray before heavy rain",
            "Improve field drainage and plant spacing to reduce relative humidity"
        ],
        "chemical_remedies": [
            "Metalaxyl + Mancozeb (Ridomil MZ) @ 2.5g/L water",
            "Cymoxanil + Mancozeb spray at first sign of outbreak"
        ],
        "irrigation_advice": "Halt all sprinkler irrigation. Irrigate only through soil trenches or drip lines.",
        "sustainability_impact": "Early detection within 48 hours halts total crop loss, safeguarding farmer investment."
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "disease": "Leaf Mold (Passalora fulva)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "Pale green to yellow patches on the upper leaf surface with no defined margin",
            "Olive-green to greyish-brown velvety mould on the corresponding underside",
            "Older leaves yellow, wither, and hang on the plant without dropping"
        ],
        "organic_remedies": [
            "Increase ventilation aggressively; this disease is most damaging in polyhouses",
            "Stake and prune plants to open the canopy and lower humidity",
            "Remove and destroy affected lower leaves at the first sign"
        ],
        "chemical_remedies": [
            "Chlorothalonil @ 2g per litre",
            "Difenoconazole 25% EC @ 0.5ml per litre where infection is established"
        ],
        "irrigation_advice": "Water at the base early in the day. Leaf mold requires relative humidity above 85% to establish.",
        "sustainability_impact": "Ventilation management alone controls this disease in most protected cultivation, avoiding chemical use."
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot (Septoria lycopersici)",
        "is_healthy": False,
        "severity": "Moderate to High",
        "symptoms": [
            "Many small circular spots with dark borders and pale grey centres",
            "Tiny black fruiting bodies visible as dots within the spot centres",
            "Progresses upward from the oldest leaves, causing severe defoliation"
        ],
        "organic_remedies": [
            "Remove infected lower leaves promptly and destroy them away from the field",
            "Mulch heavily to stop rain splashing spores from soil onto foliage",
            "Rotate out of tomato for at least two seasons"
        ],
        "chemical_remedies": [
            "Mancozeb 75% WP @ 2.5g per litre",
            "Chlorothalonil @ 2g per litre at 7-10 day intervals during wet weather"
        ],
        "irrigation_advice": "Drip irrigation is essential. Splashing water is the main means by which this fungus moves up the plant.",
        "sustainability_impact": "Mulching blocks the soil-to-leaf splash pathway and reduces the number of sprays needed per season."
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato",
        "disease": "Two-Spotted Spider Mite (Tetranychus urticae)",
        "is_healthy": False,
        "severity": "Moderate to High",
        "symptoms": [
            "Fine pale stippling or speckling across the upper leaf surface",
            "Delicate webbing on leaf undersides and between stems in heavy infestations",
            "Leaves turn bronze or reddish, dry out, and drop"
        ],
        "organic_remedies": [
            "Release predatory mites such as Phytoseiulus persimilis for biological control",
            "Spray neem oil at 5ml per litre, covering leaf undersides thoroughly",
            "Raise humidity and hose down foliage; mites thrive in hot, dusty, dry conditions"
        ],
        "chemical_remedies": [
            "Spiromesifen 22.9% SC @ 1ml per litre",
            "Abamectin 1.8% EC @ 0.5ml per litre, rotating actives as mites develop resistance quickly"
        ],
        "irrigation_advice": "Maintain adequate irrigation. Water-stressed, dusty plants are far more susceptible to mite outbreaks.",
        "sustainability_impact": "This is a pest, not a fungus. Broad-spectrum fungicides do nothing, and predatory mites avoid pesticide use entirely."
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "disease": "Target Spot (Corynespora cassiicola)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "Small brown spots that enlarge into lesions with concentric rings and a light centre",
            "Lesions may develop a pinhole-like perforation at the centre",
            "Sunken circular lesions on the fruit, and defoliation in severe cases"
        ],
        "organic_remedies": [
            "Remove crop debris after harvest, as the fungus survives on residue",
            "Stake and prune for airflow through the canopy",
            "Rotate with a non-host crop for at least one season"
        ],
        "chemical_remedies": [
            "Azoxystrobin 23% SC @ 1ml per litre",
            "Mancozeb 75% WP @ 2.5g per litre at 10 day intervals"
        ],
        "irrigation_advice": "Avoid overhead irrigation and prolonged leaf wetness, which this fungus needs to sporulate.",
        "sustainability_impact": "Target Spot is easily confused with Early Blight; correct identification prevents applying the wrong product."
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "disease": "Tomato Yellow Leaf Curl Virus (whitefly-transmitted)",
        "is_healthy": False,
        "severity": "Critical",
        "symptoms": [
            "Severe upward curling and cupping of leaves, with yellowing at the margins",
            "Marked stunting of the whole plant and shortened internodes",
            "Flowers drop and almost no fruit sets if infection occurs early"
        ],
        "organic_remedies": [
            "Control the whitefly vector using yellow sticky traps at canopy height",
            "Use 40-mesh insect-proof netting over nurseries and polyhouses",
            "Rogue out infected plants immediately and plant resistant varieties"
        ],
        "chemical_remedies": [
            "No cure exists for the virus; all treatment targets the whitefly vector",
            "Imidacloprid 17.8% SL @ 0.3ml per litre or Diafenthiuron 50% WP @ 1g per litre for whitefly"
        ],
        "irrigation_advice": "Irrigation does not affect transmission. Focus entirely on vector exclusion and control.",
        "sustainability_impact": "Netting and resistant varieties give durable protection and sharply reduce insecticide use."
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus (ToMV)",
        "is_healthy": False,
        "severity": "High",
        "symptoms": [
            "Light and dark green mottled mosaic pattern across the leaf",
            "Leaves become narrow, fern-like, or distorted, especially new growth",
            "Internal browning of the fruit and uneven, blotchy ripening"
        ],
        "organic_remedies": [
            "Wash hands and disinfect tools with skimmed milk or bleach solution between plants",
            "Do not use tobacco products near the crop; the related TMV spreads from them",
            "Remove and destroy infected plants, and use certified virus-free seed"
        ],
        "chemical_remedies": [
            "No chemical treatment exists for plant viruses",
            "Focus on strict sanitation, tool disinfection, and resistant cultivars"
        ],
        "irrigation_advice": "Irrigation method does not affect spread. This virus moves mechanically through handling and contaminated tools.",
        "sustainability_impact": "Sanitation is a zero-input control, and it prevents the mechanical spread that pesticides cannot address."
    },
    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Vibrant green coloration, uniform leaf structure, no visible necrotic lesions or chlorosis"],
        "organic_remedies": [
            "Continue regular organic compost or vermicompost application every 3-4 weeks",
            "Maintain balanced watering schedule"
        ],
        "chemical_remedies": ["None needed. Avoid unnecessary prophylactic chemical sprays."],
        "irrigation_advice": "Maintain standard soil moisture between 60-70% field capacity.",
        "sustainability_impact": "Preventive monitoring avoids reactive chemical spending and protects beneficial soil life."
    },
}


def get_disease_info(class_name: str) -> dict:
    clean_name = class_name.strip()
    if clean_name in DISEASE_DATABASE:
        return DISEASE_DATABASE[clean_name]

    # Fuzzy fallback match
    for key, val in DISEASE_DATABASE.items():
        if key.lower() in clean_name.lower() or clean_name.lower() in key.lower():
            return val

    # Default fallback
    is_healthy = "healthy" in clean_name.lower()
    return {
        "crop": clean_name.split("___")[0] if "___" in clean_name else "Crop",
        "disease": clean_name.replace("___", " - ").replace("_", " "),
        "is_healthy": is_healthy,
        "severity": "None" if is_healthy else "Moderate",
        "symptoms": ["Foliar anomalies consistent with standard pathogenic indicators."],
        "organic_remedies": [
            "Isolate and monitor affected crops",
            "Apply broad-spectrum organic bio-fungicide (Neem seed extract 5%)"
        ],
        "chemical_remedies": ["Consult local Krishi Vigyan Kendra (KVK) for regional chemical guidelines."],
        "irrigation_advice": "Maintain regulated deficit irrigation to avoid root stress.",
        "sustainability_impact": "Early intervention prevents disease spread to adjacent crops."
    }
