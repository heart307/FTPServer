import React from 'react'
import { Typography, Card, Button, Empty } from 'antd'
import { PlusOutlined } from '@ant-design/icons'

const { Title } = Typography

const SitesPage: React.FC = () => {
  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2}>站点管理</Title>
        <Button type="primary" icon={<PlusOutlined />}>
          添加站点
        </Button>
      </div>
      
      <Card>
        <Empty description="暂无FTP站点，请添加站点开始使用" />
      </Card>
    </div>
  )
}

export default SitesPage
