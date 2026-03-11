"""
========================================
AI API - FastAPI Server (Hỗ trợ Tiếng Việt)
========================================
Chạy   : uvicorn main:app --reload --port 8000
Swagger: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing   import List, Optional
from functools import lru_cache
import joblib
import numpy   as np
import os, sys, time
from datetime import datetime
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vietnamese_dict import (
    SYMPTOM_VI, DISEASE_VI,
    to_vietnamese_symptom,
    to_vietnamese_disease,
    to_english_symptom,
)

app = FastAPI(
    title       = "Health AI API v2",
    description = "Tư vấn sức khỏe AI - Phiên bản 2.0",
    version     = "2.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# ── Load model 1 lần duy nhất vào RAM ────────────────────────
BASE = os.path.join(os.path.dirname(__file__), '..', 'models')

try:
    model        = joblib.load(os.path.join(BASE, 'best_model.pkl'))
    le           = joblib.load(os.path.join(BASE, 'label_encoder.pkl'))
    all_symptoms = joblib.load(os.path.join(BASE, 'symptoms_list.pkl'))
    sym_index    = {s: i for i, s in enumerate(all_symptoms)}  # index nhanh

    with open(os.path.join(BASE, 'best_model_name.txt')) as f:
        model_name = f.read().strip()

    print(f"✅ Model '{model_name}' loaded")
    print(f"   {len(le.classes_)} bệnh | {len(all_symptoms)} triệu chứng")

except FileNotFoundError:
    print("❌ Chưa có model!")
    model = le = all_symptoms = sym_index = model_name = None

# ── Lưu lịch sử trong RAM ────────────────────────────────────
prediction_history = []

SPECIALTY = {
    "Fungal infection":"Da liễu","Allergy":"Dị ứng - Miễn dịch",
    "GERD":"Tiêu hóa","Chronic cholestasis":"Tiêu hóa",
    "Drug Reaction":"Nội khoa","Peptic ulcer diseae":"Tiêu hóa",
    "AIDS":"Truyền nhiễm","Diabetes":"Nội tiết",
    "Gastroenteritis":"Tiêu hóa","Bronchial Asthma":"Hô hấp",
    "Hypertension":"Tim mạch","Migraine":"Thần kinh",
    "Cervical spondylosis":"Cơ xương khớp",
    "Paralysis (brain hemorrhage)":"Thần kinh",
    "Jaundice":"Tiêu hóa","Malaria":"Truyền nhiễm",
    "Chicken pox":"Truyền nhiễm","Dengue":"Truyền nhiễm",
    "Typhoid":"Truyền nhiễm","hepatitis A":"Tiêu hóa - Gan",
    "Hepatitis B":"Tiêu hóa - Gan","Hepatitis C":"Tiêu hóa - Gan",
    "Hepatitis D":"Tiêu hóa - Gan","Hepatitis E":"Tiêu hóa - Gan",
    "Alcoholic hepatitis":"Tiêu hóa - Gan","Tuberculosis":"Hô hấp",
    "Common Cold":"Nội khoa tổng quát","Pneumonia":"Hô hấp",
    "Dimorphic hemmorhoids(piles)":"Tiêu hóa","Heart attack":"Tim mạch",
    "Varicose veins":"Tim mạch","Hypothyroidism":"Nội tiết",
    "Hyperthyroidism":"Nội tiết","Hypoglycemia":"Nội tiết",
    "Osteoarthristis":"Cơ xương khớp","Arthritis":"Cơ xương khớp",
    "(vertigo) Paroymsal  Positional Vertigo":"Thần kinh - Tai mũi họng",
    "Acne":"Da liễu","Urinary tract infection":"Thận - Tiết niệu",
    "Psoriasis":"Da liễu","Impetigo":"Da liễu",
    "Hand Foot Mouth Disease":"Truyền nhiễm",
    "Influenza":"Hô hấp","Heat Stroke":"Cấp cứu",
    "Food Poisoning":"Tiêu hóa","Tonsillitis":"Tai mũi họng",
    "Conjunctivitis":"Mắt","Measles":"Truyền nhiễm",
    "Mumps":"Truyền nhiễm","Whooping Cough":"Hô hấp",
    "Scabies":"Da liễu","Urticaria":"Da liễu",
    "Sinusitis":"Tai mũi họng","Bronchitis":"Hô hấp",
    "Appendicitis":"Ngoại khoa","Gallstones":"Tiêu hóa",
    "Epilepsy":"Thần kinh","Meningitis":"Thần kinh",
    "Gout":"Cơ xương khớp","Osteoporosis":"Cơ xương khớp",
    "Angina":"Tim mạch","Kidney Stones":"Thận - Tiết niệu",
    "Kidney Disease":"Thận - Tiết niệu",
}

# ── Mức độ nghiêm trọng ──────────────────────────────────────
SEVERITY = {
    "Heart attack":"🔴 Khẩn cấp","Meningitis":"🔴 Khẩn cấp",
    "Heat Stroke":"🔴 Khẩn cấp","Appendicitis":"🔴 Khẩn cấp",
    "Paralysis (brain hemorrhage)":"🔴 Khẩn cấp",
    "Pneumonia":"🟠 Nghiêm trọng","Tuberculosis":"🟠 Nghiêm trọng",
    "AIDS":"🟠 Nghiêm trọng","Dengue":"🟠 Nghiêm trọng",
    "Malaria":"🟠 Nghiêm trọng","Typhoid":"🟠 Nghiêm trọng",
    "Diabetes":"🟡 Cần theo dõi","Hypertension":"🟡 Cần theo dõi",
    "Hepatitis B":"🟡 Cần theo dõi","Hepatitis C":"🟡 Cần theo dõi",
    "Common Cold":"🟢 Nhẹ","Acne":"🟢 Nhẹ",
    "Allergy":"🟢 Nhẹ","Fungal infection":"🟢 Nhẹ",
}

# ── Hàm vector hóa tối ưu ────────────────────────────────────
def vectorize(symptoms_input):
    """Chuyển danh sách triệu chứng → vector nhanh dùng index"""
    vector  = np.zeros(len(all_symptoms))
    matched = []

    for s in symptoms_input:
        s_en    = to_english_symptom(s.strip())
        s_clean = s_en.strip().lower().replace(' ', '_')

        if s_clean in sym_index:
            vector[sym_index[s_clean]] = 1
            matched.append(s_clean)
        else:
            for sym in all_symptoms:
                if s_clean in sym or sym in s_clean:
                    vector[sym_index[sym]] = 1
                    matched.append(sym)
                    break

    return vector, matched

# ── Schemas ──────────────────────────────────────────────────
class SymptomRequest(BaseModel):
    symptoms: List[str]
    class Config:
        json_schema_extra = {"example": {"symptoms": ["Sốt", "Đau đầu", "Mệt mỏi"]}}

class DiseaseItem(BaseModel):
    disease_en: str
    disease_vi: str
    confidence: float
    severity:   str

class PredictionResponse(BaseModel):
    disease_en:       str
    disease_vi:       str
    confidence:       float
    severity:         str
    specialty:        str
    recommendation:   str
    top3:             List[DiseaseItem]
    matched_symptoms: int
    unmatched:        List[str]
    response_time_ms: float
    model_used:       str

class CompareRequest(BaseModel):
    symptoms_a: List[str]
    symptoms_b: List[str]

# ── Endpoints ────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "🏥 Health AI API v2", "docs": "http://localhost:8000/docs"}

@app.get("/health")
def health():
    return {
        "status":         "OK" if model else "ERROR",
        "model_name":     model_name,
        "total_diseases": len(le.classes_) if le else 0,
        "total_symptoms": len(all_symptoms) if all_symptoms else 0,
        "total_requests": len(prediction_history),
    }

@app.get("/symptoms")
def get_symptoms(search: str = ""):
    if not all_symptoms:
        raise HTTPException(status_code=500, detail="Model chưa load")
    result = []
    for s in sorted(all_symptoms):
        vi = to_vietnamese_symptom(s)
        if search and search.lower() not in vi.lower() and search.lower() not in s.lower():
            continue
        result.append({"en": s, "vi": vi})
    return {"total": len(result), "symptoms": result}

@app.get("/diseases")
def get_diseases():
    if not le:
        raise HTTPException(status_code=500, detail="Model chưa load")
    return {
        "total": len(le.classes_),
        "diseases": [
            {
                "name_en":  d,
                "name_vi":  to_vietnamese_disease(d),
                "specialty":SPECIALTY.get(d, "Nội khoa tổng quát"),
                "severity": SEVERITY.get(d, "🟡 Cần theo dõi"),
            }
            for d in sorted(le.classes_)
        ]
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(request: SymptomRequest):
    """Dự đoán bệnh từ triệu chứng (VI hoặc EN)"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model chưa load")
    if not request.symptoms:
        raise HTTPException(status_code=400, detail="Vui lòng nhập triệu chứng")

    t_start  = time.time()

    # Vector hóa
    vector, matched = vectorize(request.symptoms)
    unmatched = [s for s in request.symptoms
                 if to_english_symptom(s).lower().replace(' ','_') not in matched]

    if not matched:
        raise HTTPException(status_code=400, detail="Không nhận dạng được triệu chứng")

    # Dự đoán
    import pandas as pd
    input_df = pd.DataFrame([vector], columns=all_symptoms)
    proba    = model.predict_proba(input_df)[0]
    top3_idx = proba.argsort()[-3:][::-1]

    top3 = [
        DiseaseItem(
            disease_en = le.inverse_transform([i])[0],
            disease_vi = to_vietnamese_disease(le.inverse_transform([i])[0]),
            confidence = round(float(proba[i]) * 100, 2),
            severity   = SEVERITY.get(le.inverse_transform([i])[0], "🟡 Cần theo dõi"),
        )
        for i in top3_idx
    ]

    disease_en = top3[0].disease_en
    disease_vi = top3[0].disease_vi
    confidence = top3[0].confidence
    severity   = top3[0].severity
    specialty  = SPECIALTY.get(disease_en, "Nội khoa tổng quát")
    syms_vi    = [to_vietnamese_symptom(s) for s in matched[:3]]

    recommendation = (
        f"Dựa trên {len(matched)} triệu chứng ({', '.join(syms_vi)}), "
        f"AI dự đoán '{disease_vi}' với độ tin cậy {confidence:.1f}%. "
        f"Mức độ: {severity}. "
        f"Nên đến khám chuyên khoa {specialty}. "
        f"⚠️ Chỉ mang tính tham khảo, không thay thế bác sĩ."
    )

    elapsed = round((time.time() - t_start) * 1000, 2)

    # Lưu lịch sử
    prediction_history.append({
        "time":      datetime.now().isoformat(),
        "symptoms":  request.symptoms,
        "disease":   disease_vi,
        "confidence":confidence,
    })

    return PredictionResponse(
        disease_en=disease_en, disease_vi=disease_vi,
        confidence=confidence, severity=severity,
        specialty=specialty, recommendation=recommendation,
        top3=top3, matched_symptoms=len(matched),
        unmatched=unmatched,
        response_time_ms=elapsed,
        model_used=model_name or "Unknown",
    )

