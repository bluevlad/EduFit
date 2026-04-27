import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './GatewayLanding.css';

const FEATURES = [
  {
    icon: '📊',
    name: '종합 트렌드',
    desc: '학원·강사·언급량 통합 지표와 최근 트렌드를 한 화면에 제공',
    tag: 'Analytics · Trend',
    level: 'public',
    to: '/dashboard',
  },
  {
    icon: '🏫',
    name: '학원별 통계',
    desc: '학원 단위 언급량·평판·강사 수를 정렬·필터링해 비교',
    tag: 'Analytics · Academy',
    level: 'public',
    to: '/academies',
  },
  {
    icon: '🧑‍🏫',
    name: '강사 분석',
    desc: '강사별 언급·평판 점수와 상세 게시글 목록을 제공',
    tag: 'Analytics · Teacher',
    level: 'public',
    to: '/teachers',
  },
  {
    icon: '📅',
    name: '일간 리포트',
    desc: '매일 수집된 게시글 기반 일간 요약 리포트',
    tag: 'Report · Daily',
    level: 'public',
    to: '/reports',
  },
  {
    icon: '📆',
    name: '주간 리포트',
    desc: '최근 7일 학원·강사 트렌드 변화와 주요 언급 주제 정리',
    tag: 'Report · Weekly',
    level: 'public',
    to: '/weekly',
  },
  {
    icon: '🗓',
    name: '월간 리포트',
    desc: '월간 언급량·평판 흐름과 학원별 월간 순위 리포트',
    tag: 'Report · Monthly',
    level: 'public',
    to: '/monthly',
  },
  {
    icon: '📬',
    name: '뉴스레터',
    desc: '학원·강사 분석 인사이트와 교육 뉴스를 월간 이메일로 수신',
    tag: 'Public · Digest',
    level: 'public',
    to: 'https://newsletter.unmong.com/edufit/subscribe',
    external: true,
  },
  {
    icon: '🔌',
    name: 'API Docs',
    desc: 'FastAPI 자동 생성 OpenAPI 문서 — 뉴스 기사·통계 공개 API 포함',
    tag: 'Developer · OpenAPI',
    level: 'public',
    to: '/api/docs',
    externalSameDomain: true,
  },
  {
    icon: '⚙️',
    name: '학원 관리',
    desc: '학원 메타데이터·소속 강사·게시 대상 여부 편집',
    tag: 'Admin · Academy',
    level: 'admin',
    to: '/admin/academies',
  },
  {
    icon: '👥',
    name: '강사 관리',
    desc: '강사 등록·수정·소속 학원 매핑과 노출 여부 관리',
    tag: 'Admin · Teacher',
    level: 'admin',
    to: '/admin/teachers',
  },
  {
    icon: '🔍',
    name: '미등록 후보',
    desc: '크롤링에서 탐지된 미등록 강사·학원 후보를 승인/반려',
    tag: 'Admin · Candidate',
    level: 'admin',
    to: '/admin/candidates',
  },
  {
    icon: '📰',
    name: '월간 뉴스레터',
    desc: '월간 뉴스레터 초안 생성·미리보기·발송 트리거 (네이버+구글 뉴스 연동)',
    tag: 'Admin · Newsletter',
    level: 'admin',
    to: '/admin/newsletter',
  },
];

const TECH_STACK = [
  { name: 'React 18', dot: '#61dafb' },
  { name: 'Vite', dot: '#646cff' },
  { name: 'MUI 5', dot: '#007fff' },
  { name: 'FastAPI', dot: '#009688' },
  { name: 'Python 3.12', dot: '#3776ab' },
  { name: 'SQLAlchemy 2.0', dot: '#d71f00' },
  { name: 'Alembic', dot: '#6a737d' },
  { name: 'PostgreSQL 15', dot: '#336791' },
  { name: 'Docker · OrbStack', dot: '#2496ed' },
  { name: 'GitHub Actions', dot: '#2088ff' },
  { name: 'Nginx', dot: '#009639' },
];

