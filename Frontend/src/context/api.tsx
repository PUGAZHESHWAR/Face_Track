import axios from 'axios';

const api = axios.create({
  baseURL: 'http://51.21.171.26:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
