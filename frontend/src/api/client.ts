import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10_000,
})

// Chỗ này sau sẽ gắn JWT: config.headers.Authorization = `Bearer ${token}`
api.interceptors.response.use(
  (res) => res,
  (err) => {
    // Chỗ xử lý 401 -> logout, hiển thị lỗi chung...
    return Promise.reject(err)
  },
)