"""
========================================
BƯỚC 1: EDA - Khám phá & Phân tích dữ liệu
========================================
Chạy: python 01_EDA.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import os

os.makedirs('../results', exist_ok=True)

print("=" * 60)
print("  📊  EDA - PHÂN TÍCH DỮ LIỆU")
print("=" * 60)

# ── 1. Load data ─────────────────────────────────────────────
df = pd.read_csv('../data/disease_dataset.csv')

print(f"\n✅ Load thành công!")
print(f"   Số mẫu : {df.shape[0]}")
print(f"   Số cột : {df.shape[1]}")

# ── 2. Thống kê tổng quan ────────────────────────────────────
print(f"\n{'─'*40}")
print(f"📋 Tên các cột:")
print(list(df.columns))

print(f"\n📋 5 dòng đầu:")
print(df.head())

print(f"\n📋 Kiểm tra kiểu dữ liệu:")
print(df.dtypes)

print(f"\n📋 Missing values:")
missing = df.isnull().sum()
print(missing[missing > 0] if missing.sum() > 0 else "  → Không có missing values!")

# ── 3. Phân tích nhãn bệnh ───────────────────────────────────
print(f"\n{'─'*40}")
print(f"🦠 Số loại bệnh: {df['Disease'].nunique()}")
print(f"\n📊 Số mẫu mỗi bệnh:")
vc = df['Disease'].value_counts()
print(vc.to_string())

print(f"\n   Min : {vc.min()} mẫu ({vc.idxmin()})")
print(f"   Max : {vc.max()} mẫu ({vc.idxmax()})")
print(f"   Mean: {vc.mean():.1f} mẫu")

# ── 4. Phân tích triệu chứng ─────────────────────────────────
symptom_cols = [c for c in df.columns if c != 'Disease']
all_syms = []
for col in symptom_cols:
    all_syms.extend(df[col].dropna().tolist())
all_syms = [str(s).strip() for s in all_syms if str(s).strip() != 'nan']

sym_freq = pd.Series(all_syms).value_counts()
print(f"\n{'─'*40}")
print(f"🩺 Tổng số triệu chứng unique: {len(sym_freq)}")
print(f"\n📊 Top 15 triệu chứng phổ biến nhất:")
print(sym_freq.head(15).to_string())

# ── 5. Vẽ biểu đồ ───────────────────────────────────────────
fig = plt.figure(figsize=(20, 16))
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

# 5a. Phân bố bệnh
ax1 = fig.add_subplot(gs[0, :])
colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(vc)))
bars   = ax1.bar(range(len(vc)), vc.values, color=colors, edgecolor='white')
ax1.set_xticks(range(len(vc)))
ax1.set_xticklabels(vc.index, rotation=45, ha='right', fontsize=8)
ax1.set_title('Phân bố số mẫu theo loại bệnh', fontsize=14, fontweight='bold', pad=12)
ax1.set_ylabel('Số lượng mẫu')
ax1.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, vc.values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             str(val), ha='center', fontsize=7)

# 5b. Top 20 triệu chứng
ax2 = fig.add_subplot(gs[1, 0])
top20 = sym_freq.head(20)
ax2.barh(range(len(top20)), top20.values,
         color=plt.cm.cool(np.linspace(0.3, 0.8, len(top20))))
ax2.set_yticks(range(len(top20)))
ax2.set_yticklabels([s.replace('_', ' ') for s in top20.index], fontsize=9)
ax2.set_title('Top 20 triệu chứng phổ biến', fontsize=12, fontweight='bold')
ax2.set_xlabel('Số lần xuất hiện')
ax2.grid(axis='x', alpha=0.3)

# 5c. Số triệu chứng mỗi bệnh
ax3 = fig.add_subplot(gs[1, 1])
sym_per_disease = []
for disease in df['Disease'].unique():
    subset = df[df['Disease'] == disease]
    count  = sum(subset[c].notna().sum() for c in symptom_cols)
    sym_per_disease.append({'Disease': disease, 'Count': count // len(subset)})
spd_df = pd.DataFrame(sym_per_disease).sort_values('Count', ascending=True)
ax3.barh(spd_df['Disease'], spd_df['Count'], color='#48cae4')
ax3.set_title('Số triệu chứng TB mỗi bệnh', fontsize=12, fontweight='bold')
ax3.set_xlabel('Số triệu chứng trung bình')
ax3.tick_params(axis='y', labelsize=8)
ax3.grid(axis='x', alpha=0.3)

plt.suptitle('EDA - Phân tích Dataset Tư vấn Sức khỏe', fontsize=16, fontweight='bold', y=1.01)
plt.savefig('../results/01_EDA_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

print(f"\n✅ Đã lưu biểu đồ: results/01_EDA_analysis.png")
print("\n✅ EDA hoàn thành! Chạy tiếp: python 02_Preprocessing.py")
