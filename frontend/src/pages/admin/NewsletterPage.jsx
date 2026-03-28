import { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Stack,
  TextField,
  MenuItem,
  Alert,
  Snackbar,
  CircularProgress,
  Divider,
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import PreviewIcon from '@mui/icons-material/Preview';
import RefreshIcon from '@mui/icons-material/Refresh';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import apiClient from '../../services/apiClient';

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

function NewsletterPage() {
  const [year, setYear] = useState(currentYear);
  const [month, setMonth] = useState(currentMonth);
  const [days, setDays] = useState(30);
  const [htmlContent, setHtmlContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '' });
  const iframeRef = useRef(null);

  const fetchPreview = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.get('/newsletter/html', {
        params: { year, month, days },
      });
      setHtmlContent(res.data.html);
    } catch (err) {
      setError(err.response?.data?.detail || '뉴스레터 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPreview();
  }, []);

  useEffect(() => {
    if (htmlContent && iframeRef.current) {
      const doc = iframeRef.current.contentDocument;
      doc.open();
      doc.write(htmlContent);
      doc.close();
    }
  }, [htmlContent]);

  const handleCopyHtml = async () => {
    try {
      await navigator.clipboard.writeText(htmlContent);
      setSnackbar({ open: true, message: 'HTML이 클립보드에 복사되었습니다.' });
    } catch {
      setSnackbar({ open: true, message: '복사에 실패했습니다.' });
    }
  };

  const handleOpenPreview = () => {
    const basePath = import.meta.env.VITE_BACKEND_URL || '';
    const token = localStorage.getItem('admin_token');
    const params = new URLSearchParams({ year, month, days });
    const url = `${basePath}/api/v1/newsletter/preview?${params}`;
    const win = window.open('about:blank', '_blank');
    if (win) {
      fetch(url, { headers: { Authorization: `Bearer ${token}` } })
        .then((res) => res.text())
        .then((html) => {
          win.document.open();
          win.document.write(html);
          win.document.close();
        });
    }
  };

  return (
    <Box>
      <Typography variant="h5" fontWeight="bold" gutterBottom>
        월간 뉴스레터
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        트렌드 분석 데이터를 이메일 뉴스레터 형식으로 생성합니다.
        생성된 HTML을 뉴스레터 플랫폼에 복사하여 발송할 수 있습니다.
      </Typography>

      {/* Controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
          <TextField
            select
            label="연도"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            size="small"
            sx={{ width: 100 }}
          >
            {[currentYear - 1, currentYear].map((y) => (
              <MenuItem key={y} value={y}>{y}년</MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="월"
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
            size="small"
            sx={{ width: 90 }}
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <MenuItem key={m} value={m}>{m}월</MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="분석 기간"
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            size="small"
            sx={{ width: 120 }}
          >
            {[7, 14, 30, 60, 90].map((d) => (
              <MenuItem key={d} value={d}>{d}일</MenuItem>
            ))}
          </TextField>

          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={fetchPreview}
            disabled={loading}
          >
            {loading ? '생성 중...' : '생성'}
          </Button>

          <Divider orientation="vertical" flexItem />

          <Button
            variant="outlined"
            startIcon={<ContentCopyIcon />}
            onClick={handleCopyHtml}
            disabled={!htmlContent}
          >
            HTML 복사
          </Button>

          <Button
            variant="outlined"
            startIcon={<OpenInNewIcon />}
            onClick={handleOpenPreview}
            disabled={!htmlContent}
          >
            새 창에서 보기
          </Button>
        </Stack>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Preview */}
      <Paper sx={{ overflow: 'hidden' }}>
        <Box sx={{ p: 1.5, background: '#f5f5f5', borderBottom: '1px solid #e0e0e0' }}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <PreviewIcon fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              미리보기 (이메일 클라이언트 렌더링 시뮬레이션)
            </Typography>
          </Stack>
        </Box>
        {loading ? (
          <Box sx={{ p: 8, textAlign: 'center' }}>
            <CircularProgress />
            <Typography sx={{ mt: 2 }} color="text.secondary">뉴스레터 생성 중...</Typography>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 2, background: '#e8e8e8' }}>
            <iframe
              ref={iframeRef}
              title="Newsletter Preview"
              style={{
                width: 640,
                minHeight: 800,
                border: '1px solid #ccc',
                borderRadius: 4,
                background: '#fff',
              }}
            />
          </Box>
        )}
      </Paper>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={2000}
        onClose={() => setSnackbar({ open: false, message: '' })}
        message={snackbar.message}
      />
    </Box>
  );
}

export default NewsletterPage;
