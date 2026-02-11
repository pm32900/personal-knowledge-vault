import axios from 'axios';
import type { Token, User, Note, NoteCreate, NoteUpdate, NoteSearchResult, RAGResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(err);
  }
);

// Auth
export const authApi = {
  register: (email: string, password: string) =>
    api.post<User>('/auth/register', { email, password }),
  login: (email: string, password: string) =>
    api.post<Token>('/auth/login', { email, password }),
};

// Notes
export const notesApi = {
  list: (skip = 0, limit = 100) =>
    api.get<Note[]>('/notes/', { params: { skip, limit } }),
  get: (id: number) =>
    api.get<Note>(`/notes/${id}`),
  create: (data: NoteCreate) =>
    api.post<Note>('/notes/', data),
  update: (id: number, data: NoteUpdate) =>
    api.put<Note>(`/notes/${id}`, data),
  delete: (id: number) =>
    api.delete(`/notes/${id}`),
};

// Search
export const searchApi = {
  search: (query: string, topK = 5) =>
    api.get<NoteSearchResult[]>('/search/', { params: { query, top_k: topK } }),
};

// RAG
export const ragApi = {
  ask: (query: string) =>
    api.post<RAGResponse>('/rag/ask', null, { params: { query } }),
};

export default api;
