import type { HttpResponse, UserList, ServerError } from "@/services/api"
import { useToaster } from "@/composables/toast"

/**
 * Status states:
 * - idle: store has not yet loaded or has expired
 * - pending: store is in progress for loading
 * - ok: store data is available
 * - error: an error was caught during loading
 */
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
// - add useTimeout-based auto expiration

export function createStoreState<T>(fetcher: () => Promise<HttpResponse<T, any>>) {
  return (): StoreState<T> => {
    const status = ref<Status>("idle")

    /**
     * The current state of the store.
     *
     * Equivalent to the `data` computed property, but reading this does not
     * automatically trigger a load.
     */
    const currentData = ref<T | undefined>()

    /** If the `status` is "error", this holds the error details. */
    const error = ref<ServerError | undefined>()

    /**
     * Retrieve the store data, via an async Promise.
     *
     * Use this when you are willing to await on the store data and do not want
     * to handle reactive dependencies or undefined return values.
     */
    async function get(): Promise<T> {
      if (status.value === "ok" && currentData.value !== undefined)
        return currentData.value

      try {
        return useToaster(async () => {
          status.value = "pending"
          const response = await fetcher()
          currentData.value = response.data
          status.value = "ok"
          return currentData.value
        })
      } catch (resp: any) {
        error.value = {
          Code: resp?.error?.Code ?? resp?.error?.name ?? resp?.name ?? "",
          Message: resp?.error?.Message ?? resp?.error?.message ?? resp.toString(),
        }
        status.value = "error"
        throw resp
      }
    }

    /** Schedule an update of the store data without wiping the existing state. */
    function refresh() {
      status.value = "pending"
      get()
    }

    /**
     * Wipe the existing state, triggering a refresh if the store is currently in use.
     */
    function expire() {
      status.value = "idle"
      currentData.value = undefined
    }

    /**
     * A computed reactive property representing the store state.
     *
     * Automatically requests the store data, asynchronously, if it is
     * not loaded. While loading is in progress, this property will be
     * undefined.
     */
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

    /**
     * Retrieve a store that invokes the fetcher with the provided params.
     *
     * The resulting value is an instance of StoreState and can
     * therefore be used via its `get()` method or its `data` computed
     * property. The store instance will be cached and will be reused
     * on subsequent invocations.
     */
    function get(params: P): StoreState<T> {
      const encoded = JSON.stringify(params)

      let store = stores.value[encoded]
      if (!store) {
        store = createStoreState(() => fetcher(params))()
        stores.value[encoded] = store
      }
      return store
    }

    /**
     * Refresh some or all of the stores associated with this param store.
     *
     * If the params arg is omitted or empty, all stores will be
     * refreshed. Otherwise, only the stores that have a superset of
     * parameters to the ones provided will be refreshed.
     */
    function refresh(params?: Partial<P>) {
      if (!params) return

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
