import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Typography, Box, Paper, Tooltip,
} from '@mui/material';

const sentimentToColor = (score) => {
  if (score == null) return '#e0e0e0';
  // -1 → red(0), 0 → yellow(60), 1 → green(120)
  const hue = ((score + 1) / 2) * 120;
  return `hsl(${hue}, 70%, 42%)`;
};

const textColor = (score) => {
  if (score == null) return '#757575';
  return '#fff';
};

const formatWeekLabel = (weekStr) => {
  // "2026-W10" → "W10"
  const parts = weekStr.split('-');
  return parts.length === 2 ? parts[1] : weekStr;
};

function TeacherHeatmap({ data }) {
  if (!data || !data.weeks || data.weeks.length === 0 || !data.teachers || data.teachers.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">히트맵 데이터가 없습니다.</Typography>
      </Paper>
    );
  }

  const { weeks, teachers, matrix } = data;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box display="flex" gap={1} alignItems="center">
          <Typography variant="caption" color="text.secondary">감성:</Typography>
          <Box display="flex" alignItems="center" gap={0.5}>
            <Box sx={{ width: 16, height: 16, borderRadius: 0.5, bgcolor: sentimentToColor(-1) }} />
            <Typography variant="caption">부정</Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={0.5}>
            <Box sx={{ width: 16, height: 16, borderRadius: 0.5, bgcolor: sentimentToColor(0) }} />
            <Typography variant="caption">중립</Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={0.5}>
            <Box sx={{ width: 16, height: 16, borderRadius: 0.5, bgcolor: sentimentToColor(1) }} />
            <Typography variant="caption">긍정</Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={0.5} ml={1}>
            <Box sx={{ width: 16, height: 16, borderRadius: 0.5, bgcolor: '#e0e0e0' }} />
            <Typography variant="caption">데이터 없음</Typography>
          </Box>
        </Box>
      </Box>

      <TableContainer sx={{ maxHeight: 600 }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell
                sx={{ position: 'sticky', left: 0, zIndex: 3, bgcolor: 'background.paper', minWidth: 140 }}
              >
                강사
              </TableCell>
              {weeks.map((w) => (
                <TableCell key={w} align="center" sx={{ minWidth: 52, px: 0.5 }}>
                  <Typography variant="caption">{formatWeekLabel(w)}</Typography>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {teachers.map((teacher, rowIdx) => (
              <TableRow key={teacher.id} hover>
                <TableCell
                  sx={{
                    position: 'sticky',
                    left: 0,
                    zIndex: 1,
                    bgcolor: 'background.paper',
                    borderRight: '1px solid',
                    borderRightColor: 'divider',
                  }}
                >
                  <Typography variant="body2" fontWeight="medium" noWrap>
                    {teacher.name}
                  </Typography>
                  {teacher.academy && (
                    <Typography variant="caption" color="text.secondary" noWrap>
                      {teacher.academy}
                    </Typography>
                  )}
                </TableCell>
                {matrix[rowIdx].map((cell, colIdx) => (
                  <Tooltip
                    key={colIdx}
                    title={
                      cell.mentions > 0
                        ? `${weeks[colIdx]} | 언급: ${cell.mentions} | 감성: ${cell.sentiment != null ? (cell.sentiment * 100).toFixed(0) + '%' : 'N/A'}`
                        : `${weeks[colIdx]} | 데이터 없음`
                    }
                    arrow
                  >
                    <TableCell
                      align="center"
                      sx={{
                        px: 0.5,
                        py: 0.75,
                        bgcolor: sentimentToColor(cell.sentiment),
                        color: textColor(cell.sentiment),
                        fontWeight: cell.mentions > 0 ? 'bold' : 'normal',
                        fontSize: '0.75rem',
                        cursor: 'default',
                        border: '1px solid',
                        borderColor: 'rgba(255,255,255,0.3)',
                      }}
                    >
                      {cell.mentions > 0 ? cell.mentions : ''}
                    </TableCell>
                  </Tooltip>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default TeacherHeatmap;
