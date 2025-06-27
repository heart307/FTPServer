import { createSlice } from '@reduxjs/toolkit'

interface SitesState {
  sites: any[]
  loading: boolean
  error: string | null
}

const initialState: SitesState = {
  sites: [],
  loading: false,
  error: null,
}

const sitesSlice = createSlice({
  name: 'sites',
  initialState,
  reducers: {
    // TODO: 实现站点管理相关的reducers
  },
})

export default sitesSlice.reducer
