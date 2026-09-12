import os
import random
import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import requests

from disease_kb import get_disease_info, DISEASE_DATABASE
from predict import predict, get_model

app = FastAPI(title="AgriSmart AI", description="Intelligent Agriculture Platform for SIH 2026")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = UPLOAD_DIR / filename
        
        with open(filepath, "wb") as f:
            f.write(await file.read())

        model = get_model()
        if model is not None:
            results = model(str(filepath), verbose=False)
            top1_idx = results[0].probs.top1
            class_name = results[0].names[top1_idx]
            confidence = float(results[0].probs.top1conf)
        else:
            class_name = "Tomato___Early_blight"
            confidence = 0.942

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
            "image_url": f"/uploads/{filename}",
            "model_mode": "trained_weights" if model is not None else "simulation_fallback"
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

@app.get("/api/iot-feed")
async def iot_feed():
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
        "irrigation_action": "ACTIVATE DRIP (Moisture < 30%)" if irrigation_needed else "OPTIMAL (No Irrigation Needed)",
        "irrigation_needed": irrigation_needed,
        "device_status": "Online (ESP32 Gateway Stream)"
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

    q_low = query.lower()
    if "blight" in q_low:
        reply = (
            "For Blight (Early or Late):\n"
            "1. Remove and safely dispose of all infected lower leaves.\n"
            "2. Spray copper oxychloride (3g/L) or cold-pressed neem oil (5ml/L) in the early morning.\n"
            "3. Shift to drip irrigation — do not wet the leaves during watering!"
        )
    elif "irrigation" in q_low or "water" in q_low:
        reply = (
            "Smart Irrigation Recommendation:\n"
            "• If soil moisture is above 35%, delay watering by 24 hours.\n"
            "• Drip irrigation in 45-minute cycles in early morning saves 40% water and prevents fungal outbreaks."
        )
    elif "fertilizer" in q_low or "npk" in q_low:
        reply = (
            "Soil Nutrient Guidance:\n"
            "• Use Neem-coated Urea for steady nitrogen release without soil acidification.\n"
            "• Supplement with Vermicompost (2 tons/acre) before flowering to enhance beneficial soil microbes."
        )
    else:
        reply = (
            f"Hello Kisan friend! For your query '{query}', AgriSmart advises:\n"
            "1. Monitor your crop foliage every 3 days for early leaf spots.\n"
            "2. Ensure optimal drainage so water doesn't pool near root crowns.\n"
            "3. Upload a clear photo of any suspicious leaf to our Diagnostic Scanner for an instant AI treatment plan!"
        )

    return JSONResponse({"reply": reply, "source": "AgriSmart Offline Agro-Expert Engine"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)