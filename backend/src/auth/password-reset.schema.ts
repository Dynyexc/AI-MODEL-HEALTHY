import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type PasswordResetDocument = PasswordReset & Document;

@Schema({ timestamps: true })
export class PasswordReset {
  @Prop({ required: true })
  email!: string;

  @Prop({ required: true })
  otp!: string;

  @Prop({ required: true })
  expiresAt!: Date;

  @Prop({ default: false })
  used!: boolean;
}

export const PasswordResetSchema = SchemaFactory.createForClass(PasswordReset);

// Tự xoá sau khi hết hạn
PasswordResetSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });