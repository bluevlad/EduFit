-- ============================================
-- EduFit Seed Data: 수집 소스
-- TeacherHub 5개 + AcademyInsight 3개 통합
-- ============================================

INSERT INTO collection_sources (name, code, base_url, source_type, config) VALUES
-- TeacherHub 기존 소스
('네이버 카페 - 공스타그램', 'naver_gongstar', 'https://cafe.naver.com/gongstar', 'cafe',
 '{"club_id": "28956533", "requires_login": true, "mobile_url": "https://m.cafe.naver.com/gongstar"}'),
('네이버 카페 - 공드림', 'naver_gongdream', 'https://cafe.naver.com/m2school', 'cafe',
 '{"club_id": "12026840", "requires_login": true, "mobile_url": "https://m.cafe.naver.com/m2school"}'),
('네이버 카페 - 9급공무원갤러리', 'naver_9gong', 'https://cafe.naver.com/9gong', 'cafe',
 '{"club_id": "16558386", "requires_login": true}'),
('디시인사이드 - 공무원 갤러리', 'dcinside_gongmuwon', 'https://gall.dcinside.com/board/lists/?id=government', 'gallery',
 '{"gallery_id": "government", "requires_login": false}'),
('디시인사이드 - 공무원 마이너 갤러리', 'dcinside_gongmuwon_minor', 'https://gall.dcinside.com/mgallery/board/lists/?id=gongmuwon', 'gallery',
 '{"gallery_id": "gongmuwon", "is_minor": true, "requires_login": false}'),
-- AcademyInsight 통합 소스
('에펨코리아 - 공무원 게시판', 'fmkorea_gongmuwon', 'https://www.fmkorea.com/index.php?mid=civil_service', 'forum',
 '{"board_id": "civil_service", "requires_login": false}'),
('뽐뿌 - 공무원 게시판', 'ppomppu_gongmuwon', 'https://www.ppomppu.co.kr/zboard/zboard.php?id=government', 'forum',
 '{"board_id": "government", "requires_login": false}'),
('블라인드 - 공무원 게시판', 'blind_gongmuwon', 'https://www.teamblind.com/kr/topics/Civil-Service', 'forum',
 '{"topic": "Civil-Service", "requires_login": true}'),
-- 뉴스 소스
('네이버 뉴스', 'naver_news', 'https://openapi.naver.com/v1/search/news.json', 'news',
 '{"type": "api", "requires_login": false, "max_results_per_keyword": 10}'),
('구글 뉴스', 'google_news', 'https://news.google.com/rss/search', 'news',
 '{"type": "rss", "requires_login": false, "max_results_per_keyword": 10}')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    base_url = EXCLUDED.base_url,
    config = EXCLUDED.config;
