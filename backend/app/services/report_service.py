"""리포트 서비스"""
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import func, distinct, extract, text
from sqlalchemy.orm import Session

from ..models.daily_report import DailyReport
from ..models.teacher import Teacher
from ..models.academy import Academy
from ..models.subject import Subject


def _iso_week_to_month_label(year: int, week: int) -> str:
    """ISO 주차를 'YYYY년 M월 N주차' 형식으로 변환 (예: 2026년 6주차 → 2026년 2월 2주차)"""
    jan4 = date(year, 1, 4)
    start_of_week1 = jan4 - timedelta(days=jan4.isoweekday() - 1)
    thursday = start_of_week1 + timedelta(weeks=week - 1, days=3)
    month = thursday.month
    first_of_month = date(thursday.year, month, 1)
    # Monday=0 기준 weekday offset
    week_of_month = ((thursday.day - 1 + first_of_month.weekday()) // 7) + 1
    return f"{thursday.year}년 {month}월 {week_of_month}주차"


def _build_teacher_summary(report, teacher, academy, subject):
    """DailyReport + Teacher 조인 결과를 TeacherReportSummary dict로 변환"""
    return {
        "teacherId": teacher.id,
        "teacherName": teacher.name,
        "academyName": academy.name if academy else None,
        "subjectName": subject.name if subject else None,
        "mentionCount": report.mention_count or 0,
        "postMentionCount": report.post_mention_count or 0,
        "commentMentionCount": report.comment_mention_count or 0,
        "positiveCount": report.positive_count or 0,
        "negativeCount": report.negative_count or 0,
        "neutralCount": report.neutral_count or 0,
        "avgSentimentScore": report.avg_sentiment_score,
        "recommendationCount": report.recommendation_count or 0,
        "mentionChange": report.mention_change or 0,
        "sentimentChange": report.sentiment_change,
        "topKeywords": report.top_keywords,
        "summary": report.summary,
    }


def _build_period_response(period_type: str, label: str, start_date: str, end_date: str, summaries: list):
    total_mentions = sum(s["mentionCount"] for s in summaries)
    total_positive = sum(s["positiveCount"] for s in summaries)
    total_negative = sum(s["negativeCount"] for s in summaries)
    total_teachers = len(summaries)
    scores = [s["avgSentimentScore"] for s in summaries if s["avgSentimentScore"] is not None]
    avg_score = sum(scores) / len(scores) if scores else None
    positive_ratio = round(total_positive / total_mentions * 100, 1) if total_mentions > 0 else 0

    return {
        "periodType": period_type,
        "periodLabel": label,
        "startDate": start_date,
        "endDate": end_date,
        "totalMentions": total_mentions,
        "totalPositive": total_positive,
        "totalNegative": total_negative,
        "totalTeachers": total_teachers,
        "avgSentimentScore": avg_score,
        "positiveRatio": positive_ratio,
        "teacherSummaries": sorted(summaries, key=lambda x: x["mentionCount"], reverse=True),
    }


def get_daily(db: Session, report_date: Optional[str] = None):
    """일별 리포트"""
    if report_date:
        target_date = date.fromisoformat(report_date)
    else:
        target_date = date.today()

    rows = (
        db.query(DailyReport, Teacher, Academy, Subject)
        .join(Teacher, DailyReport.teacher_id == Teacher.id)
        .outerjoin(Academy, Teacher.academy_id == Academy.id)
        .outerjoin(Subject, Teacher.subject_id == Subject.id)
        .filter(DailyReport.report_date == target_date)
        .order_by(DailyReport.mention_count.desc())
        .all()
    )

    summaries = [_build_teacher_summary(r, t, a, s) for r, t, a, s in rows]
    label = target_date.strftime("%Y년 %m월 %d일")

    return _build_period_response("daily", label, str(target_date), str(target_date), summaries)


def get_weekly(db: Session, year: int, week: int):
    """주별 리포트 (해당 주에 속하는 daily_reports 집계)"""
    # ISO 주차의 시작일(월) 계산
    jan4 = date(year, 1, 4)
    start_of_week1 = jan4 - timedelta(days=jan4.isoweekday() - 1)
    week_start = start_of_week1 + timedelta(weeks=week - 1)
    week_end = week_start + timedelta(days=6)

    rows = (
        db.query(
            Teacher.id,
            Teacher.name,
            Academy.name.label("academy_name"),
            Subject.name.label("subject_name"),
            func.sum(DailyReport.mention_count).label("mention_count"),
            func.sum(DailyReport.post_mention_count).label("post_mention_count"),
            func.sum(DailyReport.comment_mention_count).label("comment_mention_count"),
            func.sum(DailyReport.positive_count).label("positive_count"),
            func.sum(DailyReport.negative_count).label("negative_count"),
            func.sum(DailyReport.neutral_count).label("neutral_count"),
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment_score"),
            func.sum(DailyReport.recommendation_count).label("recommendation_count"),
        )
        .join(Teacher, DailyReport.teacher_id == Teacher.id)
        .outerjoin(Academy, Teacher.academy_id == Academy.id)
        .outerjoin(Subject, Teacher.subject_id == Subject.id)
        .filter(DailyReport.report_date.between(week_start, week_end))
        .group_by(Teacher.id, Teacher.name, Academy.name, Subject.name)
        .order_by(func.sum(DailyReport.mention_count).desc())
        .all()
    )

    summaries = []
    for row in rows:
        summaries.append({
            "teacherId": row.id,
            "teacherName": row.name,
            "academyName": row.academy_name,
            "subjectName": row.subject_name,
            "mentionCount": int(row.mention_count or 0),
            "postMentionCount": int(row.post_mention_count or 0),
            "commentMentionCount": int(row.comment_mention_count or 0),
            "positiveCount": int(row.positive_count or 0),
            "negativeCount": int(row.negative_count or 0),
            "neutralCount": int(row.neutral_count or 0),
            "avgSentimentScore": float(row.avg_sentiment_score) if row.avg_sentiment_score else None,
            "recommendationCount": int(row.recommendation_count or 0),
            "mentionChange": 0,
            "sentimentChange": None,
            "topKeywords": None,
            "summary": None,
        })

    label = _iso_week_to_month_label(year, week)
    return _build_period_response("weekly", label, str(week_start), str(week_end), summaries)


def get_monthly(db: Session, year: int, month: int):
    """월별 리포트"""
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)

    rows = (
        db.query(
            Teacher.id,
            Teacher.name,
            Academy.name.label("academy_name"),
            Subject.name.label("subject_name"),
            func.sum(DailyReport.mention_count).label("mention_count"),
            func.sum(DailyReport.post_mention_count).label("post_mention_count"),
            func.sum(DailyReport.comment_mention_count).label("comment_mention_count"),
            func.sum(DailyReport.positive_count).label("positive_count"),
            func.sum(DailyReport.negative_count).label("negative_count"),
            func.sum(DailyReport.neutral_count).label("neutral_count"),
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment_score"),
            func.sum(DailyReport.recommendation_count).label("recommendation_count"),
        )
        .join(Teacher, DailyReport.teacher_id == Teacher.id)
        .outerjoin(Academy, Teacher.academy_id == Academy.id)
        .outerjoin(Subject, Teacher.subject_id == Subject.id)
        .filter(DailyReport.report_date.between(month_start, month_end))
        .group_by(Teacher.id, Teacher.name, Academy.name, Subject.name)
        .order_by(func.sum(DailyReport.mention_count).desc())
        .all()
    )

    summaries = []
    for row in rows:
        summaries.append({
            "teacherId": row.id,
            "teacherName": row.name,
            "academyName": row.academy_name,
            "subjectName": row.subject_name,
            "mentionCount": int(row.mention_count or 0),
            "postMentionCount": int(row.post_mention_count or 0),
            "commentMentionCount": int(row.comment_mention_count or 0),
            "positiveCount": int(row.positive_count or 0),
            "negativeCount": int(row.negative_count or 0),
            "neutralCount": int(row.neutral_count or 0),
            "avgSentimentScore": float(row.avg_sentiment_score) if row.avg_sentiment_score else None,
            "recommendationCount": int(row.recommendation_count or 0),
            "mentionChange": 0,
            "sentimentChange": None,
            "topKeywords": None,
            "summary": None,
        })

    label = f"{year}년 {month}월"
    return _build_period_response("monthly", label, str(month_start), str(month_end), summaries)


def get_periods(db: Session):
    """선택 가능한 기간 목록"""
    dates = (
        db.query(DailyReport.report_date)
        .distinct()
        .order_by(DailyReport.report_date.desc())
        .limit(90)
        .all()
    )

    daily = []
    weekly_set = {}
    monthly_set = {}

    for (d,) in dates:
        daily.append({
            "date": str(d),
            "label": d.strftime("%Y년 %m월 %d일 (%a)"),
        })

        iso = d.isocalendar()
        wk_key = (iso[0], iso[1])
        if wk_key not in weekly_set:
            weekly_set[wk_key] = {
                "year": iso[0],
                "week": iso[1],
                "label": _iso_week_to_month_label(iso[0], iso[1]),
            }

        mk_key = (d.year, d.month)
        if mk_key not in monthly_set:
            monthly_set[mk_key] = {
                "year": d.year,
                "month": d.month,
                "label": f"{d.year}년 {d.month}월",
            }

    return {
        "daily": daily,
        "weekly": sorted(weekly_set.values(), key=lambda x: (x["year"], x["week"]), reverse=True),
        "monthly": sorted(monthly_set.values(), key=lambda x: (x["year"], x["month"]), reverse=True),
    }
