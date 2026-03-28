import { Box, Typography, Paper, Chip, Tooltip as MuiTooltip } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import annotationPlugin from 'chartjs-plugin-annotation';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  annotationPlugin
);

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
};

/**
 * 이동평균 트렌드 차트
 */
export const MovingAverageTrendChart = ({ data }) => {
  if (!data || !data.dataPoints || data.dataPoints.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">트렌드 데이터가 없습니다.</Typography>
      </Paper>
    );
  }

  const { dataPoints, crossoverSignals } = data;

  // 크로스오버 시그널 annotation 생성
  const annotations = {};
  (crossoverSignals || []).forEach((signal, idx) => {
    const dataIdx = dataPoints.findIndex((p) => p.date === signal.date);
    if (dataIdx >= 0) {
      annotations[`signal_${idx}`] = {
        type: 'line',
        xMin: dataIdx,
        xMax: dataIdx,
        borderColor: signal.type === 'golden_cross' ? '#4caf50' : '#f44336',
        borderWidth: 2,
        borderDash: [4, 4],
        label: {
          display: true,
          content: signal.type === 'golden_cross' ? 'GC' : 'DC',
          position: 'start',
          backgroundColor: signal.type === 'golden_cross' ? '#4caf50' : '#f44336',
          color: '#fff',
          font: { size: 10 },
        },
      };
    }
  });

  const chartData = {
    labels: dataPoints.map((d) => formatDate(d.date)),
    datasets: [
      {
        label: '일별 언급수',
        data: dataPoints.map((d) => d.value),
        borderColor: 'rgba(25, 118, 210, 0.3)',
        backgroundColor: 'rgba(25, 118, 210, 0.05)',
        borderWidth: 1,
        pointRadius: 0,
        fill: true,
        order: 3,
      },
      {
        label: '7일 이동평균',
        data: dataPoints.map((d) => d.ma7),
        borderColor: '#1976d2',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
        order: 1,
      },
      {
        label: '21일 이동평균',
        data: dataPoints.map((d) => d.ma21),
        borderColor: '#ff9800',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
        borderDash: [6, 3],
        order: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: '언급량 이동평균 트렌드', font: { size: 14 } },
      annotation: { annotations },
      tooltip: {
        callbacks: {
          title: (items) => {
            const idx = items[0]?.dataIndex;
            return dataPoints[idx]?.date || '';
          },
        },
      },
    },
    scales: {
      x: {
        ticks: { maxTicksLimit: 15 },
      },
      y: { beginAtZero: true },
    },
  };

  return (
    <Box>
      <Box sx={{ height: 350 }}>
        <Line data={chartData} options={options} />
      </Box>
      {crossoverSignals && crossoverSignals.length > 0 && (
        <Box display="flex" gap={1} mt={1} flexWrap="wrap">
          {crossoverSignals.map((s, i) => (
            <MuiTooltip key={i} title={`${s.date}: ${s.label}`}>
              <Chip
                size="small"
                label={s.label}
                color={s.type === 'golden_cross' ? 'success' : 'error'}
                variant="outlined"
              />
            </MuiTooltip>
          ))}
        </Box>
      )}
    </Box>
  );
};

/**
 * 볼린저 밴드 차트
 */
export const BollingerBandChart = ({ data }) => {
  if (!data || !data.dataPoints || data.dataPoints.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">감성 데이터가 없습니다.</Typography>
      </Paper>
    );
  }

  const { dataPoints, anomalies } = data;

  // 이상치 포인트 마킹
  const anomalySet = new Set((anomalies || []).map((a) => a.date));

  const chartData = {
    labels: dataPoints.map((d) => formatDate(d.date)),
    datasets: [
      {
        label: '상한 밴드',
        data: dataPoints.map((d) => d.upperBand),
        borderColor: 'rgba(244, 67, 54, 0.3)',
        backgroundColor: 'rgba(244, 67, 54, 0.05)',
        borderWidth: 1,
        pointRadius: 0,
        fill: false,
        borderDash: [4, 4],
        order: 3,
      },
      {
        label: '하한 밴드',
        data: dataPoints.map((d) => d.lowerBand),
        borderColor: 'rgba(76, 175, 80, 0.3)',
        backgroundColor: 'rgba(200, 200, 200, 0.1)',
        borderWidth: 1,
        pointRadius: 0,
        fill: '-1',
        borderDash: [4, 4],
        order: 4,
      },
      {
        label: '20일 이동평균',
        data: dataPoints.map((d) => d.ma20),
        borderColor: '#ff9800',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
        order: 2,
      },
      {
        label: '감성점수',
        data: dataPoints.map((d) => d.value),
        borderColor: '#1976d2',
        borderWidth: 2,
        pointRadius: dataPoints.map((d) => (anomalySet.has(d.date) ? 6 : 0)),
        pointBackgroundColor: dataPoints.map((d) =>
          anomalySet.has(d.date) ? '#f44336' : '#1976d2'
        ),
        pointBorderColor: dataPoints.map((d) =>
          anomalySet.has(d.date) ? '#f44336' : '#1976d2'
        ),
        tension: 0.3,
        order: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: '감성점수 볼린저 밴드', font: { size: 14 } },
      tooltip: {
        callbacks: {
          title: (items) => {
            const idx = items[0]?.dataIndex;
            return dataPoints[idx]?.date || '';
          },
          afterBody: (items) => {
            const idx = items[0]?.dataIndex;
            const point = dataPoints[idx];
            if (point?.isAnomaly) {
              return ['** 이상치 감지 **'];
            }
            return [];
          },
        },
      },
    },
    scales: {
      x: { ticks: { maxTicksLimit: 15 } },
      y: {
        suggestedMin: -1,
        suggestedMax: 1,
      },
    },
  };

  return (
    <Box>
      <Box sx={{ height: 350 }}>
        <Line data={chartData} options={options} />
      </Box>
      {anomalies && anomalies.length > 0 && (
        <Box display="flex" gap={1} mt={1} flexWrap="wrap">
          {anomalies.slice(0, 5).map((a, i) => (
            <Chip
              key={i}
              size="small"
              label={`${a.date}: ${a.label}`}
              color={a.direction === 'positive' ? 'success' : 'error'}
              variant="outlined"
            />
          ))}
          {anomalies.length > 5 && (
            <Chip size="small" label={`+${anomalies.length - 5}건`} variant="outlined" />
          )}
        </Box>
      )}
    </Box>
  );
};

