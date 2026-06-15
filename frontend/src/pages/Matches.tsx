import { useEffect, useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { Card, DatePicker, Table, Tag, Empty, Button, message, Space } from 'antd'
import { SyncOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs, { Dayjs } from 'dayjs'
import { getMatches, syncMatches, Match } from '../api/client'

const statusColor: Record<string, string> = {
  scheduled: 'default',
  live: 'red',
  finished: 'green',
  postponed: 'orange',
  cancelled: 'default',
}
const statusLabel: Record<string, string> = {
  scheduled: '未开始',
  live: '进行中',
  finished: '已结束',
  postponed: '推迟',
  cancelled: '取消',
}

export default function Matches() {
  const [date, setDate] = useState<Dayjs>(dayjs())
  const [data, setData] = useState<Match[]>([])
  const [loading, setLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const { internal } = useOutletContext<{ internal: boolean }>()

  const load = (d: Dayjs) => {
    setLoading(true)
    getMatches(d.format('YYYY-MM-DD'))
      .then((r) => setData(r.data))
      .finally(() => setLoading(false))
  }

  const handleSync = async () => {
    setSyncing(true)
    try {
      const res = await syncMatches()
      message.success(res.data.message + `（${res.data.synced} 条）`)
      load(date)
    } catch {
      message.error('同步失败，请检查 API Key 是否配置')
    } finally {
      setSyncing(false)
    }
  }

  useEffect(() => {
    load(date)
  }, [])

  const columns: ColumnsType<Match> = [
    {
      title: '时间',
      dataIndex: 'kickoff_time',
      width: 80,
      render: (t: string) => t?.slice(0, 5),
    },
    {
      title: '小组',
      dataIndex: 'group_name',
      width: 60,
      render: (g: string) => <Tag>{g}</Tag>,
    },
    { title: '主队', dataIndex: 'home_team', width: 120 },
    {
      title: '比分',
      width: 80,
      render: (_, r) =>
        r.home_score !== null ? (
          <span style={{ fontWeight: 600 }}>
            {r.home_score} - {r.away_score}
          </span>
        ) : (
          <span style={{ color: '#999' }}>vs</span>
        ),
    },
    { title: '客队', dataIndex: 'away_team', width: 120 },
    { title: '场地', dataIndex: 'stadium', ellipsis: true },
    {
      title: '状态',
      dataIndex: 'status',
      width: 80,
      render: (s: string) => (
        <Tag color={statusColor[s]}>{statusLabel[s] || s}</Tag>
      ),
    },
  ]

  return (
    <Card
      title="世界杯赛程"
      extra={
        <Space>
          <DatePicker
            value={date}
            onChange={(d) => {
              if (d) {
                setDate(d)
                load(d)
              }
            }}
          />
          {internal && (
            <Button
              icon={<SyncOutlined spin={syncing} />}
              loading={syncing}
              onClick={handleSync}
            >
              同步比分
            </Button>
          )}
        </Space>
      }
    >
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={false}
        size="middle"
        locale={{ emptyText: <Empty description="该日无比赛" /> }}
      />
    </Card>
  )
}
