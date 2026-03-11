"""
========================================
MỞ RỘNG DATASET - Thêm bệnh Việt Nam
========================================
Chạy: python extend_dataset.py
Kết quả: data/disease_dataset_extended.csv
"""

import pandas as pd
import numpy  as np
import os

os.makedirs('../data', exist_ok=True)

print("=" * 60)
print("  📦  MỞ RỘNG DATASET V2")
print("=" * 60)

df_original = pd.read_csv('../data/disease_dataset_extended.csv')
print(f"\n✅ Dataset hiện tại: {df_original.shape[0]} mẫu | {df_original['Disease'].nunique()} bệnh")

symptom_cols = [c for c in df_original.columns if c != 'Disease']

# ── Bệnh mới thêm vào ────────────────────────────────────────
NEW_DISEASES = {

    # ── Bệnh trẻ em ─────────────────────────────────────────
    "Measles": {  # Sởi
        "primary":   ["skin_rash", "high_fever", "cough"],
        "secondary": ["runny_nose", "watering_from_eyes",
                      "fatigue", "loss_of_appetite"],
        "optional":  ["headache", "throat_irritation", "mild_fever"],
        "samples":   120,
    },
    "Mumps": {  # Quai bị
        "primary":   ["swollen_lymph_nodes", "fever", "fatigue"],
        "secondary": ["headache", "muscle_pain", "loss_of_appetite"],
        "optional":  ["nausea", "chills", "mild_fever"],
        "samples":   100,
    },
    "Whooping Cough": {  # Ho gà
        "primary":   ["cough", "fatigue", "runny_nose"],
        "secondary": ["fever", "throat_irritation", "loss_of_appetite"],
        "optional":  ["vomiting", "mild_fever", "headache"],
        "samples":   100,
    },

    # ── Bệnh da liễu ─────────────────────────────────────────
    "Scabies": {  # Ghẻ ngứa
        "primary":   ["itching", "skin_rash", "blister"],
        "secondary": ["nodal_skin_eruptions", "skin_peeling", "fatigue"],
        "optional":  ["fever", "loss_of_appetite"],
        "samples":   100,
    },
    "Urticaria": {  # Mề đay
        "primary":   ["skin_rash", "itching", "fatigue"],
        "secondary": ["swollen_lymph_nodes", "breathlessness",
                      "chest_pain"],
        "optional":  ["nausea", "headache", "mild_fever"],
        "samples":   100,
    },

    # ── Bệnh hô hấp ──────────────────────────────────────────
    "Sinusitis": {  # Viêm xoang
        "primary":   ["headache", "congestion", "sinus_pressure"],
        "secondary": ["runny_nose", "fatigue", "throat_irritation",
                      "mild_fever"],
        "optional":  ["cough", "loss_of_appetite", "nausea"],
        "samples":   120,
    },
    "Bronchitis": {  # Viêm phế quản
        "primary":   ["cough", "phlegm", "fatigue"],
        "secondary": ["breathlessness", "chest_pain", "mild_fever",
                      "throat_irritation"],
        "optional":  ["headache", "chills", "muscle_pain"],
        "samples":   120,
    },

    # ── Bệnh tiêu hóa ────────────────────────────────────────
    "Appendicitis": {  # Viêm ruột thừa
        "primary":   ["abdominal_pain", "fever", "nausea"],
        "secondary": ["vomiting", "loss_of_appetite", "fatigue",
                      "constipation"],
        "optional":  ["chills", "belly_pain", "dehydration"],
        "samples":   100,
    },
    "Gallstones": {  # Sỏi mật
        "primary":   ["abdominal_pain", "nausea", "vomiting"],
        "secondary": ["fatigue", "loss_of_appetite", "yellowish_skin",
                      "indigestion"],
        "optional":  ["chills", "fever", "back_pain"],
        "samples":   100,
    },

    # ── Bệnh thần kinh ───────────────────────────────────────
    "Epilepsy": {  # Động kinh
        "primary":   ["altered_sensorium", "loss_of_balance", "fatigue"],
        "secondary": ["headache", "depression", "anxiety",
                      "muscle_weakness"],
        "optional":  ["visual_disturbances", "irritability", "nausea"],
        "samples":   100,
    },
    "Meningitis": {  # Viêm màng não
        "primary":   ["stiff_neck", "high_fever", "headache"],
        "secondary": ["nausea", "vomiting", "altered_sensorium",
                      "fatigue", "chills"],
        "optional":  ["visual_disturbances", "loss_of_balance",
                      "skin_rash"],
        "samples":   100,
    },

    # ── Bệnh xương khớp ──────────────────────────────────────
    "Gout": {  # Gút
        "primary":   ["joint_pain", "swelling_joints", "fatigue"],
        "secondary": ["knee_pain", "hip_joint_pain", "muscle_pain",
                      "fever"],
        "optional":  ["loss_of_appetite", "nausea", "chills"],
        "samples":   100,
    },
    "Osteoporosis": {  # Loãng xương
        "primary":   ["back_pain", "muscle_weakness", "fatigue"],
        "secondary": ["joint_pain", "neck_pain", "muscle_pain",
                      "movement_stiffness"],
        "optional":  ["loss_of_appetite", "weight_loss", "depression"],
        "samples":   100,
    },

    # ── Bệnh tim mạch ────────────────────────────────────────
    "Angina": {  # Đau thắt ngực
        "primary":   ["chest_pain", "fatigue", "breathlessness"],
        "secondary": ["sweating", "nausea", "dizziness",
                      "fast_heart_rate"],
        "optional":  ["anxiety", "muscle_pain", "headache"],
        "samples":   100,
    },

    # ── Bệnh thận ────────────────────────────────────────────
    "Kidney Stones": {  # Sỏi thận
        "primary":   ["abdominal_pain", "burning_micturition", "nausea"],
        "secondary": ["vomiting", "fatigue", "dark_urine",
                      "continuous_feel_of_urine"],
        "optional":  ["fever", "chills", "back_pain"],
        "samples":   100,
    },
    "Kidney Disease": {  # Bệnh thận mãn tính
        "primary":   ["fatigue", "swollen_legs", "loss_of_appetite"],
        "secondary": ["nausea", "dark_urine", "dehydration",
                      "muscle_weakness"],
        "optional":  ["headache", "breathlessness", "weight_loss"],
        "samples":   100,
    },
}

