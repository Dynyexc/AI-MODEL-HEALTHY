import { Controller, Get, Patch, Query, Param, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiQuery } from '@nestjs/swagger';
import { AdminService } from './admin.service';
import { AdminGuard } from '../common/guards/guards';

@ApiTags('Admin')
@ApiBearerAuth()
@Controller('admin')
@UseGuards(AdminGuard)
export class AdminController {
  constructor(private adminService: AdminService) {}

  @Get('dashboard')
  @ApiOperation({ summary: 'Thống kê tổng quan hệ thống' })
  getDashboard() {
    return this.adminService.getDashboardStats();
  }

  @Get('users')
  @ApiOperation({ summary: 'Danh sách người dùng (có tìm kiếm)' })
  @ApiQuery({ name: 'page',   required: false, example: 1 })
  @ApiQuery({ name: 'limit',  required: false, example: 20 })
  @ApiQuery({ name: 'search', required: false, example: 'nguyen' })
  getUsers(
    @Query('page')   page   = '1',
    @Query('limit')  limit  = '20',
    @Query('search') search?: string,
  ) {
    return this.adminService.getAllUsers(+page, +limit, search);
  }

  @Get('users/:id/consultations')
  @ApiOperation({ summary: 'Lịch sử tư vấn của 1 user cụ thể' })
  @ApiQuery({ name: 'page',  required: false, example: 1 })
  @ApiQuery({ name: 'limit', required: false, example: 10 })
  getUserConsultations(
    @Param('id')    userId: string,
    @Query('page')  page   = '1',
    @Query('limit') limit  = '10',
  ) {
    return this.adminService.getUserConsultations(userId, +page, +limit);
  }

  @Patch('users/:id/toggle')
  @ApiOperation({ summary: 'Khoá / Mở khoá tài khoản user' })
  toggleUser(@Param('id') userId: string) {
    return this.adminService.toggleUser(userId);
  }

  @Get('stats/symptoms')
  @ApiOperation({ summary: 'Thống kê triệu chứng phổ biến nhất' })
  @ApiQuery({ name: 'limit', required: false, example: 20 })
  getSymptomStats(@Query('limit') limit = '20') {
    return this.adminService.getSymptomStats(+limit);
  }
}