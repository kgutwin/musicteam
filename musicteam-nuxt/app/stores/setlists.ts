import { api } from "@/services"
import type { Setlist } from "@/services/api"
import { createStoreState, createParamStoreState } from "."

export const useActiveSetlistStore = defineStore("activeSetlist", {
  state: () => {
    return {
      setlist: null as Setlist | null,
      open: true,
    }
  },
})

export const useSetlistlistStore = defineStore(
  "setlistlist",
  createStoreState(async () => await api.setlists.listSetlists()),
)

export const useSetlistStore = defineStore(
  "setlist",
  createParamStoreState(
    async (params: { setlistId: string }) =>
      await api.setlists.getSetlist(params.setlistId),
  ),
)

export const useSetlistPositionlistStore = defineStore(
  "setlistpositionlist",
  createParamStoreState(
    async (params: { setlistId: string }) =>
      await api.setlists.listSetlistPositions(params.setlistId),
  ),
)

export const useSetlistSheetlistStore = defineStore(
  "setlistsheetlist",
  createParamStoreState(
    async (params: { setlistId: string }) =>
      await api.setlists.listSetlistSheets(params.setlistId),
  ),
)

export const useSetlistRefreshStore = defineStore(
  "setlistRefresh",
  createRefreshStoreState([
    useSetlistlistStore,
    useSetlistStore,
    useSetlistPositionlistStore,
    useSetlistSheetlistStore,
  ]),
)
