"""
AgriHelp — Smart Agri Assist  |  Flask Backend  |  v2.0
==========================================================
Features:
  ✅ Livestock disease prediction  (Cow, Goat, Sheep, Poultry, Fish)
  ✅ Crop disease detection        (crop_model.pkl — 7 symptom features)
  ✅ Real-time advisory            (Gemini 1.5 Flash — Crops / Livestock / Aquaculture)
  ✅ Marketplace CRUD
  ✅ Government schemes
  ✅ Login / Auth (simple JWT-style token, no DB required)
"""

import os
import json
import time
import base64
import hashlib
import hmac
import joblib
import numpy as np
import google.generativeai as genai

from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from io import BytesIO
from functools import wraps
# ─────────────────────────────────────────────
# App Init
# ─────────────────────────────────────────────
app = Flask(__name__)
CORS(app, origins=["*"])   # allow all origins for team dev; restrict in production

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
MODEL_DIR = Path("models")

# ─────────────────────────────────────────────
# Gemini Configuration
# ─────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyClVW5_jB5ece4rNYMsIjHbETbGO78YQMk")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# ─────────────────────────────────────────────
# Auth — Simple token (no DB needed)
# ─────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "agrihelp_secret_2024")

# In-memory user store (replace with DB in production)
USERS = {
    "pranibhuyan@gmail.com": {
        "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "name": "Puja Rani Bhuyan",
    }
}

def make_token(email: str) -> str:
    payload = base64.b64encode(f"{email}:{time.time()}".encode()).decode()
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"

def verify_token(token: str) -> str | None:
    """Returns email if valid, None otherwise."""
    try:
        payload, sig = token.rsplit(".", 1)
        expected = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        email = base64.b64decode(payload.encode()).decode().split(":")[0]
        return email
    except Exception:
        return None

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Authentication required"}), 401
        token = auth_header[7:]
        email = verify_token(token)
        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401
        request.current_user = email
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────
# Load ML Models
# ─────────────────────────────────────────────
def load_model(name):
    path = MODEL_DIR / f"{name}_model.pkl"
    if path.exists():
        try:
            return joblib.load(path)
        except Exception as e:
            print(f"[WARN] Could not load {name} model: {e}")
    return None

models = {
    "cow":     load_model("cow"),
    "goat":    load_model("goat"),
    "sheep":   load_model("sheep"),
    "poultry": load_model("poultry"),
    "fish":    load_model("fish"),
    "crop":    load_model("crop"),
}

# ─────────────────────────────────────────────
# Crop — Feature Columns (matches frontend chips exactly)
# ─────────────────────────────────────────────
CROP_SYMPTOM_COLUMNS = [
    "Yellowing_leaves",
    "Brown_black_spots",
    "Wilting_drooping",
    "White_powdery_patches",
    "Stem_lesions_rot",
    "Holes_in_leaves",
    "Stunted_growth",
]

CROP_SYMPTOM_LABEL_MAP = {
    "Yellowing leaves":       "Yellowing_leaves",
    "Brown / black spots":    "Brown_black_spots",
    "Wilting / drooping":     "Wilting_drooping",
    "White powdery patches":  "White_powdery_patches",
    "Stem lesions / rot":     "Stem_lesions_rot",
    "Holes in leaves":        "Holes_in_leaves",
    "Stunted growth":         "Stunted_growth",
}

