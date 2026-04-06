"""
========================================
TÍNH NĂNG NÂNG CAO - 6 tính năng mới
========================================
1. Explainable AI (SHAP)
2. Multi-label prediction
3. Symptom Graph
4. Second Opinion (RF vs DNN)
5. Risk Score
Chạy: python 06_Advanced_Features.py
Cài: pip install shap networkx --break-system-packages
"""

import joblib
import numpy as np
import pandas as pd
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vietnamese_dict import to_vietnamese_disease, to_vietnamese_symptom

# Load model
model        = joblib.load('../models/best_model.pkl')
le           = joblib.load('../models/label_encoder.pkl')
all_symptoms = joblib.load('../models/symptoms_list.pkl')
sym_index    = {s: i for i, s in enumerate(all_symptoms)}

print("✅ Model loaded")

# ════════════════════════════════════════════════════════════
# 1. EXPLAINABLE AI - SHAP
# ════════════════════════════════════════════════════════════

def explain_prediction(symptoms_input: list, top_n: int = 5) -> dict:
    """
    Giải thích tại sao AI dự đoán bệnh đó
    Trả về top N triệu chứng quan trọng nhất
    """
    try:
        import shap
    except ImportError:
        return {"error": "Cài shap: pip install shap --break-system-packages"}

    # Vector hóa
    vector = np.zeros(len(all_symptoms))
    for s in symptoms_input:
        s_clean = s.strip().lower().replace(' ', '_')
        if s_clean in sym_index:
            vector[sym_index[s_clean]] = 1

    input_df = pd.DataFrame([vector], columns=all_symptoms)

    # Tính SHAP values
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(input_df)

    # Lấy class được dự đoán
    proba      = model.predict_proba(input_df)[0]
    pred_class = proba.argmax()
    disease_en = le.inverse_transform([pred_class])[0]

    # SHAP values cho class được dự đoán
    shap_for_class = shap_values[pred_class][0]

    # Top N triệu chứng quan trọng nhất
    top_idx = np.abs(shap_for_class).argsort()[-top_n:][::-1]
    explanations = []
    for idx in top_idx:
        sym    = all_symptoms[idx]
        impact = float(shap_for_class[idx])
        if vector[idx] == 1:  # Chỉ hiện triệu chứng người dùng nhập
            explanations.append({
                "symptom_en": sym,
                "symptom_vi": to_vietnamese_symptom(sym),
                "impact":     round(impact, 4),
                "direction":  "tăng" if impact > 0 else "giảm",
                "importance": round(abs(impact) * 100, 2),
            })

    return {
        "disease_vi":    to_vietnamese_disease(disease_en),
        "disease_en":    disease_en,
        "confidence":    round(float(proba[pred_class]) * 100, 2),
        "explanations":  sorted(explanations, key=lambda x: -x["importance"]),
        "summary": f"AI dự đoán '{to_vietnamese_disease(disease_en)}' chủ yếu dựa vào: "
                   + ", ".join([e["symptom_vi"] for e in explanations[:3]]),
    }


# ════════════════════════════════════════════════════════════
# 2. MULTI-LABEL - Dự đoán nhiều bệnh cùng lúc
# ════════════════════════════════════════════════════════════

def predict_multilabel(symptoms_input: list, threshold: float = 15.0) -> dict:
    """
    Dự đoán tất cả bệnh có khả năng > threshold%
    Thay vì chỉ trả về 1 bệnh
    """
    vector = np.zeros(len(all_symptoms))
    matched = []
    for s in symptoms_input:
        s_clean = s.strip().lower().replace(' ', '_')
        if s_clean in sym_index:
            vector[sym_index[s_clean]] = 1
            matched.append(s_clean)

    if not matched:
        return {"error": "Không nhận dạng được triệu chứng"}

    input_df = pd.DataFrame([vector], columns=all_symptoms)
    proba    = model.predict_proba(input_df)[0]

    # Lấy tất cả bệnh > threshold
    possible = []
    for i, p in enumerate(proba):
        conf = round(float(p) * 100, 2)
        if conf >= threshold:
            d_en = le.inverse_transform([i])[0]
            possible.append({
                "disease_en": d_en,
                "disease_vi": to_vietnamese_disease(d_en),
                "confidence": conf,
            })

    possible = sorted(possible, key=lambda x: -x["confidence"])

    return {
        "matched_symptoms": len(matched),
        "threshold":        threshold,
        "total_possible":   len(possible),
        "diseases":         possible,
        "summary": f"Tìm thấy {len(possible)} bệnh có khả năng > {threshold}%",
    }


# ════════════════════════════════════════════════════════════
# 3. SYMPTOM GRAPH - Mạng lưới triệu chứng-bệnh
# ════════════════════════════════════════════════════════════

