import { IsString, IsArray, IsOptional, IsEnum } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateDiseaseDto {
  @ApiProperty({ example: 'Sốt xuất huyết' })
  @IsString()
  name!: string;

  @ApiProperty({ example: 'Bệnh truyền nhiễm do virus Dengue gây ra...' })
  @IsString()
  description!: string;

  @ApiProperty({ example: ['fever', 'headache', 'skin_rash'], type: [String] })
  @IsArray()
  @IsString({ each: true })
  symptoms!: string[];

  @ApiProperty({ example: 'Truyền nhiễm' })
  @IsString()
  specialty!: string;

  @ApiPropertyOptional({ enum: ['low', 'medium', 'high'], default: 'medium' })
  @IsOptional()
  @IsEnum(['low', 'medium', 'high'])
  severityLevel?: string;

  @ApiPropertyOptional({ example: 'Nghỉ ngơi, uống nhiều nước, theo dõi tiểu cầu...' })
  @IsOptional()
  @IsString()
  treatmentAdvice?: string;
}

export class UpdateDiseaseDto extends CreateDiseaseDto {}