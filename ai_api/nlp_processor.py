"""
========================================
NLP - NHẬP CÂU TỰ NHIÊN
========================================
Người dùng gõ: "tôi bị đau đầu, sốt cao và mệt mỏi"
AI tự nhận dạng triệu chứng từ câu văn

Cài đặt: pip install underthesea --break-system-packages
Chạy: python nlp_processor.py
"""

import re
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vietnamese_dict import SYMPTOM_VI, to_english_symptom

# ── Từ điển nhận dạng câu tự nhiên ──────────────────────────
# Map từ khóa thông thường → tên triệu chứng chuẩn
NATURAL_KEYWORDS = {
    # Sốt
    "sốt":              "Sốt",
    "sốt cao":          "Sốt cao",
    "sốt nhẹ":          "Sốt nhẹ",
    "bị sốt":           "Sốt",
    "thân nhiệt cao":   "Sốt cao",
    "nóng sốt":         "Sốt",

    # Đầu
    "đau đầu":          "Đau đầu",
    "nhức đầu":         "Đau đầu",
    "đau nửa đầu":      "Đau nửa đầu (Migraine)",
    "chóng mặt":        "Chóng mặt",
    "quay đầu":         "Chóng mặt",
    "hoa mắt":          "Chóng mặt",

    # Hô hấp
    "ho":               "Ho",
    "ho khan":          "Ho",
    "ho có đờm":        "Đờm",
    "khó thở":          "Khó thở",
    "thở khó":          "Khó thở",
    "nghẹt mũi":        "Nghẹt mũi",
    "sổ mũi":           "Chảy nước mũi",
    "chảy nước mũi":    "Chảy nước mũi",
    "đau họng":         "Kích ứng cổ họng",
    "viêm họng":        "Kích ứng cổ họng",
    "rát họng":         "Kích ứng cổ họng",
    "hắt hơi":          "Hắt hơi liên tục",

    # Tiêu hóa
    "buồn nôn":         "Buồn nôn",
    "nôn":              "Nôn mửa",
    "nôn mửa":          "Nôn mửa",
    "ói":               "Nôn mửa",
    "đau bụng":         "Đau bụng",
    "đau dạ dày":       "Đau dạ dày",
    "tiêu chảy":        "Tiêu chảy",
    "đi ngoài":         "Tiêu chảy",
    "táo bón":          "Táo bón",
    "khó tiêu":         "Khó tiêu",
    "ợ chua":           "Ợ chua",
    "đầy bụng":         "Chướng bụng",
    "chán ăn":          "Chán ăn",
    "ăn không ngon":    "Chán ăn",

    # Toàn thân
    "mệt":              "Mệt mỏi",
    "mệt mỏi":          "Mệt mỏi",
    "uể oải":           "Uể oải",
    "ớn lạnh":          "Ớn lạnh",
    "run rẩy":          "Run rẩy",
    "đổ mồ hôi":        "Đổ mồ hôi",
    "ra mồ hôi":        "Đổ mồ hôi",
    "sụt cân":          "Sụt cân",
    "giảm cân":         "Sụt cân",
    "tăng cân":         "Tăng cân",
    "mất nước":         "Mất nước",
    "khát nước":        "Mất nước",

    # Cơ xương khớp
    "đau cơ":           "Đau cơ",
    "đau khớp":         "Đau khớp",
    "đau lưng":         "Đau lưng",
    "đau cổ":           "Đau cổ",
    "đau vai":          "Đau cơ",
    "cứng khớp":        "Cứng khớp",
    "sưng khớp":        "Sưng khớp",
    "chuột rút":        "Chuột rút",
    "yếu cơ":           "Yếu cơ",

    # Da
    "ngứa":             "Ngứa da",
    "ngứa da":          "Ngứa da",
    "phát ban":         "Phát ban da",
    "nổi mẩn":          "Phát ban da",
    "mẩn đỏ":           "Phát ban da",
    "nổi mụn":          "Mụn mủ",
    "mụn":              "Mụn mủ",
    "bong tróc":        "Bong tróc da",
    "vảy da":           "Bong tróc da",
    "da vàng":          "Da vàng",
    "vàng da":          "Da vàng",

    # Mắt
    "đỏ mắt":           "Đỏ mắt",
    "mắt đỏ":           "Đỏ mắt",
    "chảy nước mắt":    "Chảy nước mắt",
    "mờ mắt":           "Mờ mắt",
    "vàng mắt":         "Vàng mắt",

    # Tim mạch
    "đau ngực":         "Đau ngực",
    "tim đập nhanh":    "Nhịp tim nhanh",
    "hồi hộp":          "Hồi hộp đánh trống ngực",
    "phù chân":         "Sưng chân",
    "sưng chân":        "Sưng chân",

    # Tiết niệu
    "tiểu buốt":        "Tiểu buốt",
    "tiểu rắt":         "Buồn tiểu liên tục",
    "tiểu nhiều":       "Tiểu nhiều",
    "nước tiểu vàng":   "Nước tiểu vàng",
    "nước tiểu sẫm":    "Nước tiểu sẫm màu",

    # Thần kinh
    "mất thăng bằng":   "Mất thăng bằng",
    "tê tay":           "Yếu tứ chi",
    "tê chân":          "Yếu tứ chi",
    "lo lắng":          "Lo lắng",
    "trầm cảm":         "Trầm cảm",
    "khó ngủ":          "Lo lắng",
}

