# OT/FF 内容角度看板

深色卡片墙：每周 Orthotech + Foamfresh 内容角度（痛点、钩子、格式、参考缩略图），一个链接扫完，不用在群里读长文。

对照现网：[Foamfresh 清洁雷达](https://siewwengnick-rgb.github.io/ff-radar-/)（仓库 `siewwengnick-rgb/ff-radar-`）。

时区：**Asia/Kuala_Lumpur (UTC+8)**。

---

## Nick 如何打开（本机预览）

```bash
cd /workspace/content-angles-radar
python3 -m http.server 8766
```

浏览器打开：http://127.0.0.1:8766/

也可直接双击 `index.html`（数据已嵌在页面里，`file://` 可用；若只改了 `data.json` 请再跑一遍 `build_data.py` 以同步嵌入）。

---

## 重建数据

```bash
python3 /workspace/content-angles-radar/build_data.py
```

读取：

- `/workspace/viral-research-diy/pipeline/out/orthotech/content_angles.json`
- `/workspace/viral-research-diy/pipeline/out/foamfresh/content_angles.json`

写出：

- `data.json`（看板数据源）
- 并把同一份 JSON 嵌进 `index.html`（`<!-- ANGLES_DATA_START -->` …）

幂等：可重复跑。

---

## 页面说明

| 区块 | 说明 |
|------|------|
| 顶栏 | 「OT/FF 内容角度看板」、Live 灯、pipeline 更新时间 |
| 筛选 | 全部 / Orthotech / Foamfresh + 搜索 |
| 卡片 | 品牌 pill（OT 琥珀 / FF 青绿）、标题、痛点、主钩子、格式、RISING/保留、合规摘要；YouTube 参考用 `i.ytimg.com` 封面，Instagram 用品牌渐变占位 |
| 点开 | 侧栏：全部钩子、趋势信号、合规、参考链接（新标签）、播放量 |

合规文案只展示 pipeline 里的 `compliance` 字段；页面 chrome 不出现治疗/矫正等医疗话术。

---

## GitHub Pages（稍后部署，同 ff-radar- 模式）

建议新仓库名：**`content-angles-radar`**（或 `ot-ff-angles`）。

1. 在 `siewwengnick-rgb` 下建空仓 `content-angles-radar`
2. 推送本目录的 `index.html` + `data.json`（+ README / build 脚本可选）
3. Settings → Pages → Deploy from branch `main` / root
4. 预期地址：`https://siewwengnick-rgb.github.io/content-angles-radar/`

营销内容组周一只发：**看板已更新 + 上述链接**，不再贴整篇周报正文。

**本任务未推送 GitHub**——文件已在 box 就绪，等你确认仓库名后再部署。

---

## 与 Foamfresh 雷达的差别

| | 清洁雷达 `ff-radar-` | 本看板 |
|--|--|--|
| 对象 | 新品商品卡 + 搜索热度 | 社媒内容角度 + 参考片 |
| 数据 | 内联 PRODUCTS / TRENDS | `data.json` + 嵌入；`build_data.py` 从 pipeline 生成 |
| 品牌 | Foamfresh 单品牌 | OT + FF 双品牌筛选 |
