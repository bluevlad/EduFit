import { Box, Typography, Paper } from '@mui/material';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bubble } from 'react-chartjs-2';

ChartJS.register(LinearScale, PointElement, Tooltip, Legend);

const COLORS = [
  'rgba(25, 118, 210, 0.7)',
  'rgba(76, 175, 80, 0.7)',
  'rgba(244, 67, 54, 0.7)',
  'rgba(255, 152, 0, 0.7)',
  'rgba(156, 39, 176, 0.7)',
  'rgba(0, 188, 212, 0.7)',
  'rgba(255, 87, 34, 0.7)',
  'rgba(63, 81, 181, 0.7)',
  'rgba(139, 195, 74, 0.7)',
  'rgba(233, 30, 99, 0.7)',
  'rgba(121, 85, 72, 0.7)',
  'rgba(96, 125, 139, 0.7)',
];

const BORDER_COLORS = COLORS.map((c) => c.replace('0.7', '1'));

function AcademyBubbleChart({ data }) {
  if (!data || !data.academies || data.academies.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">학원 데이터가 없습니다.</Typography>
      </Paper>
    );
  }

  const { academies } = data;

  // 버블 크기 스케일링 (강사수 → 반지름)
  const maxTeachers = Math.max(...academies.map((a) => a.teacherCount));
  const scaleFactor = maxTeachers > 0 ? 25 / Math.sqrt(maxTeachers) : 5;

  const chartData = {
    datasets: academies.map((academy, idx) => ({
      label: academy.academyName,
      data: [
        {
          x: academy.totalMentions,
          y: academy.avgSentiment != null ? academy.avgSentiment : 0,
          r: Math.max(Math.sqrt(academy.teacherCount) * scaleFactor, 4),
        },
      ],
      backgroundColor: COLORS[idx % COLORS.length],
      borderColor: BORDER_COLORS[idx % BORDER_COLORS.length],
      borderWidth: 1,
      // 커스텀 데이터 (tooltip용)
      _academyData: academy,
    })),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 12,
        },
      },
      title: {
        display: true,
        text: '학원별 언급-감성 분포',
        font: { size: 14 },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const academy = context.dataset._academyData;
            if (!academy) return '';
            return [
              `학원: ${academy.academyName}`,
              `총 언급: ${academy.totalMentions.toLocaleString()}`,
              `평균 감성: ${academy.avgSentiment != null ? (academy.avgSentiment * 100).toFixed(0) + '%' : 'N/A'}`,
              `강사 수: ${academy.teacherCount}명`,
            ];
          },
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: '총 언급수' },
        beginAtZero: true,
      },
      y: {
        title: { display: true, text: '평균 감성점수' },
        suggestedMin: -1,
        suggestedMax: 1,
        ticks: {
          callback: (value) => (value * 100).toFixed(0) + '%',
        },
      },
    },
  };

  return (
    <Box>
      <Box sx={{ height: 400 }}>
        <Bubble data={chartData} options={options} />
      </Box>
      <Box mt={1}>
        <Typography variant="caption" color="text.secondary">
          버블 크기 = 소속 강사 수 | X축 = 총 언급수 | Y축 = 평균 감성점수
        </Typography>
      </Box>
    </Box>
  );
}

export default AcademyBubbleChart;
