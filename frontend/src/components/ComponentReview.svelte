<script>
  import { components } from '../lib/stores.js'
  import { api } from '../lib/api.js'
  import { project } from '../lib/stores.js'

  let editingId = $state(null)
  let editName = $state('')

  function confirm(id) {
    const comps = $components.map(c => c.id === id ? { ...c, status: 'confirmed' } : c)
    components.set(comps)
    sync(comps)
  }

  function remove(id) {
    const comps = $components.map(c => c.id === id ? { ...c, status: 'removed' } : c)
    components.set(comps)
    sync(comps)
  }

  function rename(id, name) {
    editingId = id
    editName = name
  }

  function saveRename(id) {
    const comps = $components.map(c => c.id === id ? { ...c, name: editName, status: 'renamed' } : c)
    components.set(comps)
    sync(comps)
    editingId = null
  }

  function sync(comps) {
    if ($project) {
      api.updateComponents($project.id, { components: comps }).catch(console.error)
    }
  }

  const typeIcons = {
    database: '🗄️', api: '⚡', service: '🔧', queue: '📬',
    storage: '☁️', load_balancer: '⚖️', cache: '⚡', gateway: '🚪',
    client: '🖥️', user: '👤', external: '🔗', unknown: '❓',
  }
</script>

<div class="component-review">
  <h3>Extracted Components</h3>
  <div class="list">
    {#each $components as comp}
      <div class="item" class:removed={comp.status === 'removed'}>
        <span class="icon">{typeIcons[comp.component_type] || '❓'}</span>
        <div class="info">
          {#if editingId === comp.id}
            <input bind:value={editName} onkeydown={(e) => e.key === 'Enter' && saveRename(comp.id)} />
          {:else}
            <strong>{comp.name}</strong>
          {/if}
          <span class="type-badge">{comp.component_type}</span>
        </div>
        <div class="actions">
          {#if comp.status !== 'confirmed'}
            <button onclick={() => confirm(comp.id)} title="Confirm">✓</button>
          {/if}
          {#if comp.status !== 'removed'}
            <button onclick={() => rename(comp.id, comp.name)} title="Rename">✎</button>
          {/if}
          {#if comp.status !== 'removed'}
            <button class="danger" onclick={() => remove(comp.id)} title="Remove">✕</button>
          {/if}
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .component-review h3 { margin: 0 0 12px; font-size: 0.9rem; color: #888; text-transform: uppercase; }
  .list { display: flex; flex-direction: column; gap: 6px; }
  .item {
    background: #1a2a3a;
    border: 1px solid #2d4a6b;
    border-radius: 6px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: opacity 0.2s;
  }
  .item.removed { opacity: 0.4; text-decoration: line-through; }
  .icon { font-size: 1.2rem; }
  .info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
  .info input { background: #2a2a4a; border: 1px solid #444; color: #e0e0e0; padding: 4px 8px; border-radius: 4px; }
  .type-badge { font-size: 0.75rem; color: #666; }
  .actions { display: flex; gap: 4px; }
  .actions button {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #888;
    width: 28px;
    height: 28px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
  }
  .actions button:hover { border-color: #00d4ff; color: #00d4ff; }
  .actions button.danger:hover { border-color: #ff6b6b; color: #ff6b6b; }
</style>