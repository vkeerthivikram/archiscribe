<script>
  import { flows, components } from '../lib/stores.js'

  function getComponentName(id) {
    const comp = $components.find(c => c.id === id)
    return comp ? comp.name : id
  }

  const typeLabels = {
    data: '📦 Data', api_call: '⚡ API Call', event: '📣 Event', async: '⏳ Async', sync: '🔄 Sync'
  }
</script>

<div class="flow-review">
  <h3>Detected Data Flows</h3>
  <div class="list">
    {#each $flows as flow}
      <div class="flow-item">
        <div class="flow-path">
          <span class="node">{getComponentName(flow.source_id)}</span>
          <span class="arrow">→</span>
          <span class="node">{getComponentName(flow.target_id)}</span>
        </div>
        <div class="flow-meta">
          {#if flow.label}<span class="label">{flow.label}</span>{/if}
          <span class="type">{typeLabels[flow.flow_type] || flow.flow_type}</span>
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .flow-review h3 { margin: 0 0 12px; font-size: 0.9rem; color: #888; text-transform: uppercase; }
  .list { display: flex; flex-direction: column; gap: 6px; }
  .flow-item {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    padding: 10px 12px;
  }
  .flow-path { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; font-family: monospace; font-size: 0.85rem; }
  .node { color: #00d4ff; }
  .arrow { color: #666; }
  .flow-meta { display: flex; gap: 8px; font-size: 0.75rem; }
  .label { color: #ffe66d; }
  .type { color: #666; }
</style>