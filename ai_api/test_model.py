"""
========================================
TEST AI MODEL - Kiểm tra kết quả dự đoán
========================================
Chạy: python test_model.py
(Không cần chạy server, test thẳng model)
"""

from turtle import pd

import joblib
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vietnamese_dict import to_vietnamese_disease, to_vietnamese_symptom, to_english_symptom

# ── Load model ───────────────────────────────────────────────
print("=" * 60)
print("  🧪  TEST AI MODEL")
print("=" * 60)

model        = joblib.load('../models/best_model.pkl')
le           = joblib.load('../models/label_encoder.pkl')
all_symptoms = joblib.load('../models/symptoms_list.pkl')

with open('../models/best_model_name.txt') as f:
    model_name = f.read().strip()

print(f"\n✅ Model: {model_name}")
print(f"   {len(le.classes_)} bệnh | {len(all_symptoms)} triệu chứng")

# ── Hàm dự đoán ──────────────────────────────────────────────
def predict(symptoms_input):
    """
    Dự đoán bệnh từ danh sách triệu chứng
    Nhận cả tiếng Việt và tiếng Anh
    """
    input_vector = np.zeros(len(all_symptoms))
    matched      = []

    for s in symptoms_input:
        # Thử dịch VI → EN
        s_en    = to_english_symptom(s.strip())
        s_clean = s_en.strip().lower().replace(' ', '_')

        if s_clean in all_symptoms:
            input_vector[all_symptoms.index(s_clean)] = 1
            matched.append(s_clean)
        else:
            # Tìm gần đúng
            for sym in all_symptoms:
                if s_clean in sym or sym in s_clean:
                    input_vector[all_symptoms.index(sym)] = 1
                    matched.append(sym)
                    break

    if not matched:
        return None

    import pandas as pd
    input_df = pd.DataFrame([input_vector], columns=all_symptoms)
    proba = model.predict_proba(input_df)[0]
    top3_idx = proba.argsort()[-3:][::-1]

    return {
        "matched":    [to_vietnamese_symptom(s) for s in matched],
        "disease_en": le.inverse_transform([top3_idx[0]])[0],
        "disease_vi": to_vietnamese_disease(le.inverse_transform([top3_idx[0]])[0]),
        "confidence": round(float(proba[top3_idx[0]]) * 100, 2),
        "top3": [
            {
                "disease_vi": to_vietnamese_disease(le.inverse_transform([i])[0]),
                "confidence": round(float(proba[i]) * 100, 2)
            }
            for i in top3_idx
        ]
    }

def print_result(test_name, symptoms, result):
    print(f"\n{'─'*55}")
    print(f"🧪 {test_name}")
    print(f"   Input   : {symptoms}")
    if result:
        print(f"   Khớp    : {result['matched']}")
        print(f"   Bệnh    : {result['disease_vi']} ({result['disease_en']})")
        print(f"   Tin cậy : {result['confidence']}%")
        print(f"   Top 3   :")
        for i, r in enumerate(result['top3'], 1):
            print(f"     {i}. {r['disease_vi']} — {r['confidence']}%")
    else:
        print("   ❌ Không nhận dạng được triệu chứng")

# ══════════════════════════════════════════════════════════════
# TEST CASES
# ══════════════════════════════════════════════════════════════

print("\n" + "=" * 55)
print("  NHÓM 1: TEST BỆNH TRONG KAGGLE GỐC")
print("=" * 55)

# Test 1 - Nhiễm nấm
print_result(
    "Nhiễm nấm da",
    ["Ngứa da", "Phát ban da", "skin_rash"],
    predict(["Ngứa da", "Phát ban da", "skin_rash"])
)

# Test 2 - Tiểu đường
print_result(
    "Tiểu đường",
    ["Tiểu nhiều", "Mệt mỏi", "Sụt cân", "Đói quá mức"],
    predict(["Tiểu nhiều", "Mệt mỏi", "Sụt cân", "Đói quá mức"])
)

# Test 3 - Sốt xuất huyết
print_result(
    "Sốt xuất huyết",
    ["Sốt cao", "Đau đầu", "Đau sau mắt", "Buồn nôn"],
    predict(["Sốt cao", "Đau đầu", "Đau sau mắt", "Buồn nôn"])
)

