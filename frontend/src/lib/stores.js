import { writable } from 'svelte/store'

export const currentStep = writable(0)
export const project = writable(null)
export const components = writable([])
export const flows = writable([])
export const stories = writable([])
export const selectedStoryId = writable(null)
export const selectedProvider = writable('openai')