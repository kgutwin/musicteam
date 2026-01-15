import { api } from "@/services"
import { sleep } from "@/utils"

export const usePingStore = defineStore("api-ping", () => {
  const timeout = 10 * 60 * 60 * 1000 // ten minutes
  const lastPing = ref<number>()
  const isPinging = ref(false)
  const pings = ref(0)

  const isAwakeNow = () => (lastPing.value ?? 0) > Date.now() - timeout
  const isAwake = computed(() => (isPinging.value, isAwakeNow()))

  async function ping(): Promise<boolean> {
    while (isPinging.value) {
      await sleep(250)
    }

    if (isAwakeNow()) return true

    try {
      isPinging.value = true
      pings.value += 1
      await api.index()
      lastPing.value = Date.now()
      pings.value = 0
      return true
    } catch {
      return false
    } finally {
      isPinging.value = false
    }
  }

  /** Ping until success */
  async function wake(): Promise<void> {
    while (!(await ping())) {
      await sleep(1000)
    }
  }

  return { lastPing, isPinging, pings, ping, wake, isAwake, isAwakeNow }
})
