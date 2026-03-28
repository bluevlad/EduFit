import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Typography, Box, Chip, CircularProgress,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import WhatshotIcon from '@mui/icons-material/Whatshot';
import AcUnitIcon from '@mui/icons-material/AcUnit';

const SIGNAL_CONFIG = {
  surge: { label: '급상승', color: 'error', icon: <WhatshotIcon sx={{ fontSize: 16 }} /> },
  rising: { label: '상승', color: 'success', icon: <TrendingUpIcon sx={{ fontSize: 16 }} /> },
  stable: { label: '유지', color: 'default', icon: <TrendingFlatIcon sx={{ fontSize: 16 }} /> },
  falling: { label: '하락', color: 'warning', icon: <TrendingDownIcon sx={{ fontSize: 16 }} /> },
  plunge: { label: '급하락', color: 'info', icon: <AcUnitIcon sx={{ fontSize: 16 }} /> },
};

const RocChip = ({ value }) => {
  if (value == null) return <Typography variant="body2" color="text.secondary">-</Typography>;
  const isPositive = value > 0;
  return (
    <Typography
      variant="body2"
      fontWeight="bold"
      color={isPositive ? 'success.main' : value < 0 ? 'error.main' : 'text.secondary'}
    >
      {isPositive ? '+' : ''}{value.toFixed(1)}%
    </Typography>
  );
};

function MomentumRankingTable({ data, loading }) {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (!data || !data.teachers || data.teachers.length === 0) {
    return (
      <Box p={3} textAlign="center">
        <Typography color="text.secondary">모멘텀 데이터가 없습니다.</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
        <Typography variant="subtitle2" color="text.secondary">
          기간: {data.period}
        </Typography>
      </Box>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell width={50}>#</TableCell>
              <TableCell>강사명</TableCell>
              <TableCell>학원</TableCell>
              <TableCell align="right">현재 언급</TableCell>
              <TableCell align="right">4주 ROC</TableCell>
              <TableCell align="right">8주 ROC</TableCell>
              <TableCell align="center">감성</TableCell>
              <TableCell align="right">감성 변화</TableCell>
              <TableCell align="center">시그널</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.teachers.map((teacher, index) => {
              const signalCfg = SIGNAL_CONFIG[teacher.momentumSignal] || SIGNAL_CONFIG.stable;
              return (
                <TableRow key={teacher.teacherId} hover>
                  <TableCell>
                    <Typography
                      fontWeight={index < 3 ? 'bold' : 'normal'}
                      color={index === 0 ? 'error.main' : index < 3 ? 'primary.main' : 'inherit'}
                    >
                      {index + 1}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography fontWeight="medium">{teacher.teacherName}</Typography>
                    {teacher.subjectName && (
                      <Typography variant="caption" color="text.secondary">
                        {teacher.subjectName}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>{teacher.academyName || '-'}</TableCell>
                  <TableCell align="right">
                    <Typography fontWeight="medium">{teacher.currentMentions}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      (이전: {teacher.previousMentions})
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <RocChip value={teacher.roc4w} />
                  </TableCell>
                  <TableCell align="right">
                    <RocChip value={teacher.roc8w} />
                  </TableCell>
                  <TableCell align="center">
                    {teacher.avgSentimentScore != null ? (
                      <Chip
                        size="small"
                        label={(teacher.avgSentimentScore * 100).toFixed(0) + '%'}
                        color={
                          teacher.avgSentimentScore > 0.2
                            ? 'success'
                            : teacher.avgSentimentScore < -0.2
                              ? 'error'
                              : 'default'
                        }
                        variant="outlined"
                      />
                    ) : '-'}
                  </TableCell>
                  <TableCell align="right">
                    {teacher.sentimentChange != null ? (
                      <Typography
                        variant="body2"
                        color={
                          teacher.sentimentChange > 0 ? 'success.main'
                          : teacher.sentimentChange < 0 ? 'error.main'
                          : 'text.secondary'
                        }
                      >
                        {teacher.sentimentChange > 0 ? '+' : ''}
                        {(teacher.sentimentChange * 100).toFixed(1)}%
                      </Typography>
                    ) : '-'}
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      size="small"
                      icon={signalCfg.icon}
                      label={signalCfg.label}
                      color={signalCfg.color}
                      variant="outlined"
                    />
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default MomentumRankingTable;
