"""뉴스 기사 조회 서비스

수집된 네이버/구글 뉴스 기사를 조회하고 소스별 통계를 제공합니다.
"""
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from ..models.collection_source import CollectionSource
from ..models.post import Post
from ..models.teacher import Teacher
from ..models.teacher_mention import TeacherMention

SOURCE_TYPE_LABELS = {
    "news": "뉴스",
    "cafe": "카페",
    "gallery": "갤러리",
    "forum": "포럼",
}


def get_recent_articles(
    db: Session,
    days: int = 7,
    limit: int = 10,
    offset: int = 0,
    teacher_id: Optional[int] = None,
) -> dict:
    """최근 뉴스 기사 목록 조회

    Parameters:
        days: 조회 기간 (일)
        limit: 조회 건수
        offset: 페이지네이션 오프셋
        teacher_id: 특정 강사 관련 기사만 조회
    """
    cutoff = date.today() - timedelta(days=days)

    base_query = (
        db.query(
            Post.id,
            Post.title,
            Post.url,
            Post.post_date,
            Post.author.label("keyword"),
            CollectionSource.name.label("source_name"),
            CollectionSource.code.label("source_code"),
            func.count(TeacherMention.id).label("mention_count"),
        )
        .join(CollectionSource, Post.source_id == CollectionSource.id)
        .outerjoin(TeacherMention, TeacherMention.post_id == Post.id)
        .filter(
            CollectionSource.source_type == "news",
            Post.post_date >= cutoff,
        )
    )

    if teacher_id:
        base_query = base_query.filter(TeacherMention.teacher_id == teacher_id)

    # 전체 건수
    count_query = (
        db.query(func.count(func.distinct(Post.id)))
        .join(CollectionSource, Post.source_id == CollectionSource.id)
        .filter(
            CollectionSource.source_type == "news",
            Post.post_date >= cutoff,
        )
    )
    if teacher_id:
        count_query = count_query.join(
            TeacherMention, TeacherMention.post_id == Post.id
        ).filter(TeacherMention.teacher_id == teacher_id)

    total = count_query.scalar() or 0

    rows = (
        base_query
        .group_by(Post.id, Post.title, Post.url, Post.post_date, Post.author,
                  CollectionSource.name, CollectionSource.code)
        .order_by(Post.post_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    articles = []
    for row in rows:
        articles.append({
            "id": row.id,
            "title": row.title,
            "url": row.url,
            "source_name": row.source_name,
            "source_code": row.source_code,
            "published_at": row.post_date.strftime("%Y-%m-%d %H:%M") if row.post_date else None,
            "keyword": row.keyword,
            "mention_count": row.mention_count,
        })

    return {
        "total": total,
        "articles": articles,
    }


def get_article_detail(db: Session, post_id: int) -> Optional[dict]:
    """뉴스 기사 상세 (언급된 강사 목록 포함)"""
    post = (
        db.query(Post, CollectionSource.name.label("source_name"))
        .join(CollectionSource, Post.source_id == CollectionSource.id)
        .filter(Post.id == post_id, CollectionSource.source_type == "news")
        .first()
    )
    if not post:
        return None

    row, source_name = post.Post, post.source_name

    # 이 기사에서 언급된 강사들
    mentioned_teachers = (
        db.query(
            Teacher.id,
            Teacher.name,
            TeacherMention.sentiment,
            TeacherMention.sentiment_score,
            TeacherMention.context,
        )
        .join(TeacherMention, TeacherMention.teacher_id == Teacher.id)
        .filter(TeacherMention.post_id == post_id)
        .all()
    )

    return {
        "id": row.id,
        "title": row.title,
        "url": row.url,
        "content_preview": (row.content[:300] + "...") if row.content and len(row.content) > 300 else row.content,
        "source_name": source_name,
        "published_at": row.post_date.strftime("%Y-%m-%d %H:%M") if row.post_date else None,
        "keyword": row.author,
        "view_count": row.view_count,
        "mentioned_teachers": [
            {
                "teacher_id": t.id,
                "teacher_name": t.name,
                "sentiment": t.sentiment,
                "sentiment_score": t.sentiment_score,
                "context": t.context,
            }
            for t in mentioned_teachers
        ],
    }


def get_source_stats(db: Session, days: int = 7) -> dict:
    """소스 유형별 언급 통계 (뉴스/카페/갤러리/포럼)"""
    cutoff = date.today() - timedelta(days=days)

    rows = (
        db.query(
            CollectionSource.source_type,
            func.count(func.distinct(Post.id)).label("post_count"),
            func.count(TeacherMention.id).label("mention_count"),
        )
        .join(Post, Post.source_id == CollectionSource.id)
        .outerjoin(TeacherMention, TeacherMention.post_id == Post.id)
        .filter(Post.post_date >= cutoff)
        .group_by(CollectionSource.source_type)
        .all()
    )

    total_mentions = sum(r.mention_count for r in rows) or 1
    total_posts = sum(r.post_count for r in rows) or 1

    distribution = []
    for r in rows:
        distribution.append({
            "source_type": r.source_type,
            "label": SOURCE_TYPE_LABELS.get(r.source_type, r.source_type),
            "post_count": r.post_count,
            "mention_count": r.mention_count,
            "mention_ratio": round(r.mention_count / total_mentions * 100, 1),
        })

    # 감성 분포 by source_type
    sentiment_rows = (
        db.query(
            CollectionSource.source_type,
            func.count(case((TeacherMention.sentiment == "positive", 1))).label("positive"),
            func.count(case((TeacherMention.sentiment == "negative", 1))).label("negative"),
            func.count(case((TeacherMention.sentiment == "neutral", 1))).label("neutral"),
            func.avg(TeacherMention.sentiment_score).label("avg_score"),
        )
        .join(Post, Post.source_id == CollectionSource.id)
        .join(TeacherMention, TeacherMention.post_id == Post.id)
        .filter(Post.post_date >= cutoff)
        .group_by(CollectionSource.source_type)
        .all()
    )

    sentiment_by_source = {}
    for r in sentiment_rows:
        sentiment_by_source[r.source_type] = {
            "positive": r.positive,
            "negative": r.negative,
            "neutral": r.neutral,
            "avg_score": round(float(r.avg_score), 4) if r.avg_score else None,
        }

    return {
        "days": days,
        "total_posts": total_posts,
        "total_mentions": total_mentions,
        "distribution": distribution,
        "sentiment_by_source": sentiment_by_source,
    }
