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
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Stack,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import academyService from '../services/academyService';
import LoadingSpinner from '../components/common/LoadingSpinner';

function AcademyListPage() {
  const navigate = useNavigate();
  const [academies, setAcademies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newAcademy, setNewAcademy] = useState({ name: '', code: '', website: '' });

  const fetchAcademies = async () => {
    try {
      const res = await academyService.getAll();
      setAcademies(res.data);
    } catch (err) {
      console.error('Failed to fetch academies:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAcademies();
  }, []);

  const handleCreate = async () => {
    try {
      await academyService.create(newAcademy);
      setDialogOpen(false);
      setNewAcademy({ name: '', code: '', website: '' });
      fetchAcademies();
    } catch (err) {
      console.error('Failed to create academy:', err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    try {
      await academyService.delete(id);
      fetchAcademies();
    } catch (err) {
      console.error('Failed to delete academy:', err);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Academies</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
          Add Academy
        </Button>
      </Stack>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Code</TableCell>
              <TableCell>Website</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {academies.map((academy) => (
              <TableRow
                key={academy.id}
                hover
                sx={{ cursor: 'pointer' }}
                onClick={() => navigate(`/academies/${academy.id}`)}
              >
                <TableCell>{academy.id}</TableCell>
                <TableCell>{academy.name}</TableCell>
                <TableCell>{academy.code}</TableCell>
                <TableCell>{academy.website}</TableCell>
                <TableCell>
                  <Chip
                    label={academy.is_active ? 'Active' : 'Inactive'}
                    color={academy.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    color="error"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(academy.id);
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Add Academy</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={newAcademy.name}
            onChange={(e) => setNewAcademy({ ...newAcademy, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Code"
            fullWidth
            value={newAcademy.code}
            onChange={(e) => setNewAcademy({ ...newAcademy, code: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Website"
            fullWidth
            value={newAcademy.website}
            onChange={(e) => setNewAcademy({ ...newAcademy, website: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default AcademyListPage;