CROP_DISEASE_INFO = {
    "Bacterial_Spot": {
        "severity": "High",
        "affected_plant": "Tomato / Pepper",
        "symptoms_observed": "Small, water-soaked spots turning dark brown with yellow halos.",
        "treatment": "Apply copper-based bactericides. Remove infected leaves. Avoid overhead irrigation.",
        "prevention": "Use disease-free seeds, crop rotation, and resistant varieties.",
        "organic_remedy": "Neem oil spray 5ml/L + copper soap solution every 7 days.",
        "urgency": "within_week",
    },
    "Late_Blight": {
        "severity": "Critical",
        "affected_plant": "Tomato / Potato",
        "symptoms_observed": "Dark water-soaked lesions on leaves, white mold on undersides.",
        "treatment": "Apply Mancozeb 75WP @ 2.5g/L immediately. Remove all infected tissue.",
        "prevention": "Avoid wet foliage, ensure good air circulation, use blight-resistant varieties.",
        "organic_remedy": "Compost tea spray + baking soda solution (1 tsp/L) every 5 days.",
        "urgency": "immediate",
    },
    "Leaf_Rust": {
        "severity": "Moderate",
        "affected_plant": "Wheat / Barley / Maize",
        "symptoms_observed": "Orange-brown powdery pustules on leaf surface.",
        "treatment": "Propiconazole or tebuconazole fungicide application. Remove heavily infected plants.",
        "prevention": "Plant resistant varieties, early sowing, avoid excess nitrogen.",
        "organic_remedy": "Garlic extract spray 10g/L every 7–10 days.",
        "urgency": "within_week",
    },
    "Pest_Infestation": {
        "severity": "High",
        "affected_plant": "General",
        "symptoms_observed": "Holes in leaves, chewed edges, insect frass visible.",
        "treatment": "Apply appropriate insecticide (chlorpyrifos/spinosad). Manual removal of egg masses.",
        "prevention": "Regular scouting, sticky traps, encourage natural predators.",
        "organic_remedy": "Neem oil 10ml/L + garlic extract spray. Release ladybugs/parasitic wasps.",
        "urgency": "within_week",
    },
    "Powdery_Mildew": {
        "severity": "Moderate",
        "affected_plant": "Cucurbits / Grapes / Wheat",
        "symptoms_observed": "White powdery coating on leaves and stems.",
        "treatment": "Sulphur-based fungicide 3g/L or systemic fungicide (myclobutanil). Improve ventilation.",
        "prevention": "Avoid excess humidity, space plants properly, use resistant varieties.",
        "organic_remedy": "Baking soda spray 1 tsp/L + potassium bicarbonate every 5–7 days.",
        "urgency": "within_week",
    },
    "Stem_Rot": {
        "severity": "High",
        "affected_plant": "Rice / Groundnut / Sunflower",
        "symptoms_observed": "Dark lesions at stem base, wilting despite adequate water.",
        "treatment": "Drench soil with carbendazim 1g/L. Remove and destroy infected plants.",
        "prevention": "Avoid waterlogging, improve drainage, treat seeds before sowing.",
        "organic_remedy": "Trichoderma viride @ 5g/L soil drench. Reduce soil moisture.",
        "urgency": "immediate",
    },
    "Healthy": {
        "severity": "None",
        "affected_plant": "N/A",
        "symptoms_observed": "No disease symptoms detected.",
        "treatment": "No treatment required. Continue regular monitoring.",
        "prevention": "Maintain crop rotation, balanced fertilization, and regular scouting.",
        "organic_remedy": "Continue preventive neem oil spray every 15 days.",
        "urgency": "none",
    },
}

# ─────────────────────────────────────────────
# Livestock — Symptom Columns & Disease Info
# ─────────────────────────────────────────────
LIVESTOCK_SYMPTOM_COLUMNS = {
    "cow": [
        "Limping_Difficulty_walking", "Loss_of_appetite", "Fever_High_temperature",
        "Visible_wounds_or_sores", "Swollen_joints_or_limbs", "Discharge_eyes_nose",
        "Labored_breathing", "Unusual_behavior_lethargy",
    ],
    "goat": [
        "Limping_Difficulty_walking", "Loss_of_appetite", "Fever_High_temperature",
        "Bloating_Distended_abdomen", "Diarrhea_Loose_stools", "Discharge_eyes_nose",
        "Labored_breathing", "Unusual_behavior_lethargy",
    ],
    "sheep": [
        "Limping_Difficulty_walking", "Loss_of_appetite", "Fever_High_temperature",
        "Wool_loss_Skin_irritation", "Swollen_face_or_limbs", "Discharge_eyes_nose",
        "Labored_breathing", "Unusual_behavior_lethargy",
    ],
    "poultry": [
        "Loss_of_appetite", "Reduced_egg_production", "Swollen_head_or_face",
        "Discharge_eyes_nostrils", "Ruffled_feathers_lethargy", "Labored_breathing",
        "Diarrhea_Unusual_droppings", "Difficulty_walking_paralysis",
    ],
    "fish": [
        "White_spots_fuzzy_patches", "Frayed_rotting_fins", "Bloating_raised_scales",
        "Swimming_erratically", "Loss_of_appetite", "Lethargy_resting_at_bottom",
        "Gasping_at_surface", "Visible_parasites",
    ],
}

LIVESTOCK_LABEL_MAP = {
    "cow": {
        "Limping / Difficulty walking": "Limping_Difficulty_walking",
        "Loss of appetite":             "Loss_of_appetite",
        "Fever / High temperature":     "Fever_High_temperature",
        "Visible wounds or sores":      "Visible_wounds_or_sores",
        "Swollen joints or limbs":      "Swollen_joints_or_limbs",
        "Discharge from eyes/nose":     "Discharge_eyes_nose",
        "Labored breathing":            "Labored_breathing",
        "Unusual behavior / lethargy":  "Unusual_behavior_lethargy",
    },
    "goat": {
        "Limping / Difficulty walking":  "Limping_Difficulty_walking",
        "Loss of appetite":              "Loss_of_appetite",
        "Fever / High temperature":      "Fever_High_temperature",
        "Bloating / Distended abdomen":  "Bloating_Distended_abdomen",
        "Diarrhea / Loose stools":       "Diarrhea_Loose_stools",
        "Discharge from eyes/nose":      "Discharge_eyes_nose",
        "Labored breathing":             "Labored_breathing",
        "Unusual behavior / lethargy":   "Unusual_behavior_lethargy",
    },
    "sheep": {
        "Limping / Difficulty walking":  "Limping_Difficulty_walking",
        "Loss of appetite":              "Loss_of_appetite",
        "Fever / High temperature":      "Fever_High_temperature",
        "Wool loss / Skin irritation":   "Wool_loss_Skin_irritation",
        "Swollen face or limbs":         "Swollen_face_or_limbs",
        "Discharge from eyes/nose":      "Discharge_eyes_nose",
        "Labored breathing":             "Labored_breathing",
        "Unusual behavior / lethargy":   "Unusual_behavior_lethargy",
    },
    "poultry": {
        "Loss of appetite":                "Loss_of_appetite",
        "Reduced egg production":          "Reduced_egg_production",
        "Swollen head or face":            "Swollen_head_or_face",
        "Discharge from eyes/nostrils":    "Discharge_eyes_nostrils",
        "Ruffled feathers / lethargy":     "Ruffled_feathers_lethargy",
        "Labored breathing":               "Labored_breathing",
        "Diarrhea / Unusual droppings":    "Diarrhea_Unusual_droppings",
        "Difficulty walking / paralysis":  "Difficulty_walking_paralysis",
    },
    "fish": {
        "White spots / fuzzy patches":    "White_spots_fuzzy_patches",
        "Frayed / rotting fins":          "Frayed_rotting_fins",
        "Bloating / raised scales":       "Bloating_raised_scales",
        "Swimming erratically":           "Swimming_erratically",
        "Loss of appetite":               "Loss_of_appetite",
        "Lethargy / resting at bottom":   "Lethargy_resting_at_bottom",
        "Gasping at surface":             "Gasping_at_surface",
        "Visible parasites":              "Visible_parasites",
    },
}

