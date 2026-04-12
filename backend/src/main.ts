import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import { NestExpressApplication } from '@nestjs/platform-express';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AllExceptionsFilter } from './common/filters/http-exception.filter';
import { join } from 'path';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);

  app.enableCors();
  app.setGlobalPrefix('api');
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
  app.useGlobalFilters(new AllExceptionsFilter());

  // Serve file tĩnh: ảnh avatar tại /uploads/avatars/filename.jpg
  app.useStaticAssets(join(process.cwd(), 'uploads'), { prefix: '/uploads' });

  // Swagger
  const config = new DocumentBuilder()
    .setTitle('HealthLine API')
    .setDescription('Hệ thống tư vấn sức khỏe trực tuyến - API Documentation')
    .setVersion('1.0')
    .addBearerAuth()
    .addTag('Auth', 'Đăng ký / Đăng nhập / OTP')
    .addTag('Consultation', 'Tư vấn triệu chứng AI')
    .addTag('Profile', 'Hồ sơ sức khỏe + Avatar')
    .addTag('Diseases', 'Thư viện bệnh lý')
    .addTag('Admin', 'Quản trị hệ thống')
    .addTag('Health', 'Kiểm tra trạng thái server')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document, {
    swaggerOptions: { persistAuthorization: true },
  });

  const port = process.env.PORT ?? 3002;
  await app.listen(port);
  console.log(`\n🚀 Server:  http://localhost:${port}/api`);
  console.log(`📖 Swagger: http://localhost:${port}/docs\n`);
}
bootstrap();