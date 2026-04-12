import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document, Types } from 'mongoose';

export type HealthProfileDocument = HealthProfile & Document;

@Schema({ timestamps: true })
export class HealthProfile {
  @Prop({ type: Types.ObjectId, ref: 'User', required: true, unique: true })
  user: Types.ObjectId;

  @Prop()
  age?: number;

  @Prop({ enum: ['male', 'female', 'other'] })
  gender?: string;

  @Prop()
  height?: number; // cm

  @Prop()
  weight?: number; // kg

  @Prop({ enum: ['A', 'B', 'AB', 'O', 'Unknown'] })
  bloodType?: string;

  @Prop({ type: [String], default: [] })
  chronicDiseases: string[];

  @Prop({ type: [String], default: [] })
  allergies: string[];

  @Prop({ type: [String], default: [] })
  currentMedications: string[];
}

export const HealthProfileSchema = SchemaFactory.createForClass(HealthProfile);