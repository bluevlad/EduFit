import { Navigate, Outlet } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

function AdminRoute() {
  const { admin, loading } = useAuth();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" py={10}>
        <CircularProgress />
      </Box>
    );
  }

  if (!admin) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

export default AdminRoute;