LIVESTOCK_DISEASE_INFO = {
    "Bovine_Respiratory_Disease": {"severity":"High","description":"Respiratory infection caused by bacteria and viruses.","treatment":"Antibiotic therapy (florfenicol or tulathromycin), anti-inflammatories, clean ventilated housing.","prevention":"Vaccination, stress reduction, avoid overcrowding."},
    "Foot_and_Mouth_Disease":     {"severity":"Critical","description":"Highly contagious viral disease affecting hooves and mouth.","treatment":"No specific cure — supportive care, wound cleaning, isolation. Report to authorities immediately.","prevention":"Regular FMD vaccination, biosecurity."},
    "Pinkeye":                    {"severity":"Moderate","description":"Infectious bovine keratoconjunctivitis causing eye inflammation.","treatment":"Oxytetracycline or penicillin injection, fly control, isolate affected animals.","prevention":"Fly control, minimize UV exposure, vaccination."},
    "Joint_Ill":                  {"severity":"Moderate","description":"Bacterial infection of joints in young calves.","treatment":"Early antibiotic treatment (penicillin/amoxicillin), joint flushing in severe cases.","prevention":"Adequate colostrum intake in newborns, navel disinfection."},
    "Blackleg":                   {"severity":"Critical","description":"Rapidly fatal bacterial disease caused by Clostridium chauvoei.","treatment":"High-dose penicillin if caught early — fatality often rapid.","prevention":"Annual Clostridial vaccination."},
    "Enterotoxemia_Overeating_Disease": {"severity":"High","description":"Caused by Clostridium perfringens — triggered by feed change.","treatment":"Antitoxin (Types C & D), reduce grain intake, supportive fluids.","prevention":"CD&T vaccination, gradual diet transitions."},
    "Pneumonia":                  {"severity":"High","description":"Lung infection caused by bacteria, viruses, or parasites.","treatment":"Broad-spectrum antibiotics (oxytetracycline), anti-inflammatories, supportive care.","prevention":"Good ventilation, avoid stress, vaccinate."},
    "Foot_Rot":                   {"severity":"Moderate","description":"Bacterial infection between toes causing lameness and foul odor.","treatment":"Foot bathing with zinc sulfate, penicillin injection, trim hooves.","prevention":"Dry conditions, foot baths, zinc supplementation."},
    "CAE_Arthritis":              {"severity":"Moderate","description":"Caprine Arthritis Encephalitis — viral, causes joint swelling.","treatment":"No cure — manage pain with NSAIDs, cull infected animals.","prevention":"Test and cull program, avoid CAE-positive colostrum."},
    "Coccidiosis":                {"severity":"Moderate","description":"Intestinal parasitic disease causing diarrhea, mainly in young animals.","treatment":"Amprolium or sulfonamide drugs, oral rehydration therapy.","prevention":"Clean pens, coccidiostat in feed, avoid overcrowding."},
    "PPR_Goat_Plague":            {"severity":"Critical","description":"Highly contagious Morbillivirus — notifiable disease.","treatment":"No specific treatment — supportive care, antibiotics for secondary infections.","prevention":"PPR vaccination, strict biosecurity, quarantine new animals."},
    "Sheep_Scab":                 {"severity":"High","description":"Highly contagious mange caused by Psoroptes ovis mites.","treatment":"Injectable ivermectin or doramectin, organophosphate dipping.","prevention":"Quarantine new sheep, regular treatments."},
    "Enterotoxemia":              {"severity":"High","description":"Clostridial overgrowth — often called pulpy kidney.","treatment":"Antitoxin, penicillin, supportive care.","prevention":"CD&T vaccination, gradual diet transitions."},
    "Orf_Disease":                {"severity":"Moderate","description":"Contagious pustular dermatitis — zoonotic risk.","treatment":"Self-limiting in 3–4 weeks; topical antiseptics, prevent secondary infection.","prevention":"Orf vaccination, wear gloves when handling."},
    "Bluetongue":                 {"severity":"High","description":"Insect-borne viral disease causing fever, oral ulcers, swelling.","treatment":"Supportive care — NSAIDs, good nutrition, wound care.","prevention":"Bluetongue vaccination, midge control."},
    "Fowl_Pox":                   {"severity":"Moderate","description":"Slow-spreading viral disease causing skin lesions.","treatment":"No specific treatment — supportive care, treat secondary infections.","prevention":"Fowl pox vaccination, mosquito control."},
    "Infectious_Coryza":          {"severity":"Moderate","description":"Bacterial respiratory disease causing nasal discharge.","treatment":"Sulfonamides, erythromycin, or tetracyclines.","prevention":"All-in/all-out management, vaccination."},
    "Newcastle_Disease":          {"severity":"Critical","description":"Highly contagious viral disease — notifiable.","treatment":"No specific treatment — supportive care, biosecurity.","prevention":"ND vaccination, strict biosecurity."},
    "Mareks_Disease":             {"severity":"High","description":"Herpesvirus causing paralysis, tumors, immunosuppression.","treatment":"No treatment — cull severely affected birds.","prevention":"Marek's vaccination at hatchery."},
    "Infectious_Bronchitis":      {"severity":"High","description":"Coronavirus causing respiratory distress and reduced egg production.","treatment":"Supportive care — antibiotics for secondary infections, electrolytes.","prevention":"IB vaccination, good biosecurity."},
    "Avian_Influenza":            {"severity":"Critical","description":"Highly pathogenic — zoonotic risk. Notifiable.","treatment":"Immediate quarantine and culling as per government protocol.","prevention":"Strict biosecurity, limit wild bird contact."},
    "Ich_White_Spot":             {"severity":"Moderate","description":"Parasitic infection causing white salt-grain-like spots.","treatment":"Raise water temp to 30°C, add salt, use malachite green or formalin.","prevention":"Quarantine new fish, maintain water quality."},
    "Fin_Rot":                    {"severity":"Moderate","description":"Bacterial infection causing fin fraying and necrosis.","treatment":"Improve water quality, antibiotics (kanamycin/tetracycline).","prevention":"Good water quality, avoid fin nipping."},
    "Dropsy":                     {"severity":"High","description":"Fluid accumulation and scale raising (pinecone appearance).","treatment":"Epsom salt baths, antibiotics (metronidazole + kanamycin), isolate fish.","prevention":"Clean water, avoid overfeeding."},
    "Columnaris":                 {"severity":"High","description":"Bacterial disease causing gray-white lesions.","treatment":"Antibiotics in water (terramycin), salt baths, improve aeration.","prevention":"High oxygen levels, avoid injury, quarantine."},
    "External_Parasites":         {"severity":"Moderate","description":"Visible parasites attached to body or gills.","treatment":"Physical removal, potassium permanganate bath, antiparasitic meds.","prevention":"Quarantine new fish, regular inspection."},
    "Swim_Bladder_Disease":       {"severity":"Moderate","description":"Disorder affecting buoyancy control.","treatment":"Fast the fish 24–48 hrs, feed peas, treat underlying infection.","prevention":"Avoid overfeeding, maintain water quality."},
    "Healthy":                    {"severity":"None","description":"No disease indicators detected.","treatment":"Continue regular health monitoring and good husbandry.","prevention":"Routine vaccination, balanced nutrition, clean water, regular vet checkups."},
}

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def encode_livestock_symptoms(animal: str, symptoms_list: list) -> list:
    cols = LIVESTOCK_SYMPTOM_COLUMNS[animal]
    label_map = LIVESTOCK_LABEL_MAP[animal]
    active = set()
    for s in symptoms_list:
        s = s.strip()
        if s in label_map:
            active.add(label_map[s])
        elif s in cols:
            active.add(s)
    return [1 if c in active else 0 for c in cols]

