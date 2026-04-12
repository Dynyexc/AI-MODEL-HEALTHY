import { Injectable, BadRequestException, NotFoundException } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Consultation, ConsultationDocument } from './consultation.schema';
import { AiService } from './ai.service';

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
    @InjectModel(Consultation.name) private model: Model<ConsultationDocument>,
    private aiService: AiService,
  ) {}

  async create(userId: string, symptoms: string[]) {
    if (!symptoms || symptoms.length === 0)
      throw new BadRequestException('Vui lòng nhập triệu chứng');

    const aiResult = await this.aiService.predictDisease(symptoms);
    const specialty = SPECIALTY_MAP[aiResult.disease] ?? 'Nội khoa tổng quát';

    const consultation = await this.model.create({
      user: userId,
      symptoms,
      aiResult,
      specialty,
      recommendation:
        `Bạn có thể đang mắc ${aiResult.disease} (độ tin cậy: ${aiResult.confidence}%). ` +
        `Nên đến khám chuyên khoa: ${specialty}. ` +
        `Đây chỉ là tư vấn tham khảo, không thay thế ý kiến bác sĩ.`,
    });

    return { success: true, data: consultation };
  }

  async getOne(userId: string, id: string) {
    const doc = await this.model.findOne({ _id: id, user: userId });
    if (!doc) throw new NotFoundException('Không tìm thấy lần tư vấn này');
    return { data: doc };
  }

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

  async submitFeedback(userId: string, id: string, rating: number, comment?: string) {
    const doc = await this.model.findOneAndUpdate(
      { _id: id, user: userId },
      { userFeedback: { rating, comment } },
      { returnDocument: 'after' },
    );
    if (!doc) throw new NotFoundException('Không tìm thấy lần tư vấn này');
    return { success: true, data: doc };
  }

  async getSymptoms() {
    const symptoms = await this.aiService.getAllSymptoms();
    // Sắp xếp theo tên tiếng Việt cho dễ tìm
    return symptoms.sort((a, b) => a.vi.localeCompare(b.vi, 'vi'));
  }
}