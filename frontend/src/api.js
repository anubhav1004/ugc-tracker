import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchHashtag = async (query, platform = 'tiktok', limit = 50) => {
  const response = await api.post('/api/search/hashtag', {
    query,
    platform,
    limit,
  });
  return response.data;
};

export const searchTerm = async (query, platform = 'tiktok', limit = 50) => {
  const response = await api.post('/api/search/term', {
    query,
    platform,
    limit,
  });
  return response.data;
};

export const getTrendingAudio = async (country = 'US', limit = 50) => {
  const response = await api.get('/api/trending/audio', {
    params: { country, limit },
  });
  return response.data;
};

export const getTrendingVideos = async (limit = 30) => {
  const response = await api.get('/api/trending/videos', {
    params: { limit },
  });
  return response.data;
};

export const getVideos = async (options = {}) => {
  const { platform = null, limit = 50, offset = 0 } = options;
  const response = await api.get('/api/videos', {
    params: { platform, limit, offset },
  });
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/api/stats');
  return response.data;
};

export const getAnalyticsTimeseries = async (days = 7) => {
  const response = await api.get('/api/analytics/timeseries', {
    params: { days },
  });
  return response.data;
};

export default api;
