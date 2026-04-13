import { Injectable, ServiceUnavailableException, BadRequestException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';
import { translateSymptoms } from '../common/constants/symptoms-vi.map';

// ── Response types từ AI API ──────────────────────────────────

export interface AiTop3Item {
  disease_vi: string;
  disease_en: string;
  confidence: number;
}

export interface AiPrediction {
  disease_vi:       string;
  disease_en:       string;
  confidence:       number;
  severity:         string;
  specialty:        string;
  top3:             AiTop3Item[];
  matched_symptoms: number;
  nlp_used?:        boolean;
  nlp_found?:       string[] | null;
  recommendation:   string;
  confidence_check?: { level: string; message: string; action: string };
}

export interface NlpAnalysisResult {
  original_text:    string;
  found_symptoms:   string[];       // Tên tiếng Việt
  english_symptoms: string[];       // Tên tiếng Anh → gửi lên predict
  total_found:      number;
  confidence:       string;
  prediction?:      AiPrediction;  // Kết quả dự đoán kèm theo (nếu có đủ triệu chứng)
}

export interface SymptomItem {
  en: string;   // gửi lên AI model
  vi: string;   // hiển thị cho người dùng
}

@Injectable()
export class AiService {
  private readonly aiUrl: string;

  constructor(private config: ConfigService) {
    this.aiUrl = this.config.get<string>('AI_API_URL', 'http://localhost:8000');
  }

  // ── 1. Dự đoán cơ bản (chỉ triệu chứng) ─────────────────────
  async predictDisease(symptoms: string[]): Promise<AiPrediction> {
    try {
      const res = await axios.post<AiPrediction>(`${this.aiUrl}/predict`, { symptoms });
      return res.data;
    } catch {
      throw new ServiceUnavailableException('AI service không phản hồi');
    }
  }

  // ── 2. Dự đoán thông minh (có tuổi + giới tính) ──────────────
  async smartPredict(
    symptoms: string[],
    age?:    number,
    gender?: string,
  ): Promise<AiPrediction> {
    try {
      const res = await axios.post<AiPrediction>(`${this.aiUrl}/smart-predict`, {
        symptoms,
        age:    age    ?? null,
        gender: gender ?? null,
      });
      return res.data;
    } catch (err: any) {
      if (err?.response?.status === 400) {
        throw new BadRequestException(
          err.response.data?.detail?.message ?? 'Không khớp triệu chứng nào trong hệ thống',
        );
      }
      throw new ServiceUnavailableException('AI service không phản hồi');
    }
  }

  // ── 3. NLP: phân tích câu văn tiếng Việt ─────────────────────
  async analyzeText(
    text: string,
    age?:    number,
    gender?: string,
  ): Promise<NlpAnalysisResult> {
    try {
      // Gọi smart-predict với text (AI sẽ tự dùng NLP trích xuất triệu chứng)
      const res = await axios.post<AiPrediction>(`${this.aiUrl}/smart-predict`, {
        text,
        age:    age    ?? null,
        gender: gender ?? null,
      });

      const prediction = res.data;

      return {
        original_text:    text,
        found_symptoms:   prediction.nlp_found ?? [],
        english_symptoms: [],
        total_found:      prediction.matched_symptoms,
        confidence:       prediction.confidence_check?.level ?? 'medium',
        prediction,
      };
    } catch (err: any) {
      if (err?.response?.status === 400) {
        const detail = err.response.data?.detail;
        // AI không nhận dạng được triệu chứng — trả về kết quả rỗng thay vì throw
        return {
          original_text:    text,
          found_symptoms:   [],
          english_symptoms: [],
          total_found:      0,
          confidence:       'low',
        };
      }
      throw new ServiceUnavailableException('AI service không phản hồi');
    }
  }

  // ── 4. Lấy danh sách triệu chứng (song ngữ) ──────────────────
  async getAllSymptoms(): Promise<SymptomItem[]> {
    try {
      const res = await axios.get<{ symptoms: string[] }>(`${this.aiUrl}/symptoms`);
      return translateSymptoms(res.data.symptoms).sort((a, b) =>
        a.vi.localeCompare(b.vi, 'vi'),
      );
    } catch {
      throw new ServiceUnavailableException('AI service không phản hồi');
    }
  }

  // ── 5. Tạo PDF báo cáo từ kết quả đã có ─────────────────────
  async generateReport(data: {
    patient_name: string;
    age?: number | null;
    gender?: string | null;
    symptoms: string[];
    disease_vi: string;
    disease_en: string;
    confidence: number;
    severity: string;
    specialty: string;
    top3: { disease_vi: string; disease_en: string; confidence: number }[];
  }): Promise<{ buffer: Buffer; filename: string }> {
    try {
      const res = await axios.post(`${this.aiUrl}/report`, data, {
        responseType: 'arraybuffer',
      });
      const disposition: string = res.headers['content-disposition'] ?? '';
      const match = disposition.match(/filename=([^\s;]+)/);
      const filename = match ? match[1] : `tuvan_${Date.now()}.pdf`;
      return { buffer: Buffer.from(res.data as ArrayBuffer), filename };
    } catch {
      throw new ServiceUnavailableException('AI service không phản hồi (PDF)');
    }
  }

  // ── 6. Chat step-by-step ──────────────────────────────────────
  async chatStart() {
    try {
      const res = await axios.post(`${this.aiUrl}/chat/start`);
      return res.data;
    } catch {
      throw new ServiceUnavailableException('AI service không phản hồi');
    }
  }

  async chatReply(sessionId: string, answer: string) {
    try {
      const res = await axios.post(`${this.aiUrl}/chat/reply`, {
        session_id: sessionId,
        answer,
      });
      return res.data;
    } catch (err: any) {
      if (err?.response?.status === 404)
        throw new BadRequestException('Session không tồn tại. Gọi /chat/start trước.');
      throw new ServiceUnavailableException('AI service không phản hồi');
    }
  }

  async chatEnd(sessionId: string) {
    try {
      const res = await axios.delete(`${this.aiUrl}/chat/${sessionId}`);
      return res.data;
    } catch {
      throw new ServiceUnavailableException('AI service không phản hồi');
    }
  }
}
