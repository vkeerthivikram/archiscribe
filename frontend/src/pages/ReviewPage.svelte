<script>
  import ComponentReview from '../components/ComponentReview.svelte'
  import FlowReview from '../components/FlowReview.svelte'
  import { project, currentStep, stories } from '../lib/stores.js'
  import { api } from '../lib/api.js'

  let generating = $state(false)

  async function generateStories() {
    if (!$project) return
    generating = true
    try {
      await api.generateStories($project.id)
      const storyData = await api.getStories($project.id)
      stories.set(storyData.stories)
      currentStep.set(2)
    } catch (e) {
      console.error(e)
    } finally {
      generating = false
    }
  }
</script>

<div class="review-page">
  <h2>Review Extracted Components</h2>
  <p class="subtitle">Confirm, rename, or remove components before generating stories</p>

  <div class="grid">
    <ComponentReview />
    <FlowReview />
  </div>

  <div class="actions">
    <button class="secondary" onclick={() => currentStep.update(s => s - 1)}>← Back</button>
    <button class="primary" onclick={generateStories} disabled={generating}>
      {generating ? 'Generating...' : 'Generate Stories →'}
    </button>
  </div>
</div>

<style>
  .review-page { max-width: 900px; margin: 0 auto; }
  h2 { margin: 0 0 8px; font-size: 1.5rem; }
  .subtitle { color: #888; margin: 0 0 24px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }
  .actions { display: flex; gap: 12px; }
  .secondary {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #ccc;
    padding: 10px 24px;
    border-radius: 8px;
    cursor: pointer;
  }
  .primary {
    background: #00d4ff;
    color: #0f1117;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
  }
  .primary:disabled { opacity: 0.5; }
</style>