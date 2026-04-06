"""
========================================
DEEP LEARNING MODEL - PyTorch
========================================
Cải tiến 1: Neural Network sâu hơn với PyTorch
Chạy: python 05_DeepLearning.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
import os

os.makedirs('../models', exist_ok=True)
os.makedirs('../results', exist_ok=True)

print("=" * 60)
print("  🧠  DEEP LEARNING - PyTorch")
print("=" * 60)

# ── Load dữ liệu ─────────────────────────────────────────────
X_train = joblib.load('../models/X_train.pkl')
X_test  = joblib.load('../models/X_test.pkl')
y_train = joblib.load('../models/y_train.pkl')
y_test  = joblib.load('../models/y_test.pkl')
le      = joblib.load('../models/label_encoder.pkl')

n_features = X_train.shape[1]
n_classes  = len(le.classes_)

print(f"\n✅ Input: {n_features} triệu chứng → {n_classes} bệnh")
print(f"   Train: {len(X_train)} | Test: {len(X_test)}")

# ── Chuyển sang Tensor ───────────────────────────────────────
X_train_t = torch.FloatTensor(X_train.values if hasattr(X_train, 'values') else X_train)
X_test_t  = torch.FloatTensor(X_test.values  if hasattr(X_test,  'values') else X_test)
y_train_t = torch.LongTensor(y_train)
y_test_t  = torch.LongTensor(y_test)

train_ds = TensorDataset(X_train_t, y_train_t)
train_dl = DataLoader(train_ds, batch_size=64, shuffle=True)

# ── Kiến trúc Deep Neural Network ───────────────────────────
class HealthDNN(nn.Module):
    def __init__(self, n_input, n_classes):
        super().__init__()
        self.network = nn.Sequential(
            # Layer 1
            nn.Linear(n_input, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),

            # Layer 2
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),

            # Layer 3
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),

            # Layer 4
            nn.Linear(128, 64),
            nn.ReLU(),

            # Output
            nn.Linear(64, n_classes),
        )

    def forward(self, x):
        return self.network(x)

# ── Train ────────────────────────────────────────────────────
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"\n⚙️  Device: {device}")

model     = HealthDNN(n_features, n_classes).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.5)

print(f"\n⏳ Training Deep Neural Network...")
print(f"   Kiến trúc: {n_features} → 512 → 256 → 128 → 64 → {n_classes}")

EPOCHS   = 80
history  = []
best_acc = 0

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    for xb, yb in train_dl:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()
        out  = model(xb)
        loss = criterion(out, yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    scheduler.step()

    # Đánh giá mỗi 10 epoch
    if (epoch + 1) % 10 == 0:
        model.eval()
        with torch.no_grad():
            out_test = model(X_test_t.to(device))
            preds    = out_test.argmax(dim=1).cpu().numpy()
            acc      = accuracy_score(y_test, preds)
            f1       = f1_score(y_test, preds, average='weighted')

        history.append({
            'epoch': epoch + 1,
            'loss':  round(total_loss / len(train_dl), 4),
            'acc':   round(acc * 100, 2),
            'f1':    round(f1 * 100, 2),
        })

        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), '../models/dnn_best.pt')

        print(f"  Epoch {epoch+1:3d}/{EPOCHS} | Loss: {total_loss/len(train_dl):.4f} | Acc: {acc*100:.2f}% | F1: {f1*100:.2f}%")

# ── Kết quả cuối ────────────────────────────────────────────
model.load_state_dict(torch.load('../models/dnn_best.pt'))
model.eval()
with torch.no_grad():
    out_final = model(X_test_t.to(device))
    preds     = out_final.argmax(dim=1).cpu().numpy()
    final_acc = accuracy_score(y_test, preds)
    final_f1  = f1_score(y_test, preds, average='weighted')

print(f"\n{'─'*50}")
print(f"🏆 Kết quả DNN tốt nhất:")
print(f"   Accuracy : {final_acc*100:.2f}%")
print(f"   F1-Score : {final_f1*100:.2f}%")

# Lưu lịch sử training
pd.DataFrame(history).to_csv('../results/dnn_training_history.csv', index=False)

# Lưu model config để load sau
torch.save({
    'model_state': model.state_dict(),
    'n_features':  n_features,
    'n_classes':   n_classes,
}, '../models/dnn_full.pt')

print(f"\n✅ Đã lưu: models/dnn_full.pt")
print(f"✅ Đã lưu: results/dnn_training_history.csv")
print(f"\n👉 Dùng DNN trong API: thêm load_dnn=True vào main_v2.py")
