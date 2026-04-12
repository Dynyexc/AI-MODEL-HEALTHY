import { Injectable, ServiceUnavailableException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';
import { translateSymptoms } from '../common/constants/symptoms-vi.map';

export interface AiPrediction {
  disease: string;
  confidence: number;
  top3: { disease: string; confidence: number }[];
}

export interface SymptomItem {
  en: string;   // tên tiếng Anh → gửi lên AI model
  vi: string;   // tên tiếng Việt → hiển thị cho người dùng
}

@Injectable()
export class AiService {
  private readonly aiUrl: string;

  constructor(private config: ConfigService) {
    this.aiUrl = this.config.get<string>('AI_API_URL', 'http://localhost:8000');
  }

  async predictDisease(symptoms: string[]): Promise<AiPrediction> {
    try {
      const res = await axios.post<AiPrediction>(`${this.aiUrl}/predict`, { symptoms });
      return res.data;
    } catch {
      throw new ServiceUnavailableException('AI service không phản hồi');
    }
  }

  async getAllSymptoms(): Promise<SymptomItem[]> {
    try {
      const res = await axios.get<{ symptoms: string[] }>(`${this.aiUrl}/symptoms`);
      return translateSymptoms(res.data.symptoms);
    } catch {
      throw new ServiceUnavailableException('AI service không phản hồi');
    }
  }
}