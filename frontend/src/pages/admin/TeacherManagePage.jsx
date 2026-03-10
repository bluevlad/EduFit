import { useState, useEffect } from 'react';
import {
  Container, Typography, Box, Button, Paper,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Chip, CircularProgress, Alert,
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Switch, FormControlLabel, Tooltip,
  MenuItem, Select, InputLabel, FormControl,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import teacherService from '../../services/teacherService';
import academyService from '../../services/academyService';
import subjectService from '../../services/subjectService';

const EMPTY_FORM = { name: '', academy_id: '', subject_id: '', aliases: '', profile_url: '', is_active: true };

function TeacherManagePage() {
  const [teachers, setTeachers] = useState([]);
  const [academies, setAcademies] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [filterAcademy, setFilterAcademy] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [teachersRes, academiesRes, subjectsRes] = await Promise.all([
        teacherService.getAll(),
        academyService.getAll(),
        subjectService.getAll(),
      ]);
      setTeachers(teachersRes.data || []);
      setAcademies(academiesRes.data || []);
      setSubjects(subjectsRes.data || []);
      setError(null);
    } catch {
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const openCreate = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setDialogOpen(true);
  };

  const openEdit = (teacher) => {
    setEditingId(teacher.id);
    setForm({
      name: teacher.name || '',
      academy_id: teacher.academy_id || '',
      subject_id: teacher.subject_id || '',
      aliases: (teacher.aliases || []).join(', '),
      profile_url: teacher.profile_url || '',
      is_active: teacher.is_active !== false,
    });
    setDialogOpen(true);
  };

  const openDelete = (teacher) => {
    setDeleteTarget(teacher);
    setDeleteDialogOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const payload = {
        ...form,
        academy_id: form.academy_id || null,
        subject_id: form.subject_id || null,
        aliases: form.aliases ? form.aliases.split(',').map((a) => a.trim()).filter(Boolean) : [],
      };

      if (editingId) {
        await teacherService.update(editingId, payload);
      } else {
        await teacherService.create(payload);
      }
      setDialogOpen(false);
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || '저장에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    try {
      await teacherService.delete(deleteTarget.id);
      setDeleteDialogOpen(false);
      setDeleteTarget(null);
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || '삭제에 실패했습니다.');
      setDeleteDialogOpen(false);
    }
  };

  const handleChange = (field) => (e) => {
    const value = field === 'is_active' ? e.target.checked : e.target.value;
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const filteredTeachers = filterAcademy
    ? teachers.filter((t) => t.academy_id === Number(filterAcademy))
    : teachers;

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold">강사 관리</Typography>
          <Typography variant="subtitle1" color="text.secondary">
            강사 {filteredTeachers.length}명 {filterAcademy ? `(필터 적용)` : `/ 전체 ${teachers.length}명`}
          </Typography>
        </Box>
        <Box display="flex" gap={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>학원 필터</InputLabel>
            <Select
              value={filterAcademy}
              label="학원 필터"
              onChange={(e) => setFilterAcademy(e.target.value)}
            >
              <MenuItem value="">전체</MenuItem>
              {academies.map((a) => (
                <MenuItem key={a.id} value={a.id}>{a.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
            강사 추가
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" py={5}><CircularProgress /></Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>강사명</TableCell>
                <TableCell>소속 학원</TableCell>
                <TableCell>과목</TableCell>
                <TableCell>별명</TableCell>
                <TableCell align="center">상태</TableCell>
                <TableCell align="center">관리</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredTeachers.map((teacher) => (
                <TableRow key={teacher.id} hover>
                  <TableCell>{teacher.id}</TableCell>
                  <TableCell>
                    <Typography fontWeight="bold">{teacher.name}</Typography>
                  </TableCell>
                  <TableCell>{teacher.academy_name || '-'}</TableCell>
                  <TableCell>{teacher.subject_name || '-'}</TableCell>
                  <TableCell>
                    <Box display="flex" gap={0.5} flexWrap="wrap">
                      {(teacher.aliases || []).map((alias, i) => (
                        <Chip key={i} label={alias} size="small" variant="outlined" />
                      ))}
                      {(!teacher.aliases || teacher.aliases.length === 0) && '-'}
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={teacher.is_active ? '활성' : '비활성'}
                      color={teacher.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="수정">
                      <IconButton size="small" onClick={() => openEdit(teacher)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="삭제">
                      <IconButton size="small" color="error" onClick={() => openDelete(teacher)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
              {filteredTeachers.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">등록된 강사가 없습니다.</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* 생성/수정 다이얼로그 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingId ? '강사 수정' : '강사 추가'}</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            <TextField label="강사명 *" value={form.name} onChange={handleChange('name')} fullWidth />
            <FormControl fullWidth>
              <InputLabel>소속 학원</InputLabel>
              <Select value={form.academy_id} label="소속 학원" onChange={handleChange('academy_id')}>
                <MenuItem value="">미지정</MenuItem>
                {academies.map((a) => (
                  <MenuItem key={a.id} value={a.id}>{a.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>과목</InputLabel>
              <Select value={form.subject_id} label="과목" onChange={handleChange('subject_id')}>
                <MenuItem value="">미지정</MenuItem>
                {subjects.map((s) => (
                  <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="별명 (Aliases)"
              value={form.aliases}
              onChange={handleChange('aliases')}
              helperText="콤마로 구분 (예: 선재쌤, 이선재T, 선재)"
              fullWidth
            />
            <TextField label="프로필 URL" value={form.profile_url} onChange={handleChange('profile_url')} fullWidth />
            <FormControlLabel
              control={<Switch checked={form.is_active} onChange={handleChange('is_active')} />}
              label="활성 상태"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>취소</Button>
          <Button variant="contained" onClick={handleSave} disabled={saving || !form.name}>
            {saving ? '저장 중...' : '저장'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 삭제 확인 다이얼로그 */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>강사 삭제</DialogTitle>
        <DialogContent>
          <Typography>
            <strong>{deleteTarget?.name}</strong>을(를) 삭제하시겠습니까?
          </Typography>
          <Typography variant="body2" color="error" mt={1}>
            해당 강사의 멘션 및 리포트 데이터에 영향을 줄 수 있습니다.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>취소</Button>
          <Button variant="contained" color="error" onClick={handleDelete}>삭제</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default TeacherManagePage;
