import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Chip,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import teacherService from '../services/teacherService';
import academyService from '../services/academyService';
import subjectService from '../services/subjectService';
import LoadingSpinner from '../components/common/LoadingSpinner';

function TeacherListPage() {
  const navigate = useNavigate();
  const [teachers, setTeachers] = useState([]);
  const [academies, setAcademies] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    academy_id: '',
    subject_id: '',
    search: '',
  });

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [academyRes, subjectRes] = await Promise.all([
          academyService.getAll(),
          subjectService.getAll(),
        ]);
        setAcademies(academyRes.data);
        setSubjects(subjectRes.data);
      } catch (err) {
        console.error('Failed to fetch filter options:', err);
      }
    };
    fetchOptions();
  }, []);

  useEffect(() => {
    const fetchTeachers = async () => {
      setLoading(true);
      try {
        const params = {};
        if (filters.academy_id) params.academy_id = filters.academy_id;
        if (filters.subject_id) params.subject_id = filters.subject_id;

        let res;
        if (filters.search) {
          res = await teacherService.search(filters.search, params);
        } else {
          res = await teacherService.getAll(params);
        }
        setTeachers(res.data);
      } catch (err) {
        console.error('Failed to fetch teachers:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTeachers();
  }, [filters]);

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Teachers
      </Typography>

      <Stack direction="row" spacing={2} mb={3}>
        <TextField
          label="Search"
          size="small"
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          InputProps={{ startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} /> }}
          sx={{ minWidth: 200 }}
        />
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Academy</InputLabel>
          <Select
            value={filters.academy_id}
            label="Academy"
            onChange={(e) => setFilters({ ...filters, academy_id: e.target.value })}
          >
            <MenuItem value="">All</MenuItem>
            {academies.map((a) => (
              <MenuItem key={a.id} value={a.id}>{a.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Subject</InputLabel>
          <Select
            value={filters.subject_id}
            label="Subject"
            onChange={(e) => setFilters({ ...filters, subject_id: e.target.value })}
          >
            <MenuItem value="">All</MenuItem>
            {subjects.map((s) => (
              <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Stack>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Academy</TableCell>
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
                  <TableCell>{teacher.academy_name || '-'}</TableCell>
                  <TableCell>{teacher.subject_name || '-'}</TableCell>
                  <TableCell>
                    {teacher.aliases?.slice(0, 3).map((alias) => (
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
      )}
    </>
  );
}

export default TeacherListPage;
