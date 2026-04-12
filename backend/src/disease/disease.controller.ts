import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiQuery } from '@nestjs/swagger';
import { DiseaseService } from './disease.service';
import { CreateDiseaseDto, UpdateDiseaseDto } from './disease.dto';
import { AdminGuard } from '../common/guards/guards';

@ApiTags('Diseases')
@Controller('diseases')
export class DiseaseController {
  constructor(private diseaseService: DiseaseService) {}

  // ── Public endpoints ────────────────────────────────────

  @Get()
  @ApiOperation({ summary: 'Danh sách bệnh lý (có tìm kiếm, lọc chuyên khoa)' })
  @ApiQuery({ name: 'page',      required: false, example: 1 })
  @ApiQuery({ name: 'limit',     required: false, example: 20 })
  @ApiQuery({ name: 'search',    required: false, example: 'sốt xuất huyết' })
  @ApiQuery({ name: 'specialty', required: false, example: 'Tim mạch' })
  getAll(
    @Query('page')      page      = '1',
    @Query('limit')     limit     = '20',
    @Query('search')    search?:    string,
    @Query('specialty') specialty?: string,
  ) {
    return this.diseaseService.getAll(+page, +limit, search, specialty);
  }

  @Get('specialties')
  @ApiOperation({ summary: 'Danh sách chuyên khoa' })
  getSpecialties() {
    return this.diseaseService.getSpecialties();
  }

  @Get(':id')
  @ApiOperation({ summary: 'Chi tiết 1 bệnh' })
  getOne(@Param('id') id: string) {
    return this.diseaseService.getOne(id);
  }

  // ── Admin-only endpoints ────────────────────────────────

  @Post()
  @ApiBearerAuth()
  @ApiOperation({ summary: '[Admin] Thêm bệnh mới' })
  @UseGuards(AdminGuard)
  create(@Body() dto: CreateDiseaseDto) {
    return this.diseaseService.create(dto);
  }

  @Put(':id')
  @ApiBearerAuth()
  @ApiOperation({ summary: '[Admin] Cập nhật bệnh' })
  @UseGuards(AdminGuard)
  update(@Param('id') id: string, @Body() dto: UpdateDiseaseDto) {
    return this.diseaseService.update(id, dto);
  }

  @Delete(':id')
  @ApiBearerAuth()
  @ApiOperation({ summary: '[Admin] Xoá bệnh' })
  @UseGuards(AdminGuard)
  delete(@Param('id') id: string) {
    return this.diseaseService.delete(id);
  }
}