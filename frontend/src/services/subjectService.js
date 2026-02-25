import apiClient from './apiClient';

const subjectService = {
  getAll: (params) => apiClient.get('/subjects', { params }),
  getById: (id) => apiClient.get(`/subjects/${id}`),
};

export default subjectService;
