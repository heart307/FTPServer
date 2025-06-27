import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout, message } from 'antd'
import { useEffect } from 'react'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import SitesPage from './pages/SitesPage'
import TasksPage from './pages/TasksPage'
import PriorityManagementPage from './pages/PriorityManagementPage'
import LogsPage from './pages/LogsPage'
import SettingsPage from './pages/SettingsPage'
import MainLayout from './components/Layout/MainLayout'
import ProtectedRoute from './components/Auth/ProtectedRoute'
import { useAppDispatch } from './store/hooks'
import { checkAuthStatus } from './store/slices/authSlice'

const { Content } = Layout

function App() {
  const dispatch = useAppDispatch()

  useEffect(() => {
    // 检查用户登录状态
    dispatch(checkAuthStatus())
    
    // 配置全局消息
    message.config({
      top: 100,
      duration: 3,
      maxCount: 3,
    })
  }, [dispatch])

  return (
    <div className="App">
      <Routes>
        {/* 登录页面 */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* 受保护的路由 */}
        <Route path="/" element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }>
          <Route index element={<DashboardPage />} />
          <Route path="sites" element={<SitesPage />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="priority" element={<PriorityManagementPage />} />
          <Route path="logs" element={<LogsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </div>
  )
}

export default App
