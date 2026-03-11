"""
========================================
BƯỚC 3: TRAIN & SO SÁNH CÁC MÔ HÌNH
========================================
Chạy: python 03_Training.py
"""

import pandas as pd
import numpy  as np
import joblib
import time
import os

from sklearn.ensemble       import RandomForestClassifier, VotingClassifier
from sklearn.svm            import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics        import accuracy_score, f1_score
from xgboost                import XGBClassifier

os.makedirs('../results', exist_ok=True)

print("=" * 60)
print("  🚀  TRAIN V2 - TỐI ƯU HÓA")
print("=" * 60)

# ── Load ─────────────────────────────────────────────────────
X_train = joblib.load('../models/X_train.pkl')
X_test  = joblib.load('../models/X_test.pkl')
y_train = joblib.load('../models/y_train.pkl')
y_test  = joblib.load('../models/y_test.pkl')

print(f"\n✅ Train: {X_train.shape} | Test: {X_test.shape}")

# ── 1. Tìm tham số tốt nhất cho Random Forest ────────────────
print("\n" + "─"*50)
print("⏳ GridSearch - Tìm tham số tốt nhất cho Random Forest...")
print("   (Mất 3-5 phút)")

param_grid = {
    'n_estimators': [100, 200],
    'max_depth':    [None, 20],
    'min_samples_split': [2, 5],
}

rf_grid = GridSearchCV(
    RandomForestClassifier(random_state=42, n_jobs=-1),
    param_grid,
    cv           = 3,
    scoring      = 'f1_weighted',
    n_jobs       = -1,
    verbose      = 1,
)
rf_grid.fit(X_train, y_train)

best_rf     = rf_grid.best_estimator_
best_params = rf_grid.best_params_
print(f"\n✅ Tham số tốt nhất: {best_params}")

y_pred_rf = best_rf.predict(X_test)
acc_rf    = accuracy_score(y_test, y_pred_rf)
f1_rf     = f1_score(y_test, y_pred_rf, average='weighted')
print(f"   Accuracy: {acc_rf*100:.2f}% | F1: {f1_rf*100:.2f}%")

# ── 2. Cross-validation ──────────────────────────────────────
print("\n" + "─"*50)
print("⏳ Cross-validation 5-fold...")

cv_scores = cross_val_score(
    best_rf, X_train, y_train,
    cv=5, scoring='f1_weighted', n_jobs=-1
)
print(f"✅ CV Scores: {[f'{s*100:.1f}%' for s in cv_scores]}")
print(f"   Mean: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")

# ── 3. Ensemble Model (kết hợp nhiều model) ──────────────────
print("\n" + "─"*50)
print("⏳ Tạo Ensemble Model (Voting Classifier)...")
print("   Kết hợp: Random Forest + XGBoost + Neural Network")

ensemble = VotingClassifier(
    estimators=[
        ('rf',  best_rf),
        ('xgb', XGBClassifier(n_estimators=100, eval_metric='mlogloss',
                              random_state=42, n_jobs=-1)),
        ('mlp', MLPClassifier(hidden_layer_sizes=(256, 128),
                              max_iter=300, random_state=42)),
    ],
    voting  = 'soft',
    n_jobs  = -1,
)

start = time.time()
ensemble.fit(X_train, y_train)
elapsed = round(time.time() - start, 2)

y_pred_ens = ensemble.predict(X_test)
acc_ens    = accuracy_score(y_test, y_pred_ens)
f1_ens     = f1_score(y_test, y_pred_ens, average='weighted')
print(f"✅ Ensemble — Accuracy: {acc_ens*100:.2f}% | F1: {f1_ens*100:.2f}% | {elapsed}s")

# ── 4. Chọn model tốt nhất ───────────────────────────────────
print("\n" + "─"*50)
print("📊 So sánh:")
print(f"   Random Forest (tuned): {acc_rf*100:.2f}%")
print(f"   Ensemble:              {acc_ens*100:.2f}%")

if f1_ens >= f1_rf:
    final_model      = ensemble
    final_model_name = "Ensemble (RF+XGB+MLP)"
    print(f"\n🏆 Chọn: Ensemble")
else:
    final_model      = best_rf
    final_model_name = f"Random Forest (tuned: {best_params})"
    print(f"\n🏆 Chọn: Random Forest")

# ── 5. Lưu model ─────────────────────────────────────────────
joblib.dump(final_model, '../models/best_model.pkl',
            compress=('lz4', 3))   # Nén để load nhanh hơn

with open('../models/best_model_name.txt', 'w') as f:
    f.write(final_model_name)

# Lưu CV results
cv_df = pd.DataFrame({
    'Fold':    range(1, 6),
    'F1':      [f'{s*100:.2f}%' for s in cv_scores],
    'Mean':    [f'{cv_scores.mean()*100:.2f}%'] * 5,
    'Std':     [f'±{cv_scores.std()*100:.2f}%'] * 5,
})
cv_df.to_csv('../results/cross_validation.csv', index=False)

print(f"\n✅ Đã lưu model: {final_model_name}")
print("✅ Đã lưu: results/cross_validation.csv")
print("\n✅ Hoàn thành! Chạy tiếp: python 04_Evaluation.py")