<script>
  import { currentStep, project } from './lib/stores.js'
  import UploadPage from './pages/UploadPage.svelte'
  import ReviewPage from './pages/ReviewPage.svelte'
  import EditorPage from './pages/EditorPage.svelte'
  import ExportPage from './pages/ExportPage.svelte'

  const steps = ['Upload', 'Review', 'Edit Stories', 'Export']
</script>

<main>
  <header>
    <h1>Archiscribe</h1>
    <nav>
      {#each steps as label, i}
        <button
          class="step-btn"
          class:active={$currentStep === i}
          disabled={i > $currentStep}
          onclick={() => currentStep.set(i)}
        >
          <span class="step-num">{i + 1}</span>
          {label}
        </button>
      {/each}
    </nav>
  </header>

  <section class="content">
    {#if $currentStep === 0}
      <UploadPage />
    {:else if $currentStep === 1}
      <ReviewPage />
    {:else if $currentStep === 2}
      <EditorPage />
    {:else if $currentStep === 3}
      <ExportPage />
    {/if}
  </section>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: system-ui, sans-serif;
    background: #0f1117;
    color: #e0e0e0;
  }
  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  header {
    background: #1a1a2e;
    padding: 16px 32px;
    border-bottom: 1px solid #2a2a4a;
    display: flex;
    align-items: center;
    gap: 32px;
  }
  h1 {
    margin: 0;
    font-size: 1.4rem;
    color: #00d4ff;
  }
  nav {
    display: flex;
    gap: 8px;
  }
  .step-btn {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #888;
    padding: 6px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .step-btn.active {
    background: #1a3a4a;
    border-color: #00d4ff;
    color: #00d4ff;
  }
  .step-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .step-num {
    background: #00d4ff22;
    color: #00d4ff;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
  }
  .content {
    flex: 1;
    padding: 32px;
  }
</style>