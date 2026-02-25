import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
} from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import PersonIcon from '@mui/icons-material/Person';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import academyService from '../services/academyService';
import teacherService from '../services/teacherService';
import subjectService from '../services/subjectService';
import LoadingSpinner from '../components/common/LoadingSpinner';

function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [academies, teachers, subjects] = await Promise.all([
          academyService.getAll(),
          teacherService.getAll(),
          subjectService.getAll(),
        ]);
        setStats({
          academyCount: academies.data.length,
          teacherCount: teachers.data.length,
          subjectCount: subjects.data.length,
        });
      } catch (err) {
        console.error('Failed to fetch stats:', err);
        setStats({ academyCount: 0, teacherCount: 0, subjectCount: 0 });
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <LoadingSpinner />;

  const cards = [
    {
      title: 'Academies',
      count: stats.academyCount,
      icon: <SchoolIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      path: '/academies',
    },
    {
      title: 'Teachers',
      count: stats.teacherCount,
      icon: <PersonIcon sx={{ fontSize: 48, color: 'secondary.main' }} />,
      path: '/teachers',
    },
    {
      title: 'Subjects',
      count: stats.subjectCount,
      icon: <MenuBookIcon sx={{ fontSize: 48, color: 'success.main' }} />,
      path: null,
    },
  ];

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        {cards.map((card) => (
          <Grid item xs={12} sm={6} md={4} key={card.title}>
            <Card>
              <CardActionArea
                onClick={() => card.path && navigate(card.path)}
                disabled={!card.path}
              >
                <CardContent sx={{ textAlign: 'center', py: 4 }}>
                  {card.icon}
                  <Typography variant="h3" sx={{ mt: 2 }}>
                    {card.count}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary">
                    {card.title}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </>
  );
}

export default DashboardPage;
