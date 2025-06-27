import { createSlice } from '@reduxjs/toolkit'

interface SystemState {
  config: any
  loading: boolean
  error: string | null
}

const initialState: SystemState = {
  config: {},
  loading: false,
  error: null,
}

const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {
    // TODO: 实现系统配置相关的reducers
  },
})

export default systemSlice.reducer
