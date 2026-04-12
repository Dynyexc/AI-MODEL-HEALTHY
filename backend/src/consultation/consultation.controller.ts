import { Controller, Post, Get, Patch, Body, Param, Query, UseGuards, Request } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiQuery } from '@nestjs/swagger';
import { ConsultationService } from './consultation.service';
import { CreateConsultationDto, FeedbackDto } from './consultation.dto';
import { JwtAuthGuard } from '../common/guards/guards';

@ApiTags('Consultation')
@ApiBearerAuth()
@Controller('consultation')
@UseGuards(JwtAuthGuard)
export class ConsultationController {
  constructor(private consultService: ConsultationService) {}

  @Get('symptoms')
  @ApiOperation({ summary: 'Lấy danh sách tất cả triệu chứng' })
  getSymptoms() {
    return this.consultService.getSymptoms();
  }

  @Post()
  @ApiOperation({ summary: 'Tư vấn bệnh từ triệu chứng (gọi AI model)' })
  create(@Request() req: any, @Body() dto: CreateConsultationDto) {
    return this.consultService.create(req.user._id.toString(), dto.symptoms);
  }

  @Get('history')
  @ApiOperation({ summary: 'Lịch sử tư vấn của người dùng' })
  @ApiQuery({ name: 'page', required: false, example: 1 })
  @ApiQuery({ name: 'limit', required: false, example: 10 })
  getHistory(
    @Request() req: any,
    @Query('page') page = '1',
    @Query('limit') limit = '10',
  ) {
    return this.consultService.getHistory(req.user._id.toString(), +page, +limit);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Chi tiết 1 lần tư vấn' })
  getOne(@Request() req: any, @Param('id') id: string) {
    return this.consultService.getOne(req.user._id.toString(), id);
  }

  @Patch(':id/feedback')
  @ApiOperation({ summary: 'Đánh giá kết quả tư vấn' })
  submitFeedback(
    @Request() req: any,
    @Param('id') id: string,
    @Body() dto: FeedbackDto,
  ) {
    return this.consultService.submitFeedback(req.user._id.toString(), id, dto.rating, dto.comment);
  }
}