@app.post("/compare")
def compare_symptoms(request: CompareRequest):
    """So sánh 2 bộ triệu chứng → xem khác nhau chỗ nào"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model chưa load")

    import pandas as pd

    def get_prediction(symptoms):
        vec, matched = vectorize(symptoms)
        if not matched:
            return None
        df   = pd.DataFrame([vec], columns=all_symptoms)
        prob = model.predict_proba(df)[0]
        idx  = prob.argmax()
        return {
            "disease_vi": to_vietnamese_disease(le.inverse_transform([idx])[0]),
            "confidence": round(float(prob[idx]) * 100, 2),
            "matched":    [to_vietnamese_symptom(s) for s in matched],
        }

    result_a = get_prediction(request.symptoms_a)
    result_b = get_prediction(request.symptoms_b)

    return {
        "case_a": result_a,
        "case_b": result_b,
        "same_disease": result_a and result_b and
                        result_a["disease_vi"] == result_b["disease_vi"],
    }

@app.get("/history")
def get_history(limit: int = 10):
    """Xem lịch sử dự đoán gần nhất"""
    return {
        "total":   len(prediction_history),
        "history": prediction_history[-limit:][::-1],
    }

@app.get("/stats")
def get_stats():
    """Thống kê các bệnh được dự đoán nhiều nhất"""
    if not prediction_history:
        return {"message": "Chưa có dữ liệu"}

    counts = defaultdict(int)
    for h in prediction_history:
        counts[h["disease"]] += 1

    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "total_requests": len(prediction_history),
        "top_diseases":   [{"disease": d, "count": c} for d, c in top],
    }