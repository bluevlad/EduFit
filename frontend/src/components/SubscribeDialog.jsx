import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Alert,
  Typography,
  Box,
} from '@mui/material';
import { requestSubscription, verifySubscription } from '../services/subscriptionService';

function SubscribeDialog({ open, onClose }) {
  const [step, setStep] = useState('email'); // 'email' | 'verify' | 'done'
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRequestCode = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await requestSubscription(email);
      if (res.data.success) {
        setStep('verify');
      } else {
        setError(res.data.message);
      }
    } catch (e) {
      setError(e.response?.data?.detail || '요청에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await verifySubscription(email, code);
      if (res.data.success) {
        setStep('done');
      } else {
        setError(res.data.message);
      }
    } catch (e) {
      setError(e.response?.data?.detail || '인증에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setStep('email');
    setEmail('');
    setCode('');
    setError('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle>리포트 구독 신청</DialogTitle>
      <DialogContent>
        {step === 'email' && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              이메일을 입력하면 인증번호가 발송됩니다.
            </Typography>
            <TextField
              autoFocus
              fullWidth
              label="이메일"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && email && handleRequestCode()}
            />
          </Box>
        )}
        {step === 'verify' && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              <strong>{email}</strong>으로 발송된 인증번호 6자리를 입력해 주세요.
            </Typography>
            <TextField
              autoFocus
              fullWidth
              label="인증번호"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && code && handleVerify()}
              inputProps={{ maxLength: 6 }}
            />
          </Box>
        )}
        {step === 'done' && (
          <Box sx={{ mt: 1 }}>
            <Alert severity="success">구독이 완료되었습니다!</Alert>
          </Box>
        )}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        {step === 'email' && (
          <>
            <Button onClick={handleClose}>취소</Button>
            <Button variant="contained" onClick={handleRequestCode} disabled={!email || loading}>
              {loading ? '발송 중...' : '인증번호 받기'}
            </Button>
          </>
        )}
        {step === 'verify' && (
          <>
            <Button onClick={() => { setStep('email'); setError(''); }}>이전</Button>
            <Button variant="contained" onClick={handleVerify} disabled={!code || loading}>
              {loading ? '확인 중...' : '인증하기'}
            </Button>
          </>
        )}
        {step === 'done' && (
          <Button variant="contained" onClick={handleClose}>
            닫기
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}

export default SubscribeDialog;
