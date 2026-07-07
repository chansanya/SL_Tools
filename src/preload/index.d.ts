import type { SlApi } from '../shared/types'

declare global {
  interface Window {
    api: SlApi
  }
}
