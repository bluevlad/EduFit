import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Typography, Box, Paper, Alert,
} from '@mui/material';

const METRIC_KEYS = [
  'mentionCount',
  'positiveCount',
  'negativeCount',
  'recommendationCount',
  'sentimentScore',
];

const METRIC_LABELS = {
  mentionCount: '언급수',
  positiveCount: '긍정수',
  negativeCount: '부정수',
  recommendationCount: '추천수',
  sentimentScore: '감성점수',
};

const correlationToColor = (r) => {
  if (r === 1) return 'rgba(25, 118, 210, 0.15)';
  if (r > 0) return `rgba(25, 118, 210, ${Math.abs(r) * 0.6})`;
  if (r < 0) return `rgba(244, 67, 54, ${Math.abs(r) * 0.6})`;
  return '#ffffff';
};

const textColorForCorrelation = (r) => {
  const ar = Math.abs(r);
  return ar >= 0.5 ? '#fff' : '#333';
};

const strengthLabel = (r) => {
  const ar = Math.abs(r);
  if (ar >= 0.7) return '강함';
  if (ar >= 0.4) return '보통';
  if (ar >= 0.2) return '약함';
  return '미미';
};

function CorrelationMatrix({ data }) {
  if (!data || !data.pairs || data.pairs.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">상관관계 데이터가 없습니다.</Typography>
      </Paper>
    );
  }

  const { pairs, insights } = data;

  // 5×5 대칭 매트릭스 구성
  const matrix = {};
  for (const key of METRIC_KEYS) {
    matrix[key] = {};
    matrix[key][key] = 1.0;
  }
  for (const pair of pairs) {
    matrix[pair.metric1][pair.metric2] = pair.correlation;
    matrix[pair.metric2][pair.metric1] = pair.correlation;
  }

  return (
    <Box>
      {/* 범례 */}
      <Box display="flex" gap={2} mb={2} alignItems="center">
        <Typography variant="caption" color="text.secondary">상관관계:</Typography>
        <Box display="flex" alignItems="center" gap={0.5}>
          <Box sx={{ width: 16, height: 16, borderRadius: 0.5, bgcolor: 'rgba(244, 67, 54, 0.6)' }} />
          <Typography variant="caption">음의 상관</Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={0.5}>
          <Box sx={{ width: 16, height: 16, borderRadius: 0.5, bgcolor: '#ffffff', border: '1px solid #e0e0e0' }} />
          <Typography variant="caption">무상관</Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={0.5}>
          <Box sx={{ width: 16, height: 16, borderRadius: 0.5, bgcolor: 'rgba(25, 118, 210, 0.6)' }} />
          <Typography variant="caption">양의 상관</Typography>
        </Box>
      </Box>

      {/* 매트릭스 테이블 */}
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ bgcolor: 'background.paper', fontWeight: 'bold' }} />
              {METRIC_KEYS.map((key) => (
                <TableCell
                  key={key}
                  align="center"
                  sx={{ fontWeight: 'bold', minWidth: 80 }}
                >
                  {METRIC_LABELS[key]}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {METRIC_KEYS.map((rowKey) => (
              <TableRow key={rowKey}>
                <TableCell sx={{ fontWeight: 'bold', bgcolor: 'background.paper' }}>
                  {METRIC_LABELS[rowKey]}
                </TableCell>
                {METRIC_KEYS.map((colKey) => {
                  const value = matrix[rowKey]?.[colKey] ?? 0;
                  const isDiagonal = rowKey === colKey;
                  return (
                    <TableCell
                      key={colKey}
                      align="center"
                      sx={{
                        bgcolor: correlationToColor(value),
                        color: textColorForCorrelation(value),
                        fontWeight: isDiagonal ? 'normal' : 'bold',
                        fontSize: '0.85rem',
                        cursor: 'default',
                        border: '1px solid',
                        borderColor: 'divider',
                      }}
                    >
                      <Typography variant="body2" fontWeight={isDiagonal ? 'normal' : 'bold'}>
                        {value.toFixed(2)}
                      </Typography>
                      {!isDiagonal && (
                        <Typography variant="caption" sx={{ opacity: 0.8, display: 'block', fontSize: '0.65rem' }}>
                          {strengthLabel(value)}
                        </Typography>
                      )}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 인사이트 */}
      {insights && insights.length > 0 && (
        <Box mt={2} display="flex" flexDirection="column" gap={1}>
          <Typography variant="subtitle2" gutterBottom>
            주요 발견
          </Typography>
          {insights.map((insight, idx) => (
            <Alert key={idx} severity="info" variant="outlined" sx={{ py: 0.5 }}>
              {insight}
            </Alert>
          ))}
        </Box>
      )}
    </Box>
  );
}

export default CorrelationMatrix;
