import { useEffect, useState } from 'react'
import { useNavigate, useOutletContext } from 'react-router-dom'
import { Row, Col, Card, Statistic, Tag, Empty, Spin, List, Button } from 'antd'
import {
  CalendarOutlined,
  AccountBookOutlined,
  FileImageOutlined,
  UploadOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { getDashboard, Dashboard as DashT } from '../api/client'
import ProfitChart from '../components/ProfitChart'

const statusColor: Record<string, string> = {
  scheduled: 'default',
  live: 'red',
  finished: 'green',
}
const statusLabel: Record<string, string> = {
  scheduled: '未开始',
  live: '进行中',
  finished: '已结束',
}

export default function Dashboard() {
  const [data, setData] = useState<DashT | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { internal } = useOutletContext<{ internal: boolean }>()

  useEffect(() => {
    getDashboard()
      .then((r) => setData(r.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '120px auto' }} />
  if (!data) return <Empty description="加载失败" />

  const totalPL = data.recent_pl.reduce((s, p) => s + p.amount, 0)

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Card hoverable onClick={() => navigate('/matches')}>
            <Statistic
              title="今日比赛"
              value={data.today_matches.length}
              prefix={<CalendarOutlined />}
              suffix="场"
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card hoverable onClick={() => navigate('/profit-loss')}>
            <Statistic
              title="总盈亏"
              value={totalPL}
              precision={2}
              prefix={<AccountBookOutlined />}
              valueStyle={{ color: totalPL >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card hoverable onClick={() => navigate('/analysis/history')}>
            <Statistic
              title="彩票总数"
              value={data.pending_analyses.length}
              prefix={<FileImageOutlined />}
              suffix="张"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={14}>
          <Card title="今日赛程" extra={internal ? <Button icon={<UploadOutlined />} onClick={() => navigate('/analysis')}>上传彩票</Button> : null}>
            {data.today_matches.length === 0 ? (
              <Empty description="今日无比赛" />
            ) : (
              <List
                dataSource={data.today_matches}
                renderItem={(m) => (
                  <List.Item>
                    <List.Item.Meta
                      title={
                        <span>
                          {m.home_team} vs {m.away_team}
                          <Tag color={statusColor[m.status]} style={{ marginLeft: 8 }}>
                            {statusLabel[m.status] || m.status}
                          </Tag>
                        </span>
                      }
                      description={
                        <>
                          <span>{m.group_name}组 · {m.stadium}</span>
                          <span style={{ marginLeft: 12 }}>
                            {m.kickoff_time?.slice(0, 5)}
                          </span>
                          {m.home_score !== null && (
                            <span style={{ marginLeft: 12, fontWeight: 600 }}>
                              {m.home_score} - {m.away_score}
                            </span>
                          )}
                        </>
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="盈亏走势">
            {data.recent_pl.length === 0 ? (
              <Empty description="暂无记录" />
            ) : (
              <ProfitChart data={data.recent_pl} />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}