const CONNECTED_SERVICES = [
  {
    name: 'NewsLetterPlatform',
    role: '뉴스레터 발송 연동',
    href: 'https://newsletter.unmong.com/',
    dot: '#ec4899',
  },
  {
    name: 'StandUp',
    role: '업무 추적 연동',
    href: 'https://standup.unmong.com/',
    dot: '#14b8a6',
  },
  {
    name: 'InfraWatcher',
    role: '컨테이너 모니터링',
    href: 'https://infrawatcher.unmong.com/',
    dot: '#06b6d4',
  },
];

function accessFor(level, { isAuthenticated, isAdmin }) {
  if (level === 'public') return 'granted';
  if (level === 'member') return isAuthenticated ? 'granted' : 'member-locked';
  if (level === 'admin') return isAdmin ? 'granted' : 'admin-locked';
  return 'granted';
}

function tagInfo(state, level, customTag) {
  if (state === 'granted' && level === 'public') {
    return { label: customTag || '🌐 공개', variant: 'public' };
  }
  if (state === 'granted') {
    return { label: '✓ 사용 가능', variant: 'granted' };
  }
  if (state === 'member-locked') {
    return { label: '🔒 회원전용', variant: 'member-locked' };
  }
  if (state === 'admin-locked') {
    return { label: '🔐 관리자 전용', variant: 'admin-locked' };
  }
  return { label: '', variant: '' };
}

function lockedToastFor(state) {
  if (state === 'member-locked') {
    return {
      icon: '🔒',
      message: '회원전용 서비스입니다',
      actionLabel: '로그인',
      actionTo: '/login',
    };
  }
  if (state === 'admin-locked') {
    return {
      icon: '🔐',
      message: '관리자 전용입니다',
      actionLabel: '관리자 로그인',
      actionTo: '/login',
    };
  }
  return null;
}

function FeatureCard({ feature, accessState, onLocked }) {
  const locked = accessState !== 'granted';
  const { label, variant } = tagInfo(accessState, feature.level, feature.tag);

  const handleClick = (e) => {
    if (locked) {
      e.preventDefault();
      onLocked(accessState);
    }
  };

  const inner = (
    <>
      {locked && (
        <span className="sl-feature-lock" aria-hidden="true">
          🔒
        </span>
      )}
      <span className="sl-feature-icon" aria-hidden="true">
        {feature.icon}
      </span>
      <div className="sl-feature-name">{feature.name}</div>
      <div className="sl-feature-desc">{feature.desc}</div>
      <span className={`sl-feature-tag sl-feature-tag--${variant}`}>{label}</span>
    </>
  );

  const commonProps = {
    className: 'sl-feature',
    'data-locked': locked ? 'true' : 'false',
    onClick: handleClick,
  };

  if (feature.external) {
    return (
      <a {...commonProps} href={feature.to} target="_blank" rel="noopener noreferrer">
        {inner}
      </a>
    );
  }
  if (feature.externalSameDomain) {
    return (
      <a {...commonProps} href={feature.to} target="_blank" rel="noopener">
        {inner}
      </a>
    );
  }
  if (locked) {
    return (
      <a {...commonProps} href={feature.to}>
        {inner}
      </a>
    );
  }
  return (
    <Link {...commonProps} to={feature.to}>
      {inner}
    </Link>
  );
}

function Toast({ toast, onClose }) {
  if (!toast) return null;
  return (
    <div className="sl-toast" role="status" aria-live="polite">
      <span className="sl-toast-icon" aria-hidden="true">
        {toast.icon}
      </span>
      <span className="sl-toast-msg">{toast.message}</span>
      <Link className="sl-toast-action" to={toast.actionTo} onClick={onClose}>
        {toast.actionLabel} →
      </Link>
      <button
        type="button"
        className="sl-toast-close"
        onClick={onClose}
        aria-label="닫기"
      >
        ×
      </button>
    </div>
  );
}

