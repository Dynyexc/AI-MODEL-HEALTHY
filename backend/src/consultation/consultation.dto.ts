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