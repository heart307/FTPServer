import { createSlice } from '@reduxjs/toolkit'

interface TasksState {
  tasks: any[]
  loading: boolean
  error: string | null
}

const initialState: TasksState = {
  tasks: [],
  loading: false,
  error: null,
}

const tasksSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {
    // TODO: 实现任务管理相关的reducers
  },
})

export default tasksSlice.reducer
