import apiClient from './apiClient';

const reportService = {
  getDaily: (date) => apiClient.get('/reports/daily', { params: { date } }),
  getWeekly: (year, week) => apiClient.get('/reports/weekly', { params: { year, week } }),
  getMonthly: (year, month) => apiClient.get('/reports/monthly', { params: { year, month } }),
  getPeriods: () => apiClient.get('/reports/periods'),
  getSummary: (date) => apiClient.get('/analysis/summary', { params: { date } }),
};

export default reportService;
