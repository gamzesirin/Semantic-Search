import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const searchAPI = {
  search: async (query, method = 'hybrid', topK = 10, threshold = 0.3, category = null) => {
    const response = await api.post('/search', {
      query,
      method,
      top_k: topK,
      similarity_threshold: threshold,
      category: category || null,
    });
    return response.data;
  },

  compare: async (query, topK = 10, threshold = 0.3, category = null) => {
    const response = await api.post('/compare', {
      query,
      top_k: topK,
      similarity_threshold: threshold,
      category: category || null,
    });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/stats');
    return response.data;
  },

  getCategories: async () => {
    const response = await api.get('/categories');
    return response.data;
  },
};

export default searchAPI;
