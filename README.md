# 🇸🇪 Stockholm AI Jobs Tracker

每日自动抓取斯德哥尔摩大公司（Amazon AWS、Google、Microsoft、Ericsson、Nokia、Spotify、Klarna、Sinch）的 AI × Telecom × Cloud 职位，按匹配度打分汇总展示。

**目标用户：** AI + 电信 + 云计算复合型技术专家

---

## 系统架构

```
GitHub Actions (每日 08:00 Stockholm)
    → scripts/fetch_jobs.py  ← 爬取各公司职位
    → data/YYYY-MM-DD.json   ← 保存数据
    → git push               ← 触发 Vercel 重新部署
```

---

## 本地运行

### 1. 安装 Python 依赖

```bash
pip install -r scripts/requirements.txt
```

### 2. 运行爬虫（生成今日数据）

```bash
python scripts/fetch_jobs.py
```

### 3. 启动 Next.js 开发服务器

```bash
npm install
npm run dev
```

访问 http://localhost:3000

---

## 部署到 GitHub + Vercel

### 第一步：创建 GitHub 仓库

```bash
cd /Users/simon/stockholm-jobs-tracker
git init
git add .
git commit -m "feat: initial Stockholm AI jobs tracker"
git remote add origin https://github.com/<你的用户名>/stockholm-jobs-tracker.git
git push -u origin main
```

### 第二步：连接 Vercel

1. 访问 [vercel.com](https://vercel.com) → 登录（推荐用 GitHub 账号）
2. 点击 **New Project** → Import 刚才创建的 GitHub 仓库
3. Framework Preset 选 **Next.js**（自动检测）
4. 点击 **Deploy** → 等待约 1 分钟
5. 获得域名如 `stockholm-jobs-tracker.vercel.app`

**可选：** 在 Vercel 项目设置中绑定自己的域名。

### 第三步：验证 GitHub Actions

推送后在 GitHub → Actions 标签页确认 workflow 可见。  
可手动点击 **Run workflow** 立即测试。

---

## 匹配分数说明

| 等级 | 分数 | 含义 |
|------|------|------|
| S    | ≥ 70 | 强烈推荐，高度匹配 |
| A    | 50–69 | 推荐关注 |
| B    | 30–49 | 可参考 |
| C    | < 30  | 弱匹配 |

### 关键词权重（部分）

| 关键词 | 分数 |
|--------|------|
| solutions architect | 30 |
| agentic AI | 20 |
| O-RAN | 25 |
| telecom | 20 |
| 5G | 18 |
| LLM / RAG | 18 |
| machine learning | 15 |
| cloud / AWS / Azure | 10 |

---

## 文件结构

```
stockholm-jobs-tracker/
├── .github/workflows/daily-fetch.yml  ← GitHub Actions 定时任务
├── data/                              ← 每日 JSON 数据（git 历史保存）
│   └── 2026-06-07.json
├── scripts/
│   ├── fetch_jobs.py                  ← 主爬虫脚本
│   └── requirements.txt
├── src/app/
│   ├── page.tsx                       ← 主页（今日职位）
│   ├── history/page.tsx               ← 历史列表
│   └── history/[date]/page.tsx        ← 某日详情
└── src/lib/
    ├── jobs.ts                        ← 数据读取工具
    └── types.ts                       ← TypeScript 类型
```
