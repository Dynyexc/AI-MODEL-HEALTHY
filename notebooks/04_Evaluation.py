"""
========================================
BƯỚC 4: ĐÁNH GIÁ & VẼ BIỂU ĐỒ
========================================
Chạy: python 04_Evaluation.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import joblib
import os
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_curve, auc
)
from sklearn.preprocessing import label_binarize

os.makedirs('../results', exist_ok=True)

print("=" * 60)
print("  📈  ĐÁNH GIÁ MÔ HÌNH")
print("=" * 60)

# ── Load ─────────────────────────────────────────────────────
model      = joblib.load('../models/best_model.pkl')
X_test     = joblib.load('../models/X_test.pkl')
y_test     = joblib.load('../models/y_test.pkl')
le         = joblib.load('../models/label_encoder.pkl')
df_cmp     = pd.read_csv('../results/model_comparison.csv', index_col=0)

with open('../models/best_model_name.txt') as f:
    best_name = f.read().strip()

print(f"\n✅ Model tốt nhất: {best_name}")

y_pred = model.predict(X_test)

# ── 1. Classification Report ────────────────────────────────
print(f"\n{'─'*50}")
print("📋 Classification Report (chi tiết từng bệnh):")
print(classification_report(
    y_test, y_pred,
    target_names=le.classes_,
    zero_division=0
))

# ── 2. Lưu report ra file ────────────────────────────────────
report = classification_report(
    y_test, y_pred,
    target_names=le.classes_,
    zero_division=0,
    output_dict=True
)
pd.DataFrame(report).transpose().to_csv('../results/classification_report.csv')
print("✅ Đã lưu: results/classification_report.csv")

# ── 3. Vẽ biểu đồ ───────────────────────────────────────────
fig = plt.figure(figsize=(22, 18))
gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.5, wspace=0.35)

# ---- Biểu đồ 1: So sánh Accuracy & F1 ----------------------
ax1 = fig.add_subplot(gs[0, 0])
x   = np.arange(len(df_cmp))
w   = 0.35
b1  = ax1.bar(x - w/2, df_cmp['Accuracy'], w,
              label='Accuracy', color='#0077b6', alpha=0.85)
b2  = ax1.bar(x + w/2, df_cmp['F1-Score'],  w,
              label='F1-Score',  color='#00B4D8', alpha=0.85)
ax1.set_xticks(x)
ax1.set_xticklabels(df_cmp['Model'], rotation=30, ha='right', fontsize=9)
ax1.set_ylim(70, 105)
ax1.set_title('Accuracy vs F1-Score', fontweight='bold', fontsize=13)
ax1.legend()
ax1.grid(axis='y', alpha=0.3)
for b, v in zip(b1, df_cmp['Accuracy']):
    ax1.text(b.get_x() + b.get_width()/2, v + 0.3, f'{v:.1f}', ha='center', fontsize=8)
for b, v in zip(b2, df_cmp['F1-Score']):
    ax1.text(b.get_x() + b.get_width()/2, v + 0.3, f'{v:.1f}', ha='center', fontsize=8)

# ---- Biểu đồ 2: Precision / Recall / F1 --------------------
ax2 = fig.add_subplot(gs[0, 1])
metrics = ['Precision', 'Recall', 'F1-Score']
colors  = ['#0077b6', '#00B4D8', '#48cae4']
bw      = 0.25
for j, (m, c) in enumerate(zip(metrics, colors)):
    ax2.bar(x + j*bw, df_cmp[m], bw, label=m, color=c, alpha=0.85)
ax2.set_xticks(x + bw)
ax2.set_xticklabels(df_cmp['Model'], rotation=30, ha='right', fontsize=9)
ax2.set_ylim(70, 108)
ax2.set_title('Precision / Recall / F1-Score', fontweight='bold', fontsize=13)
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

# ---- Biểu đồ 3: Thời gian training -------------------------
ax3 = fig.add_subplot(gs[1, 0])
colors_time = ['#2ecc71' if t < 5 else '#f39c12' if t < 20 else '#e74c3c'
               for t in df_cmp['Time (s)']]
bars = ax3.barh(df_cmp['Model'], df_cmp['Time (s)'],
                color=colors_time, edgecolor='white')
ax3.set_title('⏱ Thời gian Training', fontweight='bold', fontsize=13)
ax3.set_xlabel('Giây')
for bar, val in zip(bars, df_cmp['Time (s)']):
    ax3.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
             f'{val}s', va='center', fontsize=10)
ax3.grid(axis='x', alpha=0.3)

# ---- Biểu đồ 4: Radar chart tổng hợp -----------------------
ax4  = fig.add_subplot(gs[1, 1], polar=True)
cats = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
N    = len(cats)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

# Vẽ 3 model tốt nhất
top3_colors = ['#0077b6', '#00B4D8', '#48cae4']
for idx, (_, row) in enumerate(df_cmp.head(3).iterrows()):
    vals   = [row[c] for c in cats]
    vals  += vals[:1]
    scaled = [(v - 70) / 30 for v in vals]
    ax4.plot(angles, scaled, 'o-', linewidth=2,
             color=top3_colors[idx], label=row['Model'])
    ax4.fill(angles, scaled, alpha=0.1, color=top3_colors[idx])

ax4.set_xticks(angles[:-1])
ax4.set_xticklabels(cats, fontsize=11)
ax4.set_yticklabels([])
ax4.set_title('Radar Chart - Top 3 Models', fontweight='bold', fontsize=13, pad=20)
ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)

# ---- Biểu đồ 5: Confusion Matrix ---------------------------
ax5 = fig.add_subplot(gs[2, :])
cm  = confusion_matrix(y_test, y_pred)

# Lấy top 15 bệnh có nhiều mẫu test nhất
test_counts  = np.bincount(y_test)
top15_idx    = np.argsort(test_counts)[-15:]
cm_top15     = cm[np.ix_(top15_idx, top15_idx)]
labels_top15 = le.classes_[top15_idx]

sns.heatmap(
    cm_top15,
    ax          = ax5,
    cmap        = 'Blues',
    fmt         = 'd',
    linewidths  = 0.5,
    xticklabels = labels_top15,
    yticklabels = labels_top15,
    annot       = True,
    annot_kws   = {'size': 9}
)
ax5.set_title(f'Confusion Matrix - {best_name} (Top 15 bệnh)',
              fontweight='bold', fontsize=13)
ax5.set_xlabel('Predicted', fontsize=11)
ax5.set_ylabel('Actual',    fontsize=11)
ax5.tick_params(axis='x', rotation=45, labelsize=8)
ax5.tick_params(axis='y', rotation=0,  labelsize=8)

plt.suptitle(
    f'Kết quả Đánh giá AI Model - Hệ thống Tư vấn Sức khỏe\nModel tốt nhất: {best_name}',
    fontsize=15, fontweight='bold', y=1.01
)

plt.savefig('../results/02_evaluation_charts.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Đã lưu: results/02_evaluation_charts.png")

# ── 4. In tóm tắt kết quả ───────────────────────────────────
print(f"\n{'='*60}")
print("  🏆  TÓM TẮT KẾT QUẢ")
print(f"{'='*60}")
best_row = df_cmp.iloc[0]
print(f"\n  Model tốt nhất : {best_name}")
print(f"  Accuracy       : {best_row['Accuracy']}%")
print(f"  Precision      : {best_row['Precision']}%")
print(f"  Recall         : {best_row['Recall']}%")
print(f"  F1-Score       : {best_row['F1-Score']}%")
print(f"  Train time     : {best_row['Time (s)']}s")

print(f"\n{'─'*60}")
print("  📁  Files đã tạo:")
print("     models/best_model.pkl")
print("     models/label_encoder.pkl")
print("     models/symptoms_list.pkl")
print("     results/model_comparison.csv")
print("     results/classification_report.csv")
print("     results/01_EDA_analysis.png")
print("     results/02_evaluation_charts.png")

print("\n✅ Đánh giá hoàn thành!")
print("\n Bước tiếp theo chạy DeepLearning: python 05_DeepLearning.py" )
