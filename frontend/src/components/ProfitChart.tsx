import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { ProfitLoss } from '../api/client'

interface Props {
  data: ProfitLoss[]
}

export default function ProfitChart({ data }: Props) {
  // 按日期汇总
  const map = new Map<string, number>()
  data.forEach((d) => {
    map.set(d.date, (map.get(d.date) || 0) + d.amount)
  })
  const chartData = Array.from(map.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, amount]) => ({ date: date.slice(5), amount: Math.round(amount * 100) / 100 }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip formatter={(v: number) => [`¥${v.toFixed(2)}`, '盈亏']} />
        <ReferenceLine y={0} stroke="#999" />
        <Line
          type="monotone"
          dataKey="amount"
          stroke="#1677ff"
          strokeWidth={2}
          dot={{ r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
