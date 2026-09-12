# Comprehensive Agricultural Disease Knowledge Base & Precautionary Guidance
# Strictly satisfying Section 3.1 & 4.1 of the Hackathon requirements

DISEASE_DATABASE = {
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
        "sustainability_impact": "Zero chemical usage required. Conserves beneficial insect ecology."
    },
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight (Alternaria solani)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "Small circular brown spots expanding into concentric rings on lower leaves",
            "Premature senescence and defoliation of lower canopy"
        ],
        "organic_remedies": [
            "Rotate crops with non-solanaceous crops (e.g., maize, beans) for at least 2 seasons",
            "Spray Trichoderma viride bio-fungicide @ 5g/L water as preventive soil/foliar drench"
        ],
        "chemical_remedies": ["Azoxystrobin 23% SC @ 1ml/L or Difenoconazole 25% EC @ 0.5ml/L"],
        "irrigation_advice": "Avoid overhead watering during cloudy or humid weather.",
        "sustainability_impact": "Crop rotation preserves soil microbiome and reduces synthetic fertilizer dependence."
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight (Phytophthora infestans)",
        "is_healthy": False,
        "severity": "Critical",
        "symptoms": [
            "Rapidly expanding water-soaked dark brown blotches with pale yellow margins",
            "Tubers develop purplish-brown surface discoloration and dry rot beneath the skin"
        ],
        "organic_remedies": [
            "Destroy cull piles of infected seed tubers before planting season",
            "Use certified disease-free seed tubers and plant blight-resistant cultivars"
        ],
        "chemical_remedies": ["Dimethomorph 50% WP @ 1g/L + Mancozeb @ 2g/L water"],
        "irrigation_advice": "Cease irrigation if rain forecast exceeds 80% to avoid soil waterlogging.",
        "sustainability_impact": "Smart irrigation pauses prevent fungicide washout, saving 3500 INR/acre in chemical waste."
    },
    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Vigorous green foliage with strong stems and healthy turgor"],
        "organic_remedies": ["Routine hilling up around base to protect developing tubers from sun exposure"],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Provide 25-30mm water per week during tuber enlargement stage.",
        "sustainability_impact": "Healthy soil maintenance saves ~15% irrigation volume."
    },
    "Corn___Common_rust": {
        "crop": "Corn (Maize)",
        "disease": "Common Rust (Puccinia sorghi)",
        "is_healthy": False,
        "severity": "Moderate",
        "symptoms": [
            "Oval to elongate cinnamon-brown pustules (uredinia) on both upper and lower leaf surfaces",
            "Pustules rupture epidermal tissue, releasing powdery reddish-brown spores"
        ],
        "organic_remedies": [
            "Plant resistant corn hybrids adapted to your specific agro-climatic zone",
            "Ensure wide row spacing (60-75 cm) for adequate wind penetration and drying"
        ],
        "chemical_remedies": ["Propiconazole 25% EC @ 1ml/L water at initial appearance of pustules"],
        "irrigation_advice": "Irrigate in the early morning so leaves dry quickly in sunlight.",
        "sustainability_impact": "Planting resistant hybrids eliminates pesticide runoff into rural groundwater."
    },
    "Corn___healthy": {
        "crop": "Corn (Maize)",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Uniform green upright leaves, robust stalk development, absence of rust pustules"],
        "organic_remedies": ["Maintain nitrogen top-dressing with neem-coated urea or bio-fertilizers"],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Critical watering required during tasseling and silking stages.",
        "sustainability_impact": "Optimal nutrient timing prevents nitrogen leaching."
    },
    "Apple___Apple_scab": {
        "crop": "Apple",
        "disease": "Apple Scab (Venturia inaequalis)",
        "is_healthy": False,
        "severity": "Moderate to High",
        "symptoms": [
            "Olive-green to velvety brown lesions on leaves and young fruit",
            "Severely affected fruit becomes deformed, cracked, and unmarketable"
        ],
        "organic_remedies": [
            "Rake and compost or shred fallen orchard leaves in autumn to eliminate winter spores",
            "Apply sulfur-based bio-spray during early bud-break"
        ],
        "chemical_remedies": ["Captan 50% WP @ 2.5g/L or Difenoconazole @ 0.3ml/L"],
        "irrigation_advice": "Employ micro-sprinklers or underground drip lines below tree canopies.",
        "sustainability_impact": "Orchard floor sanitation reduces seasonal fungicide requirements by 50%."
    },
    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy Foliage",
        "is_healthy": True,
        "severity": "None",
        "symptoms": ["Clean, lustrous green leaves without scabs, powdery mildew, or rust spots"],
        "organic_remedies": ["Apply balanced micronutrient foliar spray (Zinc + Boron) before bloom"],
        "chemical_remedies": ["None required."],
        "irrigation_advice": "Maintain soil moisture with organic wood-chip mulching.",
        "sustainability_impact": "Mulching conserves 30% orchard water consumption."
    }
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
