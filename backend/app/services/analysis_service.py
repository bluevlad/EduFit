"""분석 서비스"""
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from ..models.daily_report import DailyReport
from ..models.teacher import Teacher
from ..models.teacher_mention import TeacherMention
from ..models.academy import Academy
from ..models.academy_daily_stat import AcademyDailyStat
from ..models.subject import Subject


def get_summary(db: Session, report_date: Optional[str] = None):
    """오늘 요약 통계"""
    target_date = date.fromisoformat(report_date) if report_date else date.today()

    row = (
        db.query(
            func.sum(DailyReport.mention_count).label("total_mentions"),
            func.sum(DailyReport.positive_count).label("total_positive"),
            func.sum(DailyReport.negative_count).label("total_negative"),
            func.sum(DailyReport.recommendation_count).label("total_recommendations"),
            func.count(distinct(DailyReport.teacher_id)).label("total_teachers"),
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
        )
        .filter(DailyReport.report_date == target_date)
        .first()
    )

    return {
        "totalMentions": int(row.total_mentions or 0),
        "totalPositive": int(row.total_positive or 0),
        "totalNegative": int(row.total_negative or 0),
        "totalRecommendations": int(row.total_recommendations or 0),
        "totalTeachers": int(row.total_teachers or 0),
        "avgSentimentScore": float(row.avg_sentiment) if row.avg_sentiment else None,
    }


def get_ranking(db: Session, report_date: Optional[str] = None, limit: int = 20):
    """강사 랭킹"""
    target_date = date.fromisoformat(report_date) if report_date else date.today()

    rows = (
        db.query(DailyReport, Teacher, Academy, Subject)
        .join(Teacher, DailyReport.teacher_id == Teacher.id)
        .outerjoin(Academy, Teacher.academy_id == Academy.id)
        .outerjoin(Subject, Teacher.subject_id == Subject.id)
        .filter(DailyReport.report_date == target_date)
        .order_by(DailyReport.mention_count.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "teacherId": t.id,
            "teacherName": t.name,
            "academyName": a.name if a else None,
            "subjectName": s.name if s else None,
            "mentionCount": r.mention_count or 0,
            "positiveCount": r.positive_count or 0,
            "negativeCount": r.negative_count or 0,
            "avgSentimentScore": r.avg_sentiment_score,
            "recommendationCount": r.recommendation_count or 0,
        }
        for r, t, a, s in rows
    ]


def get_academy_stats(db: Session, report_date: Optional[str] = None):
    """학원별 통계"""
    target_date = date.fromisoformat(report_date) if report_date else date.today()

    rows = (
        db.query(AcademyDailyStat, Academy)
        .join(Academy, AcademyDailyStat.academy_id == Academy.id)
        .filter(AcademyDailyStat.report_date == target_date)
        .order_by(AcademyDailyStat.total_mentions.desc())
        .all()
    )

    if not rows:
        # 해당 날짜에 academy_daily_stats가 없으면 daily_reports에서 집계
        agg_rows = (
            db.query(
                Academy.id,
                Academy.name,
                func.sum(DailyReport.mention_count).label("total_mentions"),
                func.count(distinct(DailyReport.teacher_id)).label("total_teachers"),
                func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
            )
            .join(Teacher, Teacher.academy_id == Academy.id)
            .join(DailyReport, DailyReport.teacher_id == Teacher.id)
            .filter(DailyReport.report_date == target_date)
            .group_by(Academy.id, Academy.name)
            .order_by(func.sum(DailyReport.mention_count).desc())
            .all()
        )

        result = []
        for row in agg_rows:
            # TOP 강사 조회
            top_teacher = (
                db.query(Teacher.name)
                .join(DailyReport, DailyReport.teacher_id == Teacher.id)
                .filter(Teacher.academy_id == row.id)
                .filter(DailyReport.report_date == target_date)
                .order_by(DailyReport.mention_count.desc())
                .first()
            )
            result.append({
                "academyId": row.id,
                "academyName": row.name,
                "totalMentions": int(row.total_mentions or 0),
                "totalTeachersMentioned": int(row.total_teachers or 0),
                "avgSentimentScore": float(row.avg_sentiment) if row.avg_sentiment else None,
                "topTeacherName": top_teacher[0] if top_teacher else None,
            })
        return result

    result = []
    for stat, academy in rows:
        top_teacher_name = None
        if stat.top_teacher_id:
            top_t = db.query(Teacher.name).filter(Teacher.id == stat.top_teacher_id).first()
            top_teacher_name = top_t[0] if top_t else None

        result.append({
            "academyId": academy.id,
            "academyName": academy.name,
            "totalMentions": stat.total_mentions or 0,
            "totalTeachersMentioned": stat.total_teachers_mentioned or 0,
            "avgSentimentScore": stat.avg_sentiment_score,
            "topTeacherName": top_teacher_name,
        })

    return result


def get_teacher_mentions(db: Session, teacher_id: int, limit: int = 10):
    """강사별 최근 멘션"""
    mentions = (
        db.query(TeacherMention)
        .filter(TeacherMention.teacher_id == teacher_id)
        .order_by(TeacherMention.analyzed_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": m.id,
            "mentionType": m.mention_type,
            "matchedText": m.matched_text,
            "context": m.context,
            "sentiment": m.sentiment,
            "sentimentScore": m.sentiment_score,
            "isRecommended": m.is_recommended,
            "analyzedAt": m.analyzed_at.isoformat() if m.analyzed_at else None,
        }
        for m in mentions
    ]


def get_teacher_reports(db: Session, teacher_id: int, days: int = 7):
    """강사별 리포트 이력"""
    since = date.today() - timedelta(days=days)

    reports = (
        db.query(DailyReport)
        .filter(DailyReport.teacher_id == teacher_id)
        .filter(DailyReport.report_date >= since)
        .order_by(DailyReport.report_date.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "reportDate": str(r.report_date),
            "mentionCount": r.mention_count or 0,
            "positiveCount": r.positive_count or 0,
            "negativeCount": r.negative_count or 0,
            "neutralCount": r.neutral_count or 0,
            "recommendationCount": r.recommendation_count or 0,
            "mentionChange": r.mention_change or 0,
            "avgSentimentScore": r.avg_sentiment_score,
            "summary": r.summary,
        }
        for r in reports
    ]
