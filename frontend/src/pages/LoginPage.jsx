import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Container, Paper, Typography, Button, Box, Alert } from '@mui/material';
import GoogleIcon from '@mui/icons-material/Google';
import { useAuth } from '../contexts/AuthContext';

const ERROR_MESSAGES = {
  not_admin: '관리자 권한이 없는 계정입니다.',
  oauth_failed: 'Google 인증에 실패했습니다.',
};

function LoginPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { admin } = useAuth();
  const error = searchParams.get('error');

  useEffect(() => {
    if (admin) navigate('/admin/academies');
  }, [admin, navigate]);

  const handleGoogleLogin = () => {
    const backendUrl = import.meta.env.VITE_BACKEND_URL || window.location.origin;
    window.location.href = `${backendUrl}/api/auth/google/login`;
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
            {ERROR_MESSAGES[error] || '로그인 중 오류가 발생했습니다.'}
          </Alert>
        )}

        <Button
          variant="contained"
          size="large"
          startIcon={<GoogleIcon />}
          onClick={handleGoogleLogin}
          sx={{ px: 4, py: 1.5 }}
        >
          Google 계정으로 로그인
        </Button>

        <Box mt={4}>
          <Button variant="text" onClick={() => navigate('/')}>
            분석 화면으로 돌아가기
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default LoginPage;