def build_symptom_graph(disease_name_en: str) -> dict:
    """
    Xây dựng mạng lưới quan hệ triệu chứng cho 1 bệnh
    Dựa trên feature importance của model
    """
    try:
        import networkx as nx
    except ImportError:
        return {"error": "Cài networkx: pip install networkx --break-system-packages"}

    if disease_name_en not in le.classes_:
        return {"error": f"Không tìm thấy bệnh: {disease_name_en}"}

    class_idx = list(le.classes_).index(disease_name_en)

    # Lấy feature importance từ Random Forest
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'estimators_'):
        # Voting classifier - lấy RF
        for name, est in model.named_estimators_.items():
            if hasattr(est, 'feature_importances_'):
                importances = est.feature_importances_
                break
    else:
        importances = np.ones(len(all_symptoms)) / len(all_symptoms)

    # Top 10 triệu chứng quan trọng nhất
    top_idx  = importances.argsort()[-10:][::-1]
    top_syms = [(all_symptoms[i], float(importances[i])) for i in top_idx]

    # Tạo graph
    G = nx.Graph()
    G.add_node(disease_name_en, type="disease",
               label=to_vietnamese_disease(disease_name_en))

    nodes = [{"id": disease_name_en,
              "label": to_vietnamese_disease(disease_name_en),
              "type": "disease", "size": 30}]
    edges = []

    for sym, imp in top_syms:
        G.add_node(sym, type="symptom", label=to_vietnamese_symptom(sym))
        G.add_edge(disease_name_en, sym, weight=imp)
        nodes.append({"id": sym, "label": to_vietnamese_symptom(sym),
                      "type": "symptom", "importance": round(imp * 100, 2)})
        edges.append({"from": disease_name_en, "to": sym,
                      "weight": round(imp * 100, 2)})

    return {
        "disease_vi":  to_vietnamese_disease(disease_name_en),
        "disease_en":  disease_name_en,
        "nodes":       nodes,
        "edges":       edges,
        "top_symptoms": [
            {"symptom_vi": to_vietnamese_symptom(s), "importance": round(imp*100,2)}
            for s, imp in top_syms
        ],
    }


# ════════════════════════════════════════════════════════════
# 4. SECOND OPINION - So sánh RF vs DNN
# ════════════════════════════════════════════════════════════

def second_opinion(symptoms_input: list) -> dict:
    """
    Chạy cả RF và DNN, so sánh kết quả
    Nếu đồng thuận → tin cậy cao
    Nếu khác nhau → cần xem xét thêm
    """
    import torch
    import torch.nn as nn

    vector = np.zeros(len(all_symptoms))
    matched = []
    for s in symptoms_input:
        s_clean = s.strip().lower().replace(' ', '_')
        if s_clean in sym_index:
            vector[sym_index[s_clean]] = 1
            matched.append(s_clean)

    if not matched:
        return {"error": "Không nhận dạng được triệu chứng"}

    # ── RF Prediction ────────────────────────────────────────
    input_df    = pd.DataFrame([vector], columns=all_symptoms)
    proba_rf    = model.predict_proba(input_df)[0]
    top_rf      = proba_rf.argmax()
    rf_disease  = le.inverse_transform([top_rf])[0]
    rf_conf     = round(float(proba_rf[top_rf]) * 100, 2)

    # ── DNN Prediction ───────────────────────────────────────
    dnn_result = None
    dnn_path   = os.path.join('..', 'models', 'dnn_full.pt')

    if os.path.exists(dnn_path):
        class HealthDNN(nn.Module):
            def __init__(self, n_input, n_classes):
                super().__init__()
                self.network = nn.Sequential(
                    nn.Linear(n_input, 512), nn.BatchNorm1d(512), nn.ReLU(), nn.Dropout(0.3),
                    nn.Linear(512, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.3),
                    nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.2),
                    nn.Linear(128, 64), nn.ReLU(),
                    nn.Linear(64, n_classes),
                )
            def forward(self, x): return self.network(x)

        ckpt      = torch.load(dnn_path, map_location='cpu')
        dnn_model = HealthDNN(ckpt['n_features'], ckpt['n_classes'])
        dnn_model.load_state_dict(ckpt['model_state'])
        dnn_model.eval()

        tensor = torch.FloatTensor([vector])
        with torch.no_grad():
            out       = dnn_model(tensor)
            proba_dnn = torch.softmax(out, dim=1)[0].numpy()

        top_dnn     = proba_dnn.argmax()
        dnn_disease = le.inverse_transform([top_dnn])[0]
        dnn_conf    = round(float(proba_dnn[top_dnn]) * 100, 2)
        dnn_result  = {"disease_vi": to_vietnamese_disease(dnn_disease),
                       "disease_en": dnn_disease, "confidence": dnn_conf}

    # ── So sánh ──────────────────────────────────────────────
    agreement = dnn_result and rf_disease == dnn_result["disease_en"]

    return {
        "rf_result": {
            "disease_vi": to_vietnamese_disease(rf_disease),
            "disease_en": rf_disease,
            "confidence": rf_conf,
            "model":      "Random Forest / Ensemble",
        },
        "dnn_result":   dnn_result,
        "agreement":    agreement,
        "verdict": (
            "✅ Cả 2 model đồng thuận — Kết quả tin cậy cao!" if agreement
            else "⚠️ 2 model khác nhau — Nên nhập thêm triệu chứng để chắc chắn hơn"
        ) if dnn_result else "⚠️ DNN chưa load",
        "recommendation": to_vietnamese_disease(rf_disease),
    }


