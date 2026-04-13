import { Injectable, BadRequestException, NotFoundException } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Consultation, ConsultationDocument } from './consultation.schema';
import { HealthProfile, HealthProfileDocument } from '../profile/health-profile.schema';
import { User, UserDocument } from '../auth/user.schema';
import { AiService, AiPrediction } from './ai.service';

// Map disease_en → specialty (fallback nếu AI không trả về)
const SPECIALTY_MAP: Record<string, string> = {
  'Fungal infection': 'Da liễu',
  'Allergy': 'Dị ứng - Miễn dịch',
  'GERD': 'Tiêu hóa',
  'Chronic cholestasis': 'Tiêu hóa',
  'Drug Reaction': 'Da liễu',
  'Peptic ulcer disease': 'Tiêu hóa',
  'AIDS': 'Truyền nhiễm',
  'Diabetes': 'Nội tiết',
  'Gastroenteritis': 'Tiêu hóa',
  'Bronchial Asthma': 'Hô hấp',
  'Hypertension': 'Tim mạch',
  'Migraine': 'Thần kinh',
  'Cervical spondylosis': 'Cơ xương khớp',
  'Paralysis (brain hemorrhage)': 'Thần kinh',
  'Jaundice': 'Tiêu hóa',
  'Malaria': 'Truyền nhiễm',
  'Chicken pox': 'Da liễu',
  'Dengue': 'Truyền nhiễm',
  'Typhoid': 'Truyền nhiễm',
  'hepatitis A': 'Tiêu hóa',
  'Hepatitis B': 'Tiêu hóa',
  'Hepatitis C': 'Tiêu hóa',
  'Hepatitis D': 'Tiêu hóa',
  'Hepatitis E': 'Tiêu hóa',
  'Alcoholic hepatitis': 'Tiêu hóa',
  'Tuberculosis': 'Hô hấp',
  'Common Cold': 'Nội khoa',
  'Pneumonia': 'Hô hấp',
  'Dimorphic hemmorhoids': 'Tiêu hóa',
  'Heart attack': 'Tim mạch',
  'Varicose veins': 'Tim mạch',
  'Hypothyroidism': 'Nội tiết',
  'Hyperthyroidism': 'Nội tiết',
  'Hypoglycemia': 'Nội tiết',
  'Osteoarthritis': 'Cơ xương khớp',
  'Arthritis': 'Cơ xương khớp',
  'Vertigo': 'Thần kinh',
  'Acne': 'Da liễu',
  'Urinary tract infection': 'Tiết niệu',
  'Psoriasis': 'Da liễu',
  'Impetigo': 'Da liễu',
};

@Injectable()
export class ConsultationService {
  constructor(
    @InjectModel(Consultation.name)
    private model: Model<ConsultationDocument>,
    @InjectModel(HealthProfile.name)
    private profileModel: Model<HealthProfileDocument>,
    @InjectModel(User.name)
    private userModel: Model<UserDocument>,
    private aiService: AiService,
  ) {}

  // ── Lấy hồ sơ sức khỏe của user (để truyền tuổi/giới tính vào AI) ──
  private async getUserProfile(userId: string) {
    return this.profileModel.findOne({ user: userId });
  }

  // ── Lưu kết quả tư vấn vào DB ────────────────────────────────
  private async saveConsultation(
    userId: string,
    symptoms: string[],
    aiResult: AiPrediction,
    inputText?: string,
  ) {
    const specialty =
      aiResult.specialty ?? SPECIALTY_MAP[aiResult.disease_en] ?? 'Nội khoa tổng quát';

    return this.model.create({
      user: userId,
      symptoms,
      inputText,
      aiResult: {
        disease:    aiResult.disease_vi,
        disease_en: aiResult.disease_en,
        confidence: aiResult.confidence,
        severity:   aiResult.severity,
        specialty,
        top3:       aiResult.top3,
      },
      specialty,
      recommendation: aiResult.recommendation,
    });
  }

  // ── 1. Tư vấn từ danh sách triệu chứng ───────────────────────
  async create(userId: string, symptoms: string[]) {
    if (!symptoms || symptoms.length === 0)
      throw new BadRequestException('Vui lòng nhập triệu chứng');

    // Lấy hồ sơ sức khỏe để cá nhân hoá kết quả
    const profile = await this.getUserProfile(userId);
    const age     = profile?.age;
    const gender  = profile?.gender;

    // Gọi smart-predict (có tuổi/giới tính nếu user đã điền hồ sơ)
    const aiResult = await this.aiService.smartPredict(symptoms, age, gender);
    const consultation = await this.saveConsultation(userId, symptoms, aiResult);

    return {
      success: true,
      personalized: !!(age || gender), // Cho biết có dùng hồ sơ không
      data: consultation,
    };
  }

