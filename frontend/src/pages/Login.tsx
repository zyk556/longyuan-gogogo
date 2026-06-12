import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Input, Button, Typography, message } from 'antd'
import { LockOutlined } from '@ant-design/icons'

export default function Login() {
  const [key, setKey] = useState('')
  const navigate = useNavigate()

  const handleLogin = () => {
    if (!key.trim()) {
      message.warning('请输入共享密钥')
      return
    }
    localStorage.setItem('api_key', key.trim())
    message.success('登录成功')
    navigate('/')
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1677ff 0%, #0958d9 100%)',
      }}
    >
      <Card style={{ width: 380, borderRadius: 12 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 48 }}>⚽</div>
          <Typography.Title level={3} style={{ marginBottom: 0 }}>
            世界杯小工具
          </Typography.Title>
          <Typography.Text type="secondary">请输入共享密钥</Typography.Text>
        </div>
        <Input.Password
          size="large"
          prefix={<LockOutlined />}
          placeholder="共享密钥"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          onPressEnter={handleLogin}
        />
        <Button
          type="primary"
          size="large"
          block
          style={{ marginTop: 16 }}
          onClick={handleLogin}
        >
          进入
        </Button>
        <Button
          type="link"
          block
          style={{ marginTop: 8 }}
          onClick={() => {
            localStorage.setItem('api_key', '')
            navigate('/')
          }}
        >
          跳过（无需密钥）
        </Button>
      </Card>
    </div>
  )
}