def encode_crop_symptoms(symptoms_list: list) -> list:
    active = set()
    for s in symptoms_list:
        s = s.strip()
        if s in CROP_SYMPTOM_LABEL_MAP:
            active.add(CROP_SYMPTOM_LABEL_MAP[s])
        elif s in CROP_SYMPTOM_COLUMNS:
            active.add(s)
    return [1 if c in active else 0 for c in CROP_SYMPTOM_COLUMNS]

def rule_based_livestock(animal: str, fv: list) -> tuple:
    cols = LIVESTOCK_SYMPTOM_COLUMNS[animal]
    n = sum(fv)
    if n == 0:
        return "Healthy", 95
    sv = dict(zip(cols, fv))
    if animal == "cow":
        if sv.get("Labored_breathing") and sv.get("Discharge_eyes_nose") and sv.get("Fever_High_temperature"):
            return "Bovine_Respiratory_Disease", 88
        if sv.get("Limping_Difficulty_walking") and sv.get("Visible_wounds_or_sores"):
            return "Foot_and_Mouth_Disease", 82
        if sv.get("Limping_Difficulty_walking") and sv.get("Swollen_joints_or_limbs"):
            return "Joint_Ill", 78
        if sv.get("Unusual_behavior_lethargy") and sv.get("Fever_High_temperature"):
            return "Blackleg", 75
        if sv.get("Discharge_eyes_nose"):
            return "Pinkeye", 70
    elif animal == "goat":
        if sv.get("Labored_breathing") and sv.get("Fever_High_temperature"):
            return "Pneumonia", 85
        if sv.get("Bloating_Distended_abdomen"):
            return "Enterotoxemia_Overeating_Disease", 82
        if sv.get("Limping_Difficulty_walking"):
            return "Foot_Rot", 78
        if sv.get("Diarrhea_Loose_stools"):
            return "Coccidiosis", 76
        if sv.get("Fever_High_temperature") and sv.get("Discharge_eyes_nose"):
            return "PPR_Goat_Plague", 80
    elif animal == "sheep":
        if sv.get("Labored_breathing") and sv.get("Fever_High_temperature"):
            return "Pneumonia", 85
        if sv.get("Wool_loss_Skin_irritation"):
            return "Sheep_Scab", 82
        if sv.get("Swollen_face_or_limbs") and sv.get("Fever_High_temperature"):
            return "Bluetongue", 80
        if sv.get("Limping_Difficulty_walking"):
            return "Foot_Rot", 78
    elif animal == "poultry":
        if sv.get("Swollen_head_or_face") and sv.get("Discharge_eyes_nostrils"):
            return "Infectious_Coryza", 85
        if sv.get("Difficulty_walking_paralysis"):
            return "Mareks_Disease", 82
        if sv.get("Labored_breathing") and sv.get("Reduced_egg_production"):
            return "Infectious_Bronchitis", 80
        if sv.get("Ruffled_feathers_lethargy") and sv.get("Labored_breathing"):
            return "Newcastle_Disease", 78
        if sv.get("Diarrhea_Unusual_droppings"):
            return "Coccidiosis", 76
    elif animal == "fish":
        if sv.get("White_spots_fuzzy_patches"):
            return "Ich_White_Spot", 90
        if sv.get("Frayed_rotting_fins"):
            return "Fin_Rot", 85
        if sv.get("Bloating_raised_scales"):
            return "Dropsy", 82
        if sv.get("Visible_parasites"):
            return "External_Parasites", 88
        if sv.get("Swimming_erratically"):
            return "Swim_Bladder_Disease", 78
        if sv.get("Gasping_at_surface") or sv.get("Lethargy_resting_at_bottom"):
            return "Columnaris", 72
    return "Healthy", 65


