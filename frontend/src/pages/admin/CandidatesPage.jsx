import { useState, useEffect } from 'react';
import {
  Container, Typography, Box, Paper,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Chip, CircularProgress, Alert, Tooltip,
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, Select, MenuItem, FormControl, InputLabel,
  Tabs, Tab, Badge, Collapse, List, ListItem, ListItemText,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import BlockIcon from '@mui/icons-material/Block';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import apiClient from '../../services/apiClient';
import academyService from '../../services/academyService';
import subjectService from '../../services/subjectService';

function CandidatesPage() {
  const [candidates, setCandidates] = useState([]);
  const [stats, setStats] = useState({ pending: 0, registered: 0, ignored: 0 });
  const [academies, setAcademies] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [expandedId, setExpandedId] = useState(null);
  const [registerDialog, setRegisterDialog] = useState({ open: false, candidate: null });
  const [registerForm, setRegisterForm] = useState({ academy_id: '', subject_id: '', aliases: '' });

  const STATUS_MAP = ['pending', 'registered', 'ignored'];

  const fetchData = async () => {
    setLoading(true);
    try {
      const status = STATUS_MAP[tabValue];
      const [candidatesRes, statsRes, academiesRes, subjectsRes] = await Promise.all([
        apiClient.get('/unregistered-candidates', {
          params: { status, min_mentions: 1, limit: 100 },
        }),
        apiClient.get('/unregistered-candidates/stats'),
        academyService.getAll(),
        subjectService.getAll(),
      ]);
      setCandidates(candidatesRes.data || []);
      setStats(statsRes.data || {});
      setAcademies(academiesRes.data || []);
      setSubjects(subjectsRes.data || []);
      setError(null);
    } catch {
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [tabValue]);

  const handleRegister = async () => {
    const { candidate } = registerDialog;
    try {
      await apiClient.post(`/unregistered-candidates/${candidate.id}/resolve`, {
        action: 'register',
        academy_id: registerForm.academy_id || null,
        subject_id: registerForm.subject_id || null,
        aliases: registerForm.aliases
          ? registerForm.aliases.split(',').map((a) => a.trim()).filter(Boolean)
          : [],
      });
      setRegisterDialog({ open: false, candidate: null });
      setRegisterForm({ academy_id: '', subject_id: '', aliases: '' });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || '등록에 실패했습니다.');
    }
  };

  const handleIgnore = async (candidate) => {
    try {
      await apiClient.post(`/unregistered-candidates/${candidate.id}/resolve`, {
        action: 'ignore',
      });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || '처리에 실패했습니다.');
    }
  };

  const openRegister = (candidate) => {
    setRegisterDialog({ open: true, candidate });
    setRegisterForm({ academy_id: '', subject_id: '', aliases: '' });
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('ko-KR', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    });
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold">미등록 후보</Typography>
          <Typography variant="subtitle1" color="text.secondary">
            크롤링 중 감지된 미등록 인물 후보
          </Typography>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
          <Tab
            label={
              <Badge badgeContent={stats.pending} color="warning" max={99}>
                <Box sx={{ pr: 2 }}>검토 대기</Box>
              </Badge>
            }
          />
          <Tab label={`등록 완료 (${stats.registered})`} />
          <Tab label={`무시 (${stats.ignored})`} />
        </Tabs>
      </Paper>

      {loading ? (
        <Box display="flex" justifyContent="center" py={5}><CircularProgress /></Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell width={40} />
                <TableCell>이름</TableCell>
                <TableCell align="center">언급 횟수</TableCell>
                <TableCell>감지 소스</TableCell>
                <TableCell>최초 감지</TableCell>
                <TableCell>최근 감지</TableCell>
                {tabValue === 0 && <TableCell align="center">관리</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {candidates.map((c) => (
                <>
                  <TableRow key={c.id} hover>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => setExpandedId(expandedId === c.id ? null : c.id)}
                      >
                        {expandedId === c.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </TableCell>
                    <TableCell>
                      <Typography fontWeight="bold">{c.name}</Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={c.mention_count}
                        color={c.mention_count >= 10 ? 'error' : c.mention_count >= 5 ? 'warning' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={0.5} flexWrap="wrap">
                        {Object.entries(c.source_distribution || {}).map(([src, cnt]) => (
                          <Chip key={src} label={`${src}: ${cnt}`} size="small" variant="outlined" />
                        ))}
                      </Box>
                    </TableCell>
                    <TableCell>{formatDate(c.first_seen_at)}</TableCell>
                    <TableCell>{formatDate(c.last_seen_at)}</TableCell>
                    {tabValue === 0 && (
                      <TableCell align="center">
                        <Tooltip title="강사로 등록">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => openRegister(c)}
                          >
                            <PersonAddIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="무시">
                          <IconButton
                            size="small"
                            color="default"
                            onClick={() => handleIgnore(c)}
                          >
                            <BlockIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    )}
                  </TableRow>
                  <TableRow key={`${c.id}-ctx`}>
                    <TableCell colSpan={tabValue === 0 ? 7 : 6} sx={{ py: 0, borderBottom: expandedId === c.id ? undefined : 'none' }}>
                      <Collapse in={expandedId === c.id}>
                        <Box sx={{ py: 2, px: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            감지된 문맥 샘플
                          </Typography>
                          <List dense>
                            {(c.sample_contexts || []).map((ctx, i) => (
                              <ListItem key={i} sx={{ bgcolor: 'grey.50', mb: 0.5, borderRadius: 1 }}>
                                <ListItemText
                                  primary={ctx}
                                  primaryTypographyProps={{ variant: 'body2', fontFamily: 'monospace' }}
                                />
                              </ListItem>
                            ))}
                            {(!c.sample_contexts || c.sample_contexts.length === 0) && (
                              <Typography variant="body2" color="text.secondary">문맥 데이터 없음</Typography>
                            )}
                          </List>
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </>
              ))}
              {candidates.length === 0 && (
                <TableRow>
                  <TableCell colSpan={tabValue === 0 ? 7 : 6} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">
                      {tabValue === 0 ? '검토 대기 중인 후보가 없습니다.' : '해당 상태의 후보가 없습니다.'}
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* 강사 등록 다이얼로그 */}
      <Dialog
        open={registerDialog.open}
        onClose={() => setRegisterDialog({ open: false, candidate: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <PersonAddIcon color="primary" />
            강사로 등록: {registerDialog.candidate?.name}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            감지 횟수: {registerDialog.candidate?.mention_count}회
          </Typography>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            <FormControl fullWidth>
              <InputLabel>소속 학원</InputLabel>
              <Select
                value={registerForm.academy_id}
                label="소속 학원"
                onChange={(e) => setRegisterForm((p) => ({ ...p, academy_id: e.target.value }))}
              >
                <MenuItem value="">미지정</MenuItem>
                {academies.map((a) => (
                  <MenuItem key={a.id} value={a.id}>{a.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>과목</InputLabel>
              <Select
                value={registerForm.subject_id}
                label="과목"
                onChange={(e) => setRegisterForm((p) => ({ ...p, subject_id: e.target.value }))}
              >
                <MenuItem value="">미지정</MenuItem>
                {subjects.map((s) => (
                  <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="별명 (Aliases)"
              value={registerForm.aliases}
              onChange={(e) => setRegisterForm((p) => ({ ...p, aliases: e.target.value }))}
              helperText="콤마로 구분 (예: 홍쌤, 홍길T)"
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRegisterDialog({ open: false, candidate: null })}>취소</Button>
          <Button variant="contained" startIcon={<CheckCircleIcon />} onClick={handleRegister}>
            등록
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default CandidatesPage;
