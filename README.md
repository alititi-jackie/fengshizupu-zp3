# zp3.fengshizupu.com — 各地冯氏族谱收藏（第三站）

收录各地图书馆藏本冯氏宗谱影印（公有领域），逐页在线连读。入口在主站
fengshizupu.com「各地族谱」页（恩平谱、小湴村之后）。

## 架构
- 静态站，GitHub Pages + GitHub Actions 部署，自定义域名 zp3.fengshizupu.com（site/CNAME 由生成器输出）。
- 书目数据：`data/books.json`（书名、地区、年代、纂辑者、来源、各册页数与公有领域源文件 URL）。
- 构建流程（Actions）：从本站 Release `b-20261117` 下载源 PDF → `scripts/render_pages.py` 拆页、压页眉、转 WebP → `scripts/generate.py` 生成页面 → 部署。新书入库时把 PDF 加入该 Release（books.json 的 url 字段只作来源记录）。
- 每册源 PDF 约 30MB，不入库；本地备份在维护机 ~/workspace/fengshizupu-work/。
- 本站容量约 900MB 封顶，装满后开 zp4（新仓库+子域名，同一套代码）。

## 样式（与主站/恩平站统一）
- `assets/genealogy-theme.css` 是共享主题副本。**源头在主站仓库
  fengshizupu-site 的 `public/assets/genealogy-theme.css`**：改外观先改主站，
  再同步本站与恩平站（enpingfengshi-site 的 `assets/genealogy-theme.css`）。
- `assets/style.css`、`assets/site.js`、`assets/reader-controls.js` 沿用恩平站
  现行版本；阅读器为恩平连看阅读器（`assets/volume-reader.js` 按册适配：
  图片路径 /img/<slug>/<册id>/pNNNN.webp，页签「第 X 页」，无支系数据）。
- 页头/横向导航/页脚与主站相同；导航四项（首页/资讯/族谱/关于）链回主站
  绝对地址、本窗口打开，「族谱」高亮。

## 内容规则
- 只收公有领域馆藏影印，逐部注明藏本来源与纂修年代。
- 原书藏本馆水印保留不去除；每页左上方压「冯氏族谱 · fengshizupu.com」
  深红页眉（深色页自动用米白色），由 render_pages.py 完成；页眉样式只在
  render_pages.py 里改（下载版脚本共用同一个 stamp 函数）。
- 工作流文件在 `.github/workflows/build.yml`（仓库根目录不再放副本）。

## 加新书（完整流程）
1. 核实来源为公有领域馆藏影印，下载各册 PDF 到本地，核对册数与页数。
2. 原版 PDF 上传到 Release `b-20261117`（文件名 `<slug>-<册id>.pdf`）。
3. 本地跑 `scripts/make_download_pdfs.py` 生成带页眉下载版（`-dl.pdf`），
   一并上传到同一 Release；记下每册下载版大小（MB，保留一位小数）。
4. `data/books.json` 加一条：书名、地区、年代、纂辑者、来源、各册页数、
   每册 `dl_mb`；`url` 只作来源记录，构建不直连外部站点。
5. 推仓 → Actions 自动渲染全站并部署；验收首页卡片、书页、阅读页
   （下载行在阅读栏下方、进页可见）与 sitemap。
6. 主站「各地族谱」页新增一条入口：以书名为标题、直达本站该书页；
   本站首页搜索下方同步新增一张该书的卡片（生成器按 books.json 自动出）。
7. 在 GSC 域名资源里重新提交本站 sitemap（页数随新书增加）。

## 公共组件现行维护

以 [FAMILY_UI.md](FAMILY_UI.md) 为准。公共文件由主站固定版本同步，构建会校验哈希；不要在本站直接改共享主题、阅读控制或公共模板。zp 站点差异由 `data/site.json` 配置。
