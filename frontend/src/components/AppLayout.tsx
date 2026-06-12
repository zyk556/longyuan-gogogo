import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Button, theme } from 'antd'
import {
  DashboardOutlined,
  CalendarOutlined,
  FileImageOutlined,
  AccountBookOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons'

const { Header, Sider, Content } = Layout

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '首页' },
  { key: '/matches', icon: <CalendarOutlined />, label: '赛程' },
  {
    key: 'analysis',
    icon: <FileImageOutlined />,
    label: '彩票分析',
    children: [
      { key: '/analysis', label: '上传识别' },
      { key: '/analysis/history', label: '我的彩票' },
    ],
  },
  { key: '/profit-loss', icon: <AccountBookOutlined />, label: '记账' },
]

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { token } = theme.useToken()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        style={{ background: token.colorBgContainer }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            fontSize: collapsed ? 16 : 20,
            color: token.colorPrimary,
          }}
        >
          {collapsed ? '⚽' : '⚽ 龙苑集团'}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={['analysis']}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            padding: '0 24px',
            background: token.colorBgContainer,
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
        </Header>
        <Content style={{ margin: 24, padding: 24, background: token.colorBgContainer, borderRadius: 8 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
