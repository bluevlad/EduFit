import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import DashboardPage from './pages/DashboardPage';
import AcademyListPage from './pages/AcademyListPage';
import AcademyDetailPage from './pages/AcademyDetailPage';
import TeacherListPage from './pages/TeacherListPage';
import TeacherDetailPage from './pages/TeacherDetailPage';

function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/academies" element={<AcademyListPage />} />
        <Route path="/academies/:id" element={<AcademyDetailPage />} />
        <Route path="/teachers" element={<TeacherListPage />} />
        <Route path="/teachers/:id" element={<TeacherDetailPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
