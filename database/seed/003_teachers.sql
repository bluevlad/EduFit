-- ============================================
-- EduFit Seed Data: 강사
-- TeacherHub 강사 데이터 + 박문각 강사 추가
-- ============================================

-- 공단기 강사
INSERT INTO teachers (academy_id, subject_id, name, aliases) VALUES
-- 국어
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='국어'), '이선재', ARRAY['이선재쌤', '선재쌤', '선재']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='국어'), '권규호', ARRAY['권규호쌤', '규호쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='국어'), '곽지영', ARRAY['곽지영쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='국어'), '유대종', ARRAY['유대종쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='국어'), '이얼', ARRAY['이얼쌤']),
-- 영어
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='영어'), '심우철', ARRAY['심우철쌤', '심쌤', '우철쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='영어'), '이동기', ARRAY['이동기쌤', '동기쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='영어'), '이유진', ARRAY['이유진쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='영어'), '김병태', ARRAY['김병태쌤']),
-- 한국사
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='한국사'), '문동균', ARRAY['문동균쌤', '동균쌤', '문쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='한국사'), '김신', ARRAY['김신쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='한국사'), '윤우혁', ARRAY['윤우혁쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='한국사'), '오철환', ARRAY['오철환쌤']),
-- 행정법
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='행정법'), '박준철', ARRAY['박준철쌤', '준철쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='행정법'), '김건호', ARRAY['김건호쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='행정법'), '민준호', ARRAY['민준호쌤']),
-- 행정학
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='행정학'), '황철곤', ARRAY['황철곤쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='행정학'), '신성우', ARRAY['신성우쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='행정학'), '이형재', ARRAY['이형재쌤']),
-- 헌법
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='헌법'), '이은영', ARRAY['이은영쌤']),
-- 형법
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='형법'), '이지민', ARRAY['이지민쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='형법'), '이윤탁', ARRAY['이윤탁쌤']),
-- 경제학
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='경제학'), '장선구', ARRAY['장선구쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='경제학'), '신경수', ARRAY['신경수쌤']),
-- PSAT
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='상황판단'), '이상진', ARRAY['이상진쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='상황판단'), '하주응', ARRAY['하주응쌤']),
((SELECT id FROM academies WHERE code='gongdangi'), (SELECT id FROM subjects WHERE name='자료해석'), '김승환', ARRAY['김승환쌤'])
ON CONFLICT DO NOTHING;

-- 해커스공무원 강사
INSERT INTO teachers (academy_id, subject_id, name, aliases) VALUES
-- 국어
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='국어'), '신민숙', ARRAY['신민숙쌤', '민숙쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='국어'), '황진선', ARRAY['황진선쌤']),
-- 영어
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='영어'), '비비안', ARRAY['비비안쌤', 'Vivian', '비비안영어']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='영어'), '김철용', ARRAY['김철용쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='영어'), '최진우', ARRAY['최진우쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='영어'), '김송희', ARRAY['김송희쌤']),
-- 한국사
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='한국사'), '이중석', ARRAY['이중석쌤', '중석쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='한국사'), '고혜원', ARRAY['고혜원쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='한국사'), '이명호', ARRAY['이명호쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='한국사'), '김한나', ARRAY['김한나쌤']),
-- 행정법
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='행정법'), '함수민', ARRAY['함수민쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='행정법'), '김대환', ARRAY['김대환쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='행정법'), '송상호', ARRAY['송상호쌤']),
-- 행정학
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='행정학'), '서현', ARRAY['서현쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='행정학'), '금나나', ARRAY['금나나쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='행정학'), '양소이', ARRAY['양소이쌤']),
-- 헌법
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='헌법'), '신동욱', ARRAY['신동욱쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='헌법'), '황남기', ARRAY['황남기쌤']),
-- 형법
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='형법'), '이인호', ARRAY['이인호쌤']),
-- 회계학
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='회계학'), '정윤돈', ARRAY['정윤돈쌤']),
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='회계학'), '김대현', ARRAY['김대현쌤']),
-- 경찰학
((SELECT id FROM academies WHERE code='hackers'), (SELECT id FROM subjects WHERE name='경찰학'), '김민철', ARRAY['김민철쌤'])
ON CONFLICT DO NOTHING;

