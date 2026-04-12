import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type BlacklistedTokenDocument = BlacklistedToken & Document;

@Schema()
export class BlacklistedToken {
  @Prop({ required: true, unique: true })
  token!: string;

  @Prop({ required: true })
  expiresAt!: Date;
}

export const BlacklistedTokenSchema = SchemaFactory.createForClass(BlacklistedToken);

// MongoDB tự xoá document khi expiresAt đến hạn
BlacklistedTokenSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });