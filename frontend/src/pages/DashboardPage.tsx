import React from 'react'
import { Row, Col, Card, Statistic, Typography, Alert } from 'antd'
import {
  CloudServerOutlined,
  FileTextOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'

const { Title } = Typography

const DashboardPage: React.FC = () => {
  return (
    <div className="fade-in">
      <Title level={2}>仪表板</Title>
      
      <Alert
        message="欢迎使用FTP文件传输管理系统"
        description="这是一个功能强大的FTP文件传输管理系统，支持多站点管理、任务优先级调度、文件夹监控等高级功能。"
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="FTP站点"
              value={0}
              prefix={<CloudServerOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="传输任务"
              value={0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="运行中任务"
              value={0}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已完成任务"
              value={0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="最近任务" size="small">
            <div className="empty-container">
              <p>暂无任务数据</p>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card title="系统状态" size="small">
            <div className="empty-container">
              <p>系统运行正常</p>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default DashboardPage
