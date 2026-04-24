<script>
  import { stories, selectedStoryId, project } from '../lib/stores.js'
  import { api } from '../lib/api.js'

  let editingStory = $state(null)
  let editData = $state({})

  $effect(() => {
    if ($selectedStoryId && $selectedStoryId !== '__new__') {
      const s = $stories.find(st => st.id === $selectedStoryId)
      if (s) {
        editingStory = s
        editData = { ...s, acceptance_criteria: [...(s.acceptance_criteria || [])] }
      }
    } else if ($selectedStoryId === '__new__') {
      editingStory = null
      editData = { epic: 'General', title: '', role: 'user', action: '', value: '', priority: 'Medium', acceptance_criteria: [] }
    } else {
      editingStory = null
    }
  })

  async function save() {
    if (!$project) return
    if (editingStory) {
      await api.updateStory($project.id, editingStory.id, editData)
      stories.update(list => list.map(s => s.id === editingStory.id ? { ...s, ...editData } : s))
    } else {
      const result = await api.addStory($project.id, editData)
      stories.update(list => [...list, { ...editData, id: result.id }])
      selectedStoryId.set(result.id)
    }
  }

  async function deleteStory() {
    if (!$project || !editingStory) return
    await api.deleteStory($project.id, editingStory.id)
    stories.update(list => list.filter(s => s.id !== editingStory.id))
    selectedStoryId.set(null)
  }

  async function regenerate() {
    if (!$project || !editingStory) return
    await api.regenerateStory($project.id, editingStory.id)
    const storyData = await api.getStories($project.id)
    stories.set(storyData.stories)
  }

  function addAC() {
    editData.acceptance_criteria = [...(editData.acceptance_criteria || []), { id: crypto.randomUUID().slice(0,8), description: '', is_testable: true }]
  }

  function removeAC(i) {
    editData.acceptance_criteria = editData.acceptance_criteria.filter((_, idx) => idx !== i)
  }
</script>

<div class="story-editor">
  {#if editingStory || $selectedStoryId === '__new__'}
    <div class="form">
      <div class="form-row">
        <label>Epic</label>
        <input bind:value={editData.epic} placeholder="Epic name" />
      </div>
      <div class="form-row">
        <label>Title</label>
        <input bind:value={editData.title} placeholder="Story title" />
      </div>
      <div class="form-row">
        <label>As a</label>
        <input bind:value={editData.role} placeholder="role" />
      </div>
      <div class="form-row">
        <label>I want</label>
        <input bind:value={editData.action} placeholder="action" />
      </div>
      <div class="form-row">
        <label>so that</label>
        <input bind:value={editData.value} placeholder="value" />
      </div>
      <div class="form-row">
        <label>Priority</label>
        <select bind:value={editData.priority}>
          <option>High</option><option>Medium</option><option>Low</option>
        </select>
      </div>

      <div class="ac-section">
        <div class="ac-header">
          <label>Acceptance Criteria</label>
          <button onclick={addAC}>+ Add</button>
        </div>
        {#each editData.acceptance_criteria || [] as ac, i}
          <div class="ac-row">
            <input
              value={ac.description}
              oninput={(e) => { 
                const updated = [...editData.acceptance_criteria]
                updated[i] = { ...updated[i], description: e.target.value }
                editData.acceptance_criteria = updated
              }}
              placeholder="Criterion..."
            />
            <button class="danger" onclick={() => removeAC(i)}>✕</button>
          </div>
        {/each}
      </div>

      {#if editingStory?.technical_notes}
        <div class="tech-notes">
          <label>Technical Notes</label>
          <div class="note-items">
            {#if editingStory.technical_notes.source_components?.length}
              <div><strong>Components:</strong> {editingStory.technical_notes.source_components.join(', ')}</div>
            {/if}
            {#if editingStory.technical_notes.source_flows?.length}
              <div><strong>Flows:</strong> {editingStory.technical_notes.source_flows.join(', ')}</div>
            {/if}
          </div>
        </div>
      {/if}

      <div class="actions">
        {#if editingStory}
          <button class="secondary" onclick={regenerate}>Regenerate</button>
          <button class="danger" onclick={deleteStory}>Delete</button>
        {/if}
        <button class="primary" onclick={save}>Save</button>
      </div>
    </div>
  {:else}
    <div class="empty">
      <p>Select a story to edit, or click "+ Add" to create a new one.</p>
    </div>
  {/if}
</div>

<style>
  .story-editor { flex: 1; }
  .form { display: flex; flex-direction: column; gap: 12px; max-width: 600px; }
  .form-row { display: flex; flex-direction: column; gap: 4px; }
  label { font-size: 0.8rem; color: #888; text-transform: uppercase; }
  input, select {
    background: #1a1a2e;
    border: 1px solid #3a3a5a;
    color: #e0e0e0;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.9rem;
  }
  input:focus, select:focus { outline: none; border-color: #00d4ff; }
  .ac-section { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 8px; padding: 12px; }
  .ac-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .ac-header button { background: #2a2a4a; border: 1px solid #3a3a5a; color: #4ecdc4; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
  .ac-row { display: flex; gap: 8px; margin-bottom: 6px; }
  .ac-row input { flex: 1; }
  .ac-row button.danger { background: none; border: none; color: #ff6b6b; cursor: pointer; }
  .tech-notes { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 8px; padding: 12px; }
  .tech-notes label { margin-bottom: 6px; display: block; }
  .note-items { font-size: 0.8rem; color: #888; display: flex; flex-direction: column; gap: 4px; }
  .actions { display: flex; gap: 8px; margin-top: 8px; }
  .primary { background: #00d4ff; color: #0f1117; border: none; padding: 8px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; }
  .secondary { background: #2a2a4a; border: 1px solid #3a3a5a; color: #ccc; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
  .danger { background: #3a1a1a; border: 1px solid #6b2d2d; color: #ff6b6b; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
  .empty { display: flex; align-items: center; justify-content: center; height: 200px; color: #666; }
</style>
