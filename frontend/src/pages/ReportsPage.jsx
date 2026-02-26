import { useState, useEffect } from 'react';
import {
  Container, Grid, Paper, Typography, Box, Card, CardContent,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Alert, Chip, Divider,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import CommentIcon from '@mui/icons-material/Comment';
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

const TeacherReportsTable = ({ reports, loading }) => {
  if (loading) return <CircularProgress />;

  if (!reports || reports.length === 0) {
    return (
      <Typography color="text.secondary" align="center" py={3}>
        해당 날짜의 리포트가 없습니다.
      </Typography>
    );
  }

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
            <TableCell>강사명</TableCell>
            <TableCell>학원</TableCell>
            <TableCell align="right">총 언급</TableCell>
            <TableCell align="right">긍정</TableCell>
            <TableCell align="right">부정</TableCell>
            <TableCell align="right">중립</TableCell>
            <TableCell>평균 감성</TableCell>
            <TableCell align="right">추천</TableCell>
            <TableCell>전일 대비</TableCell>
            <TableCell>키워드</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {reports.map((report) => (
            <TableRow key={report.teacherId} hover>
              <TableCell>
                <Typography fontWeight="medium">{report.teacherName}</Typography>
              </TableCell>
              <TableCell>{report.academyName}</TableCell>
              <TableCell align="right">{report.mentionCount}</TableCell>
              <TableCell align="right">
                <Typography color="success.main">{report.positiveCount}</Typography>
              </TableCell>
              <TableCell align="right">
                <Typography color="error.main">{report.negativeCount}</Typography>
              </TableCell>
              <TableCell align="right">{report.neutralCount}</TableCell>
              <TableCell>
                <Chip
                  size="small"
                  label={
                    report.avgSentimentScore
                      ? `${(report.avgSentimentScore * 100).toFixed(0)}%`
                      : '-'
                  }
                  color={getSentimentColor(report.avgSentimentScore)}
                />
              </TableCell>
              <TableCell align="right">
                <Box display="flex" alignItems="center" justifyContent="flex-end" gap={0.5}>
                  <ThumbUpIcon fontSize="small" color="primary" />
                  {report.recommendationCount}
                </Box>
              </TableCell>
              <TableCell>
                {report.mentionChange !== 0 && (
                  <Box display="flex" alignItems="center" gap={0.5}>
                    {report.mentionChange > 0 ? (
                      <TrendingUpIcon fontSize="small" color="success" />
                    ) : (
                      <TrendingDownIcon fontSize="small" color="error" />
                    )}
                    <Typography
                      variant="body2"
                      color={report.mentionChange > 0 ? 'success.main' : 'error.main'}
                    >
                      {report.mentionChange > 0 ? '+' : ''}
                      {report.mentionChange}
                    </Typography>
                  </Box>
                )}
              </TableCell>
              <TableCell>
                <Box display="flex" gap={0.5} flexWrap="wrap">
                  {report.topKeywords?.slice(0, 3).map((keyword, idx) => (
                    <Chip key={idx} label={keyword} size="small" variant="outlined" />
                  ))}
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

function ReportsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDate, setSelectedDate] = useState(dayjs());
  const [summary, setSummary] = useState(null);
  const [reports, setReports] = useState([]);

  useEffect(() => {
    fetchReports(selectedDate);
  }, [selectedDate]);

  const fetchReports = async (date) => {
    setLoading(true);
    setError(null);

    const dateStr = date.format('YYYY-MM-DD');

    try {
      const [summaryRes, reportsRes] = await Promise.all([
        reportService.getSummary(dateStr).catch(() => ({ data: null })),
        reportService.getDaily(dateStr).catch(() => ({ data: { teacherSummaries: [] } })),
      ]);

      setSummary(summaryRes.data);
      setReports(reportsRes.data?.teacherSummaries || []);
    } catch (err) {
      console.error('Failed to fetch reports:', err);
      setError('리포트를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Box>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              데일리 리포트
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              일별 강사 평판 분석 결과
            </Typography>
          </Box>
          <DatePicker
            label="날짜 선택"
            value={selectedDate}
            onChange={(newValue) => setSelectedDate(newValue)}
            maxDate={dayjs()}
            slotProps={{ textField: { size: 'small' } }}
          />
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
        )}

        {summary && (
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryCard
                title="총 언급"
                value={summary.totalMentions || 0}
                icon={<CommentIcon fontSize="large" />}
                color="primary"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryCard
                title="긍정 언급"
                value={summary.totalPositive || 0}
                icon={<ThumbUpIcon fontSize="large" />}
                color="success"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryCard
                title="부정 언급"
                value={summary.totalNegative || 0}
                icon={<ThumbDownIcon fontSize="large" />}
                color="error"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryCard
                title="추천 언급"
                value={summary.totalRecommendations || 0}
                icon={<TrendingUpIcon fontSize="large" />}
                color="info"
              />
            </Grid>
          </Grid>
        )}

        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            {selectedDate.format('YYYY년 MM월 DD일')} 강사별 리포트
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <TeacherReportsTable reports={reports} loading={loading} />
        </Paper>
      </Container>
    </LocalizationProvider>
  );
}

export default ReportsPage;
