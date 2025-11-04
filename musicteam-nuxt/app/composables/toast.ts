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
    console.log(err)
    if (options.status) options.status.value = "error"
    toasthost.toast.show({
      type: "danger",
      title: options.errorTitle ?? "Something went wrong...",
      message: err?.error?.Message ?? err.toString(),
      timeout: 5,
    })
    return Promise.reject(err)
  }
}
