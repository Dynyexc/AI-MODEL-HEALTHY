import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { InjectConnection } from '@nestjs/mongoose';
import { Connection } from 'mongoose';
import { HealthProfile, HealthProfileDocument } from './health-profile.schema';
import { User, UserDocument } from '../auth/user.schema';

@Injectable()
export class ProfileService {
  constructor(
    @InjectModel(HealthProfile.name) private model: Model<HealthProfileDocument>,
    @InjectModel(User.name) private userModel: Model<UserDocument>,
  ) {}

  async getProfile(userId: string) {
    const [profile, user] = await Promise.all([
      this.model.findOne({ user: userId }),
      this.userModel.findById(userId).select('-password'),
    ]);
    return { data: { ...profile?.toObject(), avatar: user?.avatar } };
  }

  async upsertProfile(userId: string, dto: Partial<HealthProfile>) {
    const data = await this.model.findOneAndUpdate(
      { user: userId },
      { ...dto, user: userId },
      { returnDocument: 'after', upsert: true },
    );
    return { success: true, data };
  }

  async updateAvatar(userId: string, avatarUrl: string) {
    await this.userModel.findByIdAndUpdate(userId, { avatar: avatarUrl });
    return {
      success: true,
      message: 'Cập nhật ảnh đại diện thành công',
      avatarUrl,
    };
  }
}