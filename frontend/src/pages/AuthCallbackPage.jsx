import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Container, CircularProgress, Typography, Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

function AuthCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      navigate('/login?error=oauth_failed');
      return;
    }

    login(token)
      .then(() => navigate('/admin/academies'))
      .catch(() => {
        setError('인증 처리에 실패했습니다.');
        setTimeout(() => navigate('/login?error=oauth_failed'), 2000);
      });
  }, [searchParams, login, navigate]);

  return (
    <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
      {error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <Box>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography>로그인 처리 중...</Typography>
        </Box>
      )}
    </Container>
  );
}

export default AuthCallbackPage;
