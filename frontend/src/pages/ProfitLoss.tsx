import { useEffect, useState } from 'react'
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  InputNumber,
  Input,
  DatePicker,
  Space,
  Popconfirm,
  message,
  Row,
  Col,
  Statistic,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs, { Dayjs } from 'dayjs'
import {
  getProfitLoss,
  createProfitLoss,
  updateProfitLoss,
  deleteProfitLoss,
  ProfitLoss as PLT,
} from '../api/client'
import ProfitChart from '../components/ProfitChart'

const { RangePicker } = DatePicker

export default function ProfitLoss() {
  const [data, setData] = useState<PLT[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<PLT | null>(null)
  const [range, setRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(7, 'day'),
    dayjs(),
  ])
  const [form] = Form.useForm()

  const load = () => {
    setLoading(true)
    getProfitLoss(range[0].format('YYYY-MM-DD'), range[1].format('YYYY-MM-DD'))
      .then((r) => setData(r.data))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ date: dayjs(), amount: 0 })
    setModalOpen(true)
  }

  const openEdit = (record: PLT) => {
    setEditing(record)
    form.setFieldsValue({
      date: dayjs(record.date),
      amount: record.amount,
      note: record.note,
    })
    setModalOpen(true)
  }

  const handleSubmit = async () => {
    const values = await form.validateFields()
    const payload = {
      date: values.date.format('YYYY-MM-DD'),
      amount: values.amount,
      note: values.note || undefined,
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

  const totalProfit = data.filter((d) => d.amount > 0).reduce((s, d) => s + d.amount, 0)
  const totalLoss = data.filter((d) => d.amount < 0).reduce((s, d) => s + d.amount, 0)
  const net = totalProfit + totalLoss

  const columns: ColumnsType<PLT> = [
    { title: '日期', dataIndex: 'date', width: 120 },
    {
      title: '金额',
      dataIndex: 'amount',
      width: 120,
      render: (v: number) => (
        <span style={{ color: v >= 0 ? '#3f8600' : '#cf1322', fontWeight: 600 }}>
          {v >= 0 ? '+' : ''}¥{v.toFixed(2)}
        </span>
      ),
    },
    { title: '备注', dataIndex: 'note', ellipsis: true },
    {
      title: '操作',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => openEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确认删除？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总收入"
              value={totalProfit}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总支出"
              value={Math.abs(totalLoss)}
              precision={2}
              prefix="-¥"
              valueStyle={{ color: '#cf1322' }}
            />
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
            <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
              新增
            </Button>
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
      >
        <Form form={form} layout="vertical">
          <Form.Item name="date" label="日期" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="amount"
            label="金额（正=盈，负=亏）"
            rules={[{ required: true }]}
          >
            <InputNumber style={{ width: '100%' }} step={10} />
          </Form.Item>
          <Form.Item name="note" label="备注">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
