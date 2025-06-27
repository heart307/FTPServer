import { configureStore } from '@reduxjs/toolkit'
import authSlice from './slices/authSlice'
import sitesSlice from './slices/sitesSlice'
import tasksSlice from './slices/tasksSlice'
import systemSlice from './slices/systemSlice'

export const store = configureStore({
  reducer: {
    auth: authSlice,
    sites: sitesSlice,
    tasks: tasksSlice,
    system: systemSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