-- 윌비스공무원 강사
INSERT INTO teachers (academy_id, subject_id, name, aliases) VALUES
-- 국어
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='국어'), '전선혜', ARRAY['전선혜쌤']),
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='국어'), '오태진', ARRAY['오태진쌤']),
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='국어'), '박재현', ARRAY['박재현쌤']),
-- 영어
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='영어'), '한덕현', ARRAY['한덕현쌤']),
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='영어'), '오대혁', ARRAY['오대혁쌤']),
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='영어'), '박초롱', ARRAY['박초롱쌤']),
-- 한국사
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='한국사'), '신영식', ARRAY['신영식쌤', '영식쌤']),
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='한국사'), '임진석', ARRAY['임진석쌤']),
-- 헌법
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='헌법'), '이국령', ARRAY['이국령쌤']),
-- 민법
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='민법'), '김동진', ARRAY['김동진쌤']),
-- 형법
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='형법'), '문형석', ARRAY['문형석쌤']),
-- 형사소송법
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='형사소송법'), '유안석', ARRAY['유안석쌤']),
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='형사소송법'), '신광은', ARRAY['신광은쌤']),
-- PSAT
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='자료해석'), '석치수', ARRAY['석치수쌤']),
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='상황판단'), '박준범', ARRAY['박준범쌤']),
((SELECT id FROM academies WHERE code='willbes'), (SELECT id FROM subjects WHERE name='언어논리'), '이나우', ARRAY['이나우쌤'])
ON CONFLICT DO NOTHING;

-- 에듀윌공무원 강사
INSERT INTO teachers (academy_id, subject_id, name, aliases) VALUES
-- 국어
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='국어'), '배영표', ARRAY['배영표쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='국어'), '송운학', ARRAY['송운학쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='국어'), '임지혜', ARRAY['임지혜쌤']),
-- 영어
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='영어'), '장종재', ARRAY['장종재쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='영어'), '헤더진', ARRAY['헤더진쌤', 'Heather', '헤더']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='영어'), '손재석', ARRAY['손재석쌤']),
-- 한국사
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='한국사'), '한유진', ARRAY['한유진쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='한국사'), '신형철', ARRAY['신형철쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='한국사'), '김준형', ARRAY['김준형쌤']),
-- 행정법
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='행정법'), '김용철', ARRAY['김용철쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='행정법'), '하성우', ARRAY['하성우쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='행정법'), '서정민', ARRAY['서정민쌤']),
-- 행정학
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='행정학'), '남진우', ARRAY['남진우쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='행정학'), '이광호', ARRAY['이광호쌤']),
-- 경제학
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='경제학'), '강두성', ARRAY['강두성쌤']),
-- 형법
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='형법'), '장진', ARRAY['장진쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='형법'), '신현식', ARRAY['신현식쌤']),
-- 회계학
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='회계학'), '현진환', ARRAY['현진환쌤']),
-- 경찰학
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='경찰학'), '김민현', ARRAY['김민현쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='경찰학'), '이상헌', ARRAY['이상헌쌤']),
-- PSAT
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='언어논리'), '차선우', ARRAY['차선우쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='자료해석'), '김성욱', ARRAY['김성욱쌤']),
((SELECT id FROM academies WHERE code='eduwill'), (SELECT id FROM subjects WHERE name='상황판단'), '김재형', ARRAY['김재형쌤'])
ON CONFLICT DO NOTHING;

-- 박문각공무원 강사
INSERT INTO teachers (academy_id, subject_id, name, aliases) VALUES
-- 국어
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='국어'), '이유진', ARRAY['이유진쌤', '박문각이유진']),
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='국어'), '마상국', ARRAY['마상국쌤']),
-- 영어
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='영어'), '이태종', ARRAY['이태종쌤']),
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='영어'), '박철우', ARRAY['박철우쌤']),
-- 한국사
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='한국사'), '전한길', ARRAY['전한길쌤', '한길쌤']),
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='한국사'), '고종훈', ARRAY['고종훈쌤']),
-- 행정법
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='행정법'), '이상현', ARRAY['이상현쌤']),
-- 행정학
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='행정학'), '이종학', ARRAY['이종학쌤']),
-- 헌법
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='헌법'), '김유향', ARRAY['김유향쌤']),
-- 형법
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='형법'), '진신', ARRAY['진신쌤']),
-- 경제학
((SELECT id FROM academies WHERE code='parkmungak'), (SELECT id FROM subjects WHERE name='경제학'), '이상근', ARRAY['이상근쌤'])
ON CONFLICT DO NOTHING;
