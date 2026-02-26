"""리포트 관련 스키마"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class TeacherReportSummary(BaseModel):
    """강사별 리포트 요약 (일별/주별/월별 공통)"""
    teacherId: int
    teacherName: str
    academyName: Optional[str] = None
    subjectName: Optional[str] = None
    mentionCount: int = 0
    postMentionCount: int = 0
    commentMentionCount: int = 0
    positiveCount: int = 0
    negativeCount: int = 0
    neutralCount: int = 0
    avgSentimentScore: Optional[float] = None
    recommendationCount: int = 0
    mentionChange: int = 0
    sentimentChange: Optional[float] = None
    topKeywords: Optional[list[str]] = None
    summary: Optional[str] = None


class PeriodReportResponse(BaseModel):
    """기간별 리포트 응답"""
    periodType: str
    periodLabel: str
    startDate: str
    endDate: str
    totalMentions: int = 0
    totalPositive: int = 0
    totalNegative: int = 0
    totalTeachers: int = 0
    avgSentimentScore: Optional[float] = None
    positiveRatio: Optional[float] = None
    teacherSummaries: list[TeacherReportSummary] = []


class DailyPeriod(BaseModel):
    date: str
    label: str


class WeeklyPeriod(BaseModel):
    year: int
    week: int
    label: str


class MonthlyPeriod(BaseModel):
    year: int
    month: int
    label: str


class PeriodsResponse(BaseModel):
    daily: list[DailyPeriod] = []
    weekly: list[WeeklyPeriod] = []
    monthly: list[MonthlyPeriod] = []


class AnalysisSummary(BaseModel):
    """분석 요약 통계"""
    totalMentions: int = 0
    totalPositive: int = 0
    totalNegative: int = 0
    totalRecommendations: int = 0
    totalTeachers: int = 0
    avgSentimentScore: Optional[float] = None


class TeacherRanking(BaseModel):
    """강사 랭킹"""
    teacherId: int
    teacherName: str
    academyName: Optional[str] = None
    subjectName: Optional[str] = None
    mentionCount: int = 0
    positiveCount: int = 0
    negativeCount: int = 0
    avgSentimentScore: Optional[float] = None
    recommendationCount: int = 0


class AcademyStats(BaseModel):
    """학원별 통계"""
    academyId: int
    academyName: str
    totalMentions: int = 0
    totalTeachersMentioned: int = 0
    avgSentimentScore: Optional[float] = None
    topTeacherName: Optional[str] = None


class MentionResponse(BaseModel):
    """멘션 응답"""
    id: int
    mentionType: str
    matchedText: Optional[str] = None
    context: Optional[str] = None
    sentiment: Optional[str] = None
    sentimentScore: Optional[float] = None
    isRecommended: Optional[bool] = None
    analyzedAt: Optional[datetime] = None


class TeacherReportHistory(BaseModel):
    """강사별 리포트 이력"""
    id: int
    reportDate: str
    mentionCount: int = 0
    positiveCount: int = 0
    negativeCount: int = 0
    neutralCount: int = 0
    recommendationCount: int = 0
    mentionChange: int = 0
    avgSentimentScore: Optional[float] = None
    summary: Optional[str] = None


class WeeklySummary(BaseModel):
    """주간 요약"""
    totalMentions: int = 0
    totalPositive: int = 0
    totalNegative: int = 0
    totalTeachers: int = 0
    totalRecommendations: int = 0
    mentionChangeRate: Optional[float] = None


class WeeklyTeacherReport(BaseModel):
    """주간 강사별 리포트"""
    id: Optional[int] = None
    teacherId: int
    teacherName: str
    academyName: Optional[str] = None
    mentionCount: int = 0
    positiveCount: int = 0
    negativeCount: int = 0
    avgSentimentScore: Optional[float] = None
    recommendationCount: int = 0
    weeklyRank: Optional[int] = None
    mentionChangeRate: Optional[float] = None
    topKeywords: Optional[list[str]] = None


class WeeklyTrendItem(BaseModel):
    """주간 트렌드 아이템"""
    year: int
    weekNumber: int
    weekLabel: str
    mentionCount: int = 0
    positiveCount: int = 0
    negativeCount: int = 0
    neutralCount: int = 0
    recommendationCount: int = 0
    avgSentimentScore: Optional[float] = None
    weeklyRank: Optional[int] = None
