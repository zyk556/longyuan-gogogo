import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Legend } from 'recharts'
import { ProfitLoss } from '../api/client'

interface Props {
  data: ProfitLoss[]
}

export default function ProfitChart({ data }: Props) {
  // 按日期汇总
  const map = new Map<string, { stake: number; return_amount: number }>()
  data.forEach((d) => {
    const key = d.date
    const prev = map.get(key) || { stake: 0, return_amount: 0 }
    map.set(key, {
      stake: prev.stake + d.stake,
      return_amount: prev.return_amount + d.return_amount,
    })
  })

  // 按日期排序，计算累计净盈亏
  const sorted = Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b))
  let cumulative = 0
  const chartData = sorted.map(([date, { stake, return_amount }]) => {
    cumulative += return_amount - stake
    return {
      date: date.slice(5),
      投入: Math.round(stake * 100) / 100,
      回报: Math.round(return_amount * 100) / 100,
      净盈亏: Math.round(cumulative * 100) / 100,
    }
  })

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip formatter={(v: number, name: string) => [`¥${v.toFixed(2)}`, name]} />
        <Legend />
        <ReferenceLine y={0} stroke="#999" />
        <Line type="monotone" dataKey="投入" stroke="#fa8c16" strokeWidth={1.5} strokeDasharray="6 3" dot={{ r: 2 }} />
        <Line type="monotone" dataKey="回报" stroke="#52c41a" strokeWidth={1.5} strokeDasharray="3 3" dot={{ r: 2 }} />
        <Line type="monotone" dataKey="净盈亏" stroke="#1677ff" strokeWidth={3} dot={{ r: 4, fill: '#1677ff' }} activeDot={{ r: 7 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}
