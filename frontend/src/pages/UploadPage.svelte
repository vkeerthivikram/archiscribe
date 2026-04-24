<script>
  import FileUpload from '../components/FileUpload.svelte'
  import ProviderSelect from '../components/ProviderSelect.svelte'
  import { project, currentStep, components, flows, stories } from '../lib/stores.js'
  import { api } from '../lib/api.js'

  let files = $state([])
  let uploading = $state(false)
  let error = $state('')

  async function handleAnalyze() {
    if (files.length === 0) {
      error = 'Please add at least one diagram file'
      return
    }
    uploading = true
    error = ''
    try {
      const proj = await api.createProject('Architecture Analysis')
      project.set(proj)
      await api.uploadFiles(proj.id, files)
      await api.analyzeDiagram(proj.id, 0)
      const compData = await api.getComponents(proj.id)
      components.set(compData.components)
      flows.set(compData.flows)
      stories.set([])
      currentStep.set(1)
    } catch (e) {
      error = e.message
    } finally {
      uploading = false
    }
  }
</script>

<div class="upload-page">
  <h2>Upload Architecture Diagram</h2>
  <p class="subtitle">Upload your diagram files to generate user stories</p>

  <div class="panel">
    <FileUpload bind:files />
    <ProviderSelect />
  </div>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <div class="actions">
    <button class="primary" onclick={handleAnalyze} disabled={uploading || files.length === 0}>
      {uploading ? 'Analyzing...' : 'Analyze Diagram →'}
    </button>
  </div>
</div>

<style>
  .upload-page { max-width: 700px; margin: 0 auto; }
  h2 { margin: 0 0 8px; font-size: 1.5rem; color: #e0e0e0; }
  .subtitle { color: #888; margin: 0 0 24px; }
  .panel {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  .error { color: #ff6b6b; margin: 8px 0; }
  .actions { margin-top: 24px; display: flex; gap: 12px; }
  .primary {
    background: #00d4ff;
    color: #0f1117;
    border: none;
    padding: 12px 28px;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
  }
  .primary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>