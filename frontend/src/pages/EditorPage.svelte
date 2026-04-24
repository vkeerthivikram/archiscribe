<script>
  import StoryList from '../components/StoryList.svelte'
  import StoryEditor from '../components/StoryEditor.svelte'
  import { currentStep } from '../lib/stores.js'
</script>

<div class="editor-page">
  <h2>Edit Stories</h2>
  <p class="subtitle">Review and refine generated user stories</p>

  <div class="editor-layout">
    <StoryList />
    <StoryEditor />
  </div>

  <div class="actions">
    <button class="secondary" onclick={() => currentStep.update(s => s - 1)}>← Back</button>
    <button class="primary" onclick={() => currentStep.set(3)}>Export →</button>
  </div>
</div>

<style>
  .editor-page { max-width: 1100px; margin: 0 auto; }
  h2 { margin: 0 0 8px; font-size: 1.5rem; }
  .subtitle { color: #888; margin: 0 0 24px; }
  .editor-layout { display: flex; gap: 24px; margin-bottom: 32px; }
  .actions { display: flex; gap: 12px; }
  .secondary { background: #2a2a4a; border: 1px solid #3a3a5a; color: #ccc; padding: 10px 24px; border-radius: 8px; cursor: pointer; }
  .primary { background: #00d4ff; color: #0f1117; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; }
</style>
