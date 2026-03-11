import { useState } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import Header from './Header';
import AdminSidebar from './AdminSidebar';
import { useAuth } from '../../contexts/AuthContext';

const DRAWER_WIDTH = 240;

function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { admin, loading } = useAuth();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!admin) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Header
        drawerWidth={DRAWER_WIDTH}
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        isAdmin
      />
      <AdminSidebar open={sidebarOpen} drawerWidth={DRAWER_WIDTH} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: sidebarOpen ? `${DRAWER_WIDTH}px` : 0,
          transition: 'margin-left 0.3s',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}

export default AdminLayout;
