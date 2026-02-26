import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import DashboardPage from './pages/DashboardPage';
import AcademyListPage from './pages/AcademyListPage';
import TeacherListPage from './pages/TeacherListPage';
import TeacherDetailPage from './pages/TeacherDetailPage';
import ReportsPage from './pages/ReportsPage';
import WeeklyReportsPage from './pages/WeeklyReportsPage';

function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/academies" element={<AcademyListPage />} />
        <Route path="/teachers" element={<TeacherListPage />} />
        <Route path="/teachers/:id" element={<TeacherDetailPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/weekly" element={<WeeklyReportsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