  // ── 2. Tư vấn từ câu văn tiếng Việt (NLP) ────────────────────
  async analyzeText(userId: string, text: string) {
    if (!text?.trim()) throw new BadRequestException('Vui lòng nhập mô tả triệu chứng');

    const profile = await this.getUserProfile(userId);
    const age     = profile?.age;
    const gender  = profile?.gender;

    const nlpResult = await this.aiService.analyzeText(text, age, gender);

    if (nlpResult.total_found === 0) {
      return {
        success: false,
        message: 'Không nhận dạng được triệu chứng từ văn bản. Thử mô tả cụ thể hơn.',
        hint:    'Ví dụ: "tôi bị đau đầu, sốt cao và ho nhiều"',
        original_text: text,
      };
    }

    // Lưu tư vấn nếu có kết quả
    let consultation: any = null;
    if (nlpResult.prediction) {
      const symptoms = nlpResult.english_symptoms.length > 0
        ? nlpResult.english_symptoms
        : nlpResult.found_symptoms;

      consultation = await this.saveConsultation(
        userId,
        symptoms,
        nlpResult.prediction,
        text,
      );
    }

    return {
      success:        true,
      nlp: {
        original_text:  text,
        found_symptoms: nlpResult.found_symptoms,  // Tên tiếng Việt
        total_found:    nlpResult.total_found,
        confidence:     nlpResult.confidence,
      },
      personalized: !!(age || gender),
      data: consultation,
    };
  }

  // ── 3. Xem chi tiết 1 lần tư vấn ─────────────────────────────
  async getOne(userId: string, id: string) {
    const doc = await this.model.findOne({ _id: id, user: userId });
    if (!doc) throw new NotFoundException('Không tìm thấy lần tư vấn này');
    return { data: doc };
  }

  // ── 4. Lịch sử tư vấn ────────────────────────────────────────
  async getHistory(userId: string, page = 1, limit = 10) {
    const [data, total] = await Promise.all([
      this.model
        .find({ user: userId })
        .sort({ createdAt: -1 })
        .skip((page - 1) * limit)
        .limit(limit),
      this.model.countDocuments({ user: userId }),
    ]);

    return {
      data,
      pagination: { total, page, totalPages: Math.ceil(total / limit) },
    };
  }

  // ── 5. Đánh giá kết quả ──────────────────────────────────────
  async submitFeedback(userId: string, id: string, rating: number, comment?: string) {
    const doc = await this.model.findOneAndUpdate(
      { _id: id, user: userId },
      { userFeedback: { rating, comment } },
      { returnDocument: 'after' },
    );
    if (!doc) throw new NotFoundException('Không tìm thấy lần tư vấn này');
    return { success: true, data: doc };
  }

  // ── 6. Danh sách triệu chứng ─────────────────────────────────
  async getSymptoms() {
    return this.aiService.getAllSymptoms();
  }

  // ── 7. Tải PDF báo cáo của 1 lần tư vấn ─────────────────────
  async downloadPdf(userId: string, id: string) {
    const doc = await this.model.findOne({ _id: id, user: userId });
    if (!doc) throw new NotFoundException('Không tìm thấy lần tư vấn này');

    const [user, profile] = await Promise.all([
      this.userModel.findById(userId).select('name').lean(),
      this.profileModel.findOne({ user: userId }).lean(),
    ]);

    const ai = doc.aiResult as any;
    return this.aiService.generateReport({
      patient_name: (user as any)?.name ?? 'Người dùng',
      age:          profile?.age    ?? null,
      gender:       profile?.gender ?? null,
      symptoms:     doc.symptoms,
      disease_vi:   ai?.disease_vi  ?? '',
      disease_en:   ai?.disease_en  ?? '',
      confidence:   ai?.confidence  ?? 0,
      severity:     ai?.severity    ?? '🟡 Cần theo dõi',
      specialty:    doc.specialty   ?? 'Nội khoa tổng quát',
      top3:         ai?.top3        ?? [],
    });
  }

  // ── 8. Chat step-by-step ──────────────────────────────────────
  async chatStart() {
    return this.aiService.chatStart();
  }

  async chatReply(sessionId: string, answer: string) {
    return this.aiService.chatReply(sessionId, answer);
  }

  async chatEnd(sessionId: string) {
    return this.aiService.chatEnd(sessionId);
  }
}
