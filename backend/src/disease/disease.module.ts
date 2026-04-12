import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { Disease, DiseaseSchema } from './disease.schema';
import { DiseaseService } from './disease.service';
import { DiseaseController } from './disease.controller';

@Module({
  imports: [MongooseModule.forFeature([{ name: Disease.name, schema: DiseaseSchema }])],
  controllers: [DiseaseController],
  providers: [DiseaseService],
  exports: [MongooseModule],
})
export class DiseaseModule {}