/**
 * 파레토 차트 (누적 비율 + 바)
 */
export const ParetoChart = ({ data }) => {
  if (!data || !data.items || data.items.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">파레토 데이터가 없습니다.</Typography>
      </Paper>
    );
  }

  const items = data.items.slice(0, 20);

  const chartData = {
    labels: items.map((d) => d.teacherName),
    datasets: [
      {
        type: 'bar',
        label: '언급수',
        data: items.map((d) => d.mentionCount),
        backgroundColor: items.map((_, i) =>
          i < 5 ? 'rgba(25, 118, 210, 0.8)' : 'rgba(25, 118, 210, 0.4)'
        ),
        yAxisID: 'y',
        order: 2,
      },
      {
        type: 'line',
        label: '누적 비율 (%)',
        data: items.map((d) => d.cumulativeRatio),
        borderColor: '#f44336',
        borderWidth: 2,
        pointRadius: 3,
        pointBackgroundColor: '#f44336',
        yAxisID: 'y1',
        tension: 0.3,
        order: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: '언급 집중도 (파레토 분석)', font: { size: 14 } },
      annotation: {
        annotations: {
          line80: {
            type: 'line',
            yMin: 80,
            yMax: 80,
            yScaleID: 'y1',
            borderColor: 'rgba(244, 67, 54, 0.4)',
            borderWidth: 1,
            borderDash: [6, 3],
            label: {
              display: true,
              content: '80%',
              position: 'end',
              backgroundColor: 'rgba(244, 67, 54, 0.7)',
              color: '#fff',
              font: { size: 10 },
            },
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 0,
        },
      },
      y: {
        type: 'linear',
        position: 'left',
        beginAtZero: true,
        title: { display: true, text: '언급수' },
      },
      y1: {
        type: 'linear',
        position: 'right',
        min: 0,
        max: 100,
        title: { display: true, text: '누적 비율 (%)' },
        grid: { drawOnChartArea: false },
      },
    },
  };

  return (
    <Box>
      <Box sx={{ height: 350 }}>
        <Bar data={chartData} options={options} />
      </Box>
      <Box display="flex" gap={2} mt={1}>
        {data.top5Ratio != null && (
          <Chip size="small" label={`TOP 5: ${data.top5Ratio}%`} color="primary" />
        )}
        {data.top10Ratio != null && (
          <Chip size="small" label={`TOP 10: ${data.top10Ratio}%`} color="primary" variant="outlined" />
        )}
      </Box>
    </Box>
  );
};

/**
 * 요일별 계절성 차트
 */
export const SeasonalityChart = ({ data }) => {
  if (!data || !data.dailyPattern || data.dailyPattern.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">계절성 데이터가 없습니다.</Typography>
      </Paper>
    );
  }

  const { dailyPattern, peakDay, lowDay } = data;

  const chartData = {
    labels: dailyPattern.map((d) => d.dayName),
    datasets: [
      {
        label: '평균 언급수',
        data: dailyPattern.map((d) => d.avgMentions),
        backgroundColor: dailyPattern.map((d) =>
          d.dayName === peakDay
            ? 'rgba(25, 118, 210, 0.9)'
            : d.dayName === lowDay
              ? 'rgba(244, 67, 54, 0.6)'
              : 'rgba(25, 118, 210, 0.5)'
        ),
        borderRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: { display: true, text: '요일별 언급 패턴', font: { size: 14 } },
    },
    scales: {
      y: { beginAtZero: true, title: { display: true, text: '평균 언급수' } },
    },
  };

  return (
    <Box>
      <Box sx={{ height: 250 }}>
        <Bar data={chartData} options={options} />
      </Box>
      <Box display="flex" gap={1} mt={1}>
        {peakDay && (
          <Chip size="small" label={`최다: ${peakDay}요일`} color="primary" />
        )}
        {lowDay && (
          <Chip size="small" label={`최소: ${lowDay}요일`} color="default" />
        )}
      </Box>
    </Box>
  );
};

const TrendCharts = {
  MovingAverageTrendChart,
  BollingerBandChart,
  ParetoChart,
  SeasonalityChart,
};

export default TrendCharts;
