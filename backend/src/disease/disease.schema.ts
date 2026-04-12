import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type DiseaseDocument = Disease & Document;

@Schema({ timestamps: true })
export class Disease {
  @Prop({ required: true, trim: true })
  name!: string;

  @Prop({ required: true })
  description!: string;

  @Prop({ type: [String], default: [] })
  symptoms: string[];

  @Prop()
  specialty!: string;

  @Prop({ enum: ['low', 'medium', 'high'], default: 'medium' })
  severityLevel!: string;

  @Prop()
  treatmentAdvice!: string;
}

export const DiseaseSchema = SchemaFactory.createForClass(Disease);

// Index để tìm kiếm nhanh
DiseaseSchema.index({ name: 'text', description: 'text' });