<script>
  let { files = $bindable([]) } = $props()

  let dragover = $state(false)

  function handleDrop(e) {
    e.preventDefault()
    dragover = false
    const dropped = Array.from(e.dataTransfer.files)
    files = [...files, ...dropped]
  }

  function handleFileInput(e) {
    const selected = Array.from(e.target.files)
    files = [...files, ...selected]
  }

  function removeFile(i) {
    files = files.filter((_, idx) => idx !== i)
  }

  const accepted = '.png,.jpg,.jpeg,.svg,.webp,.pdf,.drawio,.xml,.excalidraw,.vsdx'
</script>

<div
  class="dropzone"
  class:dragover
  ondrop={handleDrop}
  ondragover={(e) => { e.preventDefault(); dragover = true }}
  ondragleave={() => dragover = false}
  role="button"
  tabindex="0"
  onkeydown={(e) => e.key === 'Enter' && e.target.querySelector('input').click()}
>
  <div class="icon">📁</div>
  <p>Drop diagram files here</p>
  <p class="hint">PNG, JPEG, SVG, PDF, Draw.io, Excalidraw, Visio</p>
  <input type="file" {accepted} multiple onchange={handleFileInput} />
</div>

{#if files.length > 0}
  <div class="file-list">
    {#each files as file, i}
      <div class="file-chip">
        <span>{file.name}</span>
        <button onclick={() => removeFile(i)}>✕</button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .dropzone {
    border: 2px dashed #444;
    border-radius: 12px;
    padding: 48px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }
  .dropzone.dragover {
    border-color: #00d4ff;
    background: #00d4ff11;
  }
  .dropzone input {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
  }
  .icon { font-size: 2.5rem; margin-bottom: 8px; }
  p { margin: 4px 0; color: #aaa; }
  .hint { font-size: 0.8rem; color: #666; }
  .file-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
  .file-chip {
    background: #2a2a4a;
    padding: 6px 12px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
  }
  .file-chip button {
    background: none;
    border: none;
    color: #ff6b6b;
    cursor: pointer;
    font-size: 0.9rem;
  }
</style>