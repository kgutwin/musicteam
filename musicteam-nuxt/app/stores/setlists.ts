import { api } from "@/services"
import type { Setlist } from "@/services/api"
import { createStoreState, createParamStoreState } from "."
import { asDate } from "@/utils"

export const useActiveSetlistStore = defineStore("activeSetlist", {
  state: () => {
    return {
      setlist: null as Setlist | null,
      open: true,
    }
  },
  persist: {
    storage: sessionStorage,
    pick: ["setlist"],
    afterHydrate: async (ctx) => {
      if (ctx.store.setlist) {
        try {
          const freshSetlist = await useSetlistStore()
            .get({ setlistId: ctx.store.setlist.id })
            .get()

          // setlists in the past won't stay active on persistence
          // reload. This helps to clean things up if a user had left a
          // setlist active past its service date.
          if (freshSetlist.service_date) {
            const serviceDate = asDate(freshSetlist.service_date)
            if (serviceDate < new Date()) {
              ctx.store.setlist = null
              return
            }
          }

          ctx.store.setlist = freshSetlist
        } catch {
          ctx.store.setlist = null
          return
        }
      }
    },
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

export const useSetlistPositionStore = defineStore(
  "setlistposition",
  createParamStoreState(
    async (params: { setlistId: string; positionId: string }) =>
      await api.setlists.getSetlistPosition(params.setlistId, params.positionId),
  ),
)

export const useSetlistSheetStore = defineStore(
  "setlistsheet",
  createParamStoreState(
    async (params: { setlistId: string; sheetId: string }) =>
      await api.setlists.getSetlistSheet(params.setlistId, params.sheetId),
  ),
)

export const useSetlistSheetlistStore = defineStore(
  "setlistsheetlist",
  createParamStoreState(
    async (params: { setlistId: string }) =>
      await api.setlists.listSetlistSheets(params.setlistId),
  ),
)

export const useSetlistRecordinglistStore = defineStore(
  "setlistrecordinglist",
  createParamStoreState(
    async (params: { setlistId: string }) =>
      await api.setlists.listSetlistRecordings(params.setlistId),
  ),
)

export const useSetlistRecordingStore = defineStore(
  "setlistrecording",
  createParamStoreState(
    async (params: { setlistId: string; recordingId: string }) =>
      await api.setlists.getSetlistRecording(params.setlistId, params.recordingId),
  ),
)

export const useSetlistRecordingMarklistStore = defineStore(
  "setlistrecordingmarklist",
  createParamStoreState(
    async (params: { setlistId: string; recordingId: string }) =>
      await api.setlists.listSetlistRecordingMarks(
        params.setlistId,
        params.recordingId,
      ),
  ),
)

export const useSetlistInfoLatestStore = defineStore(
  "setlistinfolatest",
  createStoreState(async () => await api.setlists.getSetlistInfo("LATEST")),
)

export const useSetlistRefreshStore = defineStore(
  "setlistRefresh",
  createRefreshStoreState([
    useSetlistlistStore,
    useSetlistStore,
    useSetlistPositionlistStore,
    useSetlistPositionStore,
    useSetlistSheetlistStore,
    useSetlistRecordinglistStore,
    useSetlistRecordingStore,
    useSetlistRecordingMarklistStore,
    useSetlistInfoLatestStore,
  ]),
)
