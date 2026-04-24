<script>
  import { selectedProvider } from '../lib/stores.js'
  import { api } from '../lib/api.js'

  let providers = $state([])
  let loading = $state(true)

  $effect(() => {
    api.listProviders().then(data => {
      providers = data.providers
      if (providers.length > 0 && !$selectedProvider) {
        selectedProvider.set(providers[0].id)
      }
      loading = false
    }).catch(() => {
      providers = [{ id: 'openai', name: 'OpenAI GPT-4o' }]
      loading = false
    })
  })
</script>

<div class="provider-select">
  <label>AI Provider</label>
  {#if loading}
    <p class="loading">Loading providers...</p>
  {:else}
    <div class="options">
      {#each providers as p}
        <button
          class="provider-btn"
          class:selected={$selectedProvider === p.id}
          onclick={() => selectedProvider.set(p.id)}
        >
          <span class="provider-name">{p.name}</span>
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .provider-select { display: flex; flex-direction: column; gap: 8px; }
  label { font-size: 0.85rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }
  .loading { color: #666; font-size: 0.9rem; }
  .options { display: flex; flex-direction: column; gap: 6px; }
  .provider-btn {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #ccc;
    padding: 10px 14px;
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    font-size: 0.9rem;
    transition: all 0.15s;
  }
  .provider-btn:hover { border-color: #555; }
  .provider-btn.selected {
    background: #1a3a4a;
    border-color: #00d4ff;
    color: #00d4ff;
  }
</style>