# ⚽ 龙苑集团 - 世界杯工具

世界杯主题内部工具，支持赛程展示、体育彩票图片 AI 识别、识别结果编辑和盈亏记账。

## 技术栈

| 层       | 技术                                    |
| -------- | --------------------------------------- |
| 前端     | React 18 + TypeScript + Vite + Ant Design 5 |
| 后端     | Python FastAPI (异步)                   |
| 数据库   | SQLite（本地）/ PostgreSQL（部署）      |
| AI 识别  | 小米 MiMo 多模态视觉模型               |
| 赛程数据 | football-data.org API                   |

## 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --port 8000

# 前端（另一个终端，开发热更新）
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

## 部署到 Railway

### 1. 准备

- 注册 [Railway](https://railway.app) 账号
- 安装 [Railway CLI](https://docs.railway.app/guides/cli)：`npm i -g @railway/cli`

### 2. 创建项目

```bash
railway login
railway init
```

### 3. 添加 PostgreSQL

在 Railway 控制台 → New → Database → PostgreSQL，会自动注入 `DATABASE_URL` 环境变量。

### 4. 设置环境变量

在 Railway 控制台 → Variables 中添加：

| 变量             | 说明                   |
| ---------------- | ---------------------- |
| MIMO_API_KEY     | 小米 MiMo API Key      |
| MIMO_API_URL     | https://api.xiaomimimo.com/v1/chat/completions |
| MIMO_MODEL       | mimo-v2.5              |
| FOOTBALL_API_KEY | football-data.org Key  |

### 5. 部署

```bash
railway up
```

或者连接 GitHub 仓库，每次 push 自动部署。

### 6. 上传文件持久化

在 Railway 控制台 → New → Volume，挂载到 `/data/uploads`。

## 功能

| 页面     | 路径              | 功能                                         |
| -------- | ----------------- | -------------------------------------------- |
| 首页     | `/`               | 今日赛程、总盈亏、待开奖彩票、快速上传       |
| 赛程     | `/matches`        | 按日期查看比赛，同步最新比分                 |
| 彩票分析 | `/analysis`       | 上传图片 → AI 识别 → 可编辑表格 → 保存       |
| 我的彩票 | `/analysis/history` | 已保存的彩票记录，状态/结算筛选            |
| 记账     | `/profit-loss`    | 投注/回报录入，关联彩票，盈亏走势图          |

## API 接口

| 方法   | 路径                      | 说明               |
| ------ | ------------------------- | ------------------ |
| GET    | `/api/matches?date=`      | 获取赛程           |
| POST   | `/api/upload`             | 上传彩票图片       |
| GET    | `/api/analysis?saved=1`   | 获取分析记录       |
| PUT    | `/api/analysis/{id}/items`| 保存条目明细       |
| POST   | `/api/profit-loss`        | 添加盈亏           |
| GET    | `/api/profit-loss`        | 查询盈亏           |
| PUT    | `/api/profit-loss/{id}`   | 修改盈亏           |
| DELETE | `/api/profit-loss/{id}`   | 删除盈亏           |
| GET    | `/api/dashboard`          | 首页聚合数据       |
| POST   | `/api/sync`               | 同步赛程比分       |
