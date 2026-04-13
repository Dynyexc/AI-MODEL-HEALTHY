import { IsArray, IsString, ArrayNotEmpty, IsNumber, Min, Max, IsOptional } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateConsultationDto {
  @ApiProperty({
    description: 'Danh sách triệu chứng',
    example: ['itching', 'skin_rash', 'fever'],
    type: [String],
  })
  @IsArray()
  @ArrayNotEmpty({ message: 'Vui lòng nhập ít nhất 1 triệu chứng' })
  @IsString({ each: true })
  symptoms!: string[];
}

export class AnalyzeTextDto {
  @ApiProperty({
    description: 'Câu văn tiếng Việt mô tả triệu chứng',
    example: 'Tôi bị đau đầu, sốt cao và mệt mỏi từ 2 hôm nay',
  })
  @IsString()
  text!: string;
}

export class ChatReplyDto {
  @ApiProperty({ description: 'Session ID từ /chat/start', example: 'a1b2c3d4' })
  @IsString()
  sessionId!: string;

  @ApiProperty({ description: 'Câu trả lời', example: 'Có' })
  @IsString()
  answer!: string;
}

export class FeedbackDto {
  @ApiProperty({ description: 'Đánh giá từ 1-5', example: 4, minimum: 1, maximum: 5 })
  @IsNumber()
  @Min(1)
  @Max(5)
  rating!: number;

  @ApiPropertyOptional({ description: 'Nhận xét', example: 'Kết quả khá chính xác' })
  @IsOptional()
  @IsString()
  comment?: string;
}