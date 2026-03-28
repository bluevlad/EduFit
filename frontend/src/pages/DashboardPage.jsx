import { useState, useEffect, useCallback } from 'react';
import {
  Container, Grid, Paper, Typography, Box, Card, CardContent,
  CircularProgress, Alert, Tabs, Tab, ToggleButtonGroup, ToggleButton,
  Chip,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import PeopleIcon from '@mui/icons-material/People';
import InsightsIcon from '@mui/icons-material/Insights';
import BarChartIcon from '@mui/icons-material/BarChart';
import SpeedIcon from '@mui/icons-material/Speed';
import SentimentSatisfiedIcon from '@mui/icons-material/SentimentSatisfied';
import trendService from '../services/trendService';
import { MovingAverageTrendChart, BollingerBandChart, ParetoChart, SeasonalityChart } from '../components/TrendCharts';
import MomentumRankingTable from '../components/MomentumRankingTable';
import TeacherHeatmap from '../components/TeacherHeatmap';
import AcademyBubbleChart from '../components/AcademyBubbleChart';
import CorrelationMatrix from '../components/CorrelationMatrix';
import GridViewIcon from '@mui/icons-material/GridView';
import BubbleChartIcon from '@mui/icons-material/BubbleChart';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';

const VOLATILITY_LABELS = {
  stable: { text: '안정', color: 'success' },
  moderate: { text: '보통', color: 'warning' },
  high: { text: '높음', color: 'error' },
};

const KPICard = ({ title, value, subLabel, subValue, icon, color = 'primary' }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent sx={{ pb: '16px !important' }}>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography color="text.secondary" variant="body2" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" component="div" fontWeight="bold">
            {value}
          </Typography>
          {subLabel && (
            <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
              {subValue != null && subValue > 0 && (
                <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main' }} />
              )}
              {subValue != null && subValue < 0 && (
                <TrendingDownIcon sx={{ fontSize: 16, color: 'error.main' }} />
              )}
              <Typography
                variant="body2"
                color={
                  subValue != null && subValue > 0 ? 'success.main'
                  : subValue != null && subValue < 0 ? 'error.main'
                  : 'text.secondary'
                }
              >
                {subLabel}
              </Typography>
            </Box>
          )}
        </Box>
        <Box
          sx={{
            backgroundColor: `${color}.light`,
            borderRadius: 2,
            p: 1,
            display: 'flex',
            alignItems: 'center',
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [days, setDays] = useState(90);

  const loadDashboard = useCallback(async (period) => {
    setLoading(true);
    setError(null);
    try {
      const res = await trendService.getDashboard(period);
      setDashboardData(res.data);
    } catch (err) {
      console.error('Dashboard load error:', err);
      setError('트렌드 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard(days);
  }, [days, loadDashboard]);

  const handleDaysChange = (_, newDays) => {
    if (newDays != null) setDays(newDays);
  };

  const kpi = dashboardData?.kpi;

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* 헤더 */}
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            종합 트렌드 분석
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            학원 강사 평판 누적 분석 대시보드
          </Typography>
          {kpi?.dataStartDate && kpi?.dataEndDate && (
            <Typography variant="body2" color="text.secondary" mt={0.5}>
              분석 기간: {kpi.dataStartDate} ~ {kpi.dataEndDate}
            </Typography>
          )}
        </Box>
        <ToggleButtonGroup
          value={days}
          exclusive
          onChange={handleDaysChange}
          size="small"
        >
          <ToggleButton value={30}>30일</ToggleButton>
          <ToggleButton value={60}>60일</ToggleButton>
          <ToggleButton value={90}>90일</ToggleButton>
          <ToggleButton value={180}>180일</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
          <CircularProgress />
        </Box>
      ) : dashboardData ? (
        <>
          {/* KPI 카드 */}
          <Grid container spacing={2} mb={3}>
            <Grid item xs={12} sm={6} md={3}>
              <KPICard
                title="총 언급"
                value={(kpi?.totalMentions || 0).toLocaleString()}
                subLabel={
                  kpi?.mentionGrowthRate != null
                    ? `${kpi.mentionGrowthRate > 0 ? '+' : ''}${kpi.mentionGrowthRate}% (후반기)`
                    : null
                }
                subValue={kpi?.mentionGrowthRate}
                icon={<ShowChartIcon color="primary" />}
                color="primary"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <KPICard
                title="평균 감성점수"
                value={kpi?.avgSentimentScore != null ? (kpi.avgSentimentScore * 100).toFixed(0) + '%' : '-'}
                subLabel={
                  kpi?.sentimentTrend != null
                    ? `${kpi.sentimentTrend > 0 ? '+' : ''}${(kpi.sentimentTrend * 100).toFixed(1)}% 변화`
                    : null
                }
                subValue={kpi?.sentimentTrend}
                icon={<SentimentSatisfiedIcon color="success" />}
                color="success"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <KPICard
                title="변동성"
                value={kpi?.volatility != null ? kpi.volatility + '%' : '-'}
                subLabel={
                  kpi?.volatilityLevel
                    ? VOLATILITY_LABELS[kpi.volatilityLevel]?.text
                    : null
                }
                icon={<SpeedIcon color="warning" />}
                color="warning"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <KPICard
                title="분석 강사"
                value={kpi?.totalTeachers || 0}
                subLabel="명"
                icon={<PeopleIcon color="info" />}
                color="info"
              />
            </Grid>
          </Grid>

          {/* 탭 네비게이션 */}
          <Paper sx={{ mb: 3 }}>
            <Tabs
              value={tabValue}
              onChange={(_, v) => setTabValue(v)}
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab label="이동평균 트렌드" icon={<ShowChartIcon />} iconPosition="start" />
              <Tab label="볼린저 밴드" icon={<InsightsIcon />} iconPosition="start" />
              <Tab label="모멘텀 랭킹" icon={<SpeedIcon />} iconPosition="start" />
              <Tab label="파레토 분석" icon={<BarChartIcon />} iconPosition="start" />
              <Tab label="계절성 패턴" icon={<InsightsIcon />} iconPosition="start" />
              <Tab label="강사 히트맵" icon={<GridViewIcon />} iconPosition="start" />
              <Tab label="학원 버블차트" icon={<BubbleChartIcon />} iconPosition="start" />
              <Tab label="상관관계 분석" icon={<CompareArrowsIcon />} iconPosition="start" />
            </Tabs>
          </Paper>

          {/* 탭 콘텐츠 */}
          <Paper sx={{ p: 3 }}>
            {tabValue === 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  언급량 이동평균 트렌드
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  7일/21일 이동평균으로 노이즈를 제거한 실제 추세를 파악합니다.
                  골든크로스(GC)는 관심 급증, 데드크로스(DC)는 관심 감소 시그널입니다.
                </Typography>
                <MovingAverageTrendChart data={dashboardData.mentionTrend} />
              </Box>
            )}

            {tabValue === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  감성점수 볼린저 밴드
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  감성점수가 2 표준편차 밴드를 이탈하면 이상치로 감지됩니다.
                  밴드 폭이 좁아지면 큰 변화가 임박한 신호입니다.
                </Typography>
                <BollingerBandChart data={dashboardData.sentimentBollinger} />
                {dashboardData.sentimentBollinger?.bandWidth != null && (
                  <Box mt={2}>
                    <Chip
                      size="small"
                      label={`평균 밴드 폭: ${(dashboardData.sentimentBollinger.bandWidth * 100).toFixed(1)}%`}
                      variant="outlined"
                    />
                  </Box>
                )}
              </Box>
            )}

            {tabValue === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  모멘텀 기반 강사 랭킹
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  단순 언급수가 아닌 4주/8주 변화율(ROC)로 상승세/하락세를 판단합니다.
                </Typography>
                <MomentumRankingTable data={dashboardData.momentumRanking} loading={false} />
              </Box>
            )}

            {tabValue === 3 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  언급 집중도 (파레토 분석)
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  상위 강사들이 전체 언급의 몇 %를 차지하는지 분석합니다.
                  80/20 법칙 기준선을 참고하세요.
                </Typography>
                <ParetoChart data={dashboardData.pareto} />
              </Box>
            )}

            {tabValue === 4 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  요일별 언급 패턴
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  요일에 따른 언급 패턴을 파악하여 커뮤니티 활동 주기를 분석합니다.
                </Typography>
                <SeasonalityChart data={dashboardData.seasonality} />
              </Box>
            )}

            {tabValue === 5 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  강사별 주간 감성 히트맵
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  주차별 강사의 감성점수를 색상으로 시각화합니다. 셀 숫자는 언급수, 색상은 감성점수(빨강=부정, 초록=긍정)입니다.
                </Typography>
                <TeacherHeatmap data={dashboardData.teacherHeatmap} />
              </Box>
            )}

            {tabValue === 6 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  학원별 언급-감성 분포
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  각 학원의 총 언급수(X축), 평균 감성점수(Y축), 소속 강사 수(버블 크기)를 한눈에 비교합니다.
                </Typography>
                <AcademyBubbleChart data={dashboardData.academyBubble} />
              </Box>
            )}

            {tabValue === 7 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  지표 간 상관관계 분석
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  언급수, 긍정/부정수, 추천수, 감성점수 간의 피어슨 상관계수를 매트릭스로 표시합니다.
                  색상이 진할수록 상관관계가 강합니다.
                </Typography>
                <CorrelationMatrix data={dashboardData.correlation} />
              </Box>
            )}
          </Paper>
        </>
      ) : null}
    </Container>
  );
}

export default DashboardPage;
