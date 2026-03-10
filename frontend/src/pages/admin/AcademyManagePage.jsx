import { useState, useEffect } from 'react';
import {
  Container, Typography, Box, Button, Paper,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Chip, CircularProgress, Alert,
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Switch, FormControlLabel, Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import academyService from '../../services/academyService';

const EMPTY_FORM = { name: '', name_en: '', code: '', website: '', logo_url: '', keywords: '', is_active: true };

function AcademyManagePage() {
  const [academies, setAcademies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const fetchAcademies = async () => {
    setLoading(true);
    try {
      const res = await academyService.getAll();
      setAcademies(res.data || []);
      setError(null);
    } catch {
      setError('학원 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAcademies(); }, []);

  const openCreate = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setDialogOpen(true);
  };

  const openEdit = (academy) => {
    setEditingId(academy.id);
    setForm({
      name: academy.name || '',
      name_en: academy.name_en || '',
      code: academy.code || '',
      website: academy.website || '',
      logo_url: academy.logo_url || '',
      keywords: (academy.keywords || []).join(', '),
      is_active: academy.is_active !== false,
    });
    setDialogOpen(true);
  };

  const openDelete = (academy) => {
    setDeleteTarget(academy);
    setDeleteDialogOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const payload = {
        ...form,
        keywords: form.keywords ? form.keywords.split(',').map((k) => k.trim()).filter(Boolean) : [],
      };

      if (editingId) {
        const { code, ...updateData } = payload;
        await academyService.update(editingId, updateData);
      } else {
        await academyService.create(payload);
      }
      setDialogOpen(false);
      fetchAcademies();
    } catch (err) {
      setError(err.response?.data?.detail || '저장에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    try {
      await academyService.delete(deleteTarget.id);
      setDeleteDialogOpen(false);
      setDeleteTarget(null);
      fetchAcademies();
    } catch (err) {
      setError(err.response?.data?.detail || '삭제에 실패했습니다.');
      setDeleteDialogOpen(false);
    }
  };

  const handleChange = (field) => (e) => {
    const value = field === 'is_active' ? e.target.checked : e.target.value;
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold">학원 관리</Typography>
          <Typography variant="subtitle1" color="text.secondary">
            학원 {academies.length}개
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
          학원 추가
        </Button>
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
                <TableCell>학원명</TableCell>
                <TableCell>코드</TableCell>
                <TableCell>웹사이트</TableCell>
                <TableCell>키워드</TableCell>
                <TableCell align="center">상태</TableCell>
                <TableCell align="center">관리</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {academies.map((academy) => (
                <TableRow key={academy.id} hover>
                  <TableCell>{academy.id}</TableCell>
                  <TableCell>
                    <Typography fontWeight="bold">{academy.name}</Typography>
                    {academy.name_en && (
                      <Typography variant="caption" color="text.secondary">{academy.name_en}</Typography>
                    )}
                  </TableCell>
                  <TableCell><Chip label={academy.code} size="small" variant="outlined" /></TableCell>
                  <TableCell>
                    {academy.website ? (
                      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                        {academy.website}
                      </Typography>
                    ) : '-'}
                  </TableCell>
                  <TableCell>
                    <Box display="flex" gap={0.5} flexWrap="wrap">
                      {(academy.keywords || []).map((kw, i) => (
                        <Chip key={i} label={kw} size="small" />
                      ))}
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={academy.is_active ? '활성' : '비활성'}
                      color={academy.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="수정">
                      <IconButton size="small" onClick={() => openEdit(academy)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="삭제">
                      <IconButton size="small" color="error" onClick={() => openDelete(academy)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
              {academies.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">등록된 학원이 없습니다.</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* 생성/수정 다이얼로그 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingId ? '학원 수정' : '학원 추가'}</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            <TextField label="학원명 *" value={form.name} onChange={handleChange('name')} fullWidth />
            <TextField label="영문명" value={form.name_en} onChange={handleChange('name_en')} fullWidth />
            <TextField
              label="코드 *"
              value={form.code}
              onChange={handleChange('code')}
              disabled={!!editingId}
              helperText={editingId ? '코드는 변경할 수 없습니다' : '고유 식별 코드 (예: megastudy)'}
              fullWidth
            />
            <TextField label="웹사이트" value={form.website} onChange={handleChange('website')} fullWidth />
            <TextField label="로고 URL" value={form.logo_url} onChange={handleChange('logo_url')} fullWidth />
            <TextField
              label="키워드"
              value={form.keywords}
              onChange={handleChange('keywords')}
              helperText="콤마로 구분 (예: 메가스터디, 메가, mega)"
              fullWidth
            />
            <FormControlLabel
              control={<Switch checked={form.is_active} onChange={handleChange('is_active')} />}
              label="활성 상태"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>취소</Button>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saving || !form.name || !form.code}
          >
            {saving ? '저장 중...' : '저장'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 삭제 확인 다이얼로그 */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>학원 삭제</DialogTitle>
        <DialogContent>
          <Typography>
            <strong>{deleteTarget?.name}</strong>을(를) 삭제하시겠습니까?
          </Typography>
          <Typography variant="body2" color="error" mt={1}>
            소속 강사 데이터에 영향을 줄 수 있습니다.
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

export default AcademyManagePage;