# ══════════════════════════════════════════════
# ░░ ROUTES ░░
# ══════════════════════════════════════════════

# ── Health Check ─────────────────────────────
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "AgriHelp Backend v2",
        "models_loaded": {k: (v is not None) for k, v in models.items()},
    })


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = USERS.get(email)
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    if not hmac.compare_digest(pwd_hash, user["password_hash"]):
        return jsonify({"message": "Invalid email or password"}), 401

    token = make_token(email)
    return jsonify({
        "success": True,
        "data": {
            "token": token,
            "user": {"email": email, "name": user["name"]},
        }
    })

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "Farmer")

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400
    if email in USERS:
        return jsonify({"message": "Email already registered"}), 409

    USERS[email] = {
        "password_hash": hashlib.sha256(password.encode()).hexdigest(),
        "name": name,
    }
    token = make_token(email)
    return jsonify({
        "success": True,
        "data": {
            "token": token,
            "user": {"email": email, "name": name},
        }
    }), 201

@app.route("/api/auth/me", methods=["GET"])
@auth_required
def get_me():
    email = request.current_user
    user = USERS.get(email, {})
    return jsonify({"success": True, "data": {"email": email, "name": user.get("name", "Farmer")}})


# ─────────────────────────────────────────────
# CROP DISEASE DETECTION
# POST /api/crop/detect
# Form fields: symptoms (JSON array), other_observations (string, optional)
# ─────────────────────────────────────────────
@app.route("/api/crop/detect", methods=["POST"])
def crop_detect():
    try:
        raw = request.form.get("symptoms", "[]")
        symptoms = json.loads(raw)
        other_obs = request.form.get("other_observations", "").strip()

        # Add other_observations as extra context (doesn't affect model, used in response)
        fv = encode_crop_symptoms(symptoms)
        symptom_count = sum(fv)

        crop_model = models.get("crop")
        if crop_model is not None:
            X = np.array(fv).reshape(1, -1)
            disease = crop_model.predict(X)[0]
            proba = crop_model.predict_proba(X)[0]
            confidence = round(float(np.max(proba)) * 100, 1)
        else:
            # Fallback rule-based
            if fv[3]:  # White powdery patches
                disease, confidence = "Powdery_Mildew", 85
            elif fv[5]:  # Holes in leaves
                disease, confidence = "Pest_Infestation", 80
            elif fv[4]:  # Stem lesions
                disease, confidence = "Stem_Rot", 78
            elif fv[1]:  # Brown spots
                disease, confidence = "Bacterial_Spot", 75
            elif symptom_count == 0:
                disease, confidence = "Healthy", 95
            else:
                disease, confidence = "Late_Blight", 70

        info = CROP_DISEASE_INFO.get(disease, CROP_DISEASE_INFO["Healthy"])
        active_symptoms = [CROP_SYMPTOM_COLUMNS[i] for i, v in enumerate(fv) if v == 1]

        return jsonify({
            "success": True,
            "data": {
                "disease_name": disease,
                "disease_display": disease.replace("_", " "),
                "confidence": confidence,
                "severity": info["severity"],
                "affected_plant": info["affected_plant"],
                "symptoms_observed": info["symptoms_observed"],
                "treatment": info["treatment"],
                "prevention": info["prevention"],
                "organic_remedy": info["organic_remedy"],
                "urgency": info["urgency"],
                "symptoms_detected": active_symptoms,
                "symptom_count": symptom_count,
                "other_observations": other_obs,
                "disease_detected": disease != "Healthy",
                "status": "healthy" if disease == "Healthy" else "disease_detected",
            }
        })
    except Exception as e:
        app.logger.error(f"Crop detect error: {e}")
        return jsonify({"message": str(e)}), 500


