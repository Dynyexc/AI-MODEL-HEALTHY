"""
========================================
AUTO DIAGNOSIS REPORT - Font Times New Roman
========================================
Chạy: python 07_PDF_Report.py
"""

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai_api'))
from vietnamese_dict import to_vietnamese_disease, to_vietnamese_symptom
from datetime import datetime

def generate_pdf_report(prediction_data: dict, output_path: str = None) -> str:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable)
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        return "Cài reportlab: pip install reportlab --break-system-packages"

    # ── Đăng ký font Times New Roman ─────────────────────────
    FONT_DIR = "C:/Windows/Fonts"
    fonts = {
        "TNR":       os.path.join(FONT_DIR, "times.ttf"),
        "TNR-Bold":  os.path.join(FONT_DIR, "timesbd.ttf"),
        "TNR-Italic":os.path.join(FONT_DIR, "timesi.ttf"),
    }

    for name, path in fonts.items():
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
            print(f"✅ Font loaded: {name}")
        else:
            print(f"⚠️  Font không tìm thấy: {path}")

    # Fallback nếu không có Times New Roman
    try:
        pdfmetrics.getFont("TNR")
        FONT_NORMAL = "TNR"
        FONT_BOLD   = "TNR-Bold"
        FONT_ITALIC = "TNR-Italic"
    except:
        FONT_NORMAL = "Helvetica"
        FONT_BOLD   = "Helvetica-Bold"
        FONT_ITALIC = "Helvetica-Oblique"
        print("⚠️  Dùng Helvetica thay thế")

    if not output_path:
        ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"../results/diagnosis_report_{ts}.pdf"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc    = SimpleDocTemplate(output_path, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
    story  = []

    # ── Màu sắc ──────────────────────────────────────────────
    PRIMARY  = colors.HexColor('#667eea')
    DANGER   = colors.HexColor('#e53e3e')
    WARNING  = colors.HexColor('#dd6b20')
    SUCCESS  = colors.HexColor('#38a169')
    LIGHT_BG = colors.HexColor('#f7f8ff')

    # ── Styles dùng Times New Roman ──────────────────────────
    title_style = ParagraphStyle('Title',
                    fontName=FONT_BOLD, fontSize=20,
                    textColor=PRIMARY, spaceAfter=6, alignment=1)

    sub_style   = ParagraphStyle('Sub',
                    fontName=FONT_ITALIC, fontSize=12,
                    textColor=colors.grey, alignment=1, spaceAfter=2)

    h1_style    = ParagraphStyle('H1',
                    fontName=FONT_BOLD, fontSize=14,
                    textColor=PRIMARY, spaceAfter=4, spaceBefore=8)

    h2_style    = ParagraphStyle('H2',
                    fontName=FONT_BOLD, fontSize=12,
                    textColor=colors.HexColor('#4a5568'),
                    spaceAfter=3, spaceBefore=6)

    body_style  = ParagraphStyle('Body',
                    fontName=FONT_NORMAL, fontSize=11,
                    spaceAfter=4, leading=18)

    small_style = ParagraphStyle('Small',
                    fontName=FONT_NORMAL, fontSize=9,
                    textColor=colors.grey, spaceAfter=2)

    bold_style  = ParagraphStyle('Bold',
                    fontName=FONT_BOLD, fontSize=11, spaceAfter=4)

    disc_style  = ParagraphStyle('Disc',
                    fontName=FONT_ITALIC, fontSize=9,
                    textColor=DANGER,
                    borderColor=DANGER, borderWidth=1,
                    borderPadding=6,
                    backColor=colors.HexColor('#fff5f5'))

    footer_style= ParagraphStyle('Footer',
                    fontName=FONT_ITALIC, fontSize=8,
                    textColor=colors.grey, alignment=1)

    # ════════════════════════════════════════════════════════
    # HEADER
    # ════════════════════════════════════════════════════════
    story.append(Paragraph("HỆ THỐNG TƯ VẤN SỨC KHỎE AI", title_style))
    story.append(Paragraph("BÁO CÁO CHẨN ĐOÁN TỰ ĐỘNG", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
    story.append(Spacer(1, 0.3*cm))

    # Thông tin báo cáo
    now      = datetime.now()
    info_data = [
        ["Ngày tạo báo cáo:", now.strftime("%d/%m/%Y %H:%M:%S"),
         "Mã báo cáo:",       f"RPT-{now.strftime('%Y%m%d%H%M%S')}"],
        ["Phiên bản AI:",     "v2.0 (Ensemble RF+XGB+DNN)",
         "Độ chính xác:",     "99.66%"],
    ]
    info_table = Table(info_data, colWidths=[4*cm, 7*cm, 3.5*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (-1,-1), FONT_NORMAL),
        ('FONTNAME',     (1,0), (1,-1),  FONT_BOLD),
        ('FONTNAME',     (3,0), (3,-1),  FONT_BOLD),
        ('FONTNAME',     (0,0), (0,-1),  FONT_ITALIC),
        ('FONTNAME',     (2,0), (2,-1),  FONT_ITALIC),
        ('FONTSIZE',     (0,0), (-1,-1), 10),
        ('TEXTCOLOR',    (0,0), (0,-1),  colors.grey),
        ('TEXTCOLOR',    (2,0), (2,-1),  colors.grey),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))

    # ════════════════════════════════════════════════════════
    # THÔNG TIN BỆNH NHÂN
    # ════════════════════════════════════════════════════════
    patient = prediction_data.get("patient", {})
    if patient:
        story.append(Paragraph("THÔNG TIN BỆNH NHÂN", h1_style))
        p_data = [
            ["Họ tên:", patient.get("name", "---"),
             "Tuổi:",   str(patient.get("age", "---"))],
            ["Giới tính:",
             "Nam" if patient.get("gender") == "male" else
             "Nữ"  if patient.get("gender") == "female" else "---",
             "Ngày khám:", now.strftime("%d/%m/%Y")],
        ]
        p_table = Table(p_data, colWidths=[3.5*cm, 7*cm, 2.5*cm, 5.5*cm])
        p_table.setStyle(TableStyle([
            ('FONTNAME',  (0,0), (-1,-1), FONT_NORMAL),
            ('FONTNAME',  (0,0), (0,-1),  FONT_BOLD),
            ('FONTNAME',  (2,0), (2,-1),  FONT_BOLD),
            ('FONTSIZE',  (0,0), (-1,-1), 11),
            ('BACKGROUND',(0,0), (-1,-1), LIGHT_BG),
            ('GRID',      (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING',   (0,0), (-1,-1), 7),
        ]))
        story.append(p_table)
        story.append(Spacer(1, 0.4*cm))

    # ════════════════════════════════════════════════════════
    # TRIỆU CHỨNG ĐÃ NHẬP
    # ════════════════════════════════════════════════════════
    story.append(Paragraph("TRIỆU CHỨNG ĐÃ NHẬP", h1_style))
    symptoms = prediction_data.get("symptoms", [])
    sym_vi   = [to_vietnamese_symptom(s) for s in symptoms]
    story.append(Paragraph(f"Tổng số: {len(symptoms)} triệu chứng", small_style))
    story.append(Paragraph(" | ".join(sym_vi), body_style))
    story.append(Spacer(1, 0.4*cm))

    # ════════════════════════════════════════════════════════
    # KẾT QUẢ CHẨN ĐOÁN CHÍNH
    # ════════════════════════════════════════════════════════
    story.append(Paragraph("KẾT QUẢ CHẨN ĐOÁN AI", h1_style))

    disease_vi = prediction_data.get("disease_vi", "---")
    disease_en = prediction_data.get("disease_en", "---")
    confidence = prediction_data.get("confidence", 0)
    severity   = prediction_data.get("severity",   "---")
    specialty  = prediction_data.get("specialty",  "---")

    sev_color = DANGER  if "Khẩn" in severity or "Khan" in severity \
           else WARNING if "Nghiêm" in severity or "Nghiem" in severity \
           else colors.HexColor('#d69e2e') if "dõi" in severity \
           else SUCCESS

    main_data = [
        ["CHẨN ĐOÁN CHÍNH", disease_vi],
        ["Tên tiếng Anh",   disease_en],
        ["Độ tin cậy AI",   f"{confidence:.1f}%"],
        ["Mức độ",          severity],
        ["Chuyên khoa",     specialty],
    ]
    main_table = Table(main_data, colWidths=[5*cm, 13.5*cm])
    main_table.setStyle(TableStyle([
        ('FONTNAME',      (0,0), (-1,-1), FONT_NORMAL),
        ('FONTNAME',      (0,0), (0,-1),  FONT_BOLD),
        ('FONTNAME',      (1,0), (1,0),   FONT_BOLD),
        ('FONTSIZE',      (0,0), (-1,-1), 11),
        ('FONTSIZE',      (1,0), (1,0),   13),
        ('TEXTCOLOR',     (1,0), (1,0),   PRIMARY),
        ('TEXTCOLOR',     (1,3), (1,3),   sev_color),
        ('BACKGROUND',    (0,0), (-1,-1), LIGHT_BG),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [LIGHT_BG, colors.white]),
        ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING',       (0,0), (-1,-1), 8),
    ]))
    story.append(main_table)
    story.append(Spacer(1, 0.4*cm))

    # ════════════════════════════════════════════════════════
    # TOP 3 DỰ ĐOÁN
    # ════════════════════════════════════════════════════════
    top3 = prediction_data.get("top3", [])
    if top3:
        story.append(Paragraph("TOP 3 KẾT QUẢ DỰ ĐOÁN", h2_style))
        top3_data = [["#", "Tên bệnh (Tiếng Việt)", "Tên tiếng Anh", "Độ tin cậy"]]
        for i, d in enumerate(top3, 1):
            top3_data.append([
                str(i),
                d.get("disease_vi", "---"),
                d.get("disease_en", "---"),
                f"{d.get('confidence', 0):.1f}%",
            ])
        top3_table = Table(top3_data, colWidths=[1*cm, 7*cm, 7*cm, 3.5*cm])
        top3_table.setStyle(TableStyle([
            ('FONTNAME',      (0,0), (-1,-1), FONT_NORMAL),
            ('FONTNAME',      (0,0), (-1,0),  FONT_BOLD),
            ('FONTSIZE',      (0,0), (-1,-1), 10),
            ('BACKGROUND',    (0,0), (-1,0),  PRIMARY),
            ('TEXTCOLOR',     (0,0), (-1,0),  colors.white),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, LIGHT_BG]),
            ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('ALIGN',         (0,0), (0,-1),  'CENTER'),
            ('ALIGN',         (3,0), (3,-1),  'CENTER'),
            ('PADDING',       (0,0), (-1,-1), 7),
        ]))
        story.append(top3_table)
        story.append(Spacer(1, 0.4*cm))

    # ════════════════════════════════════════════════════════
    # SECOND OPINION
    # ════════════════════════════════════════════════════════
    second = prediction_data.get("second_opinion")
    if second:
        story.append(Paragraph("SO SÁNH MODEL (RF vs DNN)", h2_style))
        rf  = second.get("rf_result",  {})
        dnn = second.get("dnn_result", {})
        agree_color = SUCCESS if second.get("agreement") else WARNING
        so_data = [
            ["Model", "Dự đoán", "Độ tin cậy", "Đồng thuận"],
            ["Random Forest / Ensemble",
             rf.get("disease_vi","---"),
             f"{rf.get('confidence',0):.1f}%",
             "Có" if second.get("agreement") else "Không"],
            ["Deep Neural Network (PyTorch)",
             dnn.get("disease_vi","---") if dnn else "Chưa load",
             f"{dnn.get('confidence',0):.1f}%" if dnn else "---",
             "Có" if second.get("agreement") else "Không"],
        ]
        so_table = Table(so_data, colWidths=[5.5*cm, 6*cm, 3*cm, 4*cm])
        so_table.setStyle(TableStyle([
            ('FONTNAME',      (0,0), (-1,-1), FONT_NORMAL),
            ('FONTNAME',      (0,0), (-1,0),  FONT_BOLD),
            ('FONTSIZE',      (0,0), (-1,-1), 10),
            ('BACKGROUND',    (0,0), (-1,0),  colors.HexColor('#4a5568')),
            ('TEXTCOLOR',     (0,0), (-1,0),  colors.white),
            ('TEXTCOLOR',     (3,1), (3,-1),  agree_color),
            ('FONTNAME',      (3,1), (3,-1),  FONT_BOLD),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, LIGHT_BG]),
            ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING',       (0,0), (-1,-1), 7),
        ]))
        story.append(so_table)
        story.append(Paragraph(
            second.get("verdict",""),
            ParagraphStyle('v', fontName=FONT_ITALIC, fontSize=10,
                           textColor=agree_color, spaceAfter=4, spaceBefore=4)
        ))
        story.append(Spacer(1, 0.3*cm))

    # ════════════════════════════════════════════════════════
    # RISK SCORE
    # ════════════════════════════════════════════════════════
    risk = prediction_data.get("risk_score")
    if risk and risk.get("risks"):
        story.append(Paragraph("ĐIỂM NGUY CƠ", h2_style))
        risk_data = [["Bệnh", "Xác suất AI", "Điểm nguy cơ", "Mức độ"]]
        for r in risk["risks"][:5]:
            risk_data.append([
                r["disease_vi"],
                f"{r['model_prob']:.1f}%",
                f"{r['risk_score']}/100",
                r["risk_level"],
            ])
        risk_table = Table(risk_data, colWidths=[7*cm, 3*cm, 3.5*cm, 5*cm])
        risk_table.setStyle(TableStyle([
            ('FONTNAME',      (0,0), (-1,-1), FONT_NORMAL),
            ('FONTNAME',      (0,0), (-1,0),  FONT_BOLD),
            ('FONTSIZE',      (0,0), (-1,-1), 10),
            ('BACKGROUND',    (0,0), (-1,0),  DANGER),
            ('TEXTCOLOR',     (0,0), (-1,0),  colors.white),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, LIGHT_BG]),
            ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING',       (0,0), (-1,-1), 7),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.4*cm))

    # ════════════════════════════════════════════════════════
    # DISCLAIMER + FOOTER
    # ════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "⚠️ CẢNH BÁO QUAN TRỌNG: Báo cáo này được tạo tự động bởi hệ thống AI "
        "và chỉ mang tính chất tham khảo. Kết quả KHÔNG thay thế cho việc "
        "chẩn đoán của bác sĩ chuyên khoa. Vui lòng đến cơ sở y tế để được "
        "khám và điều trị chính xác.",
        disc_style
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Tạo bởi: Hệ thống Tư vấn Sức khỏe AI v2.0  |  "
        f"Thời gian: {now.strftime('%d/%m/%Y %H:%M:%S')}  |  "
        f"Phục vụ mục đích học tập và nghiên cứu",
        footer_style
    ))

    doc.build(story)
    return output_path