class NLPProcessor:
    """
    Nhận dạng triệu chứng từ câu văn tự nhiên tiếng Việt
    """

    def __init__(self):
        # Sắp xếp theo độ dài giảm dần để ưu tiên cụm từ dài
        self.keywords = dict(
            sorted(NATURAL_KEYWORDS.items(),
                   key=lambda x: len(x[0]), reverse=True)
        )

    def extract_symptoms(self, text: str) -> dict:
        """
        Trích xuất triệu chứng từ câu văn

        Input : "tôi bị đau đầu, sốt cao và mệt mỏi"
        Output: {
            "found_symptoms": ["Đau đầu", "Sốt cao", "Mệt mỏi"],
            "english_symptoms": ["headache", "high_fever", "fatigue"],
            "original_text": "...",
            "confidence": "high/medium/low"
        }
        """
        text_lower = text.lower().strip()

        # Loại bỏ ký tự đặc biệt nhưng giữ dấu tiếng Việt
        text_clean = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]', ' ', text_lower)

        found_vi = []
        found_en = []
        used_positions = set()

        for keyword, symptom_vi in self.keywords.items():
            if keyword in text_clean:
                start = text_clean.find(keyword)
                end   = start + len(keyword)

                # Kiểm tra không trùng với từ đã tìm
                positions = set(range(start, end))
                if not positions.intersection(used_positions):
                    used_positions.update(positions)
                    if symptom_vi not in found_vi:
                        found_vi.append(symptom_vi)
                        en = to_english_symptom(symptom_vi)
                        found_en.append(en)

        # Đánh giá độ tin cậy
        if len(found_vi) >= 3:
            confidence = "high"
        elif len(found_vi) >= 1:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "original_text":   text,
            "found_symptoms":  found_vi,
            "english_symptoms":found_en,
            "total_found":     len(found_vi),
            "confidence":      confidence,
        }

    def suggest_clarification(self, text: str) -> list:
        """Gợi ý câu hỏi làm rõ nếu tìm được ít triệu chứng"""
        result = self.extract_symptoms(text)
        suggestions = []

        if result["total_found"] == 0:
            suggestions.append("Bạn có thể mô tả cụ thể hơn không? Ví dụ: 'tôi bị đau đầu, sốt và mệt mỏi'")
        elif result["total_found"] < 3:
            suggestions.append("Bạn có thêm triệu chứng nào khác không? (ví dụ: sốt, đau cơ, mệt mỏi)")

        return suggestions


# ── Test NLP Processor ───────────────────────────────────────
if __name__ == "__main__":
    nlp = NLPProcessor()

    test_cases = [
        "tôi bị đau đầu, sốt cao và mệt mỏi từ 2 hôm nay",
        "gần đây tôi hay bị chóng mặt, buồn nôn và đau bụng",
        "tôi bị ngứa da, nổi mẩn đỏ và phát ban",
        "tôi ho nhiều, khó thở và đau họng",
        "tôi bị tiêu chảy, nôn mửa và đau dạ dày",
        "tôi cảm thấy rất mệt, ăn không ngon và sụt cân",
    ]

    print("=" * 60)
    print("  🧠  TEST NLP PROCESSOR")
    print("=" * 60)

    for text in test_cases:
        result = nlp.extract_symptoms(text)
        print(f"\n📝 Input : '{text}'")
        print(f"   Tìm được: {result['found_symptoms']}")
        print(f"   Tiếng Anh: {result['english_symptoms']}")
        print(f"   Độ tin cậy: {result['confidence']}")

    print("\n✅ NLP Processor hoạt động tốt!")
