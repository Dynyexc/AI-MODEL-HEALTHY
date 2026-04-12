import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Disease, DiseaseDocument } from './disease.schema';
import { CreateDiseaseDto, UpdateDiseaseDto } from './disease.dto';

@Injectable()
export class DiseaseService {
  constructor(@InjectModel(Disease.name) private model: Model<DiseaseDocument>) {}

  async getAll(page = 1, limit = 20, search?: string, specialty?: string) {
    const query: any = {};

    if (search) {
      query.$or = [
        { name:        { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } },
        { symptoms:    { $regex: search, $options: 'i' } },
      ];
    }
    if (specialty) {
      query.specialty = { $regex: specialty, $options: 'i' };
    }

    const [data, total] = await Promise.all([
      this.model
        .find(query)
        .sort({ name: 1 })
        .skip((page - 1) * limit)
        .limit(limit),
      this.model.countDocuments(query),
    ]);

    return { data, pagination: { total, page, totalPages: Math.ceil(total / limit) } };
  }

  async getOne(id: string) {
    const disease = await this.model.findById(id);
    if (!disease) throw new NotFoundException('Không tìm thấy bệnh');
    return { data: disease };
  }

  async getSpecialties() {
    const specialties = await this.model.distinct('specialty');
    return { data: specialties.sort() };
  }

  async create(dto: CreateDiseaseDto) {
    const disease = await this.model.create(dto);
    return { success: true, data: disease };
  }

  async update(id: string, dto: UpdateDiseaseDto) {
    const disease = await this.model.findByIdAndUpdate(id, dto, { returnDocument: 'after' });
    if (!disease) throw new NotFoundException('Không tìm thấy bệnh');
    return { success: true, data: disease };
  }

  async delete(id: string) {
    const disease = await this.model.findByIdAndDelete(id);
    if (!disease) throw new NotFoundException('Không tìm thấy bệnh');
    return { success: true, message: 'Đã xoá bệnh' };
  }
}