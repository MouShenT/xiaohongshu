import http from '@/utils/http'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  password: string
  nickname?: string
  email?: string
}

export const authApi = {
  login(data: LoginData) {
    return http.post('/auth/login', data)
  },
  register(data: RegisterData) {
    return http.post('/auth/register', data)
  },
  logout() {
    return http.post('/auth/logout')
  },
  getMe() {
    return http.get('/user/me')
  },
}
