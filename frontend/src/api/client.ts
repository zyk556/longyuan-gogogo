import axios from 'axios'
import { message } from 'antd'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

// 请求拦截：注入鉴权密钥
api.interceptors.request.use((config) => {
  const key = localStorage.getItem('api_key')
  if (key) {
    config.headers['X-API-Key'] = key
  }
  return config
})

// 响应拦截：统一错误提示
api.interceptors.response.use(
  (resp) => resp,
  (err) => {
    const msg = err.response?.data?.detail || err.message || '请求失败'
    if (err.response?.status === 401) {
      message.error('密钥无效，请重新登录')
      localStorage.removeItem('api_key')
      window.location.hash = '#/login'
    } else {
      message.error(msg)
    }
    return Promise.reject(err)
  },
)

export default api

// ── 类型定义 ────────────────────────────────────────────
export interface Match {
  id: string
  match_date: string
  home_team: string
  away_team: string
  group_name: string
  stadium: string
  kickoff_time: string
  home_score: number | null
  away_score: number | null
  status: string
}

export interface BetItem {
  id: string
  match_desc: string
  bet_type: string
  pick: string
  odds: number
  status: string
}

export interface Analysis {
  id: string
  image_id: string
  bet_date: string | null
  total_stake: number | null
  potential_return: number | null
  raw_json: any
  created_at: string
  items: BetItem[]
}

export interface ProfitLoss {
  id: string
  date: string
  amount: number
  note: string | null
  related_analysis_id: string | null
  created_at: string
}

export interface Dashboard {
  today_matches: Match[]
  recent_pl: ProfitLoss[]
  pending_analyses: Analysis[]
}

// ── API 调用 ────────────────────────────────────────────
export const getMatches = (date?: string) =>
  api.get<Match[]>('/matches', { params: date ? { date } : {} })

export const uploadImage = (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post<{ image_id: string; url: string; analysis_id: string | null }>(
    '/upload',
    fd,
  )
}

export const getAnalysis = (id: string) => api.get<Analysis>(`/analysis/${id}`)

export const updateAnalysisItems = (id: string, items: Partial<BetItem>[]) =>
  api.put<Analysis>(`/analysis/${id}/items`, { items })

export const createProfitLoss = (data: {
  date: string
  amount: number
  note?: string
  related_analysis_id?: string
}) => api.post<ProfitLoss>('/profit-loss', data)

export const getProfitLoss = (start?: string, end?: string) =>
  api.get<ProfitLoss[]>('/profit-loss', { params: { start, end } })

export const updateProfitLoss = (
  id: string,
  data: Partial<{ date: string; amount: number; note: string }>,
) => api.put<ProfitLoss>(`/profit-loss/${id}`, data)

export const deleteProfitLoss = (id: string) =>
  api.delete(`/profit-loss/${id}`)

export const getDashboard = () => api.get<Dashboard>('/dashboard')

export const syncMatches = () =>
  api.post<{ synced: number; message: string }>('/sync')
