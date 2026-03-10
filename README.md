# 🤖 AI Model - Hệ thống Tư vấn Sức khỏe

## Cấu trúc thư mục
```
ai-model/
├── data/
│   └── disease_dataset.csv       ← Tải từ Kaggle (bước 1)
├── notebooks/
│   ├── 01_EDA.py                 ← Phân tích & trực quan hóa dữ liệu
│   ├── 02_Preprocessing.py       ← One-Hot + SMOTE + lưu pkl
│   ├── 03_Training.py            ← Train 7 mô hình + so sánh
│   └── 04_Evaluation.py          ← Biểu đồ + Confusion Matrix
├── models/                       ← Tự tạo sau khi chạy
│   ├── best_model.pkl
│   ├── label_encoder.pkl
│   ├── symptoms_list.pkl
│   └── best_model_name.txt
├── results/                      ← Tự tạo sau khi chạy
│   ├── model_comparison.csv      ← Bảng so sánh → đưa vào báo cáo
│   ├── classification_report.csv
│   ├── 01_EDA_analysis.png
│   └── 02_evaluation_charts.png
├── ai_api/
│   └── main.py                   ← FastAPI server
└── requirements.txt
```

---

## BƯỚC 1 — Tải Dataset

Link: https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset

Tải `dataset.csv` → đổi tên → `disease_dataset.csv` → đặt vào `data/`

---

## BƯỚC 2 — Cài thư viện

```bash
pip install -r requirements.txt
```

---

## BƯỚC 3 — Chạy theo thứ tự

```bash
cd notebooks

python 01_EDA.py            # ~30 giây
python 02_Preprocessing.py  # ~2 phút (SMOTE)
python 03_Training.py       # ~5-15 phút
python 04_Evaluation.py     # ~1 phút
```

---

## BƯỚC 4 — Chạy API Server

```bash
cd ai_api
uvicorn main:app --reload --port 8000
```

Mở trình duyệt: **http://localhost:8000/docs**

---

## Test nhanh bằng curl

```bash
# Kiểm tra server
curl http://localhost:8000/health

# Lấy danh sách triệu chứng
curl http://localhost:8000/symptoms

# Dự đoán bệnh
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]}'
```

---

## Kết quả mong đợi

| Model | Accuracy | F1-Score | Thời gian |
|-------|----------|----------|-----------|
| Random Forest | ~98% | ~98% | ~2s |
| XGBoost | ~97% | ~97% | ~3s |
| Neural Network | ~96% | ~96% | ~30s |
| SVM | ~95% | ~95% | ~10s |
| KNN | ~93% | ~93% | ~1s |
| Decision Tree | ~91% | ~91% | ~1s |
| Naive Bayes | ~85% | ~85% | <1s |

---

## Lưu ý

- `results/model_comparison.csv` → dùng làm bảng trong báo cáo
- `results/02_evaluation_charts.png` → dùng làm hình trong báo cáo
- API server phải chạy **trước** khi khởi động Backend Node.js


#### Cách hạ verson xuống của python 
- https://www.python.org/downloads/release/python-3119/  (Kéo xuống chọn  Windows Install 64-bit) nhớ SAU KHI CÀI XONG TÍCH VÀO Ô ATH PATH 
- TIẾP TỤC VÀO VS CODE XÓA BẢN MỚI BẰNG CÁCH

START - Add or remove programs - Python 3.13 -> UNISTALL 
App execution aliases -( python.exe python3.exe) - OFF 

Cài lại pip cho Python 3.11 
py -3.11 -m ensurepip --upgrade
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip --version

py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt