import { useEffect, useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  InputNumber,
  DatePicker,
  Select,
  Space,
  Popconfirm,
  Tag,
  Descriptions,
  message,
  Row,
  Col,
  Statistic,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs, { Dayjs } from 'dayjs'
import {
  getProfitLoss,
  createProfitLoss,
  updateProfitLoss,
  deleteProfitLoss,
  getAllAnalyses,
  ProfitLoss,
  Analysis,
} from '../api/client'
import ProfitChart from '../components/ProfitChart'

const { RangePicker } = DatePicker

export default function ProfitLossPage() {
  const [data, setData] = useState<ProfitLoss[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<ProfitLoss | null>(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [currentPL, setCurrentPL] = useState<ProfitLoss | null>(null)
  const [savedAnalyses, setSavedAnalyses] = useState<Analysis[]>([])
  const [range, setRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(7, 'day'),
    dayjs(),
  ])
  const [form] = Form.useForm()
  const { internal } = useOutletContext<{ internal: boolean }>()

  const load = () => {
    setLoading(true)
    getProfitLoss(range[0].format('YYYY-MM-DD'), range[1].format('YYYY-MM-DD'))
      .then((r) => setData(r.data))
      .finally(() => setLoading(false))
  }

  const loadAnalyses = () => {
    getAllAnalyses(1).then((r) => setSavedAnalyses(r.data))
  }

  useEffect(() => {
    load()
    loadAnalyses()
  }, [])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ date: dayjs(), stake: 0, return_amount: 0 })
    setModalOpen(true)
  }

  const openEdit = (record: ProfitLoss) => {
    setEditing(record)
    form.setFieldsValue({
      date: dayjs(record.date),
      stake: record.stake,
      return_amount: record.return_amount,
      related_analysis_id: record.related_analysis_id || undefined,
    })
    setModalOpen(true)
  }

  const handleSubmit = async () => {
    const values = await form.validateFields()
    const payload = {
      date: values.date.format('YYYY-MM-DD'),
      stake: values.stake || 0,
      return_amount: values.return_amount || 0,
      related_analysis_id: values.related_analysis_id || undefined,
    }
    try {
      if (editing) {
        await updateProfitLoss(editing.id, payload)
        message.success('修改成功')
      } else {
        await createProfitLoss(payload)
        message.success('添加成功')
      }
      setModalOpen(false)
      load()
    } catch {
      message.error('操作失败')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteProfitLoss(id)
      message.success('已删除')
      load()
    } catch {
      message.error('删除失败')
    }
  }

  const showDetail = (record: ProfitLoss) => {
    setCurrentPL(record)
    setDetailOpen(true)
  }

  const totalStake = data.reduce((s, d) => s + d.stake, 0)
  const totalReturn = data.reduce((s, d) => s + d.return_amount, 0)
  const net = totalReturn - totalStake

  // 彩票 ID → 描述映射
  const analysisMap = new Map(savedAnalyses.map((a) => [a.id, a]))

  const columns: ColumnsType<ProfitLoss> = [
    { title: '日期', dataIndex: 'date', width: 110 },
    {
      title: '投注',
      dataIndex: 'stake',
      width: 100,
      render: (v: number) => <span>¥{v.toFixed(2)}</span>,
    },
    {
      title: '回报',
      dataIndex: 'return_amount',
      width: 100,
      render: (v: number) => <span>¥{v.toFixed(2)}</span>,
    },
    {
      title: '盈亏',
      dataIndex: 'amount',
      width: 100,
      render: (v: number) => (
        <span style={{ color: v >= 0 ? '#3f8600' : '#cf1322', fontWeight: 600 }}>
          {v >= 0 ? '+' : ''}¥{v.toFixed(2)}
        </span>
      ),
    },
    {
      title: '关联彩票',
      width: 180,
      ellipsis: true,
      render: (_, r) => {
        if (!r.related_analysis_id) return '-'
        const a = analysisMap.get(r.related_analysis_id)
        if (!a) return '-'
        const desc = a.items.map((i) => i.match_desc).join(', ')
        return desc || a.bet_date || '-'
      },
    },
    {
      title: '操作',
      width: 160,
      render: (_, record) => (
        <Space>
          <Button type="link" icon={<EyeOutlined />} onClick={() => showDetail(record)}>
            详情
          </Button>
          {internal && (
            <>
              <Button type="link" icon={<EditOutlined />} onClick={() => openEdit(record)}>
                编辑
              </Button>
              <Popconfirm title="确认删除？" onConfirm={() => handleDelete(record.id)}>
                <Button type="link" danger icon={<DeleteOutlined />} />
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ]

  // 分析选项
  const analysisOptions = savedAnalyses.map((a) => {
    const desc = a.items.map((i) => `${i.match_desc}(${i.pick})`).join(' + ')
    return {
      value: a.id,
      label: `${a.bet_date || ''} ${desc.slice(0, 30)}${desc.length > 30 ? '...' : ''} ¥${a.total_stake || 0}`,
    }
  })

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="总投注" value={totalStake} precision={2} prefix="¥" />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="总回报" value={totalReturn} precision={2} prefix="¥" />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="净盈亏"
              value={net}
              precision={2}
              prefix="¥"
              valueStyle={{ color: net >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="盈亏走势" style={{ marginBottom: 16 }}>
        <ProfitChart data={data} />
      </Card>

      <Card
        title="盈亏记录"
        extra={
          <Space>
            <RangePicker
              value={range}
              onChange={(v) => {
                if (v && v[0] && v[1]) {
                  setRange([v[0], v[1]])
                }
              }}
            />
            <Button onClick={load}>查询</Button>
            {internal && (
              <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
                新增
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
          pagination={{ pageSize: 20 }}
          size="middle"
        />
      </Card>

      <Modal
        title={editing ? '编辑盈亏' : '新增盈亏'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        destroyOnClose
        width={520}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="date" label="日期" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="stake" label="投注金额（¥）">
                <InputNumber style={{ width: '100%' }} min={0} step={10} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="return_amount" label="回报金额（¥）">
                <InputNumber style={{ width: '100%' }} min={0} step={10} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="related_analysis_id" label="关联彩票（可选）">
            <Select
              allowClear
              placeholder="选择对应的彩票"
              options={analysisOptions}
              showSearch
              optionFilterProp="label"
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="盈亏详情"
        open={detailOpen}
        onCancel={() => setDetailOpen(false)}
        footer={null}
        width={600}
      >
        {currentPL && (() => {
          const linked = currentPL.related_analysis_id
            ? analysisMap.get(currentPL.related_analysis_id)
            : null
          return (
            <>
              <Descriptions column={2} size="small" style={{ marginBottom: 16 }}>
                <Descriptions.Item label="日期">{currentPL.date}</Descriptions.Item>
                <Descriptions.Item label="盈亏">
                  <span style={{ color: currentPL.amount >= 0 ? '#3f8600' : '#cf1322', fontWeight: 600 }}>
                    {currentPL.amount >= 0 ? '+' : ''}¥{currentPL.amount.toFixed(2)}
                  </span>
                </Descriptions.Item>
                <Descriptions.Item label="投注">¥{currentPL.stake.toFixed(2)}</Descriptions.Item>
                <Descriptions.Item label="回报">¥{currentPL.return_amount.toFixed(2)}</Descriptions.Item>
              </Descriptions>
              {linked && (
                <>
                  <div style={{ fontWeight: 600, marginBottom: 8 }}>关联彩票</div>
                  <Descriptions column={2} size="small" style={{ marginBottom: 12 }}>
                    <Descriptions.Item label="投注日期">{linked.bet_date || '-'}</Descriptions.Item>
                    <Descriptions.Item label="投注金额">
                      ¥{linked.total_stake?.toFixed(2) || '-'}
                    </Descriptions.Item>
                    <Descriptions.Item label="潜在回报">
                      ¥{linked.potential_return?.toFixed(2) || '-'}
                    </Descriptions.Item>
                  </Descriptions>
                  <Table
                    rowKey="id"
                    dataSource={linked.items}
                    pagination={false}
                    size="small"
                    columns={[
                      { title: '比赛', dataIndex: 'match_desc', ellipsis: true },
                      { title: '玩法', dataIndex: 'bet_type', width: 80 },
                      { title: '选择', dataIndex: 'pick', width: 80 },
                      { title: '赔率', dataIndex: 'odds', width: 70, render: (v: number) => v.toFixed(2) },
                      {
                        title: '状态',
                        dataIndex: 'status',
                        width: 80,
                        render: (s: string) => {
                          const map: Record<string, { color: string; label: string }> = {
                            pending: { color: 'processing', label: '待开奖' },
                            won: { color: 'success', label: '已中奖' },
                            lost: { color: 'error', label: '未中奖' },
                            void: { color: 'default', label: '取消' },
                          }
                          const m = map[s] || { color: 'default', label: s }
                          return <Tag color={m.color}>{m.label}</Tag>
                        },
                      },
                    ]}
                  />
                </>
              )}
              {!linked && (
                <div style={{ color: '#999', textAlign: 'center', padding: 20 }}>
                  未关联彩票
                </div>
              )}
            </>
          )
        })()}
      </Modal>
    </div>
  )
}
