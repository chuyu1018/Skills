# Brand Kit 模板

当用户无法提供 Instagram 数据时，基于对话收集的信息生成此文件。

## 字段说明

```json
{
  "brand_name": "品牌名称",
  "handle": "@账号名",
  "instagram_url": "https://www.instagram.com/xxx/ (如有)",
  "tone_of_voice": "品牌语调描述，如 Warm & playful / Premium & minimal",
  "primary_colors": ["#HEX1", "#HEX2"],
  "secondary_colors": ["#HEX3"],
  "font_primary": "主字体",
  "font_secondary": "辅助字体",
  "logo_url": "logo 图片路径或描述",
  "target_audience": "目标受众描述，如 25-35岁，都市白领，喜欢探店",
  "target_market": "地理市场，如 US / UK / CN",
  "timezone": "IANA 时区，如 America/Los_Angeles",
  "content_focus": "内容聚焦，如 奶茶/咖啡/烘焙甜点",
  "no_go_topics": ["禁忌话题列表，如 politics, religion"],
  "must_include": {
    "logo_placement": "logo 在图片中的位置，如 bottom-right",
    "cta_default": "默认 CTA，如 Tag a friend who needs this! 👇"
  },
  "contact": {
    "website": "网站",
    "phone": "电话",
    "address": "地址"
  },
  "holidays_priority": ["重点节日列表，需与内容日历关联"]
}
```

## 品牌语调分类参考

| 类型 | 描述 | 适合品牌 | Caption 风格 |
|---|---|---|---|
| Warm & Playful | 亲切、活泼、有温度 | 奶茶、甜品、亲子 | 感叹句多，emoji 多 |
| Premium & Minimal | 高冷、精致、少量文字 | 高级餐厅、设计师品牌 | 极简，留白多 |
| Bold & Fun | 大胆、有冲击力、年轻 | 街头服饰、酒吧 | 颜色鲜明，句式短 |
| Professional | 专业、信任、稳定 | B2B、金融 | 术语规范，结构清晰 |
| Community-Driven | 社区感、人情味、参与感 | 独立咖啡馆、社区店 | "我们"多，互动引导 |

## 颜色词汇表（用于生成生图提示词）

| 色系 | 关键词 |
|---|---|
| 暖粉 | warm pink, blush, coral, peach |
| 中性米 | cream, ivory, sand, beige |
| 深色系 | charcoal, espresso, midnight |
| 自然色 | sage green, terracotta, oat |
| 亮色系 | electric blue, neon, vibrant |
