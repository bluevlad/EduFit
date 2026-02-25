-- ============================================
-- EduFit Seed Data: 분석 키워드 사전
-- 감성/난이도/추천 키워드
-- ============================================

INSERT INTO analysis_keywords (category, keyword, weight) VALUES
-- 긍정 키워드
('sentiment_positive', '추천', 1.5),
('sentiment_positive', '강추', 2.0),
('sentiment_positive', '좋아요', 1.0),
('sentiment_positive', '감사', 1.0),
('sentiment_positive', '합격', 1.5),
('sentiment_positive', '최고', 1.5),
('sentiment_positive', '도움', 1.0),
('sentiment_positive', '굿', 1.0),
('sentiment_positive', '명강의', 2.0),
('sentiment_positive', '이해', 1.0),
('sentiment_positive', '쉽게', 1.0),
('sentiment_positive', '친절', 1.0),
('sentiment_positive', '꼼꼼', 1.0),
('sentiment_positive', '체계적', 1.5),
('sentiment_positive', '효율적', 1.0),
-- 부정 키워드
('sentiment_negative', '비추', 2.0),
('sentiment_negative', '별로', 1.0),
('sentiment_negative', '어렵', 1.0),
('sentiment_negative', '실망', 1.5),
('sentiment_negative', '환불', 2.0),
('sentiment_negative', '답답', 1.0),
('sentiment_negative', '부족', 1.0),
('sentiment_negative', '아쉽', 0.8),
('sentiment_negative', '불친절', 1.5),
('sentiment_negative', '졸림', 1.0),
('sentiment_negative', '지루', 1.0),
('sentiment_negative', '돈아까', 2.0),
-- 난이도 쉬움
('difficulty_easy', '쉬움', 1.0),
('difficulty_easy', '쉽게', 1.0),
('difficulty_easy', '기초', 0.8),
('difficulty_easy', '입문', 0.8),
('difficulty_easy', '초보', 0.8),
('difficulty_easy', '친절', 0.5),
('difficulty_easy', '이해됨', 1.0),
-- 난이도 어려움
('difficulty_hard', '어려움', 1.0),
('difficulty_hard', '어렵', 1.0),
('difficulty_hard', '심화', 0.8),
('difficulty_hard', '고급', 0.8),
('difficulty_hard', '빡셈', 1.5),
('difficulty_hard', '헬', 1.5),
('difficulty_hard', '멘붕', 1.0),
-- 추천
('recommendation', '추천', 1.0),
('recommendation', '강추', 1.5),
('recommendation', '들어라', 1.0),
('recommendation', '꼭', 0.5),
('recommendation', '필수', 1.0),
('recommendation', '인생강의', 2.0)
ON CONFLICT (category, keyword) DO NOTHING;
