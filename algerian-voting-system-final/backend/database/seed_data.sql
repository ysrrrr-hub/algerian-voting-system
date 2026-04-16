-- ============================================================
-- Seed Data - بيانات تجريبية للتطوير والعرض
-- ============================================================

-- 5 مرشحين نموذجيين
INSERT INTO candidates
    (full_name_ar, full_name_fr, party_name_ar, party_name_fr,
     display_order, photo_url, program_summary_ar, program_summary_fr)
VALUES
    ('أحمد بن علي', 'Ahmed Ben Ali',
     'حزب المستقبل', 'Parti du Futur', 1,
     '/assets/candidates/c1.jpg',
     'برنامج يركز على التنمية الاقتصادية والرقمنة',
     'Programme axé sur le développement économique et la numérisation'),

    ('فاطمة الزهراء حسين', 'Fatima Zahra Hussein',
     'حركة التجديد', 'Mouvement de Renouveau', 2,
     '/assets/candidates/c2.jpg',
     'برنامج يركز على التعليم والصحة والمرأة',
     'Programme axé sur l''éducation, la santé et les femmes'),

    ('محمد كريم بوعلي', 'Mohamed Karim Bouali',
     'الجبهة الوطنية', 'Front National', 3,
     '/assets/candidates/c3.jpg',
     'برنامج يركز على الأمن والاستقرار الوطني',
     'Programme axé sur la sécurité et la stabilité nationale'),

    ('نادية بوعزة', 'Nadia Bouazza',
     'التحالف الديمقراطي', 'Alliance Démocratique', 4,
     '/assets/candidates/c4.jpg',
     'برنامج يركز على الإصلاح السياسي والحريات',
     'Programme axé sur la réforme politique et les libertés'),

    ('يوسف العربي صالحي', 'Youssef El Arabi Salihi',
     'حزب العدالة والتنمية', 'Parti de la Justice et du Développement', 5,
     '/assets/candidates/c5.jpg',
     'برنامج يركز على العدالة الاجتماعية والفلاحة',
     'Programme axé sur la justice sociale et l''agriculture')
ON CONFLICT DO NOTHING;

-- ناخبون تجريبيون
INSERT INTO voters
    (nfc_uid, full_name_ar, full_name_fr, date_of_birth, wilaya)
VALUES
    ('04A1B2C3D4E5F6', 'عمر بن سعيد',   'Omar Ben Said',    '1990-05-15', 'الجزائر'),
    ('04B2C3D4E5F6A1', 'سامية لعلام',    'Samia Lallam',     '1985-08-22', 'وهران'),
    ('04C3D4E5F6A1B2', 'رشيد مرابط',     'Rachid Marabout',  '1978-12-10', 'قسنطينة'),
    ('TEST_VOTER_001', 'ناخب تجريبي 1',  'Test Voter 1',     '1995-01-01', 'البليدة'),
    ('TEST_VOTER_002', 'ناخب تجريبي 2',  'Test Voter 2',     '1988-06-15', 'البليدة'),
    ('TEST_VOTER_003', 'ناخب تجريبي 3',  'Test Voter 3',     '1992-03-20', 'الجزائر'),
    ('TEST_VOTER_004', 'ناخبة تجريبية',  'Test Voter F',     '1997-09-11', 'وهران')
ON CONFLICT DO NOTHING;

-- Genesis Block (الكتلة الأولى — لا تحتوي صوتاً حقيقياً)
INSERT INTO blockchain
    (block_index, encrypted_vote, previous_hash, current_hash, nonce)
VALUES (
    0,
    'GENESIS_BLOCK',
    '0000000000000000000000000000000000000000000000000000000000000000',
    'a3f5d8b2c1e4f6a7b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
    0
) ON CONFLICT DO NOTHING;

-- مشرف افتراضي (كلمة المرور الأصلية: Admin@2026)
-- password_hash مُولّد بـ bcrypt rounds=12
INSERT INTO admin_users
    (username, password_hash, full_name, role)
VALUES (
    'admin',
    '$2b$12$LJ3m4ys3Gz8y5N2bXCqJ8e8z3v4K5.Yb1Cw2A7k8Z9dF0gH1iJ2kL',
    'المشرف الرئيسي',
    'ADMIN'
),
(
    'supervisor',
    '$2b$12$LJ3m4ys3Gz8y5N2bXCqJ8e8z3v4K5.Yb1Cw2A7k8Z9dF0gH1iJ2kL',
    'مراقب الانتخابات',
    'SUPERVISOR'
)
ON CONFLICT DO NOTHING;
