import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import Header from './Header';
import Sidebar from './Sidebar';

const DRAWER_WIDTH = 240;

function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleToggleSidebar = () => {
    setSidebarOpen((prev) => !prev);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Header drawerWidth={DRAWER_WIDTH} onToggleSidebar={handleToggleSidebar} />
      <Sidebar open={sidebarOpen} drawerWidth={DRAWER_WIDTH} />
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

export default MainLayout;
