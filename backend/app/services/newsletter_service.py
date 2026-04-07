"""월간 뉴스레터 HTML 생성 서비스

trend_service의 분석 데이터를 Jinja2 이메일 템플릿으로 렌더링합니다.
뉴스레터 플랫폼에서 발송 시 이 서비스가 생성한 HTML을 참조합니다.
"""
import os
from datetime import date, datetime, timedelta

from jinja2 import Environment, FileSystemLoader
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.collection_source import CollectionSource
from ..models.post import Post
from ..models.teacher_mention import TeacherMention
from . import trend_service

# 템플릿 디렉토리
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "templates", "email")


def _sentiment_cell(sentiment, mentions):
    """감성 점수를 히트맵 셀 스타일로 변환"""
    if sentiment is None:
        return {"bg": "#f5f5f5", "fg": "#ccc", "label": "-"}
    if sentiment >= 0.65:
        bg, fg = "#c8e6c9", "#2e7d32"
    elif sentiment >= 0.45:
        bg, fg = "#fff9c4", "#f57f17"
    else:
        bg, fg = "#ffcdd2", "#c62828"
    label = str(mentions) if mentions else "-"
    return {"bg": bg, "fg": fg, "label": label}


def _get_source_distribution(db: Session, days: int) -> dict:
    """소스 타입별 언급 수 집계 (news/cafe/gallery/forum)"""
    cutoff = date.today() - timedelta(days=days)
    rows = (
        db.query(
            CollectionSource.source_type,
            func.count(TeacherMention.id).label("cnt"),
        )
        .join(Post, TeacherMention.post_id == Post.id)
        .join(CollectionSource, Post.source_id == CollectionSource.id)
        .filter(Post.post_date >= cutoff)
        .group_by(CollectionSource.source_type)
        .all()
    )
    total = sum(r.cnt for r in rows) or 1
    source_type_labels = {
        "news": "뉴스",
        "cafe": "카페",
        "gallery": "갤러리",
        "forum": "포럼",
    }
    return {
        "distribution": [
            {
                "source_type": r.source_type,
                "label": source_type_labels.get(r.source_type, r.source_type),
                "mention_count": r.cnt,
                "ratio": round(r.cnt / total * 100, 1),
            }
            for r in rows
        ],
        "total": total,
    }


def _get_recent_news_articles(db: Session, days: int, limit: int = 10) -> list:
    """최근 뉴스 기사 원문 정보 (제목/URL/소스명/날짜)"""
    cutoff = date.today() - timedelta(days=days)
    posts = (
        db.query(
            Post,
            CollectionSource.name.label("source_name"),
            func.count(TeacherMention.id).label("mention_count"),
        )
        .join(CollectionSource, Post.source_id == CollectionSource.id)
        .outerjoin(TeacherMention, TeacherMention.post_id == Post.id)
        .filter(
            CollectionSource.source_type == "news",
            Post.post_date >= cutoff,
        )
        .group_by(Post.id, CollectionSource.name)
        .order_by(Post.post_date.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "title": row.Post.title,
            "url": row.Post.url,
            "source_name": row.source_name,
            "published_at": row.Post.post_date.strftime("%Y-%m-%d") if row.Post.post_date else None,
            "keyword": row.Post.author,
            "mention_count": row.mention_count,
        }
        for row in posts
    ]


def generate_newsletter_data(db: Session, days: int = 30):
    """뉴스레터에 필요한 데이터를 수집하고 가공"""
    kpi = trend_service.get_overview_kpi(db, days)
    mention_trend = trend_service.get_mention_trend(db, days)
    bollinger = trend_service.get_sentiment_bollinger(db, days)
    momentum = trend_service.get_momentum_ranking(db, limit=10)
    pareto = trend_service.get_pareto(db, days)
    seasonality = trend_service.get_seasonality(db, days)
    correlation = trend_service.get_correlation(db, days)
    heatmap = trend_service.get_teacher_heatmap(db, weeks=4, limit=10)
    academy_bubble = trend_service.get_academy_bubble(db, days)
    source_distribution = _get_source_distribution(db, days)
    news_articles = _get_recent_news_articles(db, days)

    return {
        "kpi": kpi,
        "mention_trend": mention_trend,
        "bollinger": bollinger,
        "momentum": momentum,
        "pareto": pareto,
        "seasonality": seasonality,
        "correlation": correlation,
        "heatmap": heatmap,
        "academy_bubble": academy_bubble,
        "source_distribution": source_distribution,
        "news_articles": news_articles,
    }


def render_newsletter_html(db: Session, year: int = None, month: int = None, days: int = 30) -> str:
    """월간 뉴스레터 HTML을 렌더링"""
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    period_label = f"{year}년 {month}월"

    data = generate_newsletter_data(db, days)

    # 히트맵 셀 가공
    heatmap = data["heatmap"]
    heatmap_cells = []
    heatmap_weeks_display = []

    if heatmap.get("weeks"):
        # 최근 4주만 표시
        weeks = heatmap["weeks"][-4:] if len(heatmap["weeks"]) > 4 else heatmap["weeks"]
        start_idx = len(heatmap["weeks"]) - len(weeks)
        heatmap_weeks_display = [w.split("-W")[1] + "주" if "-W" in w else w for w in weeks]

        for teacher_idx in range(len(heatmap.get("teachers", []))):
            row = heatmap["matrix"][teacher_idx] if teacher_idx < len(heatmap.get("matrix", [])) else []
            cells = []
            for w_idx in range(start_idx, len(heatmap.get("weeks", []))):
                if w_idx < len(row):
                    cell = row[w_idx]
                    cells.append(_sentiment_cell(cell.get("sentiment"), cell.get("mentions", 0)))
                else:
                    cells.append({"bg": "#f5f5f5", "fg": "#ccc", "label": "-"})
            heatmap_cells.append(cells)

    # 파레토 TOP 5
    pareto_items = data["pareto"].get("items", [])
    pareto_top5 = pareto_items[:5]

    # 템플릿 렌더링
    env = Environment(
        loader=FileSystemLoader(os.path.abspath(TEMPLATE_DIR)),
        autoescape=True,
    )
    template = env.get_template("monthly_report.html")

    html = template.render(
        period_label=period_label,
        kpi=data["kpi"],
        crossover_signals=data["mention_trend"].get("crossoverSignals", []),
        momentum_teachers=data["momentum"].get("teachers", []),
        pareto=data["pareto"],
        pareto_top5=pareto_top5,
        heatmap=heatmap,
        heatmap_weeks_display=heatmap_weeks_display,
        heatmap_cells=heatmap_cells,
        academies=data["academy_bubble"].get("academies", []),
        seasonality=data["seasonality"],
        correlation_insights=data["correlation"].get("insights", []),
        anomalies=data["bollinger"].get("anomalies", []),
        source_distribution=data["source_distribution"],
        news_articles=data["news_articles"],
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    return html
