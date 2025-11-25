export interface SonglistPrefsFilters {
  title?: string
  tags: Record<string, boolean>
  authors: Record<string, boolean>
}

export type SonglistPrefsSortBy =
  | "Title"
  | "Author"
  | "Tag"
  | "Date Uploaded"
  | "CCLI Number"

export const useSonglistPrefsStore = defineStore("songlistPrefs", {
  state: () => {
    return {
      filters: {
        tags: {},
        authors: {},
      } as SonglistPrefsFilters,
      sortBy: "Title" as SonglistPrefsSortBy,
      sortAsc: true,
    }
  },
  persist: true,
})