function GatewayLanding() {
  const { admin, loading } = useAuth();
  const [toast, setToast] = useState(null);

  useEffect(() => {
    if (!toast) return undefined;
    const timer = setTimeout(() => setToast(null), 4500);
    return () => clearTimeout(timer);
  }, [toast]);

  const handleLocked = useCallback((accessState) => {
    const next = lockedToastFor(accessState);
    if (next) setToast(next);
  }, []);

  if (loading) {
    return (
      <div className="gateway-landing-root">
        <div className="sl-loading">로딩 중...</div>
      </div>
    );
  }

  const authState = { isAuthenticated: !!admin, isAdmin: !!admin };

  return (
    <div className="gateway-landing-root">
      <div className="sl-container">
        <section className="sl-hero">
          <h1>EduFit</h1>
          <p className="tagline">Academy &amp; Instructor Analytics Platform</p>
          <p className="desc">
            학원과 강사의 성과를 데이터 기반으로 분석하고, 교육 품질 향상을 위한 인사이트를 제공하는 분석 플랫폼
          </p>
        </section>

        <section className="sl-section">
          <div className="sl-section-title">Features</div>
          <div className="sl-features">
            {FEATURES.map((feature) => (
              <FeatureCard
                key={feature.name}
                feature={feature}
                accessState={accessFor(feature.level, authState)}
                onLocked={handleLocked}
              />
            ))}
          </div>
        </section>

        <section className="sl-section sl-arch">
          <div className="sl-section-title">Architecture</div>
          <div className="sl-arch-diagram">
            <div className="sl-arch-node">
              <div className="sl-arch-node-label">Frontend</div>
              <div className="sl-arch-node-tech">React 18 (Vite)</div>
            </div>
            <div className="sl-arch-arrow">→</div>
            <div className="sl-arch-node highlight">
              <div className="sl-arch-node-label">Backend</div>
              <div className="sl-arch-node-tech">FastAPI</div>
            </div>
            <div className="sl-arch-arrow">→</div>
            <div className="sl-arch-node">
              <div className="sl-arch-node-label">Database</div>
              <div className="sl-arch-node-tech">PostgreSQL 15</div>
            </div>
          </div>
        </section>

        <section className="sl-section sl-flow">
          <div className="sl-section-title">Service Flow</div>
          <div className="sl-flow-steps">
            <div className="sl-flow-step">
              <div className="sl-flow-step-num">1</div>
              <div className="sl-flow-step-label">데이터 수집</div>
              <div className="sl-flow-step-desc">학원/강사 정보</div>
            </div>
            <div className="sl-flow-arrow">→</div>
            <div className="sl-flow-step">
              <div className="sl-flow-step-num">2</div>
              <div className="sl-flow-step-label">분석/통계</div>
              <div className="sl-flow-step-desc">성과 데이터 분석</div>
            </div>
            <div className="sl-flow-arrow">→</div>
            <div className="sl-flow-step">
              <div className="sl-flow-step-num">3</div>
              <div className="sl-flow-step-label">리포트</div>
              <div className="sl-flow-step-desc">대시보드 시각화</div>
            </div>
            <div className="sl-flow-arrow">→</div>
            <div className="sl-flow-step">
              <div className="sl-flow-step-num">4</div>
              <div className="sl-flow-step-label">뉴스레터</div>
              <div className="sl-flow-step-desc">구독자 발송</div>
            </div>
          </div>
        </section>

        <section className="sl-section sl-tech">
          <div className="sl-section-title">Tech Stack</div>
          <div className="sl-tech-list">
            {TECH_STACK.map((tech) => (
              <span className="sl-tech-badge" key={tech.name}>
                <span className="sl-tech-dot" style={{ background: tech.dot }} />
                {tech.name}
              </span>
            ))}
          </div>
        </section>

        <section className="sl-section sl-connected">
          <div className="sl-section-title">Connected Services</div>
          <div className="sl-connected-grid">
            {CONNECTED_SERVICES.map((svc) => (
              <a
                key={svc.name}
                href={svc.href}
                target="_blank"
                rel="noopener noreferrer"
                className="sl-connected-card"
              >
                <span className="sl-connected-dot" style={{ background: svc.dot }} />
                <div className="sl-connected-info">
                  <div className="sl-connected-name">{svc.name}</div>
                  <div className="sl-connected-role">{svc.role}</div>
                </div>
                <span className="sl-connected-arrow">→</span>
              </a>
            ))}
          </div>
        </section>
      </div>

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}

export default GatewayLanding;
