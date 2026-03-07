import { useState, useEffect, useCallback } from 'react';
import {
  Container, Grid, Paper, Typography, Box, Card, CardContent,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Alert, Chip, Divider, IconButton,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import CommentIcon from '@mui/icons-material/Comment';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import reportService from '../services/reportService';

const SummaryCard = ({ title, value, icon, color = 'primary' }) => (
  <Card>
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography color="text.secondary" variant="body2">{title}</Typography>
          <Typography variant="h4">{value}</Typography>
        </Box>
        <Box sx={{ color: `${color}.main` }}>{icon}</Box>
      </Box>
    </CardContent>
  </Card>
);

const MonthlyRankingTable = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" py={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Typography color="text.secondary" align="center" py={3}>
        해당 월의 리포트가 없습니다.
      </Typography>
    );
  }

  const getRankIcon = (rank) => {
    if (rank === 1) return <EmojiEventsIcon sx={{ color: '#FFD700' }} />;
    if (rank === 2) return <EmojiEventsIcon sx={{ color: '#C0C0C0' }} />;
    if (rank === 3) return <EmojiEventsIcon sx={{ color: '#CD7F32' }} />;
    return null;
  };

  const getSentimentColor = (score) => {
    if (score > 0.2) return 'success';
    if (score < -0.2) return 'error';
    return 'default';
  };

  return (
    <TableContainer>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell width={60}>순위</TableCell>
            <TableCell>강사명</TableCell>
            <TableCell>학원</TableCell>
            <TableCell align="right">총 언급</TableCell>
            <TableCell align="right">긍정</TableCell>
            <TableCell align="right">부정</TableCell>
            <TableCell>감성</TableCell>
            <TableCell align="right">추천</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((teacher, index) => (
            <TableRow key={teacher.teacherId || index} hover>
              <TableCell>
                <Box display="flex" alignItems="center" gap={0.5}>
                  {getRankIcon(index + 1)}
                  <Typography fontWeight={index < 3 ? 'bold' : 'normal'}>
                    {index + 1}
                  </Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Typography fontWeight="medium">{teacher.teacherName}</Typography>
              </TableCell>
              <TableCell>{teacher.academyName}</TableCell>
              <TableCell align="right">{teacher.mentionCount}</TableCell>
              <TableCell align="right">
                <Typography color="success.main">{teacher.positiveCount}</Typography>
              </TableCell>
              <TableCell align="right">
                <Typography color="error.main">{teacher.negativeCount}</Typography>
              </TableCell>
              <TableCell>
                <Chip
                  size="small"
                  label={
                    teacher.avgSentimentScore != null
                      ? `${(teacher.avgSentimentScore * 100).toFixed(0)}%`
                      : '-'
                  }
                  color={getSentimentColor(teacher.avgSentimentScore)}
                />
              </TableCell>
              <TableCell align="right">
                <Box display="flex" alignItems="center" justifyContent="flex-end" gap={0.5}>
                  <ThumbUpIcon fontSize="small" color="primary" />
                  {teacher.recommendationCount}
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

function MonthlyReportsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() + 1 };
  });
  const [report, setReport] = useState(null);

  const fetchMonthlyData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await reportService.getMonthly(selectedMonth.year, selectedMonth.month);
      setReport(res.data);
    } catch (err) {
      console.error('Failed to fetch monthly report:', err);
      setError('월별 리포트를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, [selectedMonth]);

  useEffect(() => {
    fetchMonthlyData();
  }, [fetchMonthlyData]);

  const handlePrevMonth = () => {
    setSelectedMonth((prev) => {
      let newMonth = prev.month - 1;
      let newYear = prev.year;
      if (newMonth < 1) {
        newYear -= 1;
        newMonth = 12;
      }
      return { year: newYear, month: newMonth };
    });
  };

  const handleNextMonth = () => {
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;
    if (
      selectedMonth.year < currentYear ||
      (selectedMonth.year === currentYear && selectedMonth.month < currentMonth)
    ) {
      setSelectedMonth((prev) => {
        let newMonth = prev.month + 1;
        let newYear = prev.year;
        if (newMonth > 12) {
          newYear += 1;
          newMonth = 1;
        }
        return { year: newYear, month: newMonth };
      });
    }
  };

  const isCurrentMonth = () => {
    const now = new Date();
    return (
      selectedMonth.year === now.getFullYear() &&
      selectedMonth.month === now.getMonth() + 1
    );
  };

  const monthLabel = `${selectedMonth.year}년 ${selectedMonth.month}월`;

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            월별 리포트
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            월간 강사 평판 분석 결과
          </Typography>
        </Box>

        <Box display="flex" alignItems="center" gap={1}>
          <IconButton onClick={handlePrevMonth}>
            <ChevronLeftIcon />
          </IconButton>
          <Paper sx={{ px: 3, py: 1 }}>
            <Typography variant="h6">
              {monthLabel}
              {isCurrentMonth() && (
                <Chip label="현재" size="small" color="primary" sx={{ ml: 1 }} />
              )}
            </Typography>
          </Paper>
          <IconButton onClick={handleNextMonth} disabled={isCurrentMonth()}>
            <ChevronRightIcon />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
      )}

      {report && (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard
              title="월간 총 언급"
              value={report.totalMentions || 0}
              icon={<CommentIcon fontSize="large" />}
              color="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard
              title="긍정 언급"
              value={report.totalPositive || 0}
              icon={<ThumbUpIcon fontSize="large" />}
              color="success"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard
              title="언급된 강사"
              value={report.totalTeachers || 0}
              icon={<EmojiEventsIcon fontSize="large" />}
              color="secondary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard
              title="긍정 비율"
              value={report.positiveRatio != null ? `${report.positiveRatio}%` : '-'}
              icon={<TrendingUpIcon fontSize="large" />}
              color="info"
            />
          </Grid>
        </Grid>
      )}

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          {monthLabel} 강사 랭킹
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <MonthlyRankingTable
          data={report?.teacherSummaries}
          loading={loading}
        />
      </Paper>
    </Container>
  );
}

export default MonthlyReportsPage;
