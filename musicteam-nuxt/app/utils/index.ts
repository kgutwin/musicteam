export function trimArray(arr: string[], cut: number = 3): string[] {
  if (arr.length > cut) {
    return [...arr.slice(0, cut), "..."]
  }
  return arr
}

/** Converts UTC datetime into local time; returns date as string */
export function localdate(datetime?: string): string {
  if (datetime === undefined) return ""
  if (!datetime.endsWith("Z")) datetime += "Z"
  const d = new Date(datetime)
  return d.toLocaleDateString()
}
