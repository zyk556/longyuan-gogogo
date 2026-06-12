import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Popconfirm,
  message,
  Empty,
  Modal,
  Descriptions,
} from 'antd'
import { EyeOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import { getAllAnalyses, deleteAnalysis, getProfitLoss, Analysis, BetItem } from '../api/client'

const statusColor: Record<string, string> = {
  pending: 'processing',
  won: 'success',
  lost: 'error',
  void: 'default',
}
const statusLabel: Record<string, string> = {
  pending: '待开奖',
  won: '已中奖',
  lost: '未中奖',
  void: '取消',
}

export default function AnalysisHistory() {
  const [data, setData] = useState<Analysis[]>([])
  const [referencedIds, setReferencedIds] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(false)
  const [detailOpen, setDetailOpen] = useState(false)
  const [current, setCurrent] = useState<Analysis | null>(null)
  const navigate = useNavigate()

  const load = () => {
    setLoading(true)
    getAllAnalyses(1)
      .then((r) => setData(r.data))
      .finally(() => setLoading(false))
    // 加载记账数据，找出已关联的分析 ID
    getProfitLoss().then((r) => {
      const ids = new Set<string>()
      r.data.forEach((pl) => {
        if (pl.related_analysis_id) ids.add(pl.related_analysis_id)
      })
      setReferencedIds(ids)
    })
  }

  useEffect(() => {
    load()
  }, [])

  const handleDelete = async (id: string) => {
    try {
      await deleteAnalysis(id)
      message.success('已删除')
      load()
    } catch {
      message.error('删除失败')
    }
  }

  const showDetail = (record: Analysis) => {
    setCurrent(record)
    setDetailOpen(true)
  }

  const columns: ColumnsType<Analysis> = [
    {
      title: '识别时间',
      dataIndex: 'created_at',
      width: 180,
      render: (v: string) => dayjs(v).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '投注日期',
      dataIndex: 'bet_date',
      width: 120,
      render: (v: string | null) => v || '-',
    },
    {
      title: '投注金额',
      dataIndex: 'total_stake',
      width: 100,
      render: (v: number | null) => (v != null ? `¥${v.toFixed(2)}` : '-'),
    },
    {
      title: '潜在回报',
      dataIndex: 'potential_return',
      width: 100,
      render: (v: number | null) => (v != null ? `¥${v.toFixed(2)}` : '-'),
    },
    {
      title: '条目数',
      width: 80,
      render: (_, r) => r.items.length,
    },
    {
      title: '状态',
      width: 100,
      render: (_, r) => {
        const statuses = r.items.map((i) => i.status)
        if (statuses.length > 0 && statuses.every((s) => s === 'won'))
          return <Tag color="success">已中奖</Tag>
        if (statuses.some((s) => s === 'pending'))
          return <Tag color="processing">待开奖</Tag>
        return <Tag color="error">未中奖</Tag>
      },
    },
    {
      title: '结算',
      width: 80,
      render: (_, r) =>
        referencedIds.has(r.id) ? (
          <Tag color="success">已结算</Tag>
        ) : (
          <Tag color="warning">未结算</Tag>
        ),
    },
    {
      title: '操作',
      width: 160,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => showDetail(record)}
          >
            详情
          </Button>
          <Button
            type="link"
            onClick={() => navigate(`/analysis/${record.id}`)}
          >
            编辑
          </Button>
          <Popconfirm title="确认删除？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const itemColumns: ColumnsType<BetItem> = [
    { title: '比赛', dataIndex: 'match_desc', ellipsis: true },
    { title: '玩法', dataIndex: 'bet_type', width: 100 },
    { title: '选择', dataIndex: 'pick', width: 100 },
    {
      title: '赔率',
      dataIndex: 'odds',
      width: 80,
      render: (v: number) => v.toFixed(2),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (s: string) => (
        <Tag color={statusColor[s]}>{statusLabel[s] || s}</Tag>
      ),
    },
  ]

  return (
    <>
      <Card title="我的彩票">
        <Table
          rowKey="id"
          columns={columns}
          dataSource={data}
          loading={loading}
          pagination={{ pageSize: 20 }}
          size="middle"
          locale={{ emptyText: <Empty description="暂无记录，去上传彩票吧" /> }}
        />
      </Card>

      <Modal
        title="分析详情"
        open={detailOpen}
        onCancel={() => setDetailOpen(false)}
        footer={null}
        width={700}
      >
        {current && (
          <>
            <Descriptions column={2} size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="识别时间">
                {dayjs(current.created_at).format('YYYY-MM-DD HH:mm')}
              </Descriptions.Item>
              <Descriptions.Item label="投注日期">
                {current.bet_date || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="投注金额">
                {current.total_stake != null
                  ? `¥${current.total_stake.toFixed(2)}`
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="潜在回报">
                {current.potential_return != null
                  ? `¥${current.potential_return.toFixed(2)}`
                  : '-'}
              </Descriptions.Item>
            </Descriptions>
            <Table
              rowKey="id"
              columns={itemColumns}
              dataSource={current.items}
              pagination={false}
              size="small"
            />
          </>
        )}
      </Modal>
    </>
  )
}
