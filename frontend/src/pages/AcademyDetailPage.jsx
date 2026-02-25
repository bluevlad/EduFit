import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Paper,
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Stack,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import academyService from '../services/academyService';
import LoadingSpinner from '../components/common/LoadingSpinner';

function AcademyDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [academy, setAcademy] = useState(null);
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [academyRes, teachersRes] = await Promise.all([
          academyService.getById(id),
          academyService.getTeachers(id),
        ]);
        setAcademy(academyRes.data);
        setTeachers(teachersRes.data);
      } catch (err) {
        console.error('Failed to fetch academy details:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) return <LoadingSpinner />;
  if (!academy) return <Typography>Academy not found</Typography>;

  return (
    <>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/academies')} sx={{ mb: 2 }}>
        Back to Academies
      </Button>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h4">{academy.name}</Typography>
          <Chip
            label={academy.is_active ? 'Active' : 'Inactive'}
            color={academy.is_active ? 'success' : 'default'}
          />
        </Stack>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body1" color="text.secondary">
            Code: {academy.code}
          </Typography>
          {academy.name_en && (
            <Typography variant="body1" color="text.secondary">
              English: {academy.name_en}
            </Typography>
          )}
          {academy.website && (
            <Typography variant="body1" color="text.secondary">
              Website: {academy.website}
            </Typography>
          )}
          {academy.keywords && academy.keywords.length > 0 && (
            <Box sx={{ mt: 1 }}>
              {academy.keywords.map((kw) => (
                <Chip key={kw} label={kw} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
              ))}
            </Box>
          )}
        </Box>
      </Paper>

      <Typography variant="h5" gutterBottom>
        Teachers ({teachers.length})
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Subject</TableCell>
              <TableCell>Aliases</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {teachers.map((teacher) => (
              <TableRow
                key={teacher.id}
                hover
                sx={{ cursor: 'pointer' }}
                onClick={() => navigate(`/teachers/${teacher.id}`)}
              >
                <TableCell>{teacher.id}</TableCell>
                <TableCell>{teacher.name}</TableCell>
                <TableCell>{teacher.subject_name || '-'}</TableCell>
                <TableCell>
                  {teacher.aliases?.map((alias) => (
                    <Chip key={alias} label={alias} size="small" sx={{ mr: 0.5 }} />
                  ))}
                </TableCell>
                <TableCell>
                  <Chip
                    label={teacher.is_active ? 'Active' : 'Inactive'}
                    color={teacher.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
}

export default AcademyDetailPage;
