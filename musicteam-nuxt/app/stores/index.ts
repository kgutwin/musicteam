import type { HttpResponse, UserList, ServerError } from "@/services/api"

export type Status = "idle" | "pending" | "ok" | "error"

export interface StoreState<T> {
  status: Ref<Status>
  currentData: Ref<T | undefined>
  error: Ref<ServerError | undefined>

  get: () => Promise<T>
  refresh: () => void
  expire: () => void
  data: Ref<T | undefined>
}

// TODO:
// - helper for parameter-based store
// - add useTimeout-based auto expiration

export function createStoreState<T>(fetcher: () => Promise<HttpResponse<T, any>>) {
  return (): StoreState<T> => {
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

export function createParamStoreState<P, T>(
  fetcher: (params: P) => Promise<HttpResponse<T, any>>,
) {
  return () => {
    const stores = shallowRef<Record<string, StoreState<T>>>({})

    function get(params: P): StoreState<T> {
      const encoded = JSON.stringify(params)

      let store = stores.value[encoded]
      if (!store) {
        store = createStoreState(() => fetcher(params))()
        stores.value[encoded] = store
      }
      return store
    }

    function refresh(params: Partial<P>) {
      for (const storeParamEncoded of Object.keys(stores.value)) {
        const storeParams = JSON.parse(storeParamEncoded)

        if (
          (Object.keys(params) as Array<keyof typeof params>).every(
            (p) => params[p] === storeParams[p],
          )
        ) {
          get(storeParams).refresh()
        }
      }
    }

    return { stores, get, refresh }
  }
}

type RefreshableStoreDef = () => {
  refresh: (params?: any) => void
}

export function createRefreshStoreState(stores: RefreshableStoreDef[]) {
  return () => {
    async function refresh(params?: Record<string, any>) {
      for (const storeDef of stores) {
        const store = storeDef()
        store.refresh(params)
      }
    }
    return { refresh }
  }
}
