import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { User, UserDocument } from '../auth/user.schema';
import { Consultation, ConsultationDocument } from '../consultation/consultation.schema';

@Injectable()
export class AdminService {
  constructor(
    @InjectModel(User.name) private userModel: Model<UserDocument>,
    @InjectModel(Consultation.name) private consultModel: Model<ConsultationDocument>,
  ) {}

  async getDashboardStats() {
    const [totalUsers, totalConsultations, recentConsultations, topDiseases, monthlyStats] =
      await Promise.all([
        this.userModel.countDocuments({ role: 'user' }),
        this.consultModel.countDocuments(),
        this.consultModel
          .find()
          .sort({ createdAt: -1 })
          .limit(5)
          .populate('user', 'name email'),
        this.consultModel.aggregate([
          { $group: { _id: '$aiResult.disease', count: { $sum: 1 } } },
          { $sort: { count: -1 } },
          { $limit: 5 },
          { $project: { disease: '$_id', count: 1, _id: 0 } },
        ]),
        this.consultModel.aggregate([
          {
            $group: {
              _id: { year: { $year: '$createdAt' }, month: { $month: '$createdAt' } },
              count: { $sum: 1 },
            },
          },
          { $sort: { '_id.year': -1, '_id.month': -1 } },
          { $limit: 6 },
        ]),
      ]);

    return { totalUsers, totalConsultations, recentConsultations, topDiseases, monthlyStats };
  }

  async getAllUsers(page = 1, limit = 20, search?: string) {
    const query = search
      ? {
          $or: [
            { name:  { $regex: search, $options: 'i' } },
            { email: { $regex: search, $options: 'i' } },
          ],
        }
      : {};

    const [data, total] = await Promise.all([
      this.userModel
        .find(query)
        .select('-password')
        .sort({ createdAt: -1 })
        .skip((page - 1) * limit)
        .limit(limit),
      this.userModel.countDocuments(query),
    ]);

    return { data, total };
  }

  async getUserConsultations(userId: string, page = 1, limit = 10) {
    const user = await this.userModel.findById(userId).select('-password');
    if (!user) throw new NotFoundException('Không tìm thấy user');

    const [data, total] = await Promise.all([
      this.consultModel
        .find({ user: userId })
        .sort({ createdAt: -1 })
        .skip((page - 1) * limit)
        .limit(limit),
      this.consultModel.countDocuments({ user: userId }),
    ]);

    return {
      user,
      data,
      pagination: { total, page, totalPages: Math.ceil(total / limit) },
    };
  }

  async toggleUser(userId: string) {
    const user = await this.userModel.findById(userId);
    if (!user) throw new NotFoundException('Không tìm thấy user');
    if (user.role === 'admin') throw new NotFoundException('Không thể khoá tài khoản admin');

    user.isActive = !user.isActive;
    await user.save();

    return {
      success: true,
      message: user.isActive ? 'Đã mở khoá tài khoản' : 'Đã khoá tài khoản',
      isActive: user.isActive,
    };
  }

  async getSymptomStats(limit = 20) {
    return this.consultModel.aggregate([
      { $unwind: '$symptoms' },
      { $group: { _id: '$symptoms', count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: limit },
      { $project: { symptom: '$_id', count: 1, _id: 0 } },
    ]);
  }
}