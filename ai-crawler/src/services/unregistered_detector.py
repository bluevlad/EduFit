"""
Unregistered Name Detector Service
미등록 인물 감지 서비스

크롤링된 텍스트에서 등록되지 않은 인물명 패턴을 감지하여
관리자에게 후보로 제안합니다.

감지 방식:
  1. 한국어 인명 패턴 (2~4글자 한글 + 강사/선생/쌤 등 호칭)
  2. 등록된 강사명과 비교하여 미등록만 필터
  3. 빈도 기반으로 후보 테이블에 누적

제외 규칙:
  - 1글자 이름
  - 일반 명사 (선생, 강사, 교수 등)
  - 이미 등록된 강사 이름/별명
  - 학원명과 동일한 텍스트
"""
import logging
import re
from datetime import datetime
from typing import List, Dict, Set, Optional
from sqlalchemy.orm import Session

from ..models import Teacher, Academy, UnregisteredCandidate

logger = logging.getLogger(__name__)

# 호칭 패턴: "OOO 쌤", "OOO선생님", "OOO 강사" 등
HONORIFIC_PATTERN = r'(?:쌤|샘|강사님?|선생님?|교수님?|T|t)'

# 인명 + 호칭 패턴
# 2~4글자 한글 이름 + 호칭
NAME_WITH_HONORIFIC = re.compile(
    r'(?:^|[^가-힣a-zA-Z0-9])'
    r'([가-힣]{2,4})\s*' + HONORIFIC_PATTERN +
    r'(?:[^가-힣a-zA-Z0-9]|$)'
)

# "OOO 강의", "OOO 인강", "OOO 기본서" 등 강사 문맥 패턴
NAME_WITH_CONTEXT = re.compile(
    r'(?:^|[^가-힣a-zA-Z0-9])'
    r'([가-힣]{2,4})\s*'
    r'(?:강의|인강|기본서|기출|교재|수업|커리|특강|모의고사|문풀|개념|심화|기초)'
    r'(?:[^가-힣a-zA-Z0-9]|$)'
)

# 제외할 일반 명사 목록
EXCLUDE_WORDS = {
    # 일반 호칭
    '선생', '강사', '교수', '학생', '수험생', '합격자', '불합격',
    # 과목명
    '국어', '영어', '수학', '한국사', '행정법', '헌법', '행정학',
    '경제학', '세법', '회계학', '사회', '과학', '민법', '형법',
    # 일반 명사
    '공무원', '공시생', '시험', '합격', '불합격', '환불', '추천',
    '기출', '모의', '인강', '강의', '교재', '수업', '기본',
    '심화', '개념', '문제', '정답', '해설', '요약', '정리',
    '카페', '갤러리', '게시판', '댓글', '작성', '수정', '삭제',
    '올해', '내년', '작년', '오늘', '내일', '어제', '이번',
    '이거', '저거', '그거', '여기', '거기', '이건', '저건',
    '진짜', '정말', '완전', '그냥', '아무', '모든', '최대',
    '다들', '우리', '너희', '자기', '사람', '여러', '어떤',
    '가능', '필요', '중요', '기본', '특별', '일반', '전체',
    '공단기', '메가', '해커스', '에듀윌', '박문각',
}


class UnregisteredDetector:
    """미등록 인물명 감지 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self._registered_names: Set[str] = set()
        self._academy_names: Set[str] = set()
        self._initialized = False

    def initialize(self):
        """등록된 강사/학원명 로드"""
        if self._initialized:
            return

        # 등록된 강사 이름 + 별명 로드
        teachers = self.db.query(Teacher).filter(Teacher.is_active == True).all()
        for t in teachers:
            self._registered_names.add(t.name)
            if t.aliases:
                for alias in t.aliases:
                    self._registered_names.add(alias)

        # 학원명 로드 (제외 대상)
        academies = self.db.query(Academy).all()
        for a in academies:
            self._academy_names.add(a.name)
            if a.keywords:
                for kw in a.keywords:
                    self._academy_names.add(kw)

        self._initialized = True
        logger.info(
            f"UnregisteredDetector initialized: "
            f"{len(self._registered_names)} registered names, "
            f"{len(self._academy_names)} academy names"
        )

    def detect_names(self, text: str) -> List[str]:
        """텍스트에서 미등록 인물명 후보 추출"""
        if not text:
            return []

        self.initialize()
        candidates = set()

        # 패턴 1: 이름 + 호칭
        for match in NAME_WITH_HONORIFIC.finditer(text):
            name = match.group(1).strip()
            if self._is_valid_candidate(name):
                candidates.add(name)

        # 패턴 2: 이름 + 강의 문맥
        for match in NAME_WITH_CONTEXT.finditer(text):
            name = match.group(1).strip()
            if self._is_valid_candidate(name):
                candidates.add(name)

        return list(candidates)

    def _is_valid_candidate(self, name: str) -> bool:
        """후보 유효성 검증"""
        if len(name) < 2 or len(name) > 4:
            return False
        if name in EXCLUDE_WORDS:
            return False
        if name in self._registered_names:
            return False
        if name in self._academy_names:
            return False
        # 숫자 포함 제외
        if re.search(r'\d', name):
            return False
        return True

    def process_text(
        self,
        text: str,
        source_code: str = '',
        context_size: int = 80
    ) -> List[str]:
        """텍스트 처리 후 미등록 후보 DB 업데이트

        Returns:
            감지된 미등록 이름 목록
        """
        names = self.detect_names(text)
        if not names:
            return []

        now = datetime.utcnow()

        for name in names:
            # 문맥 추출
            idx = text.find(name)
            ctx_start = max(0, idx - context_size)
            ctx_end = min(len(text), idx + len(name) + context_size)
            context = text[ctx_start:ctx_end].strip()

            # 기존 후보 조회
            candidate = self.db.query(UnregisteredCandidate).filter(
                UnregisteredCandidate.name == name,
                UnregisteredCandidate.status == 'pending'
            ).first()

            if candidate:
                # 기존 후보 업데이트
                candidate.mention_count += 1
                candidate.last_seen_at = now

                # 문맥 샘플 추가 (최대 5개)
                samples = candidate.sample_contexts or []
                if len(samples) < 5 and context not in samples:
                    samples.append(context)
                    candidate.sample_contexts = samples

                # 소스 분포 업데이트
                dist = candidate.source_distribution or {}
                dist[source_code] = dist.get(source_code, 0) + 1
                candidate.source_distribution = dist
            else:
                # 신규 후보 생성
                candidate = UnregisteredCandidate(
                    name=name,
                    mention_count=1,
                    first_seen_at=now,
                    last_seen_at=now,
                    sample_contexts=[context] if context else [],
                    source_distribution={source_code: 1} if source_code else {},
                    status='pending'
                )
                self.db.add(candidate)

        return names

    def get_pending_candidates(
        self,
        min_mentions: int = 3,
        limit: int = 50
    ) -> List[UnregisteredCandidate]:
        """관리자 검토용 후보 목록 조회"""
        return self.db.query(UnregisteredCandidate).filter(
            UnregisteredCandidate.status == 'pending',
            UnregisteredCandidate.mention_count >= min_mentions
        ).order_by(
            UnregisteredCandidate.mention_count.desc()
        ).limit(limit).all()
