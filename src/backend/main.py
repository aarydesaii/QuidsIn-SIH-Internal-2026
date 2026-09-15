import os
import io
import sys
import uuid
import random
import datetime
from pathlib import Path
from typing import Optional

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import requests

from src.backend.disease_kb import get_disease_info, DISEASE_DATABASE
from src.backend.ood_guard import screen, rejection_guidance, MIN_VIEW_MEAN_CONFIDENCE
from model.predict import predict, get_model

app = FastAPI(title="AgriSmart AI", description="Intelligent Agriculture Platform for SIH 2026")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATES_DIR = PROJECT_ROOT / "src" / "frontend" / "templates"
STATIC_DIR = PROJECT_ROOT / "src" / "frontend" / "static"
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

# Out-of-distribution screening lives in src/backend/ood_guard.py, which averages
# the softmax over five views and applies thresholds calibrated against the
# trained weights. A bare top-1 cutoff is not enough: a flat grey image still
# scores 0.575 on this model, so any single threshold below that passes junk
# through as a confident diagnosis.

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/research", response_class=HTMLResponse)
async def research(request: Request):
    return templates.TemplateResponse(request=request, name="research.html")

@app.post("/api/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    try:
        extension = Path(file.filename or "").suffix.lower()
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            return JSONResponse(
                {"status": "error", "message": "Unsupported file type. Upload a JPG, PNG or WEBP image."},
                status_code=400,
            )

        contents = await file.read()
        if len(contents) > MAX_UPLOAD_BYTES:
            return JSONResponse(
                {"status": "error", "message": "Image is too large. Maximum size is 10 MB."},
                status_code=400,
            )

        try:
            Image.open(io.BytesIO(contents)).verify()
        except Exception:
            return JSONResponse(
                {"status": "error", "message": "File is not a valid image."},
                status_code=400,
            )

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uuid.uuid4().hex[:8]}{extension}"
        filepath = UPLOAD_DIR / filename

        with open(filepath, "wb") as f:
            f.write(contents)

        model = get_model()
        if model is not None:
            verdict = screen(model, str(filepath))
        else:
            verdict = {
                "accepted": True,
                "class_name": "Tomato___Early_blight",
                "confidence": 0.942,
                "failed_checks": [],
                "diagnostics": {},
            }

        class_name = verdict["class_name"]
        confidence = verdict["confidence"]
        model_mode = "trained_weights" if model is not None else "simulation_fallback"

        if not verdict["accepted"]:
            return JSONResponse({
                "status": "low_confidence",
                "confidence": round(confidence * 100, 1),
                "threshold": round(MIN_VIEW_MEAN_CONFIDENCE * 100, 1),
                "closest_match": get_disease_info(class_name)["disease"],
                "message": "This image could not be confidently matched to a crop the model was trained on.",
                "guidance": rejection_guidance(verdict["failed_checks"]),
                "failed_checks": verdict["failed_checks"],
                "diagnostics": verdict["diagnostics"],
                "image_url": f"/uploads/{filename}",
                "model_mode": model_mode,
            })

        info = get_disease_info(class_name)

        return JSONResponse({
            "status": "success",
            "class_raw": class_name,
            "crop": info["crop"],
            "disease": info["disease"],
            "is_healthy": info["is_healthy"],
            "severity": info["severity"],
            "confidence": round(confidence * 100, 1),
            "confidence_decimal": round(confidence, 3),
            "symptoms": info["symptoms"],
            "organic_remedies": info["organic_remedies"],
            "chemical_remedies": info["chemical_remedies"],
            "irrigation_advice": info["irrigation_advice"],
            "sustainability_impact": info["sustainability_impact"],
            "diagnostics": verdict["diagnostics"],
            "image_url": f"/uploads/{filename}",
            "model_mode": model_mode
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
@app.get("/api/weather")
async def weather_endpoint(city: str = "Ahmedabad"):
    api_key = os.environ.get("OPENWEATHER_API_KEY", "")
    if api_key and api_key != "your_key_here":
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                wind = data["wind"]["speed"]
                condition = data["weather"][0]["description"].title()
                spray_ok = wind < 15 and humidity < 80
                return JSONResponse({
                    "city": city,
                    "temp_c": round(temp, 1),
                    "humidity": humidity,
                    "wind_kmh": round(wind * 3.6, 1),
                    "condition": condition,
                    "spray_advisory": "Favorable for spraying" if spray_ok else "Caution: High wind or humidity",
                    "rain_risk": "High" if "rain" in condition.lower() else "Low",
                    "source": "OpenWeatherMap Live API"
                })
        except Exception:
            pass

    return JSONResponse({
        "city": city,
        "temp_c": 31.4,
        "humidity": 64,
        "wind_kmh": 11.2,
        "condition": "Partly Cloudy",
        "spray_advisory": "Favorable for foliar spray (Wind < 15 km/h)",
        "rain_risk": "Low (15% chance in next 24h)",
        "source": "Simulated Agro-Meteorological Station"
    })

@app.get("/api/soil-analytics")
async def soil_analytics():
    moisture = round(random.uniform(28.0, 38.0), 1)
    temp = round(random.uniform(29.0, 33.5), 1)
    humidity = round(random.uniform(62.0, 72.0), 1)
    ph = round(random.uniform(6.4, 6.9), 2)
    nitrogen = round(random.uniform(140, 180), 0)
    phosphorus = round(random.uniform(35, 55), 0)
    potassium = round(random.uniform(190, 240), 0)
    irrigation_needed = moisture < 30.0

    return JSONResponse({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "soil_moisture_percent": moisture,
        "soil_temp_c": temp,
        "ambient_humidity_percent": humidity,
        "soil_ph": ph,
        "npk": {"N": int(nitrogen), "P": int(phosphorus), "K": int(potassium)},
        "irrigation_action": "IRRIGATION RECOMMENDED (Moisture < 30%)" if irrigation_needed else "OPTIMAL (No Irrigation Needed)",
        "irrigation_needed": irrigation_needed,
        "data_source": "Simulated agronomic soil model"
    })

@app.post("/api/sustainability-calc")
async def sustainability_calc(
    acres: float = Form(2.5),
    irrigation_type: str = Form("drip"),
    crop: str = Form("Tomato")
):
    base_water_l = acres * 25000
    saved_water = base_water_l * 0.42 if irrigation_type == "drip" else base_water_l * 0.10
    fungicide_reduction_kg = round(acres * 1.8, 1)
    co2_saved_kg = round(saved_water * 0.0004 + fungicide_reduction_kg * 4.2, 1)
    cost_saved_inr = round(saved_water * 0.08 + fungicide_reduction_kg * 850, 0)
    score = min(100, int(60 + (saved_water / base_water_l) * 40))

    return JSONResponse({
        "sustainability_score": score,
        "water_saved_litres": int(saved_water),
        "fungicide_reduction_kg": fungicide_reduction_kg,
        "co2_saved_kg": co2_saved_kg,
        "cost_saved_inr": int(cost_saved_inr),
        "rating": "Excellent Sustainability" if score > 80 else "Good Progress"
    })

CROP_TERMS = {
    "tomato": "Tomato", "tamatar": "Tomato",
    "potato": "Potato", "aloo": "Potato", "batata": "Potato",
    "corn": "Corn", "maize": "Corn", "makka": "Corn",
    "apple": "Apple", "seb": "Apple",
}

DISEASE_TERMS = {
    "early blight": "Early_blight", "early-blight": "Early_blight",
    "late blight": "Late_blight", "late-blight": "Late_blight",
    "blight": "blight",
    "rust": "Common_rust",
    "scab": "Apple_scab",
}


def _format_entry(key, entry, intent):
    """Render a knowledge-base entry, showing the sections the question asked for."""
    lines = [f"{entry['crop']} — {entry['disease']}"]

    if entry.get("is_healthy"):
        lines.append(f"\nSeverity: {entry['severity']}")
        lines.append("\nMaintenance:")
        lines += [f"  • {s}" for s in entry["symptoms"]]
        lines.append(f"\nIrrigation: {entry['irrigation_advice']}")
        return "\n".join(lines)

    lines.append(f"Severity: {entry['severity']}")

    show_all = intent == "all"
    if show_all or intent == "symptoms":
        lines.append("\nSymptoms to look for:")
        lines += [f"  • {s}" for s in entry["symptoms"]]
    if show_all or intent == "organic":
        lines.append("\nOrganic / bio remedies:")
        lines += [f"  • {s}" for s in entry["organic_remedies"]]
    if show_all or intent == "chemical":
        lines.append("\nChemical formulation:")
        lines.append(f"  {entry['chemical_remedies'][0] if isinstance(entry['chemical_remedies'], list) else entry['chemical_remedies']}")
    if show_all or intent == "irrigation":
        lines.append(f"\nIrrigation: {entry['irrigation_advice']}")

    return "\n".join(lines)


def _detect_intent(q):
    if any(w in q for w in ("organic", "natural", "bio", "neem", "jaivik")):
        return "organic"
    if any(w in q for w in ("chemical", "fungicide", "dosage", "dose", "spray what", "which medicine", "dawa")):
        return "chemical"
    if any(w in q for w in ("symptom", "identify", "looks like", "how to know", "sign", "pehchan")):
        return "symptoms"
    if any(w in q for w in ("irrigation", "watering", "water", "pani")):
        return "irrigation"
    return "all"


def build_grounded_reply(query: str):
    """Answer from DISEASE_DATABASE where possible. Returns (reply, grounded)."""
    q = query.lower().strip()
    if not q:
        return "Please type a question about your crop.", False

    intent = _detect_intent(q)
    crops = {c for term, c in CROP_TERMS.items() if term in q}
    # A specific term ("late blight") must win over the generic "blight" wildcard
    specific = {d for term, d in DISEASE_TERMS.items() if term in q and d != "blight"}
    diseases = specific or ({"blight"} if "blight" in q else set())

    matches = []
    for key, entry in DISEASE_DATABASE.items():
        crop_part, _, disease_part = key.partition("___")
        if crops and crop_part not in crops:
            continue
        if diseases:
            if not any(d == disease_part or (d == "blight" and "blight" in disease_part.lower())
                       for d in diseases):
                continue
        elif not crops:
            continue
        matches.append((key, entry))

    if matches:
        diseased = [m for m in matches if not m[1].get("is_healthy")]
        chosen = diseased or matches
        if len(chosen) > 3:
            chosen = chosen[:3]
        blocks = [_format_entry(k, e, intent) for k, e in chosen]
        header = ""
        if len(chosen) > 1:
            header = f"Found {len(chosen)} matching entries in the knowledge base:\n\n"
        return header + "\n\n———\n\n".join(blocks), True

    # Topic answers that are not disease-specific
    if any(w in q for w in ("irrigation", "watering", "water", "pani", "drip")):
        return (
            "Smart irrigation guidance:\n"
            "  • Irrigate when soil moisture falls below 30% — the Soil Analytics panel "
            "on the dashboard shows the current reading.\n"
            "  • Prefer drip irrigation in 45-minute early-morning cycles; it saves roughly "
            "40% water against flood irrigation.\n"
            "  • Never wet the foliage. Most fungal diseases need leaf wetness to establish.\n"
            "  • Delay irrigation by 24 hours if rain is forecast — check the Weather panel."
        ), False

    if any(w in q for w in ("fertilizer", "fertiliser", "npk", "nutrient", "urea", "khad")):
        return (
            "Soil nutrient guidance:\n"
            "  • Use neem-coated urea for steady nitrogen release without acidifying the soil.\n"
            "  • Apply vermicompost at 2 tons/acre before flowering to build microbial activity.\n"
            "  • Test soil pH before each season — 6.2 to 6.8 suits tomato, potato and corn.\n"
            "  • Split nitrogen into 2–3 doses rather than one heavy application."
        ), False

    if any(w in q for w in ("spray", "weather", "wind", "when to", "timing")):
        return (
            "Spray timing guidance:\n"
            "  • Spray only when wind is below 15 km/h — the Weather panel shows live wind speed.\n"
            "  • Early morning or late evening is best; midday heat evaporates the spray.\n"
            "  • Do not spray if rain is likely within 6 hours, or it washes off.\n"
            "  • Always wear gloves and a mask when applying chemical fungicides."
        ), False

    if any(w in q for w in ("prevent", "avoid", "protect", "healthy", "bachav")):
        return (
            "Preventive crop protection:\n"
            "  • Rotate crops — avoid planting the same family in a field two seasons running.\n"
            "  • Remove and destroy infected plant debris; do not compost it.\n"
            "  • Space plants for airflow so foliage dries quickly after dew or rain.\n"
            "  • Mulch the soil surface to stop spores splashing onto lower leaves.\n"
            "  • Scout fields every 3 days and photograph anything suspicious."
        ), False

    known_crops = sorted({e["crop"] for e in DISEASE_DATABASE.values()})
    return (
        "I could not match that to my knowledge base. I can answer questions about:\n\n"
        f"  • Diseases of: {', '.join(known_crops)}\n"
        "  • Specific conditions: early blight, late blight, common rust, apple scab\n"
        "  • Topics: irrigation, fertilizer and nutrients, spray timing, prevention\n\n"
        "Try asking something like \"organic treatment for tomato late blight\", "
        "\"symptoms of apple scab\", or \"when should I spray\".\n\n"
        "For a diagnosis, upload a leaf photo to the Diagnostic Scanner on the dashboard."
    ), False


@app.post("/api/chat")
async def chat_endpoint(query: str = Form(...), lang: str = Form("en")):
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key and gemini_key != "your_key_here":
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            sys_instruction = (
                "You are AgriSmart AI, a trusted, empathetic agricultural scientist assisting Indian farmers. "
                "Provide concise, practical, actionable farming advice. Use simple bullet points. "
                f"Respond naturally in the language requested: {lang} (e.g. Hindi, Gujarati, English)."
            )
            payload = {"contents": [{"parts": [{"text": f"{sys_instruction}\n\nFarmer Query: {query}"}]}]}
            resp = requests.post(url, json=payload, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                return JSONResponse({"reply": reply, "source": "Gemini 1.5 Flash (Live)"})
        except Exception:
            pass

    reply, matched = build_grounded_reply(query)
    return JSONResponse({
        "reply": reply,
        "source": "AgriSmart Knowledge Base (grounded)" if matched else "AgriSmart Assistant",
        "grounded": matched,
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.backend.main:app", host="127.0.0.1", port=8000, reload=True)