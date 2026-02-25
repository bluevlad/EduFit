import apiClient from './apiClient';

const academyService = {
  getAll: (params) => apiClient.get('/academies', { params }),
  getById: (id) => apiClient.get(`/academies/${id}`),
  getTeachers: (id, params) => apiClient.get(`/academies/${id}/teachers`, { params }),
  create: (data) => apiClient.post('/academies', data),
  update: (id, data) => apiClient.put(`/academies/${id}`, data),
  delete: (id) => apiClient.delete(`/academies/${id}`),
};

export default academyService;
