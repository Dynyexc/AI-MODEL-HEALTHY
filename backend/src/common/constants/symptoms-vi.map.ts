/**
 * Bảng dịch triệu chứng: English (key từ AI model) → Tiếng Việt (hiển thị)
 */
export const SYMPTOMS_VI: Record<string, string> = {
  // ── Toàn thân ───────────────────────────────────────────
  fatigue:                        'Mệt mỏi',
  high_fever:                     'Sốt cao',
  mild_fever:                     'Sốt nhẹ',
  sweating:                       'Đổ mồ hôi',
  chills:                         'Ớn lạnh',
  shivering:                      'Run rẩy',
  malaise:                        'Khó chịu toàn thân',
  dehydration:                    'Mất nước',
  weight_loss:                    'Sụt cân',
  weight_gain:                    'Tăng cân',
  lethargy:                       'Uể oải, thiếu năng lượng',
  restlessness:                   'Bồn chồn, không yên',
  anxiety:                        'Lo lắng, hồi hộp',
  mood_swings:                    'Thay đổi tâm trạng đột ngột',
  depression:                     'Trầm cảm',
  irritability:                   'Dễ cáu kỉnh',
  coma:                           'Hôn mê',
  altered_sensorium:              'Rối loạn ý thức',

  // ── Da liễu ─────────────────────────────────────────────
  itching:                        'Ngứa',
  skin_rash:                      'Phát ban da',
  nodal_skin_eruptions:           'Mụn nổi dạng hạch',
  yellowish_skin:                 'Da vàng',
  dischromic_patches:             'Mảng da đổi màu',
  red_spots_over_body:            'Đốm đỏ toàn thân',
  pus_filled_pimples:             'Mụn có mủ',
  blackheads:                     'Mụn đầu đen',
  scurring:                       'Vảy da',
  skin_peeling:                   'Bong tróc da',
  silver_like_dusting:            'Da bạc như bụi phấn',
  small_dents_in_nails:           'Móng tay có vết lõm nhỏ',
  inflammatory_nails:             'Móng tay viêm',
  blister:                        'Mụn nước, phỏng rộp',
  red_sore_around_nose:           'Lở đỏ quanh mũi',
  yellow_crust_ooze:              'Vảy vàng rỉ dịch',

  // ── Tiêu hóa ────────────────────────────────────────────
  vomiting:                       'Nôn mửa',
  nausea:                         'Buồn nôn',
  stomach_pain:                   'Đau dạ dày',
  abdominal_pain:                 'Đau bụng',
  belly_pain:                     'Đau bụng dưới',
  indigestion:                    'Khó tiêu',
  acidity:                        'Ợ chua, acid dạ dày',
  constipation:                   'Táo bón',
  diarrhoea:                      'Tiêu chảy',
  loss_of_appetite:               'Chán ăn, mất cảm giác ngon',
  increased_appetite:             'Ăn nhiều hơn bình thường',
  passage_of_gases:               'Xì hơi nhiều',
  stomach_bleeding:               'Xuất huyết dạ dày',
  distention_of_abdomen:          'Bụng căng chướng',
  swelling_of_stomach:            'Bụng sưng phồng',
  bloody_stool:                   'Phân có máu',
  pain_during_bowel_motions:      'Đau khi đại tiện',
  pain_in_anal_region:            'Đau vùng hậu môn',
  irritation_in_anus:             'Kích ứng hậu môn',
  internal_itching:               'Ngứa bên trong',
  ulcers_on_tongue:               'Loét lưỡi',
  acute_liver_failure:            'Suy gan cấp',
  fluid_overload:                 'Ứ dịch, phù nề',
  'fluid_overload.1':             'Ứ dịch (nặng)',
  history_of_alcohol_consumption: 'Tiền sử lạm dụng rượu bia',

  // ── Hô hấp ──────────────────────────────────────────────
  cough:                          'Ho',
  breathlessness:                 'Khó thở',
  chest_pain:                     'Đau ngực',
  phlegm:                         'Đờm / Đàm',
  mucoid_sputum:                  'Đờm nhầy',
  rusty_sputum:                   'Đờm màu gỉ sắt',
  blood_in_sputum:                'Đờm có máu',
  throat_irritation:              'Kích ứng họng',
  patches_in_throat:              'Mảng trắng trong họng',
  runny_nose:                     'Chảy nước mũi',
  congestion:                     'Nghẹt mũi',
  sinus_pressure:                 'Áp lực vùng xoang',
  continuous_sneezing:            'Hắt hơi liên tục',

  // ── Mắt ─────────────────────────────────────────────────
  redness_of_eyes:                'Đỏ mắt',
  yellowing_of_eyes:              'Vàng mắt',
  blurred_and_distorted_vision:   'Mờ mắt, nhìn méo',
  visual_disturbances:            'Rối loạn thị giác',
  watering_from_eyes:             'Chảy nước mắt',
  sunken_eyes:                    'Mắt trũng sâu',
  pain_behind_the_eyes:           'Đau sau nhãn cầu',
  loss_of_smell:                  'Mất khứu giác',

  // ── Cơ xương khớp ───────────────────────────────────────
  joint_pain:                     'Đau khớp',
  muscle_pain:                    'Đau cơ',
  muscle_wasting:                 'Teo cơ',
  back_pain:                      'Đau lưng',
  neck_stiffness:                 'Cứng cổ',
  weakness_in_limbs:              'Yếu tứ chi',
  weakness_of_one_body_side:      'Yếu một bên người',
  painful_walking:                'Đau khi đi lại',
  prominent_veins_on_calf:        'Tĩnh mạch nổi rõ ở bắp chân',

  // ── Tim mạch ────────────────────────────────────────────
  fast_heart_rate:                'Nhịp tim nhanh',
  palpitations:                   'Hồi hộp, đánh trống ngực',
  cold_hands_and_feets:           'Tay chân lạnh',

  // ── Thần kinh ───────────────────────────────────────────
  headache:                       'Đau đầu',
  unsteadiness:                   'Đứng không vững',
  loss_of_balance:                'Mất thăng bằng',
  lack_of_concentration:          'Khó tập trung',
  word_finding_difficulty:        'Khó nói, tìm từ khó',

  // ── Tiết niệu ───────────────────────────────────────────
  burning_micturition:            'Tiểu buốt, rát',
  spotting_urination:             'Tiểu ra máu nhẹ',
  dark_urine:                     'Nước tiểu sẫm màu',
  yellow_urine:                   'Nước tiểu vàng đậm',
  bladder_discomfort:             'Khó chịu vùng bàng quang',
  foul_smell_of_urine:            'Nước tiểu có mùi hôi',
  continuous_feel_of_urine:       'Buồn tiểu liên tục',
  polyuria:                       'Tiểu nhiều lần',

  // ── Nội tiết / Chuyển hóa ───────────────────────────────
  irregular_sugar_level:          'Đường huyết không ổn định',
  swelled_lymph_nodes:            'Hạch bạch huyết sưng',
  toxic_look_typhos:              'Mặt nhiễm độc (typhos)',
  'toxic_look_(typhos)':          'Mặt nhiễm độc (typhos)',

  // ── Sinh sản ────────────────────────────────────────────
  abnormal_menstruation:          'Rối loạn kinh nguyệt',

  // ── Khác ────────────────────────────────────────────────
  family_history:                 'Tiền sử gia đình',
  receiving_blood_transfusion:    'Đã từng truyền máu',
  receiving_unsterile_injections: 'Tiêm chích không vô trùng',
};

/**
 * Dịch 1 triệu chứng sang tiếng Việt
 * Nếu không có trong map → trả về tên gốc (format đẹp hơn)
 */
export function translateSymptom(en: string): string {
  return SYMPTOMS_VI[en] ?? en.replace(/_/g, ' ');
}

/**
 * Dịch danh sách triệu chứng
 */
export function translateSymptoms(list: string[]): { en: string; vi: string }[] {
  return list.map((en) => ({ en, vi: translateSymptom(en) }));
}