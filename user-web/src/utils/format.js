export function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

export function getFileTypeClass(type) {
  const classes = {
    pdf: 'type-pdf',
    docx: 'type-word',
    doc: 'type-word',
    md: 'type-md',
    txt: 'type-txt',
    html: 'type-html',
  }
  return classes[type] || ''
}

export function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
