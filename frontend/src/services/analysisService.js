import apiClient from './apiClient';

const analysisService = {
  getSummary: (date) => apiClient.get('/analysis/summary', { params: { date } }),
  getRanking: (date, limit = 20) =>
    apiClient.get('/analysis/ranking', { params: { date, limit } }),
  getAcademyStats: (date) =>
    apiClient.get('/analysis/academy-stats', { params: { date } }),
};

export default analysisService;
