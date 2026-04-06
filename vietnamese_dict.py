"""
vietnamese_dict.py
==================
Từ điển dịch Tiếng Anh → Tiếng Việt
cho triệu chứng và tên bệnh
"""

# ── TRIỆU CHỨNG (132 triệu chứng) ───────────────────────────
SYMPTOM_VI = {
    # Da liễu
    "itching":                        "Ngứa da",
    "skin_rash":                      "Phát ban da",
    "nodal_skin_eruptions":           "Nổi hạch da",
    "dischromic_patches":             "Đốm da đổi màu",
    "skin_peeling":                   "Bong tróc da",
    "blackheads":                     "Mụn đầu đen",
    "pus_filled_pimples":             "Mụn mủ",
    "scurring":                       "Sẹo da",
    "blister":                        "Phồng rộp",
    "red_sore_around_nose":           "Vết đỏ quanh mũi",
    "yellow_crust_ooze":              "Vảy vàng rỉ dịch",
    "inflammatory_nails":             "Viêm móng",
    "brittle_nails":                  "Móng giòn dễ gãy",
    "small_dents_in_nails":           "Lõm nhỏ trên móng",
    "silver_like_dusting":            "Bụi bạc trên da",

    # Hô hấp
    "continuous_sneezing":            "Hắt hơi liên tục",
    "cough":                          "Ho",
    "breathlessness":                 "Khó thở",
    "rusty_sputum":                   "Đờm màu rỉ sét",
    "phlegm":                         "Đờm",
    "blood_in_sputum":                "Ho ra máu",
    "mucoid_sputum":                  "Đờm nhầy",
    "throat_irritation":              "Kích ứng cổ họng",

    # Tiêu hóa
    "stomach_pain":                   "Đau dạ dày",
    "abdominal_pain":                 "Đau bụng",
    "nausea":                         "Buồn nôn",
    "vomiting":                       "Nôn mửa",
    "diarrhoea":                      "Tiêu chảy",
    "constipation":                   "Táo bón",
    "acidity":                        "Ợ chua",
    "ulcers_on_tongue":               "Loét miệng",
    "belly_pain":                     "Đau vùng bụng",
    "pain_during_bowel_movements":    "Đau khi đại tiện",
    "pain_in_anal_region":            "Đau vùng hậu môn",
    "bloody_stool":                   "Phân có máu",
    "irritation_in_anus":             "Kích ứng hậu môn",
    "stomach_bleeding":               "Xuất huyết dạ dày",
    "distention_of_abdomen":          "Chướng bụng",
    "passage_of_gases":               "Xì hơi nhiều",
    "indigestion":                    "Khó tiêu",

    # Toàn thân
    "fatigue":                        "Mệt mỏi",
    "fever":                          "Sốt",
    "high_fever":                     "Sốt cao",
    "mild_fever":                     "Sốt nhẹ",
    "chills":                         "Ớn lạnh",
    "shivering":                      "Run rẩy",
    "sweating":                       "Đổ mồ hôi",
    "cold_hands_and_feets":           "Tay chân lạnh",
    "lethargy":                       "Uể oải",
    "malaise":                        "Khó chịu toàn thân",
    "weight_loss":                    "Sụt cân",
    "weight_gain":                    "Tăng cân",
    "obesity":                        "Béo phì",
    "dehydration":                    "Mất nước",

    # Đầu / Thần kinh
    "headache":                       "Đau đầu",
    "dizziness":                      "Chóng mặt",
    "loss_of_balance":                "Mất thăng bằng",
    "unsteadiness":                   "Đi không vững",
    "lack_of_concentration":          "Khó tập trung",
    "altered_sensorium":              "Rối loạn ý thức",
    "spinning_movements":             "Cảm giác quay cuồng",
    "depression":                     "Trầm cảm",
    "irritability":                   "Dễ cáu kỉnh",
    "visual_disturbances":            "Rối loạn thị giác",
    "blurred_and_distorted_vision":   "Mờ mắt",
    "slurred_speech":                 "Nói ngọng",
    "weakness_of_one_body_side":      "Yếu một bên cơ thể",
    "loss_of_smell":                  "Mất khứu giác",
    "anxiety":                        "Lo lắng",
    "inner_canthus_haemorrhage":      "Xuất huyết góc mắt trong",

    # Cơ xương khớp
    "joint_pain":                     "Đau khớp",
    "muscle_pain":                    "Đau cơ",
    "muscle_weakness":                "Yếu cơ",
    "muscle_wasting":                 "Teo cơ",
    "back_pain":                      "Đau lưng",
    "neck_pain":                      "Đau cổ",
    "knee_pain":                      "Đau đầu gối",
    "hip_joint_pain":                 "Đau khớp háng",
    "painful_walking":                "Đau khi đi lại",
    "movement_stiffness":             "Cứng khớp",
    "stiff_neck":                     "Cứng cổ",
    "swelling_joints":                "Sưng khớp",
    "cramps":                         "Chuột rút",

    # Tim mạch
    "chest_pain":                     "Đau ngực",
    "fast_heart_rate":                "Nhịp tim nhanh",
    "palpitations":                   "Hồi hộp đánh trống ngực",
    "prominent_veins_on_calf":        "Giãn tĩnh mạch bắp chân",
    "swollen_legs":                   "Sưng chân",
    "swollen_blood_vessels":          "Giãn mạch máu",

    # Tiết niệu
    "burning_micturition":            "Tiểu buốt",
    "spotting_urination":             "Tiểu ra máu",
    "dark_urine":                     "Nước tiểu sẫm màu",
    "yellow_urine":                   "Nước tiểu vàng",
    "continuous_feel_of_urine":       "Buồn tiểu liên tục",
    "bladder_discomfort":             "Khó chịu bàng quang",
    "foul_smell_of_urine":            "Nước tiểu mùi hôi",

    # Mắt
    "redness_of_eyes":                "Đỏ mắt",
    "watering_from_eyes":             "Chảy nước mắt",
    "sunken_eyes":                    "Mắt trũng",
    "yellowish_skin":                 "Da vàng",
    "yellow_urine":                   "Nước tiểu vàng",
    "yellowing_of_eyes":              "Vàng mắt",

    # Nội tiết / Chuyển hóa
    "excessive_hunger":               "Đói quá mức",
    "increased_appetite":             "Ăn nhiều hơn bình thường",
    "polyuria":                       "Tiểu nhiều",
    "irregular_sugar_level":          "Đường huyết không ổn định",
    "enlarged_thyroid":               "Phình tuyến giáp",
    "swollen_extremities":            "Sưng tay chân",
    "puffy_face_and_eyes":            "Phù mặt và mắt",
    "brittle_nails":                  "Móng giòn",
    "dryness":                        "Khô da",
    "abnormal_menstruation":          "Kinh nguyệt bất thường",

    # Gan / Mật
    "loss_of_appetite":               "Chán ăn",
    "mild_fever":                     "Sốt nhẹ",
    "yellowing_of_eyes":              "Vàng mắt",
    "dark_urine":                     "Nước tiểu sẫm màu",
    "fluid_overload":                 "Ứ dịch",
    "swelling_of_stomach":            "Báng bụng",
    "liver_tender":                   "Gan đau khi sờ",
    "fluid_overload.1":               "Ứ dịch nặng",
    "history_of_alcohol_consumption": "Tiền sử uống rượu",
    "acute_liver_failure":            "Suy gan cấp",

    # Truyền nhiễm
    "red_spots_over_body":            "Đốm đỏ toàn thân",
    "toxic_look_(typhos)":            "Vẻ nhiễm độc",
    "swollen_lymph_nodes":            "Hạch bạch huyết sưng",
    "patches_in_throat":              "Mảng trắng họng",
    "runny_nose":                     "Chảy nước mũi",
    "congestion":                     "Nghẹt mũi",
    "sinus_pressure":                 "Áp lực xoang",
    "watery_eyes":                    "Mắt chảy nước",
    "extra_marital_contacts":         "Quan hệ tình dục không an toàn",
    "receiving_blood_transfusion":    "Truyền máu",
    "receiving_unsterile_injections": "Tiêm không vô trùng",

    # Khác
    "pain_behind_the_eyes":           "Đau sau mắt",
    "irritability":                   "Dễ cáu",
    "weakness_in_limbs":              "Yếu tứ chi",
    "swollen_legs":                   "Phù chân",
    "bruising":                       "Bầm tím",
    "coma":                           "Hôn mê",
    "toxic_look_(typhos)":            "Vẻ nhiễm độc",
    "family_history":                 "Tiền sử gia đình",
    "mucoid_sputum":                  "Đờm nhầy",
    "phlegm":                         "Đờm",
    "drying_and_tingling_lips":       "Môi khô và ngứa ran",
    "slurred_speech":                 "Nói không rõ chữ",
    "knee_pain":                      "Đau đầu gối",
    "hip_joint_pain":                 "Đau khớp háng",
}

