import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Paper,
  Box,
  Chip,
  Button,
  Stack,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import teacherService from '../services/teacherService';
import LoadingSpinner from '../components/common/LoadingSpinner';

function TeacherDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [teacher, setTeacher] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTeacher = async () => {
      try {
        const res = await teacherService.getById(id);
        setTeacher(res.data);
      } catch (err) {
        console.error('Failed to fetch teacher:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTeacher();
  }, [id]);

  if (loading) return <LoadingSpinner />;
  if (!teacher) return <Typography>Teacher not found</Typography>;

  return (
    <>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/teachers')} sx={{ mb: 2 }}>
        Back to Teachers
      </Button>

      <Paper sx={{ p: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h4">{teacher.name}</Typography>
          <Chip
            label={teacher.is_active ? 'Active' : 'Inactive'}
            color={teacher.is_active ? 'success' : 'default'}
          />
        </Stack>

        <Box sx={{ mt: 2 }}>
          {teacher.academy_name && (
            <Typography variant="body1" color="text.secondary" gutterBottom>
              Academy: {teacher.academy_name}
            </Typography>
          )}
          {teacher.subject_name && (
            <Typography variant="body1" color="text.secondary" gutterBottom>
              Subject: {teacher.subject_name}
            </Typography>
          )}
          {teacher.profile_url && (
            <Typography variant="body1" color="text.secondary" gutterBottom>
              Profile: {teacher.profile_url}
            </Typography>
          )}
        </Box>

        {teacher.aliases && teacher.aliases.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Aliases
            </Typography>
            {teacher.aliases.map((alias) => (
              <Chip key={alias} label={alias} sx={{ mr: 0.5, mb: 0.5 }} />
            ))}
          </Box>
        )}
      </Paper>
    </>
  );
}

export default TeacherDetailPage;