# ─────────────────────────────────────────────
# LIVESTOCK HEALTH CHECK
# POST /api/livestock/analyze
# Form fields: animal_type, symptoms (JSON), image (optional file)
# ─────────────────────────────────────────────
@app.route("/api/livestock/analyze", methods=["POST"])
def livestock_analyze():
    try:
        raw = request.form.get("symptoms", "[]")
        symptoms = json.loads(raw)
        animal = request.form.get("animal_type", "cow").lower().strip()

        if animal not in LIVESTOCK_SYMPTOM_COLUMNS:
            return jsonify({"message": f"Unknown animal type: {animal}"}), 400

        fv = encode_livestock_symptoms(animal, symptoms)
        model = models.get(animal)

        if model is not None:
            X = np.array(fv).reshape(1, -1)
            disease = model.predict(X)[0]
            proba = model.predict_proba(X)[0]
            confidence = round(float(np.max(proba)) * 100, 1)
            source = "ml_model"
        else:
            disease, confidence = rule_based_livestock(animal, fv)
            source = "rule_based"

        info = LIVESTOCK_DISEASE_INFO.get(disease, LIVESTOCK_DISEASE_INFO["Healthy"])
        cols = LIVESTOCK_SYMPTOM_COLUMNS[animal]
        active = [cols[i] for i, v in enumerate(fv) if v == 1]

        return jsonify({
            "success": True,
            "data": {
                "animal": animal,
                "disease": disease,
                "disease_display": disease.replace("_", " "),
                "confidence": confidence,
                "severity": info["severity"],
                "description": info["description"],
                "treatment": info["treatment"],
                "prevention": info["prevention"],
                "symptoms_detected": active,
                "symptom_count": sum(fv),
                "prediction_source": source,
                "status": "healthy" if disease == "Healthy" else "disease_detected",
                "urgency": "High" if info["severity"] in ("Critical", "High") else "Normal",
            }
        })
    except Exception as e:
        app.logger.error(f"Livestock analyze error: {e}")
        return jsonify({"message": str(e)}), 500

# Per-animal convenience routes
for _animal in ["cow", "goat", "sheep", "poultry", "fish"]:
    def _make_route(a):
        def _route():
            request.form = request.form.copy()
            # inject animal_type then call main handler
            from werkzeug.datastructures import ImmutableMultiDict
            d = request.form.to_dict()
            d["animal_type"] = a
            request.environ["werkzeug.request"].form = ImmutableMultiDict(d)
            return livestock_analyze()
        _route.__name__ = f"analyze_{a}"
        return _route
    app.add_url_rule(f"/api/livestock/{_animal}", view_func=_make_route(_animal), methods=["POST"])


# ─────────────────────────────────────────────
# REAL-TIME ADVISORY  (Gemini powered)
# POST /api/recommend
# JSON body — category determines which prompt is used
#
# category: "crops"
#   land_size_acres, soil_type, season, water_availability, budget_inr
#
# category: "livestock"
#   animal_focus, available_space_sqft, fodder_availability, budget_inr
#
# category: "aquaculture"
#   water_body_size_acres, water_source, pond_type, budget_inr
# ─────────────────────────────────────────────

