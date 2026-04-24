<script>
  let { markdown = '' } = $props()
  let copied = $state(false)

  function download() {
    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'product-backlog.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  async function copyToClipboard() {
    await navigator.clipboard.writeText(markdown)
    copied = true
    setTimeout(() => copied = false, 2000)
  }
</script>

<div class="export-panel">
  <div class="toolbar">
    <button onclick={download}>⬇ Download .md</button>
    <button onclick={copyToClipboard}>{copied ? '✓ Copied!' : '📋 Copy to Clipboard'}</button>
  </div>
  <div class="preview">
    <pre>{markdown}</pre>
  </div>
</div>

<style>
  .export-panel { display: flex; flex-direction: column; gap: 16px; }
  .toolbar { display: flex; gap: 10px; }
  .toolbar button {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #e0e0e0;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
  }
  .toolbar button:hover { border-color: #00d4ff; color: #00d4ff; }
  .preview {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 20px;
    max-height: 500px;
    overflow: auto;
  }
  pre {
    margin: 0;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    color: #ccc;
    line-height: 1.6;
  }
</style>
