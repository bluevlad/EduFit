import { useState } from 'react';
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
  Button,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SchoolIcon from '@mui/icons-material/School';
import PersonIcon from '@mui/icons-material/Person';
import AssessmentIcon from '@mui/icons-material/Assessment';
import DateRangeIcon from '@mui/icons-material/DateRange';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import EmailIcon from '@mui/icons-material/Email';
import SubscribeDialog from '../SubscribeDialog';

const analysisMenuItems = [
  { text: '종합 트렌드', icon: <DashboardIcon />, path: '/' },
  { text: '학원별 통계', icon: <SchoolIcon />, path: '/academies' },
  { text: '강사 분석', icon: <PersonIcon />, path: '/teachers' },
];

const reportMenuItems = [
  { text: '일간 리포트', icon: <AssessmentIcon />, path: '/reports' },
  { text: '주간 리포트', icon: <DateRangeIcon />, path: '/weekly' },
  { text: '월간 리포트', icon: <CalendarMonthIcon />, path: '/monthly' },
];

function Sidebar({ open, drawerWidth }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [subscribeOpen, setSubscribeOpen] = useState(false);

  const renderMenuSection = (label, items) => (
    <>
      <Box sx={{ px: 2, py: 1 }}>
        <Typography variant="caption" color="text.secondary" fontWeight="bold">
          {label}
        </Typography>
      </Box>
      <List>
        {items.map((item) => (
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
    </>
  );

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
          display: 'flex',
          flexDirection: 'column',
        },
      }}
    >
      <Toolbar />
      {renderMenuSection('분석/통계', analysisMenuItems)}
      <Divider />
      {renderMenuSection('리포트', reportMenuItems)}
      <Box sx={{ flexGrow: 1 }} />
      <Divider />
      <Box sx={{ p: 2 }}>
        <Button
          variant="outlined"
          startIcon={<EmailIcon />}
          fullWidth
          onClick={() => setSubscribeOpen(true)}
        >
          리포트 구독
        </Button>
      </Box>
      <SubscribeDialog open={subscribeOpen} onClose={() => setSubscribeOpen(false)} />
    </Drawer>
  );
}

export default Sidebar;