# ── TÊN BỆNH (41 bệnh) ──────────────────────────────────────
DISEASE_VI = {
    "Fungal infection":                          "Nhiễm nấm",
    "Allergy":                                   "Dị ứng",
    "GERD":                                      "Trào ngược dạ dày thực quản",
    "Chronic cholestasis":                       "Ứ mật mãn tính",
    "Drug Reaction":                             "Phản ứng thuốc",
    "Peptic ulcer diseae":                       "Loét dạ dày tá tràng",
    "AIDS":                                      "HIV/AIDS",
    "Diabetes":                                  "Tiểu đường",
    "Gastroenteritis":                           "Viêm dạ dày ruột",
    "Bronchial Asthma":                          "Hen phế quản",
    "Hypertension":                              "Tăng huyết áp",
    "Migraine":                                  "Đau nửa đầu (Migraine)",
    "Cervical spondylosis":                      "Thoái hóa đốt sống cổ",
    "Paralysis (brain hemorrhage)":              "Liệt (xuất huyết não)",
    "Jaundice":                                  "Vàng da",
    "Malaria":                                   "Sốt rét",
    "Chicken pox":                               "Thủy đậu",
    "Dengue":                                    "Sốt xuất huyết",
    "Typhoid":                                   "Thương hàn",
    "hepatitis A":                               "Viêm gan A",
    "Hepatitis B":                               "Viêm gan B",
    "Hepatitis C":                               "Viêm gan C",
    "Hepatitis D":                               "Viêm gan D",
    "Hepatitis E":                               "Viêm gan E",
    "Alcoholic hepatitis":                       "Viêm gan do rượu",
    "Tuberculosis":                              "Lao phổi",
    "Common Cold":                               "Cảm lạnh thông thường",
    "Pneumonia":                                 "Viêm phổi",
    "Dimorphic hemmorhoids(piles)":              "Bệnh trĩ",
    "Heart attack":                              "Nhồi máu cơ tim",
    "Varicose veins":                            "Giãn tĩnh mạch",
    "Hypothyroidism":                            "Suy giáp",
    "Hyperthyroidism":                           "Cường giáp",
    "Hypoglycemia":                              "Hạ đường huyết",
    "Osteoarthristis":                           "Thoái hóa khớp",
    "Arthritis":                                 "Viêm khớp",
    "(vertigo) Paroymsal  Positional Vertigo":   "Chóng mặt tư thế lành tính",
    "Acne":                                      "Mụn trứng cá",
    "Urinary tract infection":                   "Nhiễm trùng đường tiểu",
    "Psoriasis":                                 "Vảy nến",
    "Impetigo":                                  "Chốc lở",
}

