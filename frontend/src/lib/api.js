const API_BASE = '/api'

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: {},
  }
  if (body && !(body instanceof FormData)) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  } else if (body instanceof FormData) {
    opts.body = body
  }
  const res = await fetch(`${API_BASE}${path}`, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }))
    throw new Error(err.error || err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  listProviders: () => request('GET', '/providers'),
  createProject: (name) => request('POST', '/projects', { name }),
  getProject: (id) => request('GET', `/projects/${id}`),
  uploadFiles: (projectId, files) => {
    const form = new FormData()
    for (const f of files) form.append('files', f)
    return request('POST', `/projects/${projectId}/upload`, form)
  },
  analyzeDiagram: (projectId, fileIndex = 0) =>
    request('POST', `/projects/${projectId}/analyze?file_index=${fileIndex}`),
  getComponents: (projectId) => request('GET', `/projects/${projectId}/components`),
  updateComponents: (projectId, updates) =>
    request('PUT', `/projects/${projectId}/components`, { components: updates }),
  generateStories: (projectId) => request('POST', `/projects/${projectId}/generate-stories`),
  getStories: (projectId) => request('GET', `/projects/${projectId}/stories`),
  updateStory: (projectId, storyId, updates) =>
    request('PUT', `/projects/${projectId}/stories/${storyId}`, updates),
  deleteStory: (projectId, storyId) =>
    request('DELETE', `/projects/${projectId}/stories/${storyId}`),
  regenerateStory: (projectId, storyId) =>
    request('POST', `/projects/${projectId}/stories/${storyId}/regenerate`),
  addStory: (projectId, storyData) =>
    request('POST', `/projects/${projectId}/stories`, storyData),
  exportMarkdown: (projectId) => request('POST', `/projects/${projectId}/export/markdown`),
}