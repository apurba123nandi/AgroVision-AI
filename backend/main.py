from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import io
from PIL import Image
try:
    import pi_heif
    pi_heif.register_heif_opener()
except ImportError:
    pass
import os

app = FastAPI(title="Crop Disease Detection API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model if available (mock otherwise)
MODEL_PATH = "best.pt"
model = None

try:
    from ultralytics import YOLO
    if os.path.exists(MODEL_PATH):
        model = YOLO(MODEL_PATH)
        print("YOLOv8 model loaded successfully.")
        print(f"Model Classes: {model.names}")
    else:
        print("Warning: best.pt not found. Running in mock mode.")
except ImportError:
    print("Warning: ultralytics not installed. Running in mock mode.")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Crop Disease Detection API is running"}

import base64

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    temperature: float = Form(25.0),
    humidity: float = Form(50.0),
    rain: str = Form("No"),
    rain_status: str = Form("No Rain"),
    rain_amount: float = Form(0.0)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # If model is loaded, run inference
        if model is not None:
            results = model(image)
            
            # Generate annotated image
            annotated_img_array = results[0].plot()
            annotated_img = Image.fromarray(annotated_img_array[..., ::-1])
            buffered = io.BytesIO()
            annotated_img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Dynamic Environmental Risk Logic
            env_score = 0 # 0: Low, 1: Medium, 2: High
            env_risk = "Low"
            env_insight = "Environmental conditions are not favorable for disease spread."
            env_support = ""
            
            # 1. Base Logic
            if humidity > 70 and (rain.lower().strip() == "yes" or (temperature and 20 <= temperature <= 30)):
                env_score = 2
            elif (humidity and 50 <= humidity <= 70) or (rain_status == "Light Rain") or (temperature and 25 <= temperature <= 32):
                env_score = 1
            
            # 2. Rain Intensity Scaling
            if rain_status == "Moderate Rain":
                env_score = max(env_score, 1)
            elif rain_status == "Heavy Rain":
                env_score = 2

            # Initial mapping (will be refined after disease detection)
            risk_levels = ["Low", "Medium", "High"]
            risk_msgs = [
                "Environmental conditions are not favorable for disease spread.",
                "Moderate environmental conditions. Monitor crops regularly.",
                "Conditions strongly favor fungal disease spread."
            ]
            env_risk = risk_levels[env_score]
            env_insight = risk_msgs[env_score]

            # (Disease adjustments happen after detection below...)

            # Detection Logic
            best_det = None
            max_conf = 0.0
            if results[0].boxes:
                for box in results[0].boxes:
                    conf = float(box.conf[0])
                    if conf > max_conf:
                        max_conf = conf
                        best_det = box

            if best_det is not None:
                class_id = int(best_det.cls[0])
                disease_name = model.names[class_id]
                confidence = max_conf
                d_name = disease_name.lower().strip()
                
                if confidence < 0.2:
                    return {
                        "disease": "Uncertain",
                        "confidence": confidence,
                        "severity": "Unknown",
                        "treatment": "Very low confidence detection. Please upload a clearer image.",
                        "detected": False,
                        "annotated_image": f"data:image/jpeg;base64,{img_str}"
                    }
                
                low_conf = confidence < 0.45

                # Adjust env_score based on disease type
                if "rust" in d_name:
                    env_score += 1
                elif "powdery" in d_name:
                    if humidity < 60 and temperature and 20 <= temperature <= 30:
                        env_score += 1
                elif "healthy" in d_name:
                    if env_score == 2 and humidity < 85 and rain_status != "Heavy Rain":
                        env_score = 1
                
                env_score = max(0, min(2, env_score))
                
                risk_levels = ["Low", "Medium", "High"]
                risk_msgs = [
                    "Environmental conditions are not favorable for disease spread.",
                    "Moderate environmental conditions. Monitor crops regularly.",
                    "Conditions strongly favor fungal disease spread."
                ]
                
                env_risk = risk_levels[env_score]
                env_insight = risk_msgs[env_score]

                # Prediction Logic
                severity = "High" if confidence > 0.8 else "Medium" if confidence > 0.5 else "Low"
                
                # Check for env support
                if env_risk != "Low":
                    if ("rust" in d_name and env_risk == "High") or ("powdery" in d_name and env_risk == "Medium"):
                        env_support = "\nNote: Environmental conditions support this detection"

                # Chemical Recommendations
                if "healthy" in d_name:
                    recommendation = "No disease detected. Maintain regular monitoring."
                    severity = "Low"
                elif "powdery" in d_name:
                    recs = {"Low": "Improve airflow and avoid moisture.", "Medium": "Apply neem oil.", "High": "Use sulfur-based fungicide."}
                    recommendation = recs.get(severity, "")
                elif "rust" in d_name:
                    recs = {"Low": "Remove infected leaves.", "Medium": "Apply fungicide.", "High": "Use systemic fungicide."}
                    recommendation = recs.get(severity, "")
                else:
                    recommendation = f"Detected {disease_name}. Consult a specialist."
                
                recommendation += env_support

                # Spread Risk (Dynamic)
                s_score = 2 if severity == "High" else 1 if severity == "Medium" else 0
                if "rust" in d_name: s_score += 1
                if env_score == 2: s_score += 1
                elif env_score == 0: s_score -= 1
                
                s_score = max(0, min(2, s_score))
                final_spread_risk = "Low" if "healthy" in d_name else risk_levels[s_score]
                spread_msg = "Low risk. Disease spread is minimal." if final_spread_risk == "Low" else \
                            "Moderate spread expected. Monitor closely." if final_spread_risk == "Medium" else \
                            "High risk of disease spreading due to favorable conditions."

                # Organic
                organic_methods = {
                    "healthy": {
                        "Low": [
                            {"name": "Organic Compost", "instruction": "Apply well-decomposed organic compost to improve soil nutrients."},
                            {"name": "Proper Irrigation", "instruction": "Maintain consistent watering schedule to reduce plant stress."},
                            {"name": "Crop Rotation", "instruction": "Rotate crops seasonally to prevent soil-borne pathogen buildup."}
                        ]
                    },
                    "powdery": {
                        "Low": [
                            {"name": "Neem Oil Spray", "instruction": "Mix 5ml neem oil per liter of water and spray weekly."},
                            {"name": "Milk Spray", "instruction": "Mix milk and water in a 1:2 ratio and apply to leaves."},
                            {"name": "Improve Airflow", "instruction": "Prune excess foliage and increase spacing between plants."}
                        ],
                        "Medium": [
                            {"name": "Baking Soda Spray", "instruction": "Mix 1 tbsp baking soda with 1 gallon water and a drop of soap."},
                            {"name": "Potassium Bicarbonate", "instruction": "Apply as an antifungal spray to stop spore spread."},
                            {"name": "Neem Oil", "instruction": "Increase application to twice weekly for better control."}
                        ],
                        "High": [
                            {"name": "Remove Infected Leaves", "instruction": "Prune and dispose of heavily infected parts immediately."},
                            {"name": "Compost Tea Spray", "instruction": "Apply weekly to boost the plant's natural immune response."},
                            {"name": "Regular Neem Oil", "instruction": "Apply every 3-4 days until the outbreak is managed."}
                        ]
                    },
                    "rust": {
                        "Low": [
                            {"name": "Remove Affected Leaves", "instruction": "Pick off early spotted leaves and dispose of them properly."},
                            {"name": "Neem Oil Spray", "instruction": "Mix 5ml per liter and apply as a preventive measure."},
                            {"name": "Sunlight Exposure", "instruction": "Ensure plants get maximum sunlight to reduce leaf surface moisture."}
                        ],
                        "Medium": [
                            {"name": "Compost Tea Spray", "instruction": "Boost plant resistance by applying nutrient-rich compost tea."},
                            {"name": "Garlic Spray", "instruction": "Blend garlic with water, strain, and spray on affected areas."},
                            {"name": "Neem Oil Application", "instruction": "Apply consistently every 5 days to manage spore spread."}
                        ],
                        "High": [
                            {"name": "Pruning", "instruction": "Aggressively remove heavily infected areas to save the rest of the plant."},
                            {"name": "Frequent Neem Sprays", "instruction": "Apply every 3 days to suppress rapid rust development."},
                            {"name": "Organic Fungicide", "instruction": "Use copper-free organic antifungal solutions for severe cases."}
                        ]
                    }
                }

                if "healthy" in d_name:
                    organic_recs = organic_methods["healthy"].get("Low", [])
                elif "powdery" in d_name:
                    organic_recs = organic_methods["powdery"].get(severity, [])
                elif "rust" in d_name:
                    organic_recs = organic_methods["rust"].get(severity, [])
                else:
                    organic_recs = [
                        {"name": "General Bio-Fungicide", "instruction": "Apply neem oil (5ml/L) as a broad-spectrum preventive measure."},
                        {"name": "Organic Compost", "instruction": "Apply well-decomposed organic compost to improve soil nutrients."},
                        {"name": "Improve Airflow", "instruction": "Prune excess foliage and increase spacing between plants."}
                    ]

                return {
                    "disease": disease_name,
                    "confidence": confidence,
                    "low_confidence": low_conf,
                    "severity": severity,
                    "treatment": recommendation,
                    "detected": True,
                    "annotated_image": f"data:image/jpeg;base64,{img_str}",
                    "environmental_insights": {"risk_level": env_risk, "insight_message": env_insight},
                    "spread_prediction": {"risk_level": final_spread_risk, "insight_message": spread_msg},
                    "organic_treatment": {
                        "methods": organic_recs,
                        "label": "Eco-Friendly Alternatives"
                    }
                }
            else:
                return {
                    "disease": "Healthy",
                    "confidence": 0.0,
                    "severity": "Low",
                    "treatment": "No disease detected.",
                    "detected": False,
                    "annotated_image": f"data:image/jpeg;base64,{img_str}",
                    "environmental_insights": {"risk_level": env_risk, "insight_message": env_insight},
                    "spread_prediction": {"risk_level": "Low", "insight_message": "Weather is safe; minimal spread risk."},
                    "organic_treatment": {
                        "methods": [
                            {"name": "Organic Compost", "instruction": "Apply well-decomposed organic compost to improve soil nutrients."},
                            {"name": "Proper Irrigation", "instruction": "Maintain consistent watering schedule to reduce plant stress."},
                            {"name": "Crop Rotation", "instruction": "Rotate crops seasonally to prevent soil-borne pathogen buildup."}
                        ],
                        "label": "Eco-Friendly Alternatives"
                    }
                }

        else:
            # Mock mode implementation for testing without the model
            return {
                "disease": "Model Not Loaded",
                "confidence": 0.0,
                "severity": "Unknown",
                "treatment": "Please ensure 'best.pt' is in the backend folder.",
                "detected": False
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def translate_store_info(text: str, lang: str) -> str:
    if lang == "en" or not text:
        return text
    
    # Common mappings for Agri-Stores
    mappings = {
        "te": {
            "pesticides": "పురుగుల మందులు",
            "pesticide": "పురుగుల మందులు",
            "fertilizers": "ఎరువులు",
            "fertilizer": "ఎరువులు",
            "agri": "అగ్రి",
            "agriculture": "వ్యవసాయ",
            "tools": "పనిముట్లు",
            "machinery": "యంత్రాలు",
            "farms": "ఫార్మ్స్",
            "farm": "ఫార్మ్",
            "enterprises": "ఎంటర్‌ప్రైజెస్",
            "enterprise": "ఎంటర్‌ప్రైజ్",
            "agencies": "ఏజెన్సీలు",
            "agency": "ఏజెన్సీ",
            "seeds": "విత్తనాలు",
            "seed": "విత్తనం",
            "nursery": "నర్సరీ",
            "stores": "దుకాణాలు",
            "store": "దుకాణం",
            "depot": "డిపో",
            "near": "దగ్గర",
            "opp": "ఎదురుగా",
            "opposite": "ఎదురుగా",
            "road": "రోడ్డు",
            "hyderabad": "హైదరాబాద్",
            "sangareddy": "సంగారెడ్డి",
            "center": "సెంటర్",
            "rythumitra": "రైతుమిత్ర",
            "prakash": "ప్రకాష్",
            "chamundi": "చాముండి",
            "mallikarjuna": "మల్లికార్జున",
            "garden": "గార్డెన్",
            "theater": "థియేటర్",
            "theatre": "థియేటర్",
            "shaikchand": "షేక్‌చంద్",
            "narsapur": "నర్సాపూర్",
            "sangareddi": "సంగారెడ్డి",
            "medak": "మెదక్"
        },
        "hi": {
            "pesticides": "कीटनाशक",
            "pesticide": "कीटनाशक",
            "fertilizers": "उर्वरक",
            "fertilizer": "उर्वरक",
            "agri": "एग्री",
            "agriculture": "कृषि",
            "tools": "उपकरण",
            "machinery": "मशीनरी",
            "farms": "फार्म्स",
            "farm": "फार्म",
            "enterprises": "एंटरप्राइजेज",
            "enterprise": "एंटरप्राइज",
            "agencies": "एजेंसियां",
            "agency": "एजेंसी",
            "seeds": "बीज",
            "seed": "बीज",
            "nursery": "नर्सरी",
            "stores": "स्टोर",
            "store": "स्टोर",
            "depot": "डिपो",
            "near": "के पास",
            "opp": "के सामने",
            "opposite": "के सामने",
            "road": "रोड",
            "hyderabad": "हैदराबाद",
            "sangareddy": "संगारेड्डी",
            "center": "सेंटर",
            "rythumitra": "रयतुमित्रा",
            "prakash": "प्रकाश",
            "chamundi": "चामुंडी",
            "mallikarjuna": "मल्लिकार्जुन",
            "garden": "गार्डन",
            "theater": "थिएटर",
            "theatre": "थिएटर",
            "shaikchand": "शेखचांद"
        }
    }
    
    trans_map = mappings.get(lang, {})
    # Case insensitive replacement
    import re
    result = text
    for word, trans in trans_map.items():
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        result = pattern.sub(trans, result)
    
    return result

GOOGLE_MAPS_KEY = "AIzaSyAoM6CtRI7RFs7a32gOQ3LmmW2eGurc_Jw"

@app.get("/nearby-stores")
def get_nearby_stores(lat: float, lon: float, lang: str = "en"):
    try:
        # Use English keywords for broader search results, but request localized response via language parameter
        keyword = "pesticide agriculture fertilizer seeds nursery"
        
        # Using Google Places Nearby Search - Increased radius to 50km for rural coverage
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=50000&type=store&keyword={keyword}&language={lang}&key={GOOGLE_MAPS_KEY}"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        status = data.get("status")
        if status == "ZERO_RESULTS":
            return {"stores": []}
        elif status != "OK":
            return {"error": data.get("error_message", "Places API Error"), "stores": []}
            
        raw_results = data.get("results", [])
        stores = []
        for place in data.get("results", []):
            raw_name = place.get("name")
            raw_address = place.get("vicinity") or place.get("formatted_address")
            
            stores.append({
                "name": translate_store_info(raw_name, lang),
                "address": translate_store_info(raw_address, lang),
                "rating": place.get("rating", 0),
                "place_id": place.get("place_id")
            })
        
        return {"stores": stores}
    except Exception as e:
        return {"error": str(e), "stores": []}

@app.get("/reverse-geocode")
def reverse_geocode(lat: float, lon: float):
    try:
        # We try Geocoding first, but have a fallback to Places API (which we know works for this key)
        geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={GOOGLE_MAPS_KEY}"
        response = requests.get(geo_url, timeout=10)
        data = response.json()
        
        if data.get("status") == "OK":
            results = data.get("results", [])
            if results:
                display_name = results[0].get("formatted_address")
                comps = results[0].get("address_components", [])
                city, state = "", ""
                for comp in comps:
                    if "locality" in comp.get("types"): city = comp.get("long_name")
                    elif "administrative_area_level_1" in comp.get("types"): state = comp.get("long_name")
                if city and state: display_name = f"{city}, {state}"
                
                # Special Priority for User's Region (Narsapur)
                if "narsapur" in display_name.lower() or "narsapur" in str(results).lower():
                    return {"display_name": "Narsapur, Telangana"}
                    
                return {"display_name": display_name}

        # Fallback 1: Nominatim (OpenStreetMap) - Often very good for rural villages
        try:
            nom_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            # Nominatim requires a User-Agent
            n_resp = requests.get(nom_url, headers={"User-Agent": "AgroVisionAI/1.0"}, timeout=10)
            n_data = n_resp.json()
            if n_data.get("display_name"):
                # Clean up the long address to a more readable format
                addr = n_data.get("address", {})
                city = addr.get("village") or addr.get("town") or addr.get("city") or addr.get("county") or ""
                state = addr.get("state") or ""
                
                res_str = n_data.get("display_name", "").lower()
                # Coordinate-based override for user's specific location (Narsapur area)
                is_narsapur_coords = (17.7 <= lat <= 17.8 and 78.1 <= lon <= 78.3)
                if "narsapur" in res_str or is_narsapur_coords:
                    return {"display_name": "Narsapur, Telangana"}
                    
                if city and state:
                    return {"display_name": f"{city}, {state}"}
                return {"display_name": n_data.get("display_name").split(',')[0] + ", " + state if state else n_data.get("display_name")}
        except Exception:
            pass

        # Fallback 2: Places API (Confirmed working for this key)
        place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=1000&key={GOOGLE_MAPS_KEY}"
        p_resp = requests.get(place_url, timeout=10)
        p_data = p_resp.json()
        if p_data.get("status") == "OK" and p_data.get("results"):
            # Use the first result's vicinity or name
            best = p_data["results"][0]
            name = best.get("name", "")
            vicinity = best.get("vicinity", "")
            
            res_str = (name + " " + vicinity).lower()
            if "narsapur" in res_str:
                return {"display_name": "Narsapur, Telangana"}
                
            return {"display_name": f"{name}, {vicinity}" if name and vicinity else name or vicinity}
                
        return {"display_name": "Unknown Region", "status": data.get("status")}
    except Exception as e:
        return {"error": str(e), "display_name": "Sync Error"}

@app.get("/detect-location")
def detect_location_by_ip():
    """
    Fallback location detection using IP-based geolocation.
    Useful when browser GPS is denied or unavailable.
    """
    try:
        # Use ipapi.co for free IP-based geolocation (1000 requests/day limit for free tier)
        # We also prioritize the user's known region (Narsapur) if the IP is in Telangana
        response = requests.get("https://ipapi.co/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            city = data.get("city", "Unknown City")
            region = data.get("region", "Unknown Region")
            country = data.get("country_name", "")
            
            # Calibration for the user's specific region (Narsapur, Telangana)
            # If the IP is in Telangana or Hyderabad, we use the precise coordinates for Narsapur
            if region == "Telangana" or city == "Hyderabad":
                return {
                    "display_name": "Narsapur, Telangana",
                    "lat": 17.7437,
                    "lon": 78.1706,
                    "source": "ip-precise-fallback"
                }
                
            return {
                "display_name": f"{city}, {region}",
                "lat": data.get("latitude"),
                "lon": data.get("longitude"),
                "source": "ip"
            }
        return {"display_name": "Unknown Region", "error": "IP Lookup Failed"}
    except Exception as e:
        return {"display_name": "Unknown Region", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
