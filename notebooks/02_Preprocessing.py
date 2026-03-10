"""
========================================
BƯỚC 2: TIỀN XỬ LÝ DỮ LIỆU
========================================
Chạy: python 02_Preprocessing.py
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

os.makedirs('../models', exist_ok=True)

print("=" * 60)
print("  🧹  TIỀN XỬ LÝ DỮ LIỆU")
print("=" * 60)

# ── 1. Load ──────────────────────────────────────────────────
df = pd.read_csv('../data/disease_dataset.csv')
print(f"\n✅ Loaded: {df.shape[0]} mẫu, {df.shape[1]} cột")

symptom_cols = [c for c in df.columns if c != 'Disease']

# ── 2. Thu thập triệu chứng unique ──────────────────────────
all_symptoms = set()
for col in symptom_cols:
    for val in df[col].dropna():
        cleaned = str(val).strip()
        if cleaned and cleaned != 'nan':
            all_symptoms.add(cleaned)

all_symptoms = sorted(list(all_symptoms))
print(f"✅ Tổng số triệu chứng unique: {len(all_symptoms)}")

# ── 3. One-Hot Encoding ──────────────────────────────────────
print("\n⏳ Đang tạo ma trận One-Hot...")

symptom_index = {s: i for i, s in enumerate(all_symptoms)}
X = np.zeros((len(df), len(all_symptoms)), dtype=np.int8)

for row_idx, (_, row) in enumerate(df.iterrows()):
    for col in symptom_cols:
        val = str(row[col]).strip() if pd.notna(row[col]) else ''
        if val in symptom_index:
            X[row_idx, symptom_index[val]] = 1

    if row_idx % 1000 == 0:
        print(f"  Processed {row_idx}/{len(df)} rows...")

X_df = pd.DataFrame(X, columns=all_symptoms)
print(f"✅ Ma trận X: {X_df.shape}")

# Kiểm tra
zeros = (X_df.sum(axis=1) == 0).sum()
print(f"   Số dòng không có triệu chứng nào: {zeros}")

# ── 4. Label Encoding ────────────────────────────────────────
le = LabelEncoder()
y  = le.fit_transform(df['Disease'])

print(f"\n✅ Số lớp bệnh: {len(le.classes_)}")
print(f"   Danh sách: {list(le.classes_)}")

# ── 5. Train / Test Split ────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_df, y,
    test_size    = 0.2,
    random_state = 42,
    stratify     = y       # Đảm bảo tỉ lệ đều nhau
)
print(f"\n✅ Train: {X_train.shape[0]} mẫu")
print(f"   Test : {X_test.shape[0]} mẫu")

# ── 6. SMOTE - Cân bằng dữ liệu ─────────────────────────────
print("\n⏳ Đang áp dụng SMOTE (cân bằng dữ liệu)...")
print("   (Bước này mất ~1-2 phút)")

smote = SMOTE(random_state=42, k_neighbors=3)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)

print(f"✅ Trước SMOTE: {X_train.shape[0]} mẫu")
print(f"   Sau  SMOTE : {X_train_bal.shape[0]} mẫu")

# Kiểm tra cân bằng sau SMOTE
unique, counts = np.unique(y_train_bal, return_counts=True)
print(f"   Số mẫu mỗi lớp: {counts[0]} (đều nhau)")

# ── 7. Lưu ───────────────────────────────────────────────────
print("\n⏳ Đang lưu dữ liệu...")
joblib.dump(X_train_bal,  '../models/X_train.pkl')
joblib.dump(X_test,       '../models/X_test.pkl')
joblib.dump(y_train_bal,  '../models/y_train.pkl')
joblib.dump(y_test,       '../models/y_test.pkl')
joblib.dump(le,           '../models/label_encoder.pkl')
joblib.dump(all_symptoms, '../models/symptoms_list.pkl')

print("✅ Đã lưu vào thư mục models/:")
print("   - X_train.pkl, X_test.pkl")
print("   - y_train.pkl, y_test.pkl")
print("   - label_encoder.pkl")
print("   - symptoms_list.pkl")

print("\n✅ Tiền xử lý hoàn thành! Chạy tiếp: python 03_Training.py")
