import apiClient from './apiClient';

const teacherService = {
  getAll: (params) => apiClient.get('/teachers', { params }),
  getById: (id) => apiClient.get(`/teachers/${id}`),
  search: (q, params) => apiClient.get('/teachers/search', { params: { q, ...params } }),
  getMentions: (id, params) => apiClient.get(`/teachers/${id}/mentions`, { params }),
  getReports: (id, params) => apiClient.get(`/teachers/${id}/reports`, { params }),
  create: (data) => apiClient.post('/teachers', data),
  update: (id, data) => apiClient.put(`/teachers/${id}`, data),
  delete: (id) => apiClient.delete(`/teachers/${id}`),
};

export default teacherService;
