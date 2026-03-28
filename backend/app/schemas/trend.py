"""트렌드 분석 스키마"""
from typing import Optional
from pydantic import BaseModel


class TrendDataPoint(BaseModel):
    """일별 트렌드 데이터 포인트"""
    date: str
    mentionCount: int = 0
    positiveCount: int = 0
    negativeCount: int = 0
    neutralCount: int = 0
    recommendationCount: int = 0
    avgSentimentScore: Optional[float] = None


class MovingAveragePoint(BaseModel):
    """이동평균 데이터 포인트"""
    date: str
    value: float
    ma7: Optional[float] = None
    ma21: Optional[float] = None


class BollingerBandPoint(BaseModel):
    """볼린저 밴드 데이터 포인트"""
    date: str
    value: float
    ma20: Optional[float] = None
    upperBand: Optional[float] = None
    lowerBand: Optional[float] = None
    isAnomaly: bool = False


class MentionTrendResponse(BaseModel):
    """언급량 이동평균 트렌드 응답"""
    dataPoints: list[MovingAveragePoint] = []
    crossoverSignals: list[dict] = []


class SentimentBollingerResponse(BaseModel):
    """감성점수 볼린저 밴드 응답"""
    dataPoints: list[BollingerBandPoint] = []
    anomalies: list[dict] = []
    bandWidth: Optional[float] = None


class MomentumTeacher(BaseModel):
    """모멘텀 기반 강사 랭킹"""
    teacherId: int
    teacherName: str
    academyName: Optional[str] = None
    subjectName: Optional[str] = None
    currentMentions: int = 0
    previousMentions: int = 0
    roc4w: Optional[float] = None
    roc8w: Optional[float] = None
    avgSentimentScore: Optional[float] = None
    sentimentChange: Optional[float] = None
    momentumSignal: str = "stable"
    positiveRatio: Optional[float] = None


class MomentumRankingResponse(BaseModel):
    """모멘텀 랭킹 응답"""
    period: str
    teachers: list[MomentumTeacher] = []


class ParetoItem(BaseModel):
    """파레토 분석 아이템"""
    teacherId: int
    teacherName: str
    academyName: Optional[str] = None
    mentionCount: int = 0
    ratio: float = 0.0
    cumulativeRatio: float = 0.0


class ParetoResponse(BaseModel):
    """파레토 분석 응답"""
    items: list[ParetoItem] = []
    top5Ratio: Optional[float] = None
    top10Ratio: Optional[float] = None
    concentrationIndex: Optional[float] = None


class SeasonalityDay(BaseModel):
    """요일별 패턴"""
    dayOfWeek: int
    dayName: str
    avgMentions: float = 0.0
    avgSentiment: Optional[float] = None


class SeasonalityResponse(BaseModel):
    """계절성 분석 응답"""
    dailyPattern: list[SeasonalityDay] = []
    peakDay: Optional[str] = None
    lowDay: Optional[str] = None


class CorrelationPair(BaseModel):
    """상관관계 쌍"""
    metric1: str
    metric2: str
    correlation: float
    strength: str


class CorrelationResponse(BaseModel):
    """상관관계 분석 응답"""
    pairs: list[CorrelationPair] = []
    insights: list[str] = []


class TrendOverviewKPI(BaseModel):
    """트렌드 종합 KPI"""
    totalMentions: int = 0
    mentionGrowthRate: Optional[float] = None
    avgSentimentScore: Optional[float] = None
    sentimentTrend: Optional[float] = None
    volatility: Optional[float] = None
    volatilityLevel: str = "stable"
    totalTeachers: int = 0
    dataStartDate: Optional[str] = None
    dataEndDate: Optional[str] = None


class HeatmapCell(BaseModel):
    """히트맵 셀"""
    sentiment: Optional[float] = None
    mentions: int = 0


class HeatmapTeacher(BaseModel):
    """히트맵 강사 정보"""
    id: int
    name: str
    academy: Optional[str] = None


class TeacherHeatmapResponse(BaseModel):
    """강사 히트맵 응답"""
    weeks: list[str] = []
    teachers: list[HeatmapTeacher] = []
    matrix: list[list[HeatmapCell]] = []


class AcademyBubbleItem(BaseModel):
    """학원 버블 아이템"""
    academyId: int
    academyName: str
    totalMentions: int = 0
    avgSentiment: Optional[float] = None
    teacherCount: int = 0


class AcademyBubbleResponse(BaseModel):
    """학원 버블차트 응답"""
    academies: list[AcademyBubbleItem] = []


class TrendDashboardResponse(BaseModel):
    """트렌드 대시보드 종합 응답"""
    kpi: TrendOverviewKPI
    mentionTrend: MentionTrendResponse
    sentimentBollinger: SentimentBollingerResponse
    momentumRanking: MomentumRankingResponse
    pareto: ParetoResponse
    seasonality: SeasonalityResponse
    correlation: CorrelationResponse
    teacherHeatmap: TeacherHeatmapResponse
    academyBubble: AcademyBubbleResponse
