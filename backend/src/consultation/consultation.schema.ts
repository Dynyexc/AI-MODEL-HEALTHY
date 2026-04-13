import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document, Types } from 'mongoose';

export type ConsultationDocument = Consultation & Document;

class Top3Item {
  disease_vi!: string;
  disease_en!: string;
  confidence!: number;
}

class AiResult {
  disease_vi!: string;
  disease_en!: string;
  confidence!: number;
  severity!:   string;
  specialty!:  string;
  top3!:       Top3Item[];
}

class UserFeedback {
  rating!:   number;
  comment?:  string;
}

@Schema({ timestamps: true })
export class Consultation {
  @Prop({ type: Types.ObjectId, ref: 'User', required: true })
  user: Types.ObjectId;

  @Prop({ type: [String], required: true })
  symptoms: string[];

  @Prop({ default: null })
  inputText?: string;         // Câu văn gốc nếu nhập NLP

  @Prop({ type: Object })
  aiResult: AiResult;

  @Prop()
  recommendation: string;

  @Prop()
  specialty: string;

  @Prop({ type: Object })
  userFeedback: UserFeedback;
}

export const ConsultationSchema = SchemaFactory.createForClass(Consultation);
