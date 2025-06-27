import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { message } from 'antd'
import api from '../../services/api'

export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  is_admin: boolean
  created_at: string
  last_login_at?: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false,
  loading: false,
  error: null,
}

// 异步操作
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { username: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/login', credentials)
      const { access_token, user } = response.data
      
      localStorage.setItem('token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      message.success('登录成功')
      return { token: access_token, user }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '登录失败'
      message.error(errorMessage)
      return rejectWithValue(errorMessage)
    }
  }
)

export const register = createAsyncThunk(
  'auth/register',
  async (userData: { username: string; email: string; password: string; confirm_password: string }, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/register', userData)
      message.success('注册成功，请登录')
      return response.data.user
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '注册失败'
      message.error(errorMessage)
      return rejectWithValue(errorMessage)
    }
  }
)

export const checkAuthStatus = createAsyncThunk(
  'auth/checkStatus',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        return rejectWithValue('No token found')
      }
      
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      const response = await api.get('/auth/profile')
      
      return { token, user: response.data.user }
    } catch (error: any) {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
      return rejectWithValue('Token invalid')
    }
  }
)

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { dispatch }) => {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      // 忽略登出错误
    } finally {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
      message.success('已退出登录')
    }
  }
)

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload
      state.isAuthenticated = true
      localStorage.setItem('token', action.payload)
      api.defaults.headers.common['Authorization'] = `Bearer ${action.payload}`
    },
  },
  extraReducers: (builder) => {
    builder
      // 登录
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false
        state.isAuthenticated = true
        state.token = action.payload.token
        state.user = action.payload.user
        state.error = null
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.isAuthenticated = false
        state.token = null
        state.user = null
        state.error = action.payload as string
      })
      
      // 注册
      .addCase(register.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false
        state.error = null
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      
      // 检查认证状态
      .addCase(checkAuthStatus.fulfilled, (state, action) => {
        state.isAuthenticated = true
        state.token = action.payload.token
        state.user = action.payload.user
        state.error = null
      })
      .addCase(checkAuthStatus.rejected, (state) => {
        state.isAuthenticated = false
        state.token = null
        state.user = null
      })
      
      // 登出
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false
        state.token = null
        state.user = null
        state.error = null
      })
  },
})

export const { clearError, setToken } = authSlice.actions
export default authSlice.reducer
