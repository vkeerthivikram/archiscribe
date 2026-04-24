<script>
  import ExportPanel from '../components/ExportPanel.svelte'
  import { project, currentStep } from '../lib/stores.js'
  import { api } from '../lib/api.js'

  let markdown = $state('')
  let loading = $state(true)

  $effect(() => {
    if ($project) {
      api.exportMarkdown($project.id)
        .then(data => { markdown = data.markdown; loading = false })
        .catch(e => { console.error(e); loading = false })
    }
  })
</script>

<div class="export-page">
  <h2>Export Backlog</h2>
  <p class="subtitle">Download your product backlog as Markdown</p>

  {#if loading}
    <p class="loading">Generating markdown...</p>
  {:else}
    <ExportPanel {markdown} />
  {/if}

  <div class="actions">
    <button class="secondary" onclick={() => currentStep.update(s => s - 1)}>← Back to Editor</button>
  </div>
</div>

<style>
  .export-page { max-width: 900px; margin: 0 auto; }
  h2 { margin: 0 0 8px; font-size: 1.5rem; }
  .subtitle { color: #888; margin: 0 0 24px; }
  .loading { color: #666; }
  .actions { margin-top: 24px; }
  .secondary { background: #2a2a4a; border: 1px solid #3a3a5a; color: #ccc; padding: 10px 24px; border-radius: 8px; cursor: pointer; }
</style>
