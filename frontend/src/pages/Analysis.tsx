import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Upload,
  Table,
  Button,
  InputNumber,
  Input,
  Select,
  Image,
  Space,
  message,
  Spin,
  Empty,
  Popconfirm,
} from 'antd'
import { InboxOutlined, SaveOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd/es/upload/interface'
import type { ColumnsType } from 'antd/es/table'
import { uploadImage, getAnalysis, updateAnalysisItems, Analysis as AnalysisT, BetItem } from '../api/client'

const { Dragger } = Upload

const statusOptions = [
  { label: '待开奖', value: 'pending' },
  { label: '已中奖', value: 'won' },
  { label: '未中奖', value: 'lost' },
  { label: '取消', value: 'void' },
]

export default function Analysis() {
  const { id: routeId } = useParams()
  const navigate = useNavigate()
  const [imageUrl, setImageUrl] = useState<string>('')
  const [analysis, setAnalysis] = useState<AnalysisT | null>(null)
  const [items, setItems] = useState<Partial<BetItem>[]>([])
  const [uploading, setUploading] = useState(false)
  const [saving, setSaving] = useState(false)

  // 加载已有分析
  useEffect(() => {
    if (routeId) {
      getAnalysis(routeId).then((r) => {
        setAnalysis(r.data)
        setItems(r.data.items)
        setImageUrl('')
      })
    }
  }, [routeId])

  const handleUpload = async (file: File) => {
    setUploading(true)
    try {
      const res = await uploadImage(file)
      const { analysis_id, url } = res.data
      setImageUrl(url)
      if (analysis_id) {
        const aRes = await getAnalysis(analysis_id)
        setAnalysis(aRes.data)
        setItems(aRes.data.items)
        navigate(`/analysis/${analysis_id}`, { replace: true })
        message.success('识别完成')
      } else {
        message.warning('图片已上传，但 AI 识别未返回结果')
      }
    } catch {
      message.error('上传失败')
    } finally {
      setUploading(false)
    }
    return false // 阻止 antd 自动上传
  }

  const handleSave = async () => {
    if (!analysis) return
    setSaving(true)
    try {
      const res = await updateAnalysisItems(
        analysis.id,
        items.map((i) => ({
          match_desc: i.match_desc || '',
          bet_type: i.bet_type || '',
          pick: i.pick || '',
          odds: i.odds || 0,
          status: i.status || 'pending',
        })),
      )
      setAnalysis(res.data)
      setItems(res.data.items)
      message.success('保存成功')
    } catch {
      message.error('保存失败')
    } finally {
      setSaving(false)
    }
  }

  const updateItem = (index: number, field: string, value: any) => {
    const next = [...items]
    next[index] = { ...next[index], [field]: value }
    setItems(next)
  }

  const addItem = () => {
    setItems([...items, { match_desc: '', bet_type: '', pick: '', odds: 0, status: 'pending' }])
  }

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const columns: ColumnsType<Partial<BetItem>> = [
    {
      title: '比赛',
      dataIndex: 'match_desc',
      render: (v, _, idx) => (
        <Input value={v} onChange={(e) => updateItem(idx, 'match_desc', e.target.value)} />
      ),
    },
    {
      title: '玩法',
      dataIndex: 'bet_type',
      width: 120,
      render: (v, _, idx) => (
        <Input value={v} onChange={(e) => updateItem(idx, 'bet_type', e.target.value)} />
      ),
    },
    {
      title: '选择',
      dataIndex: 'pick',
      width: 120,
      render: (v, _, idx) => (
        <Input value={v} onChange={(e) => updateItem(idx, 'pick', e.target.value)} />
      ),
    },
    {
      title: '赔率',
      dataIndex: 'odds',
      width: 100,
      render: (v, _, idx) => (
        <InputNumber
          value={v}
          step={0.01}
          min={0}
          style={{ width: '100%' }}
          onChange={(val) => updateItem(idx, 'odds', val)}
        />
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 110,
      render: (v, _, idx) => (
        <Select
          value={v || 'pending'}
          options={statusOptions}
          style={{ width: '100%' }}
          onChange={(val) => updateItem(idx, 'status', val)}
        />
      ),
    },
    {
      title: '',
      width: 50,
      render: (_, __, idx) => (
        <Popconfirm title="确认删除？" onConfirm={() => removeItem(idx)}>
          <Button type="text" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ]

  return (
    <div>
      <Card title="上传彩票图片" style={{ marginBottom: 16 }}>
        <Dragger
          accept="image/*"
          showUploadList={false}
          beforeUpload={handleUpload}
          disabled={uploading}
          style={{ padding: '20px 0' }}
        >
          {uploading ? (
            <Spin><div style={{ padding: 40 }} /></Spin>
          ) : (
            <>
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽图片到此处上传</p>
              <p className="ant-upload-hint">支持 JPG、PNG 格式的体育彩票照片</p>
            </>
          )}
        </Dragger>
        {imageUrl && (
          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <Image src={imageUrl} width={300} style={{ borderRadius: 8 }} />
          </div>
        )}
      </Card>

      {analysis ? (
        <Card
          title="识别结果（可编辑）"
          extra={
            <Space>
              {analysis.total_stake != null && (
                <span>投注 ¥{analysis.total_stake.toFixed(2)}</span>
              )}
              {analysis.potential_return != null && (
                <span>潜在回报 ¥{analysis.potential_return.toFixed(2)}</span>
              )}
              <Button icon={<PlusOutlined />} onClick={addItem}>
                添加条目
              </Button>
              <Button type="primary" icon={<SaveOutlined />} loading={saving} onClick={handleSave}>
                保存修改
              </Button>
            </Space>
          }
        >
          <Table
            rowKey={(record) => (record as any).id || Math.random().toString()}
            columns={columns}
            dataSource={items}
            pagination={false}
            size="small"
          />
        </Card>
      ) : (
        <Card>
          <Empty description="上传图片后将显示识别结果" />
        </Card>
      )}
    </div>
  )
}
