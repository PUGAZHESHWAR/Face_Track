import axios from 'axios';

declare global {
  interface Window {
    _env_?: {
      BASE_URL?: string;
    };
  }
}

// export const baseURL = 'http://51.21.171.26:8000';
// const baseURL = window._env_?.BASE_URL || 'http://51.21.171.26:8000';
const baseURL = window._env_?.BASE_URL || 'http://localhost:8000';
// const baseURL = window._env_?.BASE_URL || 'https://face-track-1049299844333.asia-south2.run.app';

const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
export { baseURL };
