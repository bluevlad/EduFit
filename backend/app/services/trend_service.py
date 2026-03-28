"""트렌드 분석 서비스 - 이동평균, 볼린저밴드, 모멘텀, 파레토, 계절성"""
import math
from collections import defaultdict
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, distinct, extract
from sqlalchemy.orm import Session

from ..models.daily_report import DailyReport
from ..models.teacher import Teacher
from ..models.academy import Academy
from ..models.subject import Subject


DAY_NAMES_KO = ["월", "화", "수", "목", "금", "토", "일"]


def _safe_div(a, b):
    """0 나눗셈 방지"""
    return a / b if b else None


def _calc_moving_average(values: list[float], window: int) -> list[Optional[float]]:
    """단순 이동평균 계산"""
    result = []
    for i in range(len(values)):
        if i < window - 1:
            result.append(None)
        else:
            avg = sum(values[i - window + 1 : i + 1]) / window
            result.append(round(avg, 2))
    return result


def _calc_std(values: list[float], window: int) -> list[Optional[float]]:
    """이동 표준편차 계산"""
    result = []
    for i in range(len(values)):
        if i < window - 1:
            result.append(None)
        else:
            subset = values[i - window + 1 : i + 1]
            mean = sum(subset) / window
            variance = sum((x - mean) ** 2 for x in subset) / window
            result.append(round(math.sqrt(variance), 4))
    return result


def get_mention_trend(db: Session, days: int = 90):
    """언급량 이동평균 트렌드"""
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            DailyReport.report_date,
            func.sum(DailyReport.mention_count).label("mentions"),
        )
        .filter(DailyReport.report_date >= since)
        .group_by(DailyReport.report_date)
        .order_by(DailyReport.report_date)
        .all()
    )

    if not rows:
        return {"dataPoints": [], "crossoverSignals": []}

    dates = [str(r.report_date) for r in rows]
    values = [float(r.mentions or 0) for r in rows]

    ma7 = _calc_moving_average(values, 7)
    ma21 = _calc_moving_average(values, 21)

    data_points = []
    for i in range(len(dates)):
        data_points.append({
            "date": dates[i],
            "value": values[i],
            "ma7": ma7[i],
            "ma21": ma21[i],
        })

    # 골든크로스/데드크로스 시그널 탐지
    crossover_signals = []
    for i in range(1, len(dates)):
        if ma7[i] is None or ma21[i] is None or ma7[i - 1] is None or ma21[i - 1] is None:
            continue
        prev_diff = ma7[i - 1] - ma21[i - 1]
        curr_diff = ma7[i] - ma21[i]
        if prev_diff <= 0 < curr_diff:
            crossover_signals.append({
                "date": dates[i],
                "type": "golden_cross",
                "label": "관심 급증 시그널",
            })
        elif prev_diff >= 0 > curr_diff:
            crossover_signals.append({
                "date": dates[i],
                "type": "dead_cross",
                "label": "관심 감소 시그널",
            })

    return {"dataPoints": data_points, "crossoverSignals": crossover_signals}


