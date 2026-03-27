---
name: social-media-agent
description: 社媒运营全流程 Agent。从 Instagram 账号 URL 或用户名出发，自动完成竞品调研、内容日历生成、Brief + 文案撰写、合规审核、发布排期。适用场景：用户说"帮我做一个月的 Instagram 内容"、提供 Instagram 账号链接、希望自动生成社媒内容 pipeline。无 Instagram 账号时，要求用户上传图片或描述业务，再走相同流程。
---

# Social Media Agent — 社媒运营全流程

## 输入

- **有 Instagram 账号**：提供 URL（如 `https://www.instagram.com/bubbleula/`）或 handle（如 `@bubbleula`）
- **无 Instagram 账号**：用户提供业务介绍（文字描述或上传品牌资料），Skill 引导用户补充品牌信息

## 输出文件结构

```
workspace/social_media_output/
├── brand_kit.json          # 品牌资产（由用户信息生成或补充）
├── research_brief.md       # 账号健康度 + 竞品调研报告
├── competitive_landscape.md # 竞品矩阵 + 差距分析
├── content_pack/
│   ├── calendar.md         # 月度内容日历
│   └── posts/
│       └── YYYY-MM-DD_topic/
│           ├── brief.md    # 单帖 Brief
│           └── caption.md  # Caption × 3 变体
├── review_report.md        # 合规审核报告
└── calendar.json           # 发布排期（可直接导入 Meta Business Suite）
```

---

## 流程总览（4 个阶段）

```
输入账号 → ① 调研 → ② 内容生产 → ③ 合规审核 → ④ 输出排期
```

---

## 阶段 ①：调研（Scout）

### Step 1A：抓取本品数据

**使用 agent-browser（Playwright）：**

```bash
# 打开 Instagram 账号页面
agent-browser open https://www.instagram.com/{handle}/

# 等待页面加载
agent-browser wait --load networkidle

# 提取账号基本信息（JS eval）
agent-browser eval --stdin <<'EOF'
(function() {
  var body = document.body.innerText;
  var lines = body.split('\n');
  var r = { handle: '', followers: 0, posts: 0, following: 0, bio: '', latestPostUrls: [] };
  for (var i = 0; i < Math.min(lines.length, 30); i++) {
    var l = lines[i].trim();
    if (l.match(/@[\w.]+/)) r.handle = l;
    if (l.match(/[\d,]+\s*followers?$/)) r.followers = l;
    if (l.match(/[\d,]+\s*posts$/)) r.posts = l;
    if (l.match(/[\d,]+\s*following$/)) r.following = l;
  }
  // Bio: after posts/followers/following
  var pidx = body.indexOf('following'); if (pidx > 0) r.bio = body.substring(pidx, pidx + 400);
  // Latest post URLs
  var links = document.querySelectorAll('a[href]');
  var posts = [];
  links.forEach(function(l) {
    var h = l.href;
    if (h.match(/\/(p|reel)\/[a-zA-Z0-9_-]+/) && h.includes('{handle}')) posts.push(h);
  });
  r.latestPostUrls = [...new Set(posts)].slice(0, 9);
  return JSON.stringify(r, null, 2);
})()
EOF
```

> ⚠️ 如果页面跳转到登录页，说明账号有隐私设置，改用帖子 URL 抓取（见 Step 1B）

### Step 1B：抓取单条帖子数据（获取互动率）

对每条帖子 URL 单独访问：

```bash
agent-browser open {post_url}
agent-browser wait --load networkidle

agent-browser eval --stdin <<'EOF'
(function() {
  var og = document.querySelector('meta[property="og:description"]');
  var ts = document.querySelector('time');
  return JSON.stringify({
    ogDesc: og ? og.content : '',
    postedAt: ts ? ts.getAttribute('datetime') : '',
    url: window.location.href
  }, null, 2);
})()
EOF
```

`og:description` 格式：`"{N} likes, {N} comments - {handle} on {date}: {caption}"`

从 N 个帖子的 og:description 提取 likes 数，计算平均 ER：
```
Avg ER = (avg likes) / followers × 100%
```

### Step 1C：竞品发现

从本品的 Related Accounts 自动发现竞品：

```bash
agent-browser eval --stdin <<'EOF'
(function() {
  var links = document.querySelectorAll('a[href]');
  var accounts = [];
  links.forEach(function(l) {
    var h = l.href;
    if (h.match(/instagram\.com\/[a-z0-9._]+\/?$/) &&
        !h.match(/\/(explore|p\/|reel|igtv|tags|login|about|privacy|terms|help)/) &&
        !h.includes('#')) {
      var handle = h.replace('https://www.instagram.com/','').replace('/','');
      if (handle && handle !== '{handle}') accounts.push(handle);
    }
  });
  return [...new Set(accounts)].slice(0, 15);
})()
EOF
```

**筛选原则：** 选择 3-10 个核心竞品，优先：
1. 同城（同城市/区域）
2. 同规模（粉丝数相近，1K-20K）
3. 同品类（boba、奶茶、饮品）
4. 高活跃（有近期帖子）

### Step 1D：竞品数据抓取（循环）

