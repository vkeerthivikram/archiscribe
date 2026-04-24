<script>
  import StoryCard from './StoryCard.svelte'
  import { stories, selectedStoryId } from '../lib/stores.js'

  function selectStory(id) {
    selectedStoryId.set(id)
  }

  let epics = $derived.by(() => {
    const map = {}
    for (const s of $stories) {
      if (!map[s.epic]) map[s.epic] = []
      map[s.epic].push(s)
    }
    return map
  })
</script>

<div class="story-list">
  <div class="list-header">
    <h3>Stories ({$stories.length})</h3>
    <button class="add-btn" onclick={() => selectedStoryId.set('__new__')}>+ Add</button>
  </div>
  {#each Object.entries(epics) as [epic, epicStories]}
    <div class="epic-group">
      <div class="epic-label">{epic}</div>
      {#each epicStories as story}
        <StoryCard
          {story}
          selected={$selectedStoryId === story.id}
          onselect={() => selectStory(story.id)}
        />
      {/each}
    </div>
  {/each}
</div>

<style>
  .story-list { display: flex; flex-direction: column; gap: 8px; min-width: 240px; }
  .list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
  h3 { margin: 0; font-size: 0.85rem; color: #888; text-transform: uppercase; }
  .add-btn {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #4ecdc4;
    padding: 4px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
  }
  .epic-group { display: flex; flex-direction: column; gap: 4px; }
  .epic-label { font-size: 0.75rem; color: #666; padding: 4px 0; border-bottom: 1px solid #2a2a4a; }
</style>
