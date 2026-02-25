-- ============================================
-- EduFit Seed Data: 과목 (18개)
-- ============================================

INSERT INTO subjects (name, category, display_order) VALUES
('국어', 'common', 1),
('영어', 'common', 2),
('한국사', 'common', 3),
('행정법', 'major', 10),
('행정학', 'major', 11),
('헌법', 'major', 12),
('형법', 'major', 13),
('형사소송법', 'major', 14),
('민법', 'major', 15),
('민사소송법', 'major', 16),
('경제학', 'major', 17),
('회계학', 'major', 18),
('세법', 'major', 19),
('사회복지학', 'major', 20),
('교정학', 'major', 21),
('경찰학', 'major', 22),
('언어논리', 'psat', 30),
('자료해석', 'psat', 31),
('상황판단', 'psat', 32)
ON CONFLICT (name) DO UPDATE SET
    category = EXCLUDED.category,
    display_order = EXCLUDED.display_order;
