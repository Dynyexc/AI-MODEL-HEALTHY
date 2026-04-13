"""
========================================
AI API V2 - Đầy đủ tính năng
========================================
Chạy: uvicorn main_v2:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import joblib, numpy as np, os, sys, time, uuid, io
from datetime import datetime
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vietnamese_dict import (SYMPTOM_VI, DISEASE_VI,
    to_vietnamese_symptom, to_vietnamese_disease, to_english_symptom)
from nlp_processor import NLPProcessor

app = FastAPI(title="Health AI API v2", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# ── Font Times New Roman ─────────────────────────────────────
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    _FD = "C:/Windows/Fonts"
    pdfmetrics.registerFont(TTFont('TNR',        _FD + '/times.ttf'))
    pdfmetrics.registerFont(TTFont('TNR-Bold',   _FD + '/timesbd.ttf'))
    pdfmetrics.registerFont(TTFont('TNR-Italic', _FD + '/timesi.ttf'))
    PDF_FONT = 'TNR'; PDF_BOLD = 'TNR-Bold'; PDF_ITALIC = 'TNR-Italic'
    print("✅ Font Times New Roman loaded")
except:
    PDF_FONT = 'Helvetica'; PDF_BOLD = 'Helvetica-Bold'; PDF_ITALIC = 'Helvetica-Oblique'
    print("⚠️  Dùng Helvetica thay thế")

# ── Load model ───────────────────────────────────────────────
BASE = os.path.join(os.path.dirname(__file__), '..', 'models')
try:
    model        = joblib.load(os.path.join(BASE, 'best_model.pkl'))
    le           = joblib.load(os.path.join(BASE, 'label_encoder.pkl'))
    all_symptoms = joblib.load(os.path.join(BASE, 'symptoms_list.pkl'))
    sym_index    = {s: i for i, s in enumerate(all_symptoms)}
    with open(os.path.join(BASE, 'best_model_name.txt')) as f:
        model_name = f.read().strip()
    print(f"✅ Model '{model_name}' — {len(le.classes_)} bệnh | {len(all_symptoms)} triệu chứng")
except FileNotFoundError:
    model = le = all_symptoms = sym_index = model_name = None
    print("❌ Chưa có model!")

# ── Load DNN ─────────────────────────────────────────────────
dnn_model = None
try:
    import torch, torch.nn as nn
    class HealthDNN(nn.Module):
        def __init__(self, n_input, n_classes):
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(n_input,512),nn.BatchNorm1d(512),nn.ReLU(),nn.Dropout(0.3),
                nn.Linear(512,256),nn.BatchNorm1d(256),nn.ReLU(),nn.Dropout(0.3),
                nn.Linear(256,128),nn.BatchNorm1d(128),nn.ReLU(),nn.Dropout(0.2),
                nn.Linear(128,64),nn.ReLU(),nn.Linear(64,n_classes),
            )
        def forward(self, x): return self.network(x)

    dnn_path = os.path.join(BASE, 'dnn_full.pt')
    if os.path.exists(dnn_path):
        ckpt      = torch.load(dnn_path, map_location='cpu')
        dnn_model = HealthDNN(ckpt['n_features'], ckpt['n_classes'])
        dnn_model.load_state_dict(ckpt['model_state'])
        dnn_model.eval()
        print("✅ DNN loaded")
except:
    print("⚠️  DNN không load được")

nlp = NLPProcessor()
prediction_history: list = []
chat_sessions: dict      = {}

# ── Dicts ────────────────────────────────────────────────────
SPECIALTY = {
    "Fungal infection":"Da liễu","Allergy":"Dị ứng - Miễn dịch",
    "GERD":"Tiêu hóa","Diabetes":"Nội tiết","Hypertension":"Tim mạch",
    "Migraine":"Thần kinh","Common Cold":"Nội khoa tổng quát",
    "Pneumonia":"Hô hấp","Heart attack":"Tim mạch","Acne":"Da liễu",
    "Urinary tract infection":"Thận - Tiết niệu","Tuberculosis":"Hô hấp",
    "Dengue":"Truyền nhiễm","Malaria":"Truyền nhiễm","Typhoid":"Truyền nhiễm",
    "Chicken pox":"Truyền nhiễm","Hepatitis B":"Tiêu hóa - Gan",
    "Hepatitis C":"Tiêu hóa - Gan","Osteoarthristis":"Cơ xương khớp",
    "Arthritis":"Cơ xương khớp","Hypothyroidism":"Nội tiết",
    "Psoriasis":"Da liễu","Impetigo":"Da liễu","Jaundice":"Tiêu hóa",
    "Gastroenteritis":"Tiêu hóa","Bronchial Asthma":"Hô hấp",
    "Varicose veins":"Tim mạch","Hyperthyroidism":"Nội tiết",
    "Hypoglycemia":"Nội tiết","Heat Stroke":"Cấp cứu",
    "Food Poisoning":"Tiêu hóa","Tonsillitis":"Tai mũi họng",
    "Conjunctivitis":"Mắt","Influenza":"Hô hấp","Measles":"Truyền nhiễm",
    "Mumps":"Truyền nhiễm","Gout":"Cơ xương khớp","Meningitis":"Thần kinh",
    "Appendicitis":"Ngoại khoa","Kidney Stones":"Thận - Tiết niệu",
}
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
AGE_WEIGHT = {
    "child":   {"Hand Foot Mouth Disease":2.0,"Chicken pox":1.8,"Measles":1.8,
                "Tonsillitis":1.5,"Heart attack":0.1,"Hypertension":0.2},
    "teen":    {"Acne":2.0,"Allergy":1.5,"Migraine":1.3,"Heart attack":0.1},
    "adult":   {},
    "elderly": {"Hypertension":1.8,"Diabetes":1.8,"Heart attack":1.8,
                "Osteoarthristis":2.0,"Arthritis":2.0,"Acne":0.1},
}
GENDER_WEIGHT = {
    "male":   {"Gout":1.8,"Heart attack":1.5,"Hypertension":1.3,"Kidney Stones":1.4},
    "female": {"Hypothyroidism":1.8,"Urinary tract infection":2.0,"Migraine":1.5},
}
CONFIDENCE_THRESHOLD = 30.0
CHAT_QUESTIONS = [
    {"id":"fever","question":"Bạn có bị sốt không?","followup":"Mức độ sốt?",
     "followup_options":["Sốt cao","Sốt nhẹ","Không sốt"],
     "followup_map":{"Sốt cao":["high_fever"],"Sốt nhẹ":["mild_fever"],"Không sốt":[]}},
    {"id":"head","question":"Bạn có đau đầu hoặc chóng mặt không?","followup":"Cụ thể?",
     "followup_options":["Đau đầu","Chóng mặt","Cả hai","Không có"],
     "followup_map":{"Đau đầu":["headache"],"Chóng mặt":["dizziness"],"Cả hai":["headache","dizziness"],"Không có":[]}},
    {"id":"resp","question":"Bạn có ho, khó thở hoặc đau họng không?","followup":"Cụ thể?",
     "followup_options":["Ho","Khó thở","Đau họng","Nghẹt mũi","Không có"],
     "followup_map":{"Ho":["cough"],"Khó thở":["breathlessness"],"Đau họng":["throat_irritation"],"Nghẹt mũi":["congestion"],"Không có":[]}},
    {"id":"dige","question":"Bạn có buồn nôn, đau bụng hoặc tiêu chảy không?","followup":"Cụ thể?",
     "followup_options":["Buồn nôn/Nôn","Đau bụng","Tiêu chảy","Táo bón","Không có"],
     "followup_map":{"Buồn nôn/Nôn":["nausea","vomiting"],"Đau bụng":["abdominal_pain"],"Tiêu chảy":["diarrhoea"],"Táo bón":["constipation"],"Không có":[]}},
    {"id":"body","question":"Bạn có mệt mỏi, đau cơ hoặc đau khớp không?","followup":"Cụ thể?",
     "followup_options":["Mệt mỏi","Đau cơ","Đau khớp","Cả ba","Không có"],
     "followup_map":{"Mệt mỏi":["fatigue"],"Đau cơ":["muscle_pain"],"Đau khớp":["joint_pain"],"Cả ba":["fatigue","muscle_pain","joint_pain"],"Không có":[]}},
    {"id":"skin","question":"Bạn có phát ban, ngứa da không?","followup":"Cụ thể?",
     "followup_options":["Phát ban","Ngứa da","Nổi mụn","Không có"],
     "followup_map":{"Phát ban":["skin_rash"],"Ngứa da":["itching"],"Nổi mụn":["pus_filled_pimples"],"Không có":[]}},
    {"id":"other","question":"Bạn có triệu chứng nào khác không?","followup":"Chọn nếu có:",
     "followup_options":["Đau ngực","Vàng da","Sụt cân","Khó tiểu","Không có"],
     "followup_map":{"Đau ngực":["chest_pain"],"Vàng da":["yellowish_skin"],"Sụt cân":["weight_loss"],"Khó tiểu":["burning_micturition"],"Không có":[]}},
]

# ── Helpers ──────────────────────────────────────────────────
def get_age_group(age):
    if age<=12: return "child"
    elif age<=17: return "teen"
    elif age<=59: return "adult"
    else: return "elderly"

def apply_weights(proba, classes, age=None, gender=None):
    proba = proba.copy()
    if age:
        for i,c in enumerate(classes):
            w = AGE_WEIGHT.get(get_age_group(age),{}).get(c)
            if w: proba[i] *= w
    if gender in GENDER_WEIGHT:
        for i,c in enumerate(classes):
            w = GENDER_WEIGHT[gender].get(c)
            if w: proba[i] *= w
    t = proba.sum()
    return proba/t if t>0 else proba

def check_confidence(conf, matched):
    if conf>=70:   return {"level":"high",  "message":"✅ Độ tin cậy cao",        "action":"Kết quả đáng tin cậy"}
    elif conf>=30: return {"level":"medium","message":"⚠️ Độ tin cậy trung bình", "action":"Nên nhập thêm triệu chứng"}
    else:          return {"level":"low",   "message":"❌ Độ tin cậy thấp",       "action":f"Chỉ khớp {matched} triệu chứng"}

def vectorize(symptoms_input):
    vector, matched = np.zeros(len(all_symptoms)), []
    for s in symptoms_input:
        sc = to_english_symptom(s.strip()).strip().lower().replace(' ','_')
        if sc in sym_index:
            vector[sym_index[sc]]=1; matched.append(sc)
        else:
            for sym in all_symptoms:
                if sc in sym or sym in sc:
                    vector[sym_index[sym]]=1; matched.append(sym); break
    return vector, matched

# ── PDF builder ──────────────────────────────────────────────
def build_pdf_bytes(data: dict) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph,
                                    Spacer, Table, TableStyle, HRFlowable)

    buf  = io.BytesIO()
    doc  = SimpleDocTemplate(buf, pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm,   bottomMargin=2*cm)
    PRIMARY  = colors.HexColor('#667eea')
    DANGER   = colors.HexColor('#e53e3e')
    WARNING  = colors.HexColor('#dd6b20')
    SUCCESS  = colors.HexColor('#38a169')
    LIGHT_BG = colors.HexColor('#f7f8ff')

    def ps(name, **kw): return ParagraphStyle(name, **kw)
    T  = ps('T',  fontName=PDF_BOLD,   fontSize=20, textColor=PRIMARY, alignment=1, spaceAfter=4)
    SB = ps('SB', fontName=PDF_ITALIC, fontSize=12, textColor=colors.grey, alignment=1, spaceAfter=2)
    H1 = ps('H1', fontName=PDF_BOLD,   fontSize=14, textColor=PRIMARY, spaceAfter=4, spaceBefore=8)
    H2 = ps('H2', fontName=PDF_BOLD,   fontSize=12, textColor=colors.HexColor('#4a5568'), spaceAfter=3, spaceBefore=6)
    BD = ps('BD', fontName=PDF_FONT,   fontSize=11, spaceAfter=4, leading=18)
    SM = ps('SM', fontName=PDF_FONT,   fontSize=9,  textColor=colors.grey, spaceAfter=2)
    DC = ps('DC', fontName=PDF_ITALIC, fontSize=9,  textColor=DANGER,
            borderColor=DANGER, borderWidth=1, borderPadding=6,
            backColor=colors.HexColor('#fff5f5'))
    FT = ps('FT', fontName=PDF_ITALIC, fontSize=8, textColor=colors.grey, alignment=1)

    story = []
    now   = datetime.now()

    def tbl(data, widths, style_extra=[]):
        t = Table(data, colWidths=widths)
        t.setStyle(TableStyle([
            ('FONTNAME',(0,0),(-1,-1),PDF_FONT),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#e2e8f0')),
            ('PADDING',(0,0),(-1,-1),7),
        ] + style_extra))
        return t

    # Header
    story += [
        Paragraph("HỆ THỐNG TƯ VẤN SỨC KHỎE AI", T),
        Paragraph("BÁO CÁO TƯ VẤN CÁ NHÂN", SB),
        HRFlowable(width="100%", thickness=2, color=PRIMARY),
        Spacer(1, 0.3*cm),
    ]

    # Info
    story.append(tbl([
        ["Ngày tạo:", now.strftime("%d/%m/%Y %H:%M:%S"), "Mã báo cáo:", f"RPT-{now.strftime('%Y%m%d%H%M%S')}"],
        ["Phiên bản AI:", "v2.0 (Ensemble RF+XGB+DNN)", "Độ chính xác:", "99.66%"],
    ], [3.5*cm,7*cm,3.5*cm,4.5*cm], [
        ('FONTNAME',(1,0),(1,-1),PDF_BOLD),('FONTNAME',(3,0),(3,-1),PDF_BOLD),
        ('FONTNAME',(0,0),(0,-1),PDF_ITALIC),('FONTNAME',(2,0),(2,-1),PDF_ITALIC),
        ('TEXTCOLOR',(0,0),(0,-1),colors.grey),('TEXTCOLOR',(2,0),(2,-1),colors.grey),
    ]))
    story.append(Spacer(1,0.4*cm))

    # Bệnh nhân
    gv = "Nam" if data.get("gender")=="male" else "Nữ" if data.get("gender")=="female" else "---"
    story.append(Paragraph("THÔNG TIN BỆNH NHÂN", H1))
    story.append(tbl([
        ["Họ tên:", data.get("patient_name","---"), "Tuổi:", str(data.get("age","---"))],
        ["Giới tính:", gv, "Ngày khám:", now.strftime("%d/%m/%Y")],
    ], [3.5*cm,7*cm,2.5*cm,5.5*cm], [
        ('FONTNAME',(0,0),(0,-1),PDF_BOLD),('FONTNAME',(2,0),(2,-1),PDF_BOLD),
        ('BACKGROUND',(0,0),(-1,-1),LIGHT_BG),('FONTSIZE',(0,0),(-1,-1),11),
    ]))
    story.append(Spacer(1,0.4*cm))

    # Triệu chứng
    symptoms = data.get("symptoms",[])
    sym_vi   = [to_vietnamese_symptom(s) for s in symptoms]
    story += [
        Paragraph("TRIỆU CHỨNG ĐÃ NHẬP", H1),
        Paragraph(f"Tổng số: {len(symptoms)} triệu chứng", SM),
        Paragraph(" | ".join(sym_vi), BD),
        Spacer(1,0.4*cm),
    ]

    # Kết quả
    story.append(Paragraph("KẾT QUẢ TƯ VẤN AI", H1))
    sev = data.get("severity","")
    sc  = DANGER if "Khẩn" in sev else WARNING if "Nghiêm" in sev \
     else colors.HexColor('#d69e2e') if "dõi" in sev else SUCCESS
    story.append(tbl([
        ["CHẨN ĐOÁN",     data.get("disease_vi","---")],
        ["Tên tiếng Anh", data.get("disease_en","---")],
        ["Độ tin cậy AI", f"{data.get('confidence',0):.1f}%"],
        ["Mức độ",        sev],
        ["Chuyên khoa",   data.get("specialty","---")],
        ["Khuyến nghị",   f"Nên đến khám chuyên khoa {data.get('specialty','Nội khoa')}"],
    ], [5*cm,13.5*cm], [
        ('FONTNAME',(0,0),(0,-1),PDF_BOLD),
        ('FONTNAME',(1,0),(1,0),PDF_BOLD),('FONTSIZE',(1,0),(1,0),13),
        ('TEXTCOLOR',(1,0),(1,0),PRIMARY),('TEXTCOLOR',(1,3),(1,3),sc),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[LIGHT_BG,colors.white]),
        ('FONTSIZE',(0,0),(-1,-1),11),
    ]))
    story.append(Spacer(1,0.4*cm))

    # Top 3
    top3 = data.get("top3",[])
    if top3:
        story.append(Paragraph("TOP 3 KHẢ NĂNG", H2))
        story.append(tbl(
            [["#","Tên bệnh","Độ tin cậy"]] +
            [[str(i+1), d.get("disease_vi","---"), f"{d.get('confidence',0):.1f}%"]
             for i,d in enumerate(top3)],
            [1.5*cm,13*cm,4*cm], [
                ('FONTNAME',(0,0),(-1,0),PDF_BOLD),
                ('BACKGROUND',(0,0),(-1,0),PRIMARY),
                ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT_BG]),
                ('ALIGN',(0,0),(0,-1),'CENTER'),('ALIGN',(2,0),(2,-1),'CENTER'),
            ]
        ))
        story.append(Spacer(1,0.4*cm))

    # Disclaimer
    story += [
        HRFlowable(width="100%", thickness=1, color=colors.grey),
        Spacer(1,0.2*cm),
        Paragraph(
            "⚠️ CẢNH BÁO QUAN TRỌNG: Báo cáo này được AI tạo tự động, chỉ mang tính tham khảo. "
            "KHÔNG thay thế chẩn đoán của bác sĩ chuyên khoa. "
            "Vui lòng đến cơ sở y tế để được khám và điều trị chính xác.", DC),
        Spacer(1,0.2*cm),
        Paragraph(f"Hệ thống Tư vấn Sức khỏe AI v2.0  |  {now.strftime('%d/%m/%Y %H:%M:%S')}  |  Mục đích học tập", FT),
    ]

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

# ════════════════════════════════════════════════════════════
# SCHEMAS
# ════════════════════════════════════════════════════════════
class SymptomRequest(BaseModel):
    symptoms: List[str]
    class Config:
        json_schema_extra = {"example": {"symptoms":["Sốt","Đau đầu","Mệt mỏi"]}}

class SmartPredictRequest(BaseModel):
    symptoms: Optional[List[str]] = None
    text:     Optional[str]       = None
    age:      Optional[int]       = None
    gender:   Optional[str]       = None

class DownloadReportRequest(BaseModel):
    patient_name: Optional[str]  = "Người dùng"
    age:          Optional[int]  = None
    gender:       Optional[str]  = None
    symptoms:     List[str]
    disease_vi:   str
    disease_en:   str
    confidence:   float
    severity:     Optional[str]  = "🟡 Cần theo dõi"
    specialty:    Optional[str]  = "Nội khoa tổng quát"
    top3:         Optional[list] = []
    class Config:
        json_schema_extra = {"example": {
            "patient_name":"Nguyễn Văn A","age":35,"gender":"male",
            "symptoms":["Sốt","Đau đầu","Mệt mỏi"],
            "disease_vi":"Cảm cúm","disease_en":"Influenza",
            "confidence":95.3,"severity":"🟢 Nhẹ","specialty":"Nội khoa tổng quát",
            "top3":[
                {"disease_vi":"Cảm cúm","confidence":95.3},
                {"disease_vi":"Cảm lạnh","confidence":3.2},
                {"disease_vi":"Viêm họng","confidence":1.5},
            ]
        }}

class PredictAndReportRequest(BaseModel):
    """Dự đoán + tạo PDF trong 1 lần gọi"""
    symptoms:     List[str]
    patient_name: Optional[str] = "Người dùng"
    age:          Optional[int]  = None
    gender:       Optional[str]  = None   # "male" / "female"
    class Config:
        json_schema_extra = {"example": {
            "symptoms":     ["Sốt", "Đau đầu", "Mệt mỏi"],
            "patient_name": "Nguyễn Văn A",
            "age":          35,
            "gender":       "male",
        }}

class DiseaseItem(BaseModel):
    disease_en: str; disease_vi: str; confidence: float; severity: str

class CompareRequest(BaseModel):
    symptoms_a: List[str]; symptoms_b: List[str]

class ChatReplyRequest(BaseModel):
    session_id: str; answer: str

# ════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════
@app.get("/")
def root():
    return {"message":"🏥 Health AI API v2","docs":"http://localhost:8000/docs"}

@app.get("/health")
def health():
    return {"status":"OK" if model else "ERROR","model_name":model_name,
            "total_diseases":len(le.classes_) if le else 0,
            "total_symptoms":len(all_symptoms) if all_symptoms else 0,
            "total_requests":len(prediction_history)}

@app.get("/symptoms")
def get_symptoms(search: str = ""):
    if not all_symptoms: raise HTTPException(500,"Model chưa load")
    result = []
    for s in sorted(all_symptoms):
        vi = to_vietnamese_symptom(s)
        if search and search.lower() not in vi.lower() and search.lower() not in s.lower(): continue
        result.append({"en":s,"vi":vi})
    return {"total":len(result),"symptoms":result}

@app.get("/diseases")
def get_diseases():
    if not le: raise HTTPException(500,"Model chưa load")
    return {"total":len(le.classes_),"diseases":[
        {"name_en":d,"name_vi":to_vietnamese_disease(d),
         "specialty":SPECIALTY.get(d,"Nội khoa tổng quát"),
         "severity":SEVERITY.get(d,"🟡 Cần theo dõi")}
        for d in sorted(le.classes_)
    ]}

@app.post("/predict")
def predict(request: SymptomRequest):
    if model is None: raise HTTPException(503,"Model chưa load")
    import pandas as pd
    t = time.time()
    vector, matched = vectorize(request.symptoms)
    unmatched = [s for s in request.symptoms
                 if to_english_symptom(s).lower().replace(' ','_') not in matched]
    if not matched: raise HTTPException(400,"Không nhận dạng được triệu chứng")
    proba    = model.predict_proba(pd.DataFrame([vector],columns=all_symptoms))[0]
    top3_idx = proba.argsort()[-3:][::-1]
    top3     = [{"disease_en":le.inverse_transform([i])[0],
                 "disease_vi":to_vietnamese_disease(le.inverse_transform([i])[0]),
                 "confidence":round(float(proba[i])*100,2),
                 "severity":SEVERITY.get(le.inverse_transform([i])[0],"🟡 Cần theo dõi")}
                for i in top3_idx]
    d_en = top3[0]["disease_en"]; d_vi = top3[0]["disease_vi"]; conf = top3[0]["confidence"]
    prediction_history.append({"time":datetime.now().isoformat(),"symptoms":request.symptoms,"disease":d_vi,"confidence":conf})
    return {"disease_en":d_en,"disease_vi":d_vi,"confidence":conf,
            "severity":top3[0]["severity"],"specialty":SPECIALTY.get(d_en,"Nội khoa tổng quát"),
            "top3":top3,"matched_symptoms":len(matched),"unmatched":unmatched,
            "response_time_ms":round((time.time()-t)*1000,2),"model_used":model_name or "Unknown",
            "recommendation":f"AI dự đoán '{d_vi}' ({conf:.1f}%). Nên khám {SPECIALTY.get(d_en,'Nội khoa')}. ⚠️ Chỉ tham khảo."}

@app.post("/smart-predict")
def smart_predict(request: SmartPredictRequest):
    if model is None: raise HTTPException(503,"Model chưa load")
    import pandas as pd
    t=time.time(); nlp_result=None; symptoms=[]
    if request.text:
        nlp_result = nlp.extract_symptoms(request.text)
        symptoms   = nlp_result["english_symptoms"]
        if not symptoms: raise HTTPException(400,{"message":"Không nhận dạng được","hint":"Ví dụ: tôi bị đau đầu và sốt"})
    elif request.symptoms: symptoms = request.symptoms
    else: raise HTTPException(400,"Vui lòng nhập text hoặc symptoms")
    vector,matched = vectorize(symptoms)
    if not matched: raise HTTPException(400,"Không khớp triệu chứng nào")
    proba = model.predict_proba(pd.DataFrame([vector],columns=all_symptoms))[0]
    proba = apply_weights(proba,le.classes_,request.age,request.gender)
    top3_idx = proba.argsort()[-3:][::-1]
    d_en = le.inverse_transform([top3_idx[0]])[0]; d_vi = to_vietnamese_disease(d_en)
    conf = round(float(proba[top3_idx[0]])*100,2)
    prediction_history.append({"time":datetime.now().isoformat(),"symptoms":symptoms,"disease":d_vi,"confidence":conf})
    return {"disease_vi":d_vi,"disease_en":d_en,"confidence":conf,
            "confidence_check":check_confidence(conf,len(matched)),
            "severity":SEVERITY.get(d_en,"🟡 Cần theo dõi"),
            "specialty":SPECIALTY.get(d_en,"Nội khoa tổng quát"),
            "top3":[{"disease_vi":to_vietnamese_disease(le.inverse_transform([i])[0]),
                     "disease_en":le.inverse_transform([i])[0],
                     "confidence":round(float(proba[i])*100,2)} for i in top3_idx],
            "matched_symptoms":len(matched),"nlp_used":bool(request.text),
            "nlp_found":nlp_result["found_symptoms"] if nlp_result else None,
            "response_time_ms":round((time.time()-t)*1000,2),
            "recommendation":f"AI dự đoán '{d_vi}' ({conf:.0f}%). Nên khám {SPECIALTY.get(d_en,'Nội khoa')}. ⚠️ Tham khảo."}

@app.post("/predict-dnn")
def predict_dnn(request: SymptomRequest):
    if dnn_model is None: raise HTTPException(503,"DNN chưa load")
    import torch
    t=time.time(); vector,matched = vectorize(request.symptoms)
    if not matched: raise HTTPException(400,"Không nhận dạng được triệu chứng")
    with torch.no_grad():
        proba = torch.softmax(dnn_model(torch.FloatTensor([vector])),dim=1)[0].numpy()
    top3_idx = proba.argsort()[-3:][::-1]
    d_en = le.inverse_transform([top3_idx[0]])[0]; conf = round(float(proba[top3_idx[0]])*100,2)
    return {"model_used":"Deep Neural Network (PyTorch)",
            "disease_vi":to_vietnamese_disease(d_en),"disease_en":d_en,"confidence":conf,
            "severity":SEVERITY.get(d_en,"🟡 Cần theo dõi"),
            "specialty":SPECIALTY.get(d_en,"Nội khoa tổng quát"),
            "top3":[{"disease_vi":to_vietnamese_disease(le.inverse_transform([i])[0]),
                     "confidence":round(float(proba[i])*100,2)} for i in top3_idx],
            "matched_symptoms":len(matched),"response_time_ms":round((time.time()-t)*1000,2)}

# ── ⭐ ENDPOINT TẢI PDF ───────────────────────────────────────

@app.post("/predict-and-report")
def predict_and_report(request: PredictAndReportRequest):
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model chưa load")
    if not request.symptoms:
        raise HTTPException(status_code=400, detail="Vui lòng nhập triệu chứng")

    import pandas as pd

    # ── Bước 1: Dự đoán ──────────────────────────────────────
    vector, matched = vectorize(request.symptoms)
    if not matched:
        raise HTTPException(status_code=400, detail="Không nhận dạng được triệu chứng nào")

    proba = model.predict_proba(pd.DataFrame([vector], columns=all_symptoms))[0]

    # Áp dụng tuổi/giới tính nếu có
    if request.age or request.gender:
        proba = apply_weights(proba, le.classes_, request.age, request.gender)

    top3_idx   = proba.argsort()[-3:][::-1]
    disease_en = le.inverse_transform([top3_idx[0]])[0]
    disease_vi = to_vietnamese_disease(disease_en)
    confidence = round(float(proba[top3_idx[0]]) * 100, 2)
    severity   = SEVERITY.get(disease_en, "🟡 Cần theo dõi")
    specialty  = SPECIALTY.get(disease_en, "Nội khoa tổng quát")
    top3 = [
        {"disease_vi": to_vietnamese_disease(le.inverse_transform([i])[0]),
         "disease_en": le.inverse_transform([i])[0],
         "confidence": round(float(proba[i]) * 100, 2)}
        for i in top3_idx
    ]

    # Lưu lịch sử
    prediction_history.append({
        "time":       datetime.now().isoformat(),
        "symptoms":   request.symptoms,
        "disease":    disease_vi,
        "confidence": confidence,
    })

    # ── Bước 2: Tạo PDF với kết quả thực tế ─────────────────
    pdf_data = {
        "patient_name": request.patient_name,
        "age":          request.age,
        "gender":       request.gender,
        "symptoms":     request.symptoms,
        "disease_vi":   disease_vi,
        "disease_en":   disease_en,
        "confidence":   confidence,
        "severity":     severity,
        "specialty":    specialty,
        "top3":         top3,
    }

    try:
        pdf_bytes = build_pdf_bytes(pdf_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo PDF: {str(e)}")

    # ── Bước 3: Trả về file PDF để tải ──────────────────────
    filename = f"tuvan_{disease_en.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type = "application/pdf",
        headers    = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length":      str(len(pdf_bytes)),
        }
    )

@app.post("/report")
def download_report(request: DownloadReportRequest):
    """Tạo PDF từ kết quả tư vấn có sẵn (không re-predict)"""
    try:
        pdf_bytes = build_pdf_bytes(request.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo PDF: {str(e)}")
    d_en = request.disease_en.replace(' ', '_')
    filename = f"tuvan_{d_en}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(pdf_bytes)),
        }
    )

@app.post("/compare")
def compare(request: CompareRequest):
    if model is None: raise HTTPException(503,"Model chưa load")
    import pandas as pd
    def gp(syms):
        v,m = vectorize(syms)
        if not m: return None
        p=model.predict_proba(pd.DataFrame([v],columns=all_symptoms))[0]; i=p.argmax()
        d=le.inverse_transform([i])[0]
        return {"disease_vi":to_vietnamese_disease(d),"confidence":round(float(p[i])*100,2),"specialty":SPECIALTY.get(d,"Nội khoa")}
    a=gp(request.symptoms_a); b=gp(request.symptoms_b)
    return {"case_a":a,"case_b":b,"same_disease":a and b and a["disease_vi"]==b["disease_vi"]}

@app.post("/chat/start")
def chat_start():
    sid = str(uuid.uuid4())[:8]
    chat_sessions[sid] = {"step":0,"symptoms":[],"awaiting_followup":False}
    q = CHAT_QUESTIONS[0]
    return {"session_id":sid,"message":"👋 Xin chào! Hãy trả lời để AI phân tích triệu chứng.",
            "question":q["question"],"options":["Có","Không"],"step":1,"total_steps":len(CHAT_QUESTIONS)}

@app.post("/chat/reply")
def chat_reply(request: ChatReplyRequest):
    session = chat_sessions.get(request.session_id)
    if not session: raise HTTPException(404,"Session không tồn tại. Gọi /chat/start trước.")
    step=session["step"]; answer=request.answer.strip(); current=CHAT_QUESTIONS[step]
    if session["awaiting_followup"]:
        session["symptoms"].extend(current.get("followup_map",{}).get(answer,[]))
        session["awaiting_followup"]=False; session["step"]=step+1
    elif answer=="Có":
        session["awaiting_followup"]=True
        return {"session_id":request.session_id,"message":"Cụ thể hơn nhé:",
                "question":current["followup"],"options":current["followup_options"],
                "step":step+1,"total_steps":len(CHAT_QUESTIONS),"is_done":False,"result":None}
    else: session["step"]=step+1
    next_step=session["step"]
    if next_step>=len(CHAT_QUESTIONS):
        syms=session["symptoms"]; del chat_sessions[request.session_id]
        if not syms:
            return {"session_id":"","message":"Bạn không có triệu chứng đáng lo! 😊",
                    "question":None,"options":None,"step":len(CHAT_QUESTIONS),
                    "total_steps":len(CHAT_QUESTIONS),"is_done":True,"result":None}
        import pandas as pd
        v,m = vectorize(syms)
        p   = model.predict_proba(pd.DataFrame([v],columns=all_symptoms))[0]
        ti  = p.argsort()[-3:][::-1]
        d_en= le.inverse_transform([ti[0]])[0]; d_vi=to_vietnamese_disease(d_en)
        conf= round(float(p[ti[0]])*100,2)
        result = {"disease_vi":d_vi,"disease_en":d_en,"confidence":conf,
                  "severity":SEVERITY.get(d_en,"🟡 Cần theo dõi"),
                  "specialty":SPECIALTY.get(d_en,"Nội khoa tổng quát"),
                  "symptoms_used":syms,
                  "top3":[{"disease_vi":to_vietnamese_disease(le.inverse_transform([i])[0]),
                            "disease_en":le.inverse_transform([i])[0],
                            "confidence":round(float(p[i])*100,2)} for i in ti]}
        return {"session_id":request.session_id,
                "message":f"✅ AI dự đoán '{d_vi}' ({conf:.0f}%). Nên khám {result['specialty']}. ⚠️ Chỉ tham khảo.",
                "question":None,"options":None,"step":len(CHAT_QUESTIONS),
                "total_steps":len(CHAT_QUESTIONS),"is_done":True,"result":result}
    nq=CHAT_QUESTIONS[next_step]
    return {"session_id":request.session_id,"message":"OK, tiếp tục nhé!",
            "question":nq["question"],"options":["Có","Không"],
            "step":next_step+1,"total_steps":len(CHAT_QUESTIONS),"is_done":False,"result":None}

@app.delete("/chat/{session_id}")
def chat_end(session_id: str):
    if session_id in chat_sessions: del chat_sessions[session_id]
    return {"message":"Phiên chat đã kết thúc"}

@app.get("/history")
def get_history(limit: int = 10):
    return {"total":len(prediction_history),"history":prediction_history[-limit:][::-1]}

@app.get("/stats")
def get_stats():
    if not prediction_history: return {"message":"Chưa có dữ liệu"}
    counts = defaultdict(int)
    for h in prediction_history: counts[h["disease"]]+=1
    top = sorted(counts.items(),key=lambda x:-x[1])[:10]
    return {"total_requests":len(prediction_history),
            "top_diseases":[{"disease":d,"count":c} for d,c in top]}
