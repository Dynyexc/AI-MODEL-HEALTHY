/**
 * Script tạo tài khoản Admin
 * Chạy: npx ts-node -r tsconfig-paths/register src/seed.ts
 */
import * as mongoose from 'mongoose';
import * as bcrypt from 'bcryptjs';
import * as dotenv from 'dotenv';

dotenv.config();

const MONGO_URI =
  process.env.MONGODB_URI || 'mongodb://localhost:27017/health_consultant';

const UserSchema = new mongoose.Schema(
  {
    name:     { type: String, required: true },
    email:    { type: String, required: true, unique: true },
    password: { type: String, required: true },
    role:     { type: String, default: 'user' },
    isActive: { type: Boolean, default: true },
  },
  { timestamps: true },
);

async function seed() {
  console.log('Đang kết nối MongoDB...');
  await mongoose.connect(MONGO_URI);
  console.log('Kết nối thành công!');

  const User = mongoose.model('User', UserSchema);

  const adminEmail    = 'admin@healthline.com';
  const adminPassword = 'Admin@123';

  const existing = await User.findOne({ email: adminEmail });
  if (existing) {
    console.log(`\n⚠️  Admin đã tồn tại: ${adminEmail}`);
    await mongoose.disconnect();
    return;
  }

  const hashed = await bcrypt.hash(adminPassword, 12);
  await User.create({
    name:     'Admin',
    email:    adminEmail,
    password: hashed,
    role:     'admin',
  });

  console.log('\n✅ Tạo admin thành công!');
  console.log(`   Email:    ${adminEmail}`);
  console.log(`   Password: ${adminPassword}`);
  console.log('\nDùng thông tin trên để đăng nhập vào Admin Dashboard.');

  await mongoose.disconnect();
}

seed().catch((err) => {
  console.error('Seed thất bại:', err.message);
  process.exit(1);
});