def get_sentiment_bollinger(db: Session, days: int = 90):
    """감성점수 볼린저 밴드"""
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            DailyReport.report_date,
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
        )
        .filter(DailyReport.report_date >= since)
        .filter(DailyReport.avg_sentiment_score.isnot(None))
        .group_by(DailyReport.report_date)
        .order_by(DailyReport.report_date)
        .all()
    )

    if not rows:
        return {"dataPoints": [], "anomalies": [], "bandWidth": None}

    dates = [str(r.report_date) for r in rows]
    values = [float(r.avg_sentiment) for r in rows]

    window = min(20, len(values))
    ma20 = _calc_moving_average(values, window)
    std20 = _calc_std(values, window)

    data_points = []
    anomalies = []
    band_widths = []

    for i in range(len(dates)):
        upper = round(ma20[i] + 2 * std20[i], 4) if ma20[i] is not None and std20[i] is not None else None
        lower = round(ma20[i] - 2 * std20[i], 4) if ma20[i] is not None and std20[i] is not None else None
        is_anomaly = False

        if upper is not None and lower is not None:
            is_anomaly = values[i] > upper or values[i] < lower
            band_widths.append(upper - lower)

        if is_anomaly:
            direction = "positive" if values[i] > upper else "negative"
            anomalies.append({
                "date": dates[i],
                "value": round(values[i], 4),
                "direction": direction,
                "label": f"{'긍정' if direction == 'positive' else '부정'} 이상치 감지",
            })

        data_points.append({
            "date": dates[i],
            "value": round(values[i], 4),
            "ma20": ma20[i],
            "upperBand": upper,
            "lowerBand": lower,
            "isAnomaly": is_anomaly,
        })

    avg_band_width = round(sum(band_widths) / len(band_widths), 4) if band_widths else None

    return {
        "dataPoints": data_points,
        "anomalies": anomalies,
        "bandWidth": avg_band_width,
    }


def get_momentum_ranking(db: Session, limit: int = 20):
    """모멘텀 기반 강사 랭킹 (4주/8주 ROC)"""
    today = date.today()
    w4_start = today - timedelta(weeks=4)
    w8_start = today - timedelta(weeks=8)
    w4_prev_start = w8_start
    w4_prev_end = w4_start - timedelta(days=1)

    # 최근 4주 집계
    recent_rows = (
        db.query(
            DailyReport.teacher_id,
            func.sum(DailyReport.mention_count).label("mentions"),
            func.sum(DailyReport.positive_count).label("positive"),
            func.sum(DailyReport.negative_count).label("negative"),
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
        )
        .filter(DailyReport.report_date >= w4_start)
        .group_by(DailyReport.teacher_id)
        .all()
    )

    recent_map = {}
    for r in recent_rows:
        total = int(r.mentions or 0)
        pos = int(r.positive or 0)
        recent_map[r.teacher_id] = {
            "mentions": total,
            "positive": pos,
            "negative": int(r.negative or 0),
            "avg_sentiment": float(r.avg_sentiment) if r.avg_sentiment else None,
            "positive_ratio": round(pos / total * 100, 1) if total > 0 else None,
        }

    # 이전 4주 (4~8주 전) 집계
    prev_rows = (
        db.query(
            DailyReport.teacher_id,
            func.sum(DailyReport.mention_count).label("mentions"),
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
        )
        .filter(DailyReport.report_date >= w4_prev_start)
        .filter(DailyReport.report_date <= w4_prev_end)
        .group_by(DailyReport.teacher_id)
        .all()
    )

    prev_map = {r.teacher_id: {"mentions": int(r.mentions or 0),
                                "avg_sentiment": float(r.avg_sentiment) if r.avg_sentiment else None}
                for r in prev_rows}

    # 8주 전 집계 (8주 ROC 용)
    w8_prev_start = today - timedelta(weeks=16)
    w8_prev_end = w8_start - timedelta(days=1)

    prev8_rows = (
        db.query(
            DailyReport.teacher_id,
            func.sum(DailyReport.mention_count).label("mentions"),
        )
        .filter(DailyReport.report_date >= w8_prev_start)
        .filter(DailyReport.report_date <= w8_prev_end)
        .group_by(DailyReport.teacher_id)
        .all()
    )

    prev8_map = {r.teacher_id: int(r.mentions or 0) for r in prev8_rows}

    # 강사 정보 조회
    all_teacher_ids = set(recent_map.keys())
    teachers_info = (
        db.query(Teacher, Academy, Subject)
        .outerjoin(Academy, Teacher.academy_id == Academy.id)
        .outerjoin(Subject, Teacher.subject_id == Subject.id)
        .filter(Teacher.id.in_(all_teacher_ids))
        .all()
    )

    teacher_map = {}
    for t, a, s in teachers_info:
        teacher_map[t.id] = {
            "name": t.name,
            "academy": a.name if a else None,
            "subject": s.name if s else None,
        }

    # 모멘텀 계산
    results = []
    for tid, data in recent_map.items():
        prev_mentions = prev_map.get(tid, {}).get("mentions", 0)
        prev8_mentions = prev8_map.get(tid, 0)
        prev_sentiment = prev_map.get(tid, {}).get("avg_sentiment")

        roc4w = _safe_div((data["mentions"] - prev_mentions), prev_mentions) * 100 if prev_mentions else None
        roc8w = _safe_div((data["mentions"] - prev8_mentions), prev8_mentions) * 100 if prev8_mentions else None

        sentiment_change = None
        if data["avg_sentiment"] is not None and prev_sentiment is not None:
            sentiment_change = round(data["avg_sentiment"] - prev_sentiment, 4)

        # 모멘텀 시그널 결정
        signal = "stable"
        if roc4w is not None:
            if roc4w >= 50:
                signal = "surge"
            elif roc4w >= 20:
                signal = "rising"
            elif roc4w <= -50:
                signal = "plunge"
            elif roc4w <= -20:
                signal = "falling"

        info = teacher_map.get(tid, {"name": f"강사#{tid}", "academy": None, "subject": None})

        results.append({
            "teacherId": tid,
            "teacherName": info["name"],
            "academyName": info["academy"],
            "subjectName": info["subject"],
            "currentMentions": data["mentions"],
            "previousMentions": prev_mentions,
            "roc4w": round(roc4w, 1) if roc4w is not None else None,
            "roc8w": round(roc8w, 1) if roc8w is not None else None,
            "avgSentimentScore": round(data["avg_sentiment"], 4) if data["avg_sentiment"] else None,
            "sentimentChange": sentiment_change,
            "momentumSignal": signal,
            "positiveRatio": data["positive_ratio"],
        })

    # 모멘텀 순 (roc4w 기준) 정렬, None은 뒤로
    results.sort(key=lambda x: (x["roc4w"] is None, -(x["roc4w"] or 0)))

    return {
        "period": f"{w4_start} ~ {today}",
        "teachers": results[:limit],
    }


def get_pareto(db: Session, days: int = 90):
    """파레토 분석 (80/20 법칙)"""
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            DailyReport.teacher_id,
            Teacher.name,
            Academy.name.label("academy_name"),
            func.sum(DailyReport.mention_count).label("total_mentions"),
        )
        .join(Teacher, DailyReport.teacher_id == Teacher.id)
        .outerjoin(Academy, Teacher.academy_id == Academy.id)
        .filter(DailyReport.report_date >= since)
        .group_by(DailyReport.teacher_id, Teacher.name, Academy.name)
        .order_by(func.sum(DailyReport.mention_count).desc())
        .all()
    )

    if not rows:
        return {"items": [], "top5Ratio": None, "top10Ratio": None, "concentrationIndex": None}

    total = sum(int(r.total_mentions or 0) for r in rows)
    cumulative = 0
    items = []

    for r in rows:
        count = int(r.total_mentions or 0)
        ratio = round(count / total * 100, 1) if total else 0
        cumulative += ratio
        items.append({
            "teacherId": r.teacher_id,
            "teacherName": r.name,
            "academyName": r.academy_name,
            "mentionCount": count,
            "ratio": ratio,
            "cumulativeRatio": round(cumulative, 1),
        })

    top5_ratio = items[4]["cumulativeRatio"] if len(items) >= 5 else (items[-1]["cumulativeRatio"] if items else None)
    top10_ratio = items[9]["cumulativeRatio"] if len(items) >= 10 else (items[-1]["cumulativeRatio"] if items else None)

    # HHI (허핀달-허쉬만 지수) 집중도
    hhi = sum((count / total * 100) ** 2 for count in [int(r.total_mentions or 0) for r in rows]) if total else None

    return {
        "items": items,
        "top5Ratio": top5_ratio,
        "top10Ratio": top10_ratio,
        "concentrationIndex": round(hhi, 1) if hhi else None,
    }


def get_seasonality(db: Session, days: int = 90):
    """요일별 계절성 분석"""
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            extract("dow", DailyReport.report_date).label("dow"),
            func.avg(DailyReport.mention_count).label("avg_mentions"),
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
        )
        .filter(DailyReport.report_date >= since)
        .group_by(extract("dow", DailyReport.report_date))
        .order_by(extract("dow", DailyReport.report_date))
        .all()
    )

    # PostgreSQL dow: 0=Sunday, 1=Monday, ..., 6=Saturday
    # 월~일 순으로 변환
    day_data = {}
    for r in rows:
        dow = int(r.dow)
        # PostgreSQL: 0=Sun -> 6, 1=Mon -> 0, ..., 6=Sat -> 5
        mapped = (dow - 1) % 7
        day_data[mapped] = {
            "dayOfWeek": mapped,
            "dayName": DAY_NAMES_KO[mapped],
            "avgMentions": round(float(r.avg_mentions or 0), 1),
            "avgSentiment": round(float(r.avg_sentiment), 4) if r.avg_sentiment else None,
        }

    pattern = [day_data.get(i, {"dayOfWeek": i, "dayName": DAY_NAMES_KO[i], "avgMentions": 0, "avgSentiment": None})
               for i in range(7)]

    peak = max(pattern, key=lambda x: x["avgMentions"]) if pattern else None
    low = min(pattern, key=lambda x: x["avgMentions"]) if pattern else None

    return {
        "dailyPattern": pattern,
        "peakDay": peak["dayName"] if peak else None,
        "lowDay": low["dayName"] if low else None,
    }


def get_correlation(db: Session, days: int = 90):
    """지표 간 상관관계 분석"""
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            DailyReport.mention_count,
            DailyReport.positive_count,
            DailyReport.negative_count,
            DailyReport.recommendation_count,
            DailyReport.avg_sentiment_score,
        )
        .filter(DailyReport.report_date >= since)
        .filter(DailyReport.avg_sentiment_score.isnot(None))
        .all()
    )

    if len(rows) < 5:
        return {"pairs": [], "insights": []}

    metrics = {
        "mentionCount": [float(r.mention_count or 0) for r in rows],
        "positiveCount": [float(r.positive_count or 0) for r in rows],
        "negativeCount": [float(r.negative_count or 0) for r in rows],
        "recommendationCount": [float(r.recommendation_count or 0) for r in rows],
        "sentimentScore": [float(r.avg_sentiment_score or 0) for r in rows],
    }

    metric_labels = {
        "mentionCount": "언급수",
        "positiveCount": "긍정수",
        "negativeCount": "부정수",
        "recommendationCount": "추천수",
        "sentimentScore": "감성점수",
    }

    def pearson(x, y):
        n = len(x)
        if n == 0:
            return 0
        mx, my = sum(x) / n, sum(y) / n
        sx = math.sqrt(sum((xi - mx) ** 2 for xi in x) / n)
        sy = math.sqrt(sum((yi - my) ** 2 for yi in y) / n)
        if sx == 0 or sy == 0:
            return 0
        cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / n
        return round(cov / (sx * sy), 3)

    def strength_label(r):
        ar = abs(r)
        if ar >= 0.7:
            return "strong"
        elif ar >= 0.4:
            return "moderate"
        elif ar >= 0.2:
            return "weak"
        return "negligible"

    keys = list(metrics.keys())
    pairs = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            r = pearson(metrics[keys[i]], metrics[keys[j]])
            pairs.append({
                "metric1": keys[i],
                "metric2": keys[j],
                "correlation": r,
                "strength": strength_label(r),
            })

    # 주요 인사이트 생성
    insights = []
    strong_pairs = [p for p in pairs if abs(p["correlation"]) >= 0.5]
    for p in sorted(strong_pairs, key=lambda x: abs(x["correlation"]), reverse=True)[:3]:
        direction = "양의" if p["correlation"] > 0 else "음의"
        m1 = metric_labels[p["metric1"]]
        m2 = metric_labels[p["metric2"]]
        insights.append(
            f"{m1}와(과) {m2} 사이에 {direction} 상관관계가 있습니다 (r={p['correlation']})"
        )

    return {"pairs": pairs, "insights": insights}


def get_teacher_heatmap(db: Session, weeks: int = 12, limit: int = 15):
    """강사별 주간 감성 히트맵 (주차×강사 매트릭스)"""
    today = date.today()
    since = today - timedelta(weeks=weeks)

    # 주차별 강사별 집계
    rows = (
        db.query(
            extract("isoyear", DailyReport.report_date).label("iso_year"),
            extract("week", DailyReport.report_date).label("iso_week"),
            DailyReport.teacher_id,
            func.sum(DailyReport.mention_count).label("mentions"),
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
        )
        .filter(DailyReport.report_date >= since)
        .group_by(
            extract("isoyear", DailyReport.report_date),
            extract("week", DailyReport.report_date),
            DailyReport.teacher_id,
        )
        .all()
    )

    if not rows:
        return {"weeks": [], "teachers": [], "matrix": []}

    # 전체 기간 총 언급수로 TOP 강사 선정
    teacher_totals = defaultdict(int)
    for r in rows:
        teacher_totals[r.teacher_id] += int(r.mentions or 0)

    top_teacher_ids = sorted(teacher_totals, key=teacher_totals.get, reverse=True)[:limit]
    top_set = set(top_teacher_ids)

    # 강사 정보 조회
    teachers_info = (
        db.query(Teacher, Academy)
        .outerjoin(Academy, Teacher.academy_id == Academy.id)
        .filter(Teacher.id.in_(top_teacher_ids))
        .all()
    )
    teacher_map = {t.id: {"id": t.id, "name": t.name, "academy": a.name if a else None}
                   for t, a in teachers_info}

    # 주차 목록 정렬
    week_keys = sorted({(int(r.iso_year), int(r.iso_week)) for r in rows})
    week_labels = [f"{y}-W{w:02d}" for y, w in week_keys]

    # 매트릭스 구성 (row=teacher, col=week)
    data_map = {}
    for r in rows:
        if r.teacher_id not in top_set:
            continue
        key = (r.teacher_id, int(r.iso_year), int(r.iso_week))
        data_map[key] = {
            "sentiment": round(float(r.avg_sentiment), 4) if r.avg_sentiment is not None else None,
            "mentions": int(r.mentions or 0),
        }

    matrix = []
    for tid in top_teacher_ids:
        row = []
        for y, w in week_keys:
            cell = data_map.get((tid, y, w), {"sentiment": None, "mentions": 0})
            row.append(cell)
        matrix.append(row)

    teachers_list = [teacher_map.get(tid, {"id": tid, "name": f"강사#{tid}", "academy": None})
                     for tid in top_teacher_ids]

    return {
        "weeks": week_labels,
        "teachers": teachers_list,
        "matrix": matrix,
    }


def get_academy_bubble(db: Session, days: int = 90):
    """학원별 버블차트 데이터 (x=언급, y=감성, 크기=강사수)"""
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            Academy.id,
            Academy.name,
            func.sum(DailyReport.mention_count).label("total_mentions"),
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
            func.count(distinct(DailyReport.teacher_id)).label("teacher_count"),
        )
        .join(Teacher, Teacher.academy_id == Academy.id)
        .join(DailyReport, DailyReport.teacher_id == Teacher.id)
        .filter(DailyReport.report_date >= since)
        .group_by(Academy.id, Academy.name)
        .order_by(func.sum(DailyReport.mention_count).desc())
        .all()
    )

    academies = []
    for r in rows:
        academies.append({
            "academyId": r.id,
            "academyName": r.name,
            "totalMentions": int(r.total_mentions or 0),
            "avgSentiment": round(float(r.avg_sentiment), 4) if r.avg_sentiment is not None else None,
            "teacherCount": int(r.teacher_count or 0),
        })

    return {"academies": academies}


