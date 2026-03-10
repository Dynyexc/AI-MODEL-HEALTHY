"""
========================================
BƯỚC 3: TRAIN & SO SÁNH CÁC MÔ HÌNH
========================================
Chạy: python 03_Training.py
"""

import pandas as pd
import numpy as np
import joblib
import time
import os

from sklearn.ensemble      import RandomForestClassifier
from sklearn.svm           import SVC
from sklearn.naive_bayes   import GaussianNB
from sklearn.neighbors     import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree          import DecisionTreeClassifier
from xgboost               import XGBClassifier
from sklearn.metrics       import (
    accuracy_score, precision_score,
    recall_score, f1_score
)

os.makedirs('../results', exist_ok=True)

print("=" * 60)
print("  🏋️   TRAIN CÁC MÔ HÌNH")
print("=" * 60)

# ── Load dữ liệu ─────────────────────────────────────────────
X_train = joblib.load('../models/X_train.pkl')
X_test  = joblib.load('../models/X_test.pkl')
y_train = joblib.load('../models/y_train.pkl')
y_test  = joblib.load('../models/y_test.pkl')

print(f"\n✅ Dữ liệu: Train {X_train.shape} | Test {X_test.shape}")
print(f"   Số lớp: {len(np.unique(y_train))}")

# ── Định nghĩa các mô hình ───────────────────────────────────
models = {
    "Decision Tree":  DecisionTreeClassifier(
        max_depth=20,
        random_state=42
    ),
    "Random Forest":  RandomForestClassifier(
        n_estimators=100,
        max_depth=None,
        n_jobs=-1,
        random_state=42
    ),
    "SVM":            SVC(
        kernel='rbf',
        C=10,
        probability=True,
        random_state=42
    ),
    "Naive Bayes":    GaussianNB(),
    "KNN":            KNeighborsClassifier(
        n_neighbors=5,
        metric='euclidean',
        n_jobs=-1
    ),
    "Neural Network": MLPClassifier(
        hidden_layer_sizes=(256, 128, 64),
        activation='relu',
        max_iter=500,
        early_stopping=True,
        random_state=42
    ),
    "XGBoost":        XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        eval_metric='mlogloss',
        use_label_encoder=False,
        n_jobs=-1,
        random_state=42
    ),
}

# ── Train từng mô hình ───────────────────────────────────────
results = []
trained = {}

for name, model in models.items():
    print(f"\n{'─'*50}")
    print(f"⏳ Training: {name}...")
    start = time.time()

    model.fit(X_train, y_train)
    elapsed = round(time.time() - start, 2)
    trained[name] = model

    y_pred = model.predict(X_test)

    acc  = accuracy_score (y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec  = recall_score   (y_test, y_pred, average='weighted', zero_division=0)
    f1   = f1_score       (y_test, y_pred, average='weighted', zero_division=0)

    results.append({
        'Model':      name,
        'Accuracy':   round(acc  * 100, 2),
        'Precision':  round(prec * 100, 2),
        'Recall':     round(rec  * 100, 2),
        'F1-Score':   round(f1   * 100, 2),
        'Time (s)':   elapsed,
    })

    print(f"  ✅ Accuracy : {acc*100:.2f}%")
    print(f"     F1-Score : {f1*100:.2f}%")
    print(f"     Time     : {elapsed}s")

# ── Bảng kết quả ────────────────────────────────────────────
df_results = pd.DataFrame(results).sort_values('F1-Score', ascending=False)
df_results = df_results.reset_index(drop=True)
df_results.index += 1  # Bắt đầu từ 1

print(f"\n{'='*60}")
print("  📊  BẢNG SO SÁNH CÁC MÔ HÌNH")
print(f"{'='*60}")
print(df_results.to_string())

df_results.to_csv('../results/model_comparison.csv', index=True)
print(f"\n✅ Đã lưu: results/model_comparison.csv")

# ── Lưu model tốt nhất ──────────────────────────────────────
best_name  = df_results.iloc[0]['Model']
best_model = trained[best_name]
joblib.dump(best_model, '../models/best_model.pkl')

print(f"\n🏆 Model tốt nhất: {best_name}")
print(f"   Accuracy : {df_results.iloc[0]['Accuracy']}%")
print(f"   F1-Score : {df_results.iloc[0]['F1-Score']}%")
print(f"\n✅ Đã lưu: models/best_model.pkl")

# Lưu tên model tốt nhất để dùng sau
with open('../models/best_model_name.txt', 'w') as f:
    f.write(best_name)

print("\n✅ Training hoàn thành! Chạy tiếp: python 04_Evaluation.py")
