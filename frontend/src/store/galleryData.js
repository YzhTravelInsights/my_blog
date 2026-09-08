/**
 * 图库原始数据：用 Vite 的 import.meta.glob 自动扫描 src/assets/gallery/ 下的所有图片。
 *
 * 约定：
 *  - 专辑 = 子文件夹名（如 流萤同人 / 游戏截图）
 *  - 标题 / 描述从文件名解析，支持「标题.描述.png」格式；没有点时标题 = 文件名
 *
 * 以后发图：把图片拖进 src/assets/gallery/<专辑名>/ 即可自动出现，无需改任何代码。
 */
// 相对路径：本文件在 src/store/ 下，../assets/gallery → src/assets/gallery
const modules = import.meta.glob('../assets/gallery/**/*.{jpg,jpeg,png,webp,gif}', {
  eager: true,
  query: '?url',
  import: 'default',
})

export function loadGalleryRaw() {
  const list = []
  for (const [path, url] of Object.entries(modules)) {
    const parts = path.split('/')
    const album = parts[parts.length - 2]
    const file = parts[parts.length - 1]
    const base = file.replace(/\.[^.]+$/, '')
    let title = base
    let desc = ''
    const seg = base.split('.')
    if (seg.length >= 2) {
      title = seg[0]
      desc = seg.slice(1).join('.')
    }
    list.push({ id: path, album, title, desc, url, file })
  }
  // 专辑按字母序，专辑内按文件名排序，展示顺序稳定
  list.sort((a, b) => (a.album === b.album ? a.file.localeCompare(b.file) : a.album.localeCompare(b.album)))
  return list
}
