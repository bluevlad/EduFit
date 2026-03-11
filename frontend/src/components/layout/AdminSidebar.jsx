import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  Toolbar,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Box,
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import GroupIcon from '@mui/icons-material/Group';
import PersonSearchIcon from '@mui/icons-material/PersonSearch';
import BarChartIcon from '@mui/icons-material/BarChart';

const adminMenuItems = [
  { text: '학원 관리', icon: <SettingsIcon />, path: '/admin/academies' },
  { text: '강사 관리', icon: <GroupIcon />, path: '/admin/teachers' },
  { text: '미등록 후보', icon: <PersonSearchIcon />, path: '/admin/candidates' },
];

function AdminSidebar({ open, drawerWidth }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant="persistent"
      open={open}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar />
      <Box sx={{ px: 2, py: 1 }}>
        <Typography variant="caption" color="text.secondary" fontWeight="bold">
          관리
        </Typography>
      </Box>
      <List>
        {adminMenuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={() => navigate('/')}>
            <ListItemIcon><BarChartIcon /></ListItemIcon>
            <ListItemText primary="분석/통계 화면으로" />
          </ListItemButton>
        </ListItem>
      </List>
    </Drawer>
  );
}

export default AdminSidebar;
