import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import DashboardPage from './pages/DashboardPage';
import AcademyListPage from './pages/AcademyListPage';
import TeacherListPage from './pages/TeacherListPage';
import TeacherDetailPage from './pages/TeacherDetailPage';
import ReportsPage from './pages/ReportsPage';
import WeeklyReportsPage from './pages/WeeklyReportsPage';
import MonthlyReportsPage from './pages/MonthlyReportsPage';
import LoginPage from './pages/LoginPage';
import AuthCallbackPage from './pages/AuthCallbackPage';
import AcademyManagePage from './pages/admin/AcademyManagePage';
import TeacherManagePage from './pages/admin/TeacherManagePage';
import CandidatesPage from './pages/admin/CandidatesPage';
import AdminRoute from './components/AdminRoute';

function App() {
  return (
    <Routes>
      {/* 인증 페이지 (레이아웃 없음) */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthCallbackPage />} />

      {/* 메인 레이아웃 */}
      <Route element={<MainLayout />}>
        {/* 분석/통계 (공개) */}
        <Route path="/" element={<DashboardPage />} />
        <Route path="/academies" element={<AcademyListPage />} />
        <Route path="/teachers" element={<TeacherListPage />} />
        <Route path="/teachers/:id" element={<TeacherDetailPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/weekly" element={<WeeklyReportsPage />} />
        <Route path="/monthly" element={<MonthlyReportsPage />} />

        {/* 관리자 전용 */}
        <Route element={<AdminRoute />}>
          <Route path="/admin/academies" element={<AcademyManagePage />} />
          <Route path="/admin/teachers" element={<TeacherManagePage />} />
          <Route path="/admin/candidates" element={<CandidatesPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
