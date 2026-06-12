# ⚽ 世界杯小工具

世界杯主题内部工具，支持赛程展示、体育彩票图片 AI 识别、识别结果编辑和盈亏记账。

## 技术栈

| 层       | 技术                                    |
| -------- | --------------------------------------- |
| 前端     | React 18 + TypeScript + Vite + Ant Design 5 |
| 后端     | Python FastAPI (异步)                   |
| 数据库   | SQLite + SQLAlchemy (async)         |
| AI 识别  | 小米 MiMo 多模态视觉模型 (OpenAI 兼容) |
| 图表     | Recharts                                |

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py         # 环境变量配置
│   │   ├── database.py       # 数据库引擎
│   │   ├── models.py         # ORM 模型（5 张表）
│   │   ├── schemas.py        # Pydantic 请求/响应模型
│   │   ├── auth.py           # 共享密钥鉴权
│   │   ├── routers/          # API 路由
│   │   └── services/mimo.py  # MiMo 识别服务
│   ├── seed.py               # 2026 世界杯模拟数据
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.tsx           # 路由布局
    │   ├── api/client.ts     # Axios 客户端 + API 调用
    │   ├── pages/            # 4 个页面
    │   └── components/       # 公共组件
    ├── package.json
    └── vite.config.ts
```

## 快速开始

### 1. 后端启动

```bash
cd backend

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

# 初始化赛程数据
python seed.py

# 启动后端（默认 8000 端口）
uvicorn app.main:app --reload --port 8000
```

### 2. 前端启动

```bash
cd frontend
npm install
npm run dev
# 浏览器访问 http://localhost:5173
```

### 4. Vite 代理配置（已内置）

前端开发模式已配置 `/api` → `http://localhost:8000` 的代理，以及 `/uploads` → 后端的静态文件代理。

## 功能说明

| 页面     | 路径              | 功能                                         |
| -------- | ----------------- | -------------------------------------------- |
| 首页     | `/`               | 今日赛程卡片、近7日盈亏、待开奖彩票、快速上传 |
| 赛程     | `/matches`        | 按日期切换查看比赛列表                       |
| 彩票分析 | `/analysis`       | 拖拽上传图片 → AI 识别 → 可编辑表格 → 保存   |
| 记账     | `/profit-loss`    | 盈亏增删改查、日期筛选、近一周折线图         |

## API 接口

| 方法   | 路径                      | 说明               |
| ------ | ------------------------- | ------------------ |
| GET    | `/api/matches?date=`      | 获取赛程           |
| POST   | `/api/upload`             | 上传彩票图片       |
| GET    | `/api/analysis/{id}`      | 获取分析结果       |
| PUT    | `/api/analysis/{id}/items`| 更新条目明细       |
| POST   | `/api/profit-loss`        | 添加盈亏           |
| GET    | `/api/profit-loss`        | 查询盈亏           |
| PUT    | `/api/profit-loss/{id}`   | 修改盈亏           |
| DELETE | `/api/profit-loss/{id}`   | 删除盈亏           |
| GET    | `/api/dashboard`          | 首页聚合数据       |

## 环境变量

| 变量          | 说明                   | 默认值                                |
| ------------- | ---------------------- | ------------------------------------- |
| DATABASE_URL  | 数据库连接串           | sqlite+aiosqlite:///./worldcup.db |
| MIMO_API_URL  | MiMo API 地址          | https://api.mimo.com/v1/chat/completions |
| MIMO_MODEL    | 模型名                 | MiMo-VL-7B                            |
| MIMO_API_KEY  | API 密钥               |                                       |
| UPLOAD_DIR    | 上传文件目录           | ./uploads                             |
| SHARED_SECRET | 共享密钥（空=不鉴权）  |                                       |

## 图片去重

上传时计算文件 SHA256 哈希，相同哈希的图片不会重复存储和分析，直接返回已有结果。

## License

内部使用
