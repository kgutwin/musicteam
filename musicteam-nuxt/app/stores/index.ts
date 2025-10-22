import type { HttpResponse, UserList, ServerError } from "@/services/api"

export type Status = "idle" | "pending" | "ok" | "error"

export interface State<T> {
  status: Status
  currentData?: T
  error?: ServerError
}

// TODO:
// - helper for parameter-based store
// - add useTimeout-based auto expiration

export function createStoreState<T>(fetcher: () => Promise<HttpResponse<T, any>>) {
  return () => {
    const status = ref<Status>("idle")
    const currentData = ref<T | undefined>()
    const error = ref<ServerError | undefined>()

    async function get(): Promise<T> {
      if (status.value === "ok" && currentData.value !== undefined)
        return currentData.value

      try {
        status.value = "pending"
        const response = await fetcher()
        currentData.value = response.data
        status.value = "ok"
        return currentData.value
      } catch (resp: any) {
        error.value = {
          Code: resp?.error?.Code ?? resp?.error?.name ?? resp?.name ?? "",
          Message: resp?.error?.Message ?? resp?.error?.message ?? resp.toString(),
        }
        status.value = "error"
        throw resp
      }
    }

    function refresh() {
      status.value = "pending"
      get()
    }

    function expire() {
      status.value = "idle"
      currentData.value = undefined
    }

    const data = computed<T | undefined>(() => {
      if (status.value === "idle") get()
      return currentData.value
    })

    return { status, currentData, error, get, refresh, expire, data }
  }
}