# ── Hàm sinh dữ liệu ─────────────────────────────────────────
def generate_samples(disease_name, config, symptom_cols, n_samples):
    rows     = []
    primary  = config["primary"]
    secondary= config["secondary"]
    optional = config["optional"]

    for _ in range(n_samples):
        symptoms  = list(primary)
        n_sec     = np.random.randint(2, min(5, len(secondary) + 1))
        symptoms += list(np.random.choice(secondary, n_sec, replace=False))
        if optional and np.random.random() > 0.4:
            n_opt = np.random.randint(1, min(3, len(optional) + 1))
            symptoms += list(np.random.choice(optional, n_opt, replace=False))

        symptoms = list(set(symptoms))
        np.random.shuffle(symptoms)

        row = {"Disease": disease_name}
        for i, col in enumerate(symptom_cols):
            row[col] = symptoms[i] if i < len(symptoms) else np.nan
        rows.append(row)

    return pd.DataFrame(rows)

# ── Sinh dữ liệu ─────────────────────────────────────────────
print("\n⏳ Đang sinh dữ liệu bổ sung...")
new_frames = []

for disease, config in NEW_DISEASES.items():
    df_new = generate_samples(disease, config, symptom_cols, config["samples"])
    new_frames.append(df_new)
    print(f"  ✅ {disease}: {config['samples']} mẫu")

df_new_all = pd.concat(new_frames, ignore_index=True)

# ── Merge tất cả ─────────────────────────────────────────────
df_final = pd.concat([df_original, df_new_all], ignore_index=True)
df_final  = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\n{'─'*50}")
print(f"📊 KẾT QUẢ:")
print(f"   Dataset cũ : {len(df_original)} mẫu | {df_original['Disease'].nunique()} bệnh")
print(f"   Thêm mới   : {len(df_new_all)} mẫu | {len(NEW_DISEASES)} bệnh")
print(f"   Tổng cộng  : {len(df_final)} mẫu | {df_final['Disease'].nunique()} bệnh")

df_final.to_csv('../data/disease_dataset_v2.csv', index=False)
print(f"\n✅ Đã lưu: data/disease_dataset_v2.csv")
print("\n👉 Tiếp theo sửa 02_Preprocessing.py:")
print("   disease_dataset_extended.csv → disease_dataset_v2.csv")
print("   Rồi chạy lại: 02 → 03 → 04")

