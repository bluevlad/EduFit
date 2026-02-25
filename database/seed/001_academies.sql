-- ============================================
-- EduFit Seed Data: 학원
-- ============================================

INSERT INTO academies (name, name_en, code, website, keywords) VALUES
('공단기', 'Gongdangi', 'gongdangi', 'https://gong.conects.com',
 ARRAY['공단기', '커넥츠공단기', '공무원단기', 'conects']),
('해커스공무원', 'Hackers', 'hackers', 'https://gosi.hackers.com',
 ARRAY['해커스', '해커스공무원', '해커스고시', 'hackers']),
('윌비스공무원', 'Willbes', 'willbes', 'https://pass.willbes.net',
 ARRAY['윌비스', '윌비스공무원', 'willbes']),
('에듀윌공무원', 'Eduwill', 'eduwill', 'https://gov.eduwill.net',
 ARRAY['에듀윌', '에듀윌공무원', 'eduwill']),
('박문각공무원', 'Parkmungak', 'parkmungak', 'https://www.pmg.co.kr',
 ARRAY['박문각', '박문각공무원', 'pmg'])
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    name_en = EXCLUDED.name_en,
    website = EXCLUDED.website,
    keywords = EXCLUDED.keywords;