对每个竞品重复 Step 1A + 1B，记录：
- 粉丝数 / 帖子数 / 简介
- 最近 1-3 条帖子的内容主题和互动数
- 内容规律（BTS 多？季节性？员工故事？）

### Step 1E：竞品共同规律分析

分析所有竞品数据，提取：
1. **内容类型分布**：BTS / 产品硬广 / 社区故事 / UGC / 促销 各占多少
2. **高频 Hashtag**：竞品共同使用的标签
3. **Caption 风格**：长短、语气、结构
4. **互动规律**：哪类内容 ER 最高
5. **Gap 发现**：竞品没做但存在机会的内容线

### Step 1F：输出 research_brief.md

写入 `workspace/social_media_output/research_brief.md`，包含：
- 账号健康度（粉丝/ER/发帖频率）
- 竞品对比表
- 热门话题 + Hashtag 建议
- 用户画像（推断）
- 内容策略建议

---

## 阶段 ②：无账号 Brand Intake

如果用户没有 Instagram 账号：

### 引导用户填写品牌信息

请用户提供以下信息（通过对话收集）：

1. **品牌名称** + 简介（一句话描述业务）
2. **目标受众**：谁会来买？（年龄/地域/身份）
3. **主要产品/服务**：最想推广的是什么
4. **视觉风格**：品牌色调、整体风格描述
5. **竞品**：用户自己知道哪些类似品牌（2-5个）
6. **目标市场**：城市/地区
7. **已有社媒账号**（如有）：任何平台的链接

基于用户提供的信息，生成 `brand_kit.json`，再进入内容生产阶段。

---

## 阶段 ③：内容生产（Creator）

### Step 3A：制定月度内容主题

基于 `research_brief.md` 中的策略建议，制定：
- 每月 4 周，每周 3 篇（IG Feed / IG Reel / TikTok）
- 内容主题分布：产品（1） + BTS（1） + 互动/社区（1）
- 覆盖当月节日节点

### Step 3B：为每条帖子生成内容

每个 `posts/` 子目录包含：

**brief.md：**
```markdown
# Post Brief: {标题}

**日期：** YYYY-MM-DD ({星期})
**平台：** Instagram + TikTok
**内容类型：** BTS / Product / Community / Promo
**关联调研依据：** §{N} of research_brief: "{竞品发现}"

## 核心信息
{一句话卖点}

## 视觉方向
- 风格：{参考竞品X的风格}
- 构图：{具体描述}
- 必须包含：Logo（右下角）

## Caption 公式
[Hook - 10字内] / [内容 - 2-3句] / [CTA] / [Hashtags]

## 研究依据
"{竞品X的做法}" → BubbleU 应该这样做
```

**caption.md（3 个变体）：**
- Variant A：情感化叙事风格
- Variant B：轻松随性风格
- Variant C：简洁直接风格

### Step 3C：生成 image_prompt

为每条帖子生成 4-5 张轮播图或视频的生图提示词：
```
{风格描述}, {主体}, {构图}, {光线}, {配色：参考 brand_kit.json}
{负面提示：no text, no watermark, no copyright}
```

---

## 阶段 ④：合规审核（Publisher）

### Step 4A：逐篇审核

使用 `references/review_rules.md` 中的 Checklist，对每条帖子检查：

**Copy 检查：**
- [ ] Caption ≤ 2200 chars（IG/TikTok）
- [ ] Hashtag 数量：IG 5-15，TikTok 3-5
- [ ] 无违禁词（竞奖/速富类）
- [ ] CTA 存在
- [ ] 无未注明促销条款

**Visual 检查：**
- [ ] 图片文字占比 ≤ 20%（FB/IG 广告规则）
- [ ] Logo 存在于图片中

**合规检查：**
- [ ] 无健康/医疗声明
- [ ] 促销帖含法律文本（"While supplies last. Not valid with other offers."）

### Step 4B：评级与修复建议

每条帖子评级：
- 🔴 **BLOCK**：含不可发布内容 → 给出具体修改方案
- 🟡 **WARN**：建议修改 → 给出建议
- ✅ **PASS**：可发布

### Step 4C：发布排期

生成 `calendar.json`，根据平台最佳时间排期：
- IG Feed：周二/周四 11:30 AM（本地时间）
- IG Reel：周五 6:00 PM（本地时间）
- TikTok：周三/周六 8:00 PM（本地时间）

---

## 关键提示

- **无 Instagram API**：全程使用 agent-browser 公开数据爬取，不需要登录
- **竞品数量**：至少抓 3 个核心竞品，有时间多抓几个
- **互动数据**：仅能获取已登录可见帖子的点赞/评论数，部分数据可能缺失
- **法律合规**：美国市场促销内容必须附法律文本
- **品牌调性**：参考 `brand_kit.json` 中的 tone_of_voice
- **竞品缺口**：重点标注竞品没做但你可以做的内容线

## 参考文件

- `references/brand_kit_template.md` — brand_kit.json 模板
- `references/content_patterns.md` — 竞品内容规律分析框架
- `references/review_rules.md` — 合规审核清单与违禁词表
