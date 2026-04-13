import { Controller, Post, Get, Patch, Delete, Body, Param, Query, UseGuards, Request, Res } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiQuery } from '@nestjs/swagger';
import { ConsultationService } from './consultation.service';
import { CreateConsultationDto, AnalyzeTextDto, ChatReplyDto, FeedbackDto } from './consultation.dto';
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

  @Post('analyze-text')
  @ApiOperation({ summary: 'Tư vấn từ câu văn tiếng Việt (NLP)' })
  analyzeText(@Request() req: any, @Body() dto: AnalyzeTextDto) {
    return this.consultService.analyzeText(req.user._id.toString(), dto.text);
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

  @Get(':id/pdf')
  @ApiOperation({ summary: 'Tải báo cáo PDF của 1 lần tư vấn' })
  async downloadPdf(
    @Request() req: any,
    @Param('id') id: string,
    @Res() res: any,
  ) {
    const { buffer, filename } = await this.consultService.downloadPdf(
      req.user._id.toString(),
      id,
    );
    res.set({
      'Content-Type': 'application/pdf',
      'Content-Disposition': `attachment; filename="${filename}"`,
      'Content-Length': buffer.length.toString(),
    });
    res.send(buffer);
  }

  // ── Chat step-by-step ─────────────────────────────────────────
  @Post('chat/start')
  @ApiOperation({ summary: 'Bắt đầu phiên chat chẩn đoán theo từng bước' })
  chatStart() {
    return this.consultService.chatStart();
  }

  @Post('chat/reply')
  @ApiOperation({ summary: 'Trả lời câu hỏi trong phiên chat' })
  chatReply(@Body() dto: ChatReplyDto) {
    return this.consultService.chatReply(dto.sessionId, dto.answer);
  }

  @Delete('chat/:sessionId')
  @ApiOperation({ summary: 'Kết thúc phiên chat' })
  chatEnd(@Param('sessionId') sessionId: string) {
    return this.consultService.chatEnd(sessionId);
  }
}