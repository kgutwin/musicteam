import { api } from "@/services"
import { sleep } from "@/utils"

export const usePingStore = defineStore("api-ping", () => {
  const timeout = 10 * 60 * 60 * 1000 // ten minutes
  const lastPing = ref<number>()
  const isPinging = ref(false)

  async function ping(): Promise<boolean> {
    while (isPinging.value) {
      await sleep(250)
    }

    if ((lastPing.value ?? 0) > Date.now() - timeout) return true

    try {
      isPinging.value = true
      await api.index()
      lastPing.value = Date.now()
      return true
    } catch {
      return false
    } finally {
      isPinging.value = false
    }
  }

  /** Ping until success */
  async function wake(): Promise<void> {
    while (!ping()) {
      await sleep(1000)
    }
  }

  return { lastPing, ping, wake }
})
