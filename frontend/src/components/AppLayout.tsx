import { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Button, Modal, Input, Tag, message, theme } from 'antd'
import {
  DashboardOutlined,
  CalendarOutlined,
  FileImageOutlined,
  AccountBookOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  LockOutlined,
  UnlockOutlined,
} from '@ant-design/icons'
import { login, isInternal } from '../api/client'

const { Header, Sider, Content } = Layout

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [internal, setInternal] = useState(false)
  const [loginOpen, setLoginOpen] = useState(false)
  const [password, setPassword] = useState('')
  const [logging, setLogging] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { token } = theme.useToken()

  useEffect(() => {
    setInternal(isInternal())
  }, [])

  // 分析子菜单在内部模式才显示上传
  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: '首页' },
    { key: '/matches', icon: <CalendarOutlined />, label: '赛程' },
    {
      key: 'analysis',
      icon: <FileImageOutlined />,
      label: '彩票',
      children: internal
        ? [
            { key: '/analysis', label: '上传识别' },
            { key: '/analysis/history', label: '我的彩票' },
          ]
        : [
            { key: '/analysis/history', label: '我的彩票' },
          ],
    },
    ...(internal ? [{ key: '/profit-loss', icon: <AccountBookOutlined />, label: '记账' }] : []),
  ]

  const handleLogin = async () => {
    setLogging(true)
    try {
      const res = await login(password)
      if (res.data.success) {
        localStorage.setItem('auth_token', res.data.token)
        setInternal(true)
        setLoginOpen(false)
        setPassword('')
        message.success('已切换到内部模式')
      }
    } catch {
      message.error('密码错误')
    } finally {
      setLogging(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    setInternal(false)
    message.info('已切换到访客模式')
    if (location.pathname === '/analysis' || location.pathname === '/profit-loss') {
      navigate('/analysis/history')
    }
  }

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
            justifyContent: 'space-between',
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
          {internal ? (
            <Tag
              color="success"
              style={{ cursor: 'pointer', fontSize: 14, padding: '4px 12px' }}
              icon={<UnlockOutlined />}
              onClick={handleLogout}
            >
              内部模式（点击退出）
            </Tag>
          ) : (
            <Tag
              color="default"
              style={{ cursor: 'pointer', fontSize: 14, padding: '4px 12px' }}
              icon={<LockOutlined />}
              onClick={() => setLoginOpen(true)}
            >
              访客模式（点击登录）
            </Tag>
          )}
        </Header>
        <Content style={{ margin: 24, padding: 24, background: token.colorBgContainer, borderRadius: 8 }}>
          <Outlet context={{ internal }} />
        </Content>
      </Layout>

      <Modal
        title="内部登录"
        open={loginOpen}
        onOk={handleLogin}
        onCancel={() => { setLoginOpen(false); setPassword('') }}
        confirmLoading={logging}
        okText="登录"
        cancelText="取消"
      >
        <Input.Password
          placeholder="请输入内部密码"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onPressEnter={handleLogin}
          prefix={<LockOutlined />}
        />
      </Modal>
    </Layout>
  )
}
