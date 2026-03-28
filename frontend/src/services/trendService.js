import apiClient from './apiClient';

const trendService = {
  getDashboard: (days = 90) =>
    apiClient.get('/analytics/dashboard', { params: { days } }),
  getMentionTrend: (days = 90) =>
    apiClient.get('/analytics/mention-trend', { params: { days } }),
  getSentimentBollinger: (days = 90) =>
    apiClient.get('/analytics/sentiment-bollinger', { params: { days } }),
  getMomentum: (limit = 20) =>
    apiClient.get('/analytics/momentum', { params: { limit } }),
  getPareto: (days = 90) =>
    apiClient.get('/analytics/pareto', { params: { days } }),
  getSeasonality: (days = 90) =>
    apiClient.get('/analytics/seasonality', { params: { days } }),
  getCorrelation: (days = 90) =>
    apiClient.get('/analytics/correlation', { params: { days } }),
  getTeacherHeatmap: (weeks = 12, limit = 15) =>
    apiClient.get('/analytics/teacher-heatmap', { params: { weeks, limit } }),
  getAcademyBubble: (days = 90) =>
    apiClient.get('/analytics/academy-bubble', { params: { days } }),
};

export default trendService;