# ── CHUYÊN KHOA ──────────────────────────────────────────────
SPECIALTY_VI = {
    "Da liễu":                    "Da liễu",
    "Dị ứng - Miễn dịch":        "Dị ứng - Miễn dịch",
    "Tiêu hóa":                   "Tiêu hóa",
    "Nội khoa":                   "Nội khoa",
    "Truyền nhiễm":               "Truyền nhiễm",
    "Nội tiết":                   "Nội tiết",
    "Hô hấp":                     "Hô hấp",
    "Tim mạch":                   "Tim mạch",
    "Thần kinh":                  "Thần kinh",
    "Cơ xương khớp":              "Cơ xương khớp",
    "Tiêu hóa - Gan":             "Tiêu hóa - Gan",
    "Thận - Tiết niệu":           "Thận - Tiết niệu",
    "Thần kinh - Tai mũi họng":   "Thần kinh - Tai mũi họng",
    "Nội khoa tổng quát":         "Nội khoa tổng quát",
}


def to_vietnamese_symptom(symptom_en: str) -> str:
    """Dịch triệu chứng sang tiếng Việt"""
    return SYMPTOM_VI.get(symptom_en, symptom_en.replace("_", " ").title())


def to_vietnamese_disease(disease_en: str) -> str:
    """Dịch tên bệnh sang tiếng Việt"""
    return DISEASE_VI.get(disease_en, disease_en)


def to_english_symptom(symptom_vi: str) -> str:
    """Dịch triệu chứng tiếng Việt → tiếng Anh (để feed vào model)"""
    reverse = {v: k for k, v in SYMPTOM_VI.items()}
    return reverse.get(symptom_vi, symptom_vi)


if __name__ == "__main__":
    # Test thử
    print("Test dịch triệu chứng:")
    print(f"  itching       → {to_vietnamese_symptom('itching')}")
    print(f"  fever         → {to_vietnamese_symptom('fever')}")
    print(f"  joint_pain    → {to_vietnamese_symptom('joint_pain')}")

    print("\nTest dịch tên bệnh:")
    print(f"  Diabetes      → {to_vietnamese_disease('Diabetes')}")
    print(f"  Dengue        → {to_vietnamese_disease('Dengue')}")
    print(f"  Tuberculosis  → {to_vietnamese_disease('Tuberculosis')}")

    print("\nTest dịch ngược (VI → EN):")
    print(f"  Ngứa da       → {to_english_symptom('Ngứa da')}")
    print(f"  Sốt           → {to_english_symptom('Sốt')}")
