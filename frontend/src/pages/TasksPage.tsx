import React from 'react'
import { Typography, Card, Empty } from 'antd'

const { Title } = Typography

const TasksPage: React.FC = () => {
  return (
    <div className="fade-in">
      <Title level={2}>传输任务</Title>
      
      <Card>
        <Empty description="暂无传输任务" />
      </Card>
    </div>
  )
}

export default TasksPage