def _build_crop_prompt(d: dict) -> str:
    return f"""
You are KisanAI, an expert agricultural consultant specializing in Indian farming.
A farmer has:
- Land: {d.get('land_size_acres', 'N/A')} acres
- Soil: {d.get('soil_type', 'N/A')}
- Season: {d.get('season', 'N/A')}
- Water: {d.get('water_availability', 'N/A')}
- Budget: ₹{float(d.get('budget_inr') or 0):,.0f}

Return EXACTLY 3 crop recommendations as a JSON array. Each object must have:
- "activity_name": string (specific crop, e.g. "Bt Cotton")
- "recommendation_type": "Primary" | "Alternative 1" | "Alternative 2"
- "estimated_roi_percentage": string (e.g. "35–45%")
- "risk_level": "Low" | "Medium" | "High"
- "timeline_to_revenue": string (e.g. "90–120 days")
- "expected_revenue_inr": string (e.g. "₹1,20,000 – ₹1,50,000 per season")
- "brief_reason": string (2 sentences)
- "key_tips": array of 3 strings

Return ONLY the JSON array. No markdown, no extra text.
"""

def _build_livestock_prompt(d: dict) -> str:
    return f"""
You are KisanAI, an expert in Indian animal husbandry.
A farmer has:
- Animal focus: {d.get('animal_focus', 'N/A')}
- Space: {d.get('available_space_sqft', 'N/A')} sq ft
- Fodder: {d.get('fodder_availability', 'N/A')}
- Budget: ₹{float(d.get('budget_inr') or 0):,.0f}

Return EXACTLY 3 livestock recommendations as a JSON array. Each object must have:
- "activity_name": string (e.g. "Murrah Buffalo Dairy")
- "recommendation_type": "Primary" | "Alternative 1" | "Alternative 2"
- "estimated_roi_percentage": string
- "risk_level": "Low" | "Medium" | "High"
- "timeline_to_revenue": string
- "expected_revenue_inr": string
- "brief_reason": string (2 sentences)
- "key_tips": array of 3 strings

Return ONLY the JSON array. No markdown, no extra text.
"""

def _build_aquaculture_prompt(d: dict) -> str:
    return f"""
You are KisanAI, an expert in Indian aquaculture.
A farmer has:
- Water body: {d.get('water_body_size_acres', 'N/A')} acres
- Water source: {d.get('water_source', 'N/A')}
- Pond type: {d.get('pond_type', 'N/A')}
- Budget: ₹{float(d.get('budget_inr') or 0):,.0f}

Return EXACTLY 3 aquaculture recommendations as a JSON array. Each object must have:
- "activity_name": string (e.g. "Rohu-Catla Polyculture")
- "recommendation_type": "Primary" | "Alternative 1" | "Alternative 2"
- "estimated_roi_percentage": string
- "risk_level": "Low" | "Medium" | "High"
- "timeline_to_revenue": string
- "expected_revenue_inr": string
- "brief_reason": string (2 sentences)
- "key_tips": array of 3 strings

Return ONLY the JSON array. No markdown, no extra text.
"""

@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json() or {}
        category = data.get("category", "crops").lower()

        if category == "crops":
            prompt = _build_crop_prompt(data)
        elif category == "livestock":
            prompt = _build_livestock_prompt(data)
        elif category == "aquaculture":
            prompt = _build_aquaculture_prompt(data)
        else:
            return jsonify({"message": f"Unknown category: {category}. Use crops/livestock/aquaculture"}), 400

        response = gemini_model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        recommendations = json.loads(response.text)

        return jsonify({
            "success": True,
            "data": {
                "category": category,
                "recommendations": recommendations,
            }
        })

    except json.JSONDecodeError:
        return jsonify({"message": "AI response could not be parsed. Please try again."}), 500
    except Exception as e:
        app.logger.error(f"Recommend error: {e}")
        return jsonify({"message": str(e)}), 500

# Also keep the KisanAI-compatible direct routes
@app.route("/recommend/crops", methods=["POST"])
def recommend_crops_compat():
    data = request.get_json() or {}
    data["category"] = "crops"
    with app.test_request_context(
        "/api/recommend", method="POST",
        json=data, content_type="application/json"
    ):
        return recommend()

@app.route("/recommend/livestock", methods=["POST"])
def recommend_livestock_compat():
    data = request.get_json() or {}
    data["category"] = "livestock"
    with app.test_request_context(
        "/api/recommend", method="POST",
        json=data, content_type="application/json"
    ):
        return recommend()

@app.route("/recommend/aquaculture", methods=["POST"])
def recommend_aquaculture_compat():
    data = request.get_json() or {}
    data["category"] = "aquaculture"
    with app.test_request_context(
        "/api/recommend", method="POST",
        json=data, content_type="application/json"
    ):
        return recommend()


