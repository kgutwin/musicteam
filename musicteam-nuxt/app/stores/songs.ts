import { api } from "@/services"
import { createStoreState, createParamStoreState } from "."

export const useSonglistStore = defineStore(
  "songlist",
  createStoreState(async () => await api.songs.listSongs()),
)

export const useSongStore = defineStore(
  "song",
  createParamStoreState(
    async (params: { songId: string }) => await api.songs.getSong(params.songId),
  ),
)

export const useSongVersionlistStore = defineStore(
  "songversionlist",
  createParamStoreState(
    async (params: { songId: string }) =>
      await api.songs.listSongVersions(params.songId),
  ),
)

export const useSongVersionStore = defineStore(
  "songversion",
  createParamStoreState(
    async (params: { songId: string; versionId: string }) =>
      await api.songs.getSongVersion(params.songId, params.versionId),
  ),
)

export const useSongSheetlistStore = defineStore(
  "songsheetlist",
  createParamStoreState(
    async (params: { songId: string; versionId: string }) =>
      await api.songs.listSongSheets(params.songId, params.versionId),
  ),
)

export const useSongSheetStore = defineStore(
  "songsheet",
  createParamStoreState(
    async (params: { songId: string; versionId: string; sheetId: string }) =>
      await api.songs.getSongSheet(params.songId, params.versionId, params.sheetId),
  ),
)

export const useSongRefreshStore = defineStore(
  "songRefresh",
  createRefreshStoreState([
    useSonglistStore,
    useSongStore,
    useSongVersionlistStore,
    useSongVersionStore,
    useSongSheetlistStore,
    useSongSheetStore,
  ]),
)
