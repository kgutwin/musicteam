export type ToasterStatus = "pending" | "ok" | "error"

export interface UseToasterOptions {
  errorTitle?: string
  status?: Ref<ToasterStatus | undefined>
}