# ─────────────────────────────────────────────
# MARKETPLACE
# ─────────────────────────────────────────────
_LISTINGS = [
    {"id":1,"productName":"Basmati Rice","name":"Basmati Rice","category":"Grains","description":"Premium grade long-grain basmati","quantity":"2000","price":"48","location":"Karnal, Haryana","sellerName":"Rajesh Sharma","seller":"Rajesh Sharma","createdAt":"2026-03-27T00:00:00Z","date":"27 Mar"},
    {"id":2,"productName":"Tomatoes","name":"Tomatoes","category":"Vegetables","description":"Fresh farm tomatoes, just harvested","quantity":"500","price":"18","location":"Nashik, Maharashtra","sellerName":"Priya Patil","seller":"Priya Patil","createdAt":"2026-03-27T00:00:00Z","date":"27 Mar"},
    {"id":3,"productName":"Wheat","name":"Wheat","category":"Grains","description":"Grade A wheat from MP plains","quantity":"5000","price":"22","location":"Bhopal, MP","sellerName":"Anil Kumar","seller":"Anil Kumar","createdAt":"2026-03-27T00:00:00Z","date":"27 Mar"},
    {"id":4,"productName":"Alphonso Mangoes","name":"Alphonso Mangoes","category":"Fruits","description":"GI tagged Alphonso, export quality","quantity":"300","price":"120","location":"Ratnagiri, Maharashtra","sellerName":"Suresh Desai","seller":"Suresh Desai","createdAt":"2026-03-27T00:00:00Z","date":"27 Mar"},
    {"id":5,"productName":"Masoor Dal","name":"Masoor Dal","category":"Pulses","description":"Organically grown red lentils","quantity":"800","price":"85","location":"Indore, MP","sellerName":"Meena Verma","seller":"Meena Verma","createdAt":"2026-03-27T00:00:00Z","date":"27 Mar"},
    {"id":6,"productName":"Turmeric","name":"Turmeric","category":"Spices","description":"High curcumin content, dried & cleaned","quantity":"200","price":"120","location":"Erode, Tamil Nadu","sellerName":"Rajan Iyer","seller":"Rajan Iyer","createdAt":"2026-03-27T00:00:00Z","date":"27 Mar"},
]
_NEXT_ID = 7

@app.route("/api/marketplace/listings", methods=["GET"])
def get_listings():
    cat = request.args.get("category", "").strip()
    data = [l for l in _LISTINGS if cat.lower() in ("", "all") or l["category"].lower() == cat.lower()]
    return jsonify({"success": True, "data": data, "total": len(data)})

@app.route("/api/marketplace/listings", methods=["POST"])
def create_listing():
    global _NEXT_ID
    d = request.get_json() or {}
    for f in ["productName", "category", "price", "quantity"]:
        if f not in d and f.replace("productName","name") not in d:
            pass
    name = d.get("productName") or d.get("name", "")
    if not name:
        return jsonify({"message": "productName is required"}), 400
    import datetime
    listing = {
        "id": _NEXT_ID, "productName": name, "name": name,
        "category": d.get("category","Others"),
        "description": d.get("description",""),
        "quantity": str(d.get("quantity","")),
        "price": str(d.get("price","")),
        "location": d.get("location",""),
        "sellerName": d.get("sellerName", d.get("seller","Anonymous")),
        "seller": d.get("sellerName", d.get("seller","Anonymous")),
        "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
        "date": datetime.datetime.utcnow().strftime("%d %b"),
    }
    _LISTINGS.append(listing)
    _NEXT_ID += 1
    return jsonify({"success": True, "data": listing}), 201

@app.route("/api/marketplace/listings/<int:lid>", methods=["DELETE"])
def delete_listing(lid):
    global _LISTINGS
    before = len(_LISTINGS)
    _LISTINGS = [l for l in _LISTINGS if l["id"] != lid]
    if len(_LISTINGS) == before:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"success": True})


# ─────────────────────────────────────────────
# GOVERNMENT SCHEMES
# ─────────────────────────────────────────────
_SCHEMES = [
    {"id":1,"name":"PM-KISAN","level":"Central","category":"Direct Benefit","benefit":"₹6,000/year in 3 installments","description":"Direct income support to farmers."},
    {"id":2,"name":"PM Fasal Bima Yojana (PMFBY)","level":"Central","category":"Crop Insurance","benefit":"Crop loss coverage at low premium","description":"Affordable crop insurance for natural calamities."},
    {"id":3,"name":"Kisan Credit Card (KCC)","level":"Central","category":"Credit / Loan","benefit":"Credit up to ₹3 lakh at 4% interest","description":"Short-term credit for farm operations."},
    {"id":4,"name":"Soil Health Card Scheme","level":"Central","category":"Advisory","benefit":"Free soil testing & nutrient recommendations","description":"Helps farmers improve soil fertility."},
    {"id":5,"name":"National Mission for Sustainable Agriculture","level":"Central","category":"Sustainability","benefit":"Subsidies on sustainable farm practices","description":"Promotes climate-resilient farming."},
    {"id":6,"name":"National Livestock Mission","level":"Central","category":"Livestock","benefit":"Subsidies for breed improvement & feed","description":"Supports livestock development programs."},
    {"id":7,"name":"MP Mukhyamantri Krishak Udyami Yojana","level":"State (MP)","category":"Agri-Business","benefit":"Loan up to ₹2 crore with 15% subsidy","description":"Supports agri-business ventures in MP."},
]

@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    cat = request.args.get("category","").strip()
    q = request.args.get("q","").strip().lower()
    data = _SCHEMES
    if cat and cat.lower() != "all":
        data = [s for s in data if s["category"].lower() == cat.lower()]
    if q:
        data = [s for s in data if q in s["name"].lower() or q in s["description"].lower()]
    return jsonify({"success": True, "data": data, "total": len(data)})


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