# Test 4 - Tăng huyết áp
print_result(
    "Tăng huyết áp",
    ["Đau đầu", "Chóng mặt", "Đau ngực"],
    predict(["Đau đầu", "Chóng mặt", "Đau ngực"])
)

# Test 5 - Viêm phổi
print_result(
    "Viêm phổi",
    ["Sốt cao", "Ho", "Khó thở", "Đau ngực", "Mệt mỏi"],
    predict(["Sốt cao", "Ho", "Khó thở", "Đau ngực", "Mệt mỏi"])
)

print("\n" + "=" * 55)
print("  NHÓM 2: TEST BỆNH MỚI THÊM (VIỆT NAM)")
print("=" * 55)

# Test 6 - Tay chân miệng
print_result(
    "Tay chân miệng",
    ["Phát ban da", "Sốt", "Loét miệng", "Mệt mỏi"],
    predict(["Phát ban da", "Sốt", "Loét miệng", "Mệt mỏi"])
)

# Test 7 - Cúm mùa
print_result(
    "Cúm mùa",
    ["Sốt", "Đau đầu", "Mệt mỏi", "Đau cơ", "Ho"],
    predict(["Sốt", "Đau đầu", "Mệt mỏi", "Đau cơ", "Ho"])
)

# Test 8 - Say nắng
print_result(
    "Say nắng",
    ["Sốt cao", "Đau đầu", "Chóng mặt", "Mất nước"],
    predict(["Sốt cao", "Đau đầu", "Chóng mặt", "Mất nước"])
)

# Test 9 - Ngộ độc thực phẩm
print_result(
    "Ngộ độc thực phẩm",
    ["Nôn mửa", "Buồn nôn", "Đau bụng", "Tiêu chảy"],
    predict(["Nôn mửa", "Buồn nôn", "Đau bụng", "Tiêu chảy"])
)

# Test 10 - Viêm amidan
print_result(
    "Viêm amidan",
    ["Kích ứng cổ họng", "Sốt", "Mệt mỏi", "Hạch bạch huyết sưng"],
    predict(["Kích ứng cổ họng", "Sốt", "Mệt mỏi", "Hạch bạch huyết sưng"])
)

print("\n" + "=" * 55)
print("  NHÓM 3: TEST TIẾNG ANH")
print("=" * 55)

# Test 11 - Mix tiếng Anh
print_result(
    "Mix tiếng Anh + Việt",
    ["fever", "headache", "Mệt mỏi", "cough"],
    predict(["fever", "headache", "Mệt mỏi", "cough"])
)

# Test 12 - Hoàn toàn tiếng Anh
print_result(
    "Hoàn toàn tiếng Anh",
    ["itching", "skin_rash", "nodal_skin_eruptions"],
    predict(["itching", "skin_rash", "nodal_skin_eruptions"])
)

print("\n" + "=" * 55)
print("  NHÓM 4: TEST TRƯỜNG HỢP ĐẶC BIỆT")
print("=" * 55)

# Test 13 - 1 triệu chứng
print_result(
    "Chỉ 1 triệu chứng",
    ["Sốt"],
    predict(["Sốt"])
)

# Test 14 - Triệu chứng không tồn tại
print_result(
    "Triệu chứng không tồn tại",
    ["abc xyz", "không có trong dataset"],
    predict(["abc xyz", "không có trong dataset"])
)

# Test 15 - Nhiều triệu chứng
print_result(
    "Nhiều triệu chứng (10 cái)",
    ["Sốt", "Đau đầu", "Ho", "Mệt mỏi", "Buồn nôn",
     "Đau cơ", "Ớn lạnh", "Chán ăn", "Đau họng", "Nghẹt mũi"],
    predict(["Sốt", "Đau đầu", "Ho", "Mệt mỏi", "Buồn nôn",
             "Đau cơ", "Ớn lạnh", "Chán ăn", "Đau họng", "Nghẹt mũi"])
)

print("\n" + "=" * 55)
print("✅ TEST HOÀN THÀNH!")
print("=" * 55)