def get_overview_kpi(db: Session, days: int = 90):
    """종합 KPI 지표"""
    today = date.today()
    since = today - timedelta(days=days)
    mid = today - timedelta(days=days // 2)

    # 전체 기간 집계
    total_row = (
        db.query(
            func.sum(DailyReport.mention_count).label("total"),
            func.avg(DailyReport.avg_sentiment_score).label("avg_sentiment"),
            func.count(distinct(DailyReport.teacher_id)).label("teachers"),
            func.min(DailyReport.report_date).label("start_date"),
            func.max(DailyReport.report_date).label("end_date"),
        )
        .filter(DailyReport.report_date >= since)
        .first()
    )

    # 최근 절반 vs 이전 절반 비교 (성장률)
    recent_total = (
        db.query(func.sum(DailyReport.mention_count))
        .filter(DailyReport.report_date >= mid)
        .scalar()
    )

    prev_total = (
        db.query(func.sum(DailyReport.mention_count))
        .filter(DailyReport.report_date >= since)
        .filter(DailyReport.report_date < mid)
        .scalar()
    )

    recent_sentiment = (
        db.query(func.avg(DailyReport.avg_sentiment_score))
        .filter(DailyReport.report_date >= mid)
        .filter(DailyReport.avg_sentiment_score.isnot(None))
        .scalar()
    )

    prev_sentiment = (
        db.query(func.avg(DailyReport.avg_sentiment_score))
        .filter(DailyReport.report_date >= since)
        .filter(DailyReport.report_date < mid)
        .filter(DailyReport.avg_sentiment_score.isnot(None))
        .scalar()
    )

    growth_rate = None
    if recent_total and prev_total and prev_total > 0:
        growth_rate = round((int(recent_total) - int(prev_total)) / int(prev_total) * 100, 1)

    sentiment_trend = None
    if recent_sentiment is not None and prev_sentiment is not None:
        sentiment_trend = round(float(recent_sentiment) - float(prev_sentiment), 4)

    # 변동성 (일별 언급수의 변동계수)
    daily_rows = (
        db.query(func.sum(DailyReport.mention_count).label("daily_total"))
        .filter(DailyReport.report_date >= since)
        .group_by(DailyReport.report_date)
        .all()
    )

    volatility = None
    volatility_level = "stable"
    if len(daily_rows) > 1:
        vals = [float(r.daily_total or 0) for r in daily_rows]
        mean = sum(vals) / len(vals)
        if mean > 0:
            std = math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals))
            volatility = round(std / mean * 100, 1)  # CV (%)
            if volatility >= 50:
                volatility_level = "high"
            elif volatility >= 25:
                volatility_level = "moderate"

    return {
        "totalMentions": int(total_row.total or 0),
        "mentionGrowthRate": growth_rate,
        "avgSentimentScore": round(float(total_row.avg_sentiment), 4) if total_row.avg_sentiment else None,
        "sentimentTrend": sentiment_trend,
        "volatility": volatility,
        "volatilityLevel": volatility_level,
        "totalTeachers": int(total_row.teachers or 0),
        "dataStartDate": str(total_row.start_date) if total_row.start_date else None,
        "dataEndDate": str(total_row.end_date) if total_row.end_date else None,
    }


def get_dashboard(db: Session, days: int = 90):
    """종합 트렌드 대시보드 데이터"""
    return {
        "kpi": get_overview_kpi(db, days),
        "mentionTrend": get_mention_trend(db, days),
        "sentimentBollinger": get_sentiment_bollinger(db, days),
        "momentumRanking": get_momentum_ranking(db),
        "pareto": get_pareto(db, days),
        "seasonality": get_seasonality(db, days),
        "correlation": get_correlation(db, days),
        "teacherHeatmap": get_teacher_heatmap(db),
        "academyBubble": get_academy_bubble(db, days),
    }
