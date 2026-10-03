export function downloadFile(content, filename, contentType) {
  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function exportToMarkdown(brd) {
  const md = `# ${brd.title || 'BRD Document'}\n\n## Summary\n${brd.summary || ''}\n`;
  downloadFile(md, 'BRD-Document.md', 'text/markdown');
}
