"""주간 리포트 서비스"""
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from ..models.daily_report import DailyReport
from ..models.teacher import Teacher
from ..models.academy import Academy
from ..models.subject import Subject


def _iso_week_to_short_label(year: int, week: int) -> str:
    """ISO 주차를 'M월N주' 형식으로 변환 (차트용 짧은 라벨)"""
    jan4 = date(year, 1, 4)
    start_of_week1 = jan4 - timedelta(days=jan4.isoweekday() - 1)
    thursday = start_of_week1 + timedelta(weeks=week - 1, days=3)
    month = thursday.month
    first_of_month = date(thursday.year, month, 1)
    week_of_month = ((thursday.day - 1 + first_of_month.weekday()) // 7) + 1
    return f"{month}월{week_of_month}주"


def _get_week_range(year: int, week: int):
    """ISO 주차의 시작/종료일 계산"""
    jan4 = date(year, 1, 4)
    start_of_week1 = jan4 - timedelta(days=jan4.isoweekday() - 1)
    week_start = start_of_week1 + timedelta(weeks=week - 1)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def get_summary(db: Session, year: int, week: int):
    """주간 요약"""
    week_start, week_end = _get_week_range(year, week)

    row = (
        db.query(
            func.sum(DailyReport.mention_count).label("total_mentions"),
            func.sum(DailyReport.positive_count).label("total_positive"),
            func.sum(DailyReport.negative_count).label("total_negative"),
            func.sum(DailyReport.recommendation_count).label("total_recommendations"),
            func.count(distinct(DailyReport.teacher_id)).label("total_teachers"),
        )
        .filter(DailyReport.report_date.between(week_start, week_end))
        .first()
    )

    # 전주 대비 변화율
    prev_start, prev_end = _get_week_range(year, week - 1) if week > 1 else _get_week_range(year - 1, 52)

    prev_row = (
        db.query(func.sum(DailyReport.mention_count).label("total_mentions"))
        .filter(DailyReport.report_date.between(prev_start, prev_end))
        .first()
    )

    prev_mentions = int(prev_row.total_mentions or 0) if prev_row else 0
    curr_mentions = int(row.total_mentions or 0)
    change_rate = None
    if prev_mentions > 0:
        change_rate = round((curr_mentions - prev_mentions) / prev_mentions * 100, 1)

    return {
        "totalMentions": curr_mentions,
        "totalPositive": int(row.total_positive or 0),
        "totalNegative": int(row.total_negative or 0),
        "totalTeachers": int(row.total_teachers or 0),
        "totalRecommendations": int(row.total_recommendations or 0),
        "mentionChangeRate": change_rate,
    }


def get_ranking(db: Session, year: int, week: int, limit: int = 20):
    """주간 랭킹"""
    week_start, week_end = _get_week_range(year, week)

    # 전주 범위
    prev_start, prev_end = _get_week_range(year, week - 1) if week > 1 else _get_week_range(year - 1, 52)

    rows = (
        db.query(
            Teacher.id,
            Teacher.name,
            Academy.name.label("academy_name"),
            func.sum(DailyReport.mention_count).label("mention_count"),
            func.sum(DailyReport.positive_count).label("positive_count"),
            func.sum(DailyReport.negative_count).label("negative_count"),
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
            func.sum(DailyReport.recommendation_count).label("recommendation_count"),
        )
        .join(Teacher, DailyReport.teacher_id == Teacher.id)
        .outerjoin(Academy, Teacher.academy_id == Academy.id)
        .filter(DailyReport.report_date.between(week_start, week_end))
        .group_by(Teacher.id, Teacher.name, Academy.name)
        .order_by(func.sum(DailyReport.mention_count).desc())
        .limit(limit)
        .all()
    )

    # 전주 데이터 (변화율 계산용)
    prev_data = {}
    prev_rows = (
        db.query(
            Teacher.id,
            func.sum(DailyReport.mention_count).label("mention_count"),
        )
        .join(Teacher, DailyReport.teacher_id == Teacher.id)
        .filter(DailyReport.report_date.between(prev_start, prev_end))
        .group_by(Teacher.id)
        .all()
    )
    for pr in prev_rows:
        prev_data[pr.id] = int(pr.mention_count or 0)

    # 상위 키워드 조회
    from ..models.daily_report import DailyReport as DR
    keyword_data = {}
    keyword_rows = (
        db.query(Teacher.id, DailyReport.top_keywords)
        .join(Teacher, DailyReport.teacher_id == Teacher.id)
        .filter(DailyReport.report_date.between(week_start, week_end))
        .filter(DailyReport.top_keywords.isnot(None))
        .all()
    )
    for tid, keywords in keyword_rows:
        if keywords:
            keyword_data.setdefault(tid, []).extend(keywords)

    result = []
    for rank, row in enumerate(rows, 1):
        curr = int(row.mention_count or 0)
        prev = prev_data.get(row.id, 0)
        change_rate = round((curr - prev) / prev * 100, 1) if prev > 0 else None

        # 가장 빈번한 키워드 3개
        kws = keyword_data.get(row.id, [])
        from collections import Counter
        top_kw = [k for k, _ in Counter(kws).most_common(3)] if kws else None

        result.append({
            "teacherId": row.id,
            "teacherName": row.name,
            "academyName": row.academy_name,
            "mentionCount": curr,
            "positiveCount": int(row.positive_count or 0),
            "negativeCount": int(row.negative_count or 0),
            "avgSentimentScore": float(row.avg_sentiment) if row.avg_sentiment else None,
            "recommendationCount": int(row.recommendation_count or 0),
            "weeklyRank": rank,
            "mentionChangeRate": change_rate,
            "topKeywords": top_kw,
        })

    return result


def get_teacher_trend(db: Session, teacher_id: int, weeks: int = 8):
    """강사 트렌드 (최근 N주)"""
    today = date.today()
    iso = today.isocalendar()
    current_year, current_week = iso[0], iso[1]

    result = []
    for i in range(weeks - 1, -1, -1):
        # i주 전의 year/week 계산
        target_week = current_week - i
        target_year = current_year
        while target_week < 1:
            target_year -= 1
            target_week += 52

        week_start, week_end = _get_week_range(target_year, target_week)

        row = (
            db.query(
                func.sum(DailyReport.mention_count).label("mention_count"),
                func.sum(DailyReport.positive_count).label("positive_count"),
                func.sum(DailyReport.negative_count).label("negative_count"),
                func.sum(DailyReport.neutral_count).label("neutral_count"),
                func.sum(DailyReport.recommendation_count).label("recommendation_count"),
                func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
            )
            .filter(DailyReport.teacher_id == teacher_id)
            .filter(DailyReport.report_date.between(week_start, week_end))
            .first()
        )

        result.append({
            "year": target_year,
            "weekNumber": target_week,
            "weekLabel": _iso_week_to_short_label(target_year, target_week),
            "mentionCount": int(row.mention_count or 0) if row else 0,
            "positiveCount": int(row.positive_count or 0) if row else 0,
            "negativeCount": int(row.negative_count or 0) if row else 0,
            "neutralCount": int(row.neutral_count or 0) if row else 0,
            "recommendationCount": int(row.recommendation_count or 0) if row else 0,
            "avgSentimentScore": float(row.avg_sentiment) if row and row.avg_sentiment else None,
            "weeklyRank": None,
        })

    return result