# ── Test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))

    print("⏳ Đang tạo báo cáo PDF với font Times New Roman...")

    # Dữ liệu test mẫu
    prediction_data = {
        "patient":   {"name": "Nguyễn Văn A", "age": 35, "gender": "male"},
        "symptoms":  ["itching", "skin_rash", "nodal_skin_eruptions"],
        "disease_vi": "Nhiễm nấm",
        "disease_en": "Fungal infection",
        "confidence": 99.3,
        "severity":   "🟢 Nhẹ",
        "specialty":  "Da liễu",
        "top3": [
            {"disease_vi":"Nhiễm nấm",  "disease_en":"Fungal infection", "confidence":99.3},
            {"disease_vi":"Vảy nến",    "disease_en":"Psoriasis",         "confidence":0.5},
            {"disease_vi":"Dị ứng",     "disease_en":"Allergy",           "confidence":0.2},
        ],
        "second_opinion": {
            "rf_result":  {"disease_vi":"Nhiễm nấm", "confidence":99.3},
            "dnn_result": {"disease_vi":"Nhiễm nấm", "confidence":98.1},
            "agreement":  True,
            "verdict":    "✅ Cả 2 model đồng thuận — Kết quả tin cậy cao!",
        },
        "risk_score": {
            "risks": [
                {"disease_vi":"Nhiễm nấm",  "model_prob":99.3, "risk_score":25, "risk_level":"🟢 Thấp"},
                {"disease_vi":"Vảy nến",    "model_prob":0.5,  "risk_score":10, "risk_level":"🟢 Thấp"},
            ]
        },
    }

    output = generate_pdf_report(prediction_data,
                                  "../results/sample_diagnosis_report.pdf")
    print(f"✅ Báo cáo đã tạo: {output}")
    print("\n👉 Mở file:")
    print('   start "" "C:\\AI Model Healthy\\results\\sample_diagnosis_report.pdf"')