# ════════════════════════════════════════════════════════════
# 5. RISK SCORE - Điểm nguy cơ từng bệnh
# ════════════════════════════════════════════════════════════

RISK_FACTORS = {
    "Heart attack":     {"base": 5, "age_adult": 2, "age_elderly": 5, "male": 3},
    "Diabetes":         {"base": 5, "age_adult": 2, "age_elderly": 3, "obesity": 4},
    "Hypertension":     {"base": 5, "age_adult": 2, "age_elderly": 4, "male": 2},
    "Tuberculosis":     {"base": 3, "crowded": 4},
    "Dengue":           {"base": 6, "tropical": 5},
    "Hepatitis B":      {"base": 4, "unprotected": 5},
}

def calculate_risk_score(symptoms_input: list, age: int = None,
                          gender: str = None) -> dict:
    """
    Tính điểm nguy cơ cho tất cả bệnh có khả năng
    Kết hợp: xác suất model + yếu tố nguy cơ bổ sung
    """
    vector = np.zeros(len(all_symptoms))
    for s in symptoms_input:
        s_clean = s.strip().lower().replace(' ', '_')
        if s_clean in sym_index:
            vector[sym_index[s_clean]] = 1

    input_df = pd.DataFrame([vector], columns=all_symptoms)
    proba    = model.predict_proba(input_df)[0]
    top5_idx = proba.argsort()[-5:][::-1]

    risk_results = []
    for i in top5_idx:
        d_en   = le.inverse_transform([i])[0]
        base_p = float(proba[i]) * 100

        # Tính risk score bổ sung
        risk_score = base_p
        factors    = []

        if d_en in RISK_FACTORS:
            rf = RISK_FACTORS[d_en]
            risk_score += rf.get("base", 0)
            factors.append(f"Yếu tố cơ bản +{rf.get('base',0)}")

            if age:
                if age >= 60 and "age_elderly" in rf:
                    risk_score += rf["age_elderly"]
                    factors.append(f"Tuổi cao +{rf['age_elderly']}")
                elif age >= 18 and "age_adult" in rf:
                    risk_score += rf["age_adult"]
                    factors.append(f"Người lớn +{rf['age_adult']}")

            if gender == "male" and "male" in rf:
                risk_score += rf["male"]
                factors.append(f"Nam giới +{rf['male']}")

        # Normalize 0-100
        risk_score = min(round(risk_score, 1), 100)

        risk_results.append({
            "disease_vi":  to_vietnamese_disease(d_en),
            "disease_en":  d_en,
            "model_prob":  round(base_p, 2),
            "risk_score":  risk_score,
            "risk_level":  "🔴 Cao" if risk_score >= 70
                      else "🟠 Trung bình cao" if risk_score >= 50
                      else "🟡 Trung bình" if risk_score >= 30
                      else "🟢 Thấp",
            "risk_factors": factors,
        })

    risk_results.sort(key=lambda x: -x["risk_score"])
    return {
        "age":    age,
        "gender": gender,
        "risks":  risk_results,
        "highest_risk": risk_results[0] if risk_results else None,
    }


# ════════════════════════════════════════════════════════════
# TEST TẤT CẢ
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    test_symptoms = ["itching", "skin_rash", "nodal_skin_eruptions"]

    print("\n" + "="*55)
    print("  2. MULTI-LABEL PREDICTION")
    print("="*55)
    r = predict_multilabel(test_symptoms, threshold=10.0)
    print(f"Tìm thấy {r['total_possible']} bệnh:")
    for d in r["diseases"][:5]:
        print(f"  - {d['disease_vi']}: {d['confidence']}%")

    print("\n" + "="*55)
    print("  3. SYMPTOM GRAPH")
    print("="*55)
    r = build_symptom_graph("Fungal infection")
    print(f"Bệnh: {r['disease_vi']}")
    print("Top triệu chứng quan trọng:")
    for s in r["top_symptoms"][:5]:
        print(f"  - {s['symptom_vi']}: {s['importance']}%")

    print("\n" + "="*55)
    print("  4. SECOND OPINION")
    print("="*55)
    r = second_opinion(test_symptoms)
    print(f"RF  : {r['rf_result']['disease_vi']} ({r['rf_result']['confidence']}%)")
    if r["dnn_result"]:
        print(f"DNN : {r['dnn_result']['disease_vi']} ({r['dnn_result']['confidence']}%)")
    print(f"Kết luận: {r['verdict']}")

    print("\n" + "="*55)
    print("  5. RISK SCORE")
    print("="*55)
    r = calculate_risk_score(["chest_pain", "fatigue", "fast_heart_rate"],
                              age=55, gender="male")
    for risk in r["risks"][:3]:
        print(f"  {risk['risk_level']} {risk['disease_vi']}: {risk['risk_score']}/100")

    print("\n✅ Tất cả tính năng nâng cao hoạt động!")
    print("\n👉 Chạy tiếp: python 07_PDF_Report.py")
