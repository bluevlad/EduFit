import { Box, Typography, Paper } from '@mui/material';
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
  Filler
);

export const MentionTrendChart = ({ data, title = '주간 언급 트렌드' }) => {
  if (!data || data.length === 0) {
    return (
      <Paper sx={{ p: 2, textAlign: 'center' }}>
        <Typography color="text.secondary">트렌드 데이터가 없습니다.</Typography>
      </Paper>
    );
  }

  const chartData = {
    labels: data.map((d) => d.weekLabel || `${d.weekNumber}주`),
    datasets: [
      {
        label: '언급 수',
        data: data.map((d) => d.mentionCount),
        borderColor: 'rgb(25, 118, 210)',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: '추천',
        data: data.map((d) => d.recommendationCount),
        borderColor: 'rgb(76, 175, 80)',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        fill: false,
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: title },
    },
    scales: {
      y: { beginAtZero: true },
    },
  };

  return (
    <Box sx={{ height: 300 }}>
      <Line data={chartData} options={options} />
    </Box>
  );
};

export const SentimentTrendChart = ({ data, title = '주간 감성 트렌드' }) => {
  if (!data || data.length === 0) {
    return (
      <Paper sx={{ p: 2, textAlign: 'center' }}>
        <Typography color="text.secondary">감성 데이터가 없습니다.</Typography>
      </Paper>
    );
  }

  const chartData = {
    labels: data.map((d) => d.weekLabel || `${d.weekNumber}주`),
    datasets: [
      {
        label: '긍정',
        data: data.map((d) => d.positiveCount),
        backgroundColor: 'rgba(76, 175, 80, 0.8)',
      },
      {
        label: '중립',
        data: data.map((d) => d.neutralCount || 0),
        backgroundColor: 'rgba(158, 158, 158, 0.8)',
      },
      {
        label: '부정',
        data: data.map((d) => d.negativeCount),
        backgroundColor: 'rgba(244, 67, 54, 0.8)',
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: title },
    },
    scales: {
      x: { stacked: true },
      y: { stacked: true, beginAtZero: true },
    },
  };

  return (
    <Box sx={{ height: 300 }}>
      <Bar data={chartData} options={options} />
    </Box>
  );
};

const WeeklyCharts = { MentionTrendChart, SentimentTrendChart };
export default WeeklyCharts;
