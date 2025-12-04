import { useToastStore } from "@/stores/toasts"

import type { TailvueToast } from "tailvue"
import type { UseToasterOptions } from "@/types/toast"

export async function useToaster<T>(
  fn: (toast: TailvueToast) => Promise<T>,
  options: UseToasterOptions = {},
): Promise<T> {
  const toasthost = useToastStore()

  try {
    if (options.status) options.status.value = "pending"
    const rv = await fn(toasthost.toast)
    if (options.status) options.status.value = "ok"
    return rv
  } catch (err: any) {
    if (options.status) options.status.value = "error"
    let message = err?.error?.Message ?? err.toString()
    if (!message && err?.statusText) {
      message = err.statusText
    }
    console.error(err)
    toasthost.toast.show({
      type: "danger",
      title: options.errorTitle ?? "Something went wrong...",
      message,
      timeout: 5,
    })
    return Promise.reject(err)
  }
}
