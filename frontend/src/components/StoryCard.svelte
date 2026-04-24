<script>
  let { story, selected = false, onselect } = $props()

  const priorityColors = { High: '#ff6b6b', Medium: '#ffe66d', Low: '#4ecdc4' }
</script>

<div class="card" class:selected onclick={onselect}>
  <div class="header">
    <span class="epic-badge">{story.epic}</span>
    <span class="priority" style="color: {priorityColors[story.priority] || '#888'}">
      {story.priority}
    </span>
  </div>
  <h4>{story.title}</h4>
  <p class="as-a">As a <strong>{story.role}</strong></p>
  <p class="ac-count">{story.acceptance_criteria?.length || 0} acceptance criteria</p>
</div>

<style>
  .card {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 12px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .card:hover { border-color: #3a3a5a; }
  .card.selected { border-color: #00d4ff; background: #1a2a3a; }
  .header { display: flex; justify-content: space-between; margin-bottom: 6px; }
  .epic-badge { font-size: 0.7rem; background: #2a2a4a; color: #888; padding: 2px 6px; border-radius: 3px; }
  .priority { font-size: 0.75rem; font-weight: 600; }
  h4 { margin: 0 0 4px; font-size: 0.95rem; color: #e0e0e0; }
  .as-a { margin: 0; font-size: 0.8rem; color: #888; }
  .ac-count { margin: 4px 0 0; font-size: 0.75rem; color: #666; }
</style>
