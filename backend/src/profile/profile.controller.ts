import {
  Controller, Get, Put, Post, Body, UseGuards,
  Request, UseInterceptors, UploadedFile, BadRequestException,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { diskStorage } from 'multer';
import { extname } from 'path';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiConsumes, ApiBody } from '@nestjs/swagger';
import { ProfileService } from './profile.service';
import { JwtAuthGuard } from '../common/guards/guards';

const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp'];

@ApiTags('Profile')
@ApiBearerAuth()
@Controller('profile')
@UseGuards(JwtAuthGuard)
export class ProfileController {
  constructor(private profileService: ProfileService) {}

  @Get()
  @ApiOperation({ summary: 'Xem hồ sơ sức khỏe cá nhân' })
  getProfile(@Request() req: any) {
    return this.profileService.getProfile(req.user._id.toString());
  }

  @Put()
  @ApiOperation({ summary: 'Cập nhật hồ sơ sức khỏe (tạo mới nếu chưa có)' })
  upsertProfile(@Request() req: any, @Body() body: any) {
    return this.profileService.upsertProfile(req.user._id.toString(), body);
  }

  @Post('avatar')
  @ApiOperation({ summary: 'Upload ảnh đại diện (jpg, png, webp — tối đa 2MB)' })
  @ApiConsumes('multipart/form-data')
  @ApiBody({ schema: { type: 'object', properties: { file: { type: 'string', format: 'binary' } } } })
  @UseInterceptors(
    FileInterceptor('file', {
      storage: diskStorage({
        destination: './uploads/avatars',
        filename: (_req, file, cb) => {
          const uniqueName = `${Date.now()}-${Math.round(Math.random() * 1e6)}`;
          cb(null, `${uniqueName}${extname(file.originalname)}`);
        },
      }),
      limits: { fileSize: 2 * 1024 * 1024 }, // 2MB
      fileFilter: (_req, file, cb) => {
        const ext = extname(file.originalname).toLowerCase();
        if (ALLOWED_EXTENSIONS.includes(ext)) {
          cb(null, true);
        } else {
          cb(new BadRequestException('Chỉ chấp nhận file jpg, jpeg, png, webp'), false);
        }
      },
    }),
  )
  uploadAvatar(@Request() req: any, @UploadedFile() file: Express.Multer.File) {
    if (!file) throw new BadRequestException('Vui lòng chọn file ảnh');
    const avatarUrl = `/uploads/avatars/${file.filename}`;
    return this.profileService.updateAvatar(req.user._id.toString(), avatarUrl);
  }
}