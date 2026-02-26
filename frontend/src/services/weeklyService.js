import apiClient from './apiClient';

const weeklyService = {
  getSummary: (year, week) => apiClient.get('/weekly/summary', { params: { year, week } }),
  getRanking: (year, week, limit = 20) =>
    apiClient.get('/weekly/ranking', { params: { year, week, limit } }),
  getTeacherTrend: (teacherId, weeks = 8) =>
    apiClient.get(`/weekly/teacher/${teacherId}/trend`, { params: { weeks } }),
};

export default weeklyService;
