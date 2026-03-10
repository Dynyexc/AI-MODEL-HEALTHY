"""
========================================
AI API - FastAPI Server
========================================
Chạy   : uvicorn main:app --reload --port 8000
Swagger: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing  import List
import joblib
import numpy  as np
import os

# ── Khởi tạo app ─────────────────────────────────────────────
app = FastAPI(
    title       = "Health AI API",
    description = "Dự đoán bệnh từ triệu chứng - Hệ thống Tư vấn Sức khỏe AI",
    version     = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

# ── Load model khi server khởi động ─────────────────────────
BASE = os.path.join(os.path.dirname(__file__), '..', 'models')

try:
    model        = joblib.load(os.path.join(BASE, 'best_model.pkl'))
    le           = joblib.load(os.path.join(BASE, 'label_encoder.pkl'))
    all_symptoms = joblib.load(os.path.join(BASE, 'symptoms_list.pkl'))

    with open(os.path.join(BASE, 'best_model_name.txt')) as f:
        model_name = f.read().strip()

    print(f"✅ Model '{model_name}' loaded")
    print(f"   → {len(le.classes_)} bệnh | {len(all_symptoms)} triệu chứng")

except FileNotFoundError as e:
    print(f"❌ Chưa có model! Hãy chạy các bước training trước.")
    print(f"   {e}")
    model = le = all_symptoms = model_name = None

# ── Chuyên khoa theo bệnh ────────────────────────────────────
SPECIALTY = {
    "Fungal infection":         "Da liễu",
    "Allergy":                  "Dị ứng - Miễn dịch",
    "GERD":                     "Tiêu hóa",
    "Chronic cholestasis":      "Tiêu hóa",
    "Drug Reaction":            "Nội khoa",
    "Peptic ulcer diseae":      "Tiêu hóa",
    "AIDS":                     "Truyền nhiễm",
    "Diabetes":                 "Nội tiết",
    "Gastroenteritis":          "Tiêu hóa",
    "Bronchial Asthma":         "Hô hấp",
    "Hypertension":             "Tim mạch",
    "Migraine":                 "Thần kinh",
    "Cervical spondylosis":     "Cơ xương khớp",
    "Paralysis (brain hemorrhage)": "Thần kinh",
    "Jaundice":                 "Tiêu hóa",
    "Malaria":                  "Truyền nhiễm",
    "Chicken pox":              "Truyền nhiễm",
    "Dengue":                   "Truyền nhiễm",
    "Typhoid":                  "Truyền nhiễm",
    "hepatitis A":              "Tiêu hóa - Gan",
    "Hepatitis B":              "Tiêu hóa - Gan",
    "Hepatitis C":              "Tiêu hóa - Gan",
    "Hepatitis D":              "Tiêu hóa - Gan",
    "Hepatitis E":              "Tiêu hóa - Gan",
    "Alcoholic hepatitis":      "Tiêu hóa - Gan",
    "Tuberculosis":             "Hô hấp",
    "Common Cold":              "Nội khoa tổng quát",
    "Pneumonia":                "Hô hấp",
    "Dimorphic hemmorhoids(piles)": "Tiêu hóa",
    "Heart attack":             "Tim mạch",
    "Varicose veins":           "Tim mạch",
    "Hypothyroidism":           "Nội tiết",
    "Hyperthyroidism":          "Nội tiết",
    "Hypoglycemia":             "Nội tiết",
    "Osteoarthristis":          "Cơ xương khớp",
    "Arthritis":                "Cơ xương khớp",
    "(vertigo) Paroymsal  Positional Vertigo": "Thần kinh - Tai mũi họng",
    "Acne":                     "Da liễu",
    "Urinary tract infection":  "Thận - Tiết niệu",
    "Psoriasis":                "Da liễu",
    "Impetigo":                 "Da liễu",
}

# ── Schemas ──────────────────────────────────────────────────
class SymptomRequest(BaseModel):
    symptoms: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]
            }
        }

class DiseaseItem(BaseModel):
    disease:    str
    confidence: float

class PredictionResponse(BaseModel):
    disease:        str
    confidence:     float
    specialty:      str
    recommendation: str
    top3:           List[DiseaseItem]
    matched_symptoms: int
    model_used:     str

# ── Endpoints ────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message":  "🏥 Health AI API đang chạy!",
        "docs":     "http://localhost:8000/docs",
        "status":   "ready" if model else "model not loaded",
    }

@app.get("/health")
def health_check():
    return {
        "status":          "OK" if model else "ERROR",
        "model_loaded":    model is not None,
        "model_name":      model_name,
        "total_diseases":  len(le.classes_)   if le            else 0,
        "total_symptoms":  len(all_symptoms)  if all_symptoms  else 0,
    }

@app.get("/symptoms")
def get_symptoms(search: str = ""):
    """Lấy danh sách tất cả triệu chứng — dùng cho dropdown UI"""
    if not all_symptoms:
        raise HTTPException(status_code=500, detail="Model chưa được load")

    syms = sorted(all_symptoms)
    if search:
        syms = [s for s in syms if search.lower() in s.lower()]

    return {
        "total":    len(syms),
        "symptoms": syms,
    }

@app.get("/diseases")
def get_diseases():
    """Lấy danh sách tất cả bệnh"""
    if not le:
        raise HTTPException(status_code=500, detail="Model chưa được load")
    return {
        "total":    len(le.classes_),
        "diseases": [
            {"name": d, "specialty": SPECIALTY.get(d, "Nội khoa tổng quát")}
            for d in le.classes_
        ]
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_disease(request: SymptomRequest):
    """Dự đoán bệnh từ danh sách triệu chứng"""

    # Kiểm tra model
    if model is None:
        raise HTTPException(
            status_code = 503,
            detail      = "Model chưa được load. Hãy chạy training trước."
        )

    # Kiểm tra input
    if not request.symptoms:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp ít nhất 1 triệu chứng")

    # Vector hóa input
    input_vector = np.zeros(len(all_symptoms))
    matched = 0

    for s in request.symptoms:
        s_clean = s.strip().lower().replace(' ', '_')
        if s_clean in all_symptoms:
            input_vector[all_symptoms.index(s_clean)] = 1
            matched += 1
        # Thử tìm gần đúng nếu không khớp chính xác
        else:
            for sym in all_symptoms:
                if s_clean in sym or sym in s_clean:
                    input_vector[all_symptoms.index(sym)] = 1
                    matched += 1
                    break

    if matched == 0:
        raise HTTPException(
            status_code = 400,
            detail      = (
                f"Không nhận dạng được triệu chứng nào từ: {request.symptoms}. "
                f"Dùng GET /symptoms để xem danh sách hợp lệ."
            )
        )

    # Dự đoán
    proba    = model.predict_proba([input_vector])[0]
    top3_idx = proba.argsort()[-3:][::-1]

    top3 = [
        DiseaseItem(
            disease    = le.inverse_transform([i])[0],
            confidence = round(float(proba[i]) * 100, 2)
        )
        for i in top3_idx
    ]

    disease    = top3[0].disease
    confidence = top3[0].confidence
    specialty  = SPECIALTY.get(disease, "Nội khoa tổng quát")

    recommendation = (
        f"Dựa trên {matched} triệu chứng bạn mô tả, hệ thống AI dự đoán "
        f"bạn có khả năng mắc bệnh '{disease}' với độ tin cậy {confidence:.1f}%. "
        f"Khuyến nghị đến khám tại chuyên khoa {specialty}. "
        f"⚠️ Lưu ý: Đây chỉ là kết quả tham khảo, không thay thế chẩn đoán của bác sĩ."
    )

    return PredictionResponse(
        disease          = disease,
        confidence       = confidence,
        specialty        = specialty,
        recommendation   = recommendation,
        top3             = top3,
        matched_symptoms = matched,
        model_used       = model_name or "Unknown",
    )
