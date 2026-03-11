import { useNavigate } from 'react-router-dom';
import { AppBar, Toolbar, Typography, IconButton, Box, Button, Avatar, Tooltip } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import LoginIcon from '@mui/icons-material/Login';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuth } from '../../contexts/AuthContext';

function Header({ drawerWidth, onToggleSidebar, isAdmin = false }) {
  const navigate = useNavigate();
  const { admin, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        ...(isAdmin && { bgcolor: '#1a237e' }),
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          edge="start"
          onClick={onToggleSidebar}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          {isAdmin ? 'EduFit Admin' : 'EduFit'}
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          {admin ? (
            <>
              <Tooltip title={admin.email}>
                <Avatar src={admin.picture} sx={{ width: 32, height: 32 }}>
                  {admin.name?.[0]}
                </Avatar>
              </Tooltip>
              <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
                {admin.name}
              </Typography>
              <IconButton color="inherit" onClick={handleLogout} size="small">
                <LogoutIcon />
              </IconButton>
            </>
          ) : (
            <Button
              color="inherit"
              startIcon={<LoginIcon />}
              onClick={() => navigate('/login')}
              size="small"
            >
              Admin
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
