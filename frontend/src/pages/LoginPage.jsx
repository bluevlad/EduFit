import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Paper, Typography, Box, Alert, Button } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

function LoginPage() {
  const navigate = useNavigate();
  const { admin, verifyGoogleToken } = useAuth();
  const googleBtnRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (admin) navigate('/admin/academies');
  }, [admin, navigate]);

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return;

    const initGoogleBtn = () => {
      if (!window.google?.accounts?.id || !googleBtnRef.current) return;
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleCredential,
      });
      window.google.accounts.id.renderButton(
        googleBtnRef.current,
        { theme: 'outline', size: 'large', width: 320, text: 'signin_with', locale: 'ko' },
      );
    };

    if (window.google?.accounts?.id) {
      initGoogleBtn();
    } else {
      const interval = setInterval(() => {
        if (window.google?.accounts?.id) {
          clearInterval(interval);
          initGoogleBtn();
        }
      }, 100);
      return () => clearInterval(interval);
    }
  }, []);

  const handleGoogleCredential = async (response) => {
    setLoading(true);
    setError('');
    try {
      await verifyGoogleToken(response.credential);
      navigate('/admin/academies');
    } catch (err) {
      const detail = err.response?.data?.detail || '';
      if (detail === 'not_admin') {
        setError('관리자 권한이 없는 계정입니다.');
      } else {
        setError('Google 인��에 실패했습니다.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          EduFit Admin
        </Typography>
        <Typography variant="body1" color="text.secondary" mb={3}>
          관리자 로그인이 필요합니다
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Typography color="text.secondary">인증 중...</Typography>
        ) : GOOGLE_CLIENT_ID ? (
          <Box ref={googleBtnRef} sx={{ display: 'flex', justifyContent: 'center' }} />
        ) : (
          <Alert severity="warning">Google OAuth가 설정되지 않았습니다.</Alert>
        )}

        <Box mt={4}>
          <Button variant="text" onClick={() => navigate('/')}>
            분석 화면으로 돌아가���
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default LoginPage;
