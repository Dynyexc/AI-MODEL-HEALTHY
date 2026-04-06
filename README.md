# 🤖 AI Model - Hệ thống Tư vấn Sức khỏe



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

python 01_EDA.py            
python extend_dataset.py
python 02_Preprocessing.py  
python 03_Training.py      = NẾU BỊ LỖI THÌ CÀI THÊM (pip install lz4 --break-system-packages)
python 04_Evaluation.py     
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

# Version 
pip install torch --break-system-packages
pip install shap networkx reportlab --break-system-packages

## BƯỚC 5 Thêm dữ liệu về bệnh bằng cách
- Mở file extend_dataset.py, tìm phần VIETNAM_DISEASES và thêm vào cuối 

## Cách đẩy code nhánh riêng của mình 
git checkout -b duy (tên tùy ý)
git add .
git commit -m "update AI medical model"
git push --set-upstream origin duy 

## cách lấy code từ máy khách 

git clone <repo>
cd AI-Model-Healthy
git checkout -b Duy origin/Duy

##Natural Language Processing (NLP) là lĩnh vực trong AI giúp máy tính hiểu, 
# phân tích và xử lý ngôn ngữ tự nhiên của con người như tiếng Việt, tiếng Anh…'
# Trong phần này, chúng ta sẽ xây dựng một mô hình Deep Learning để dự đoán bệnh dựa trên triệu chứng.

#Threshold = ngưỡng quyết định để AI chấp nhận hoặc từ chối kết quả. 
# Độ giống (Similarity)	Threshold	Kết quả
#0.85	0.80	Chấp nhận
#0.60	0.80	Từ chối

# Người	Tuổi dự đoán	Giới tính
#Người A	25	Nam
#Người B	32	Nữ
#(Age / Gender) Là thuộc tính mà AI dự đoán từ khuôn mặt.


GET  /              → Kiểm tra server
GET  /health        → Trạng thái model
GET  /symptoms      → Danh sách triệu chứng
GET  /diseases      → Danh sách bệnh
POST /predict               → Dự đoán → trả JSON
POST /smart-predict         → NLP + tuổi/giới tính → trả JSON
POST /predict-dnn           → Dự đoán bằng Deep Learning → trả JSON
POST /predict-and-report ⭐ → Dự đoán → trả PDF tải về luôn
POST /compare       → So sánh 2 bộ triệu chứng
POST /chat/start    → Bắt đầu chatbot
POST /chat/reply    → Trả lời chatbot
GET  /history       → Lịch sử dự đoán
GET  /stats         → Thống kê bệnh phổ biến