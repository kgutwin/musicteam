import { Api } from "./api"

export const api = new Api({
  baseUrl: "/api",
  baseApiParams: { format: "json" },
})
