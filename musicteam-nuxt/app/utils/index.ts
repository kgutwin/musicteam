export function trimArray(arr: string[], cut: number = 3): string[] {
  if (arr.length > cut) {
    return [...arr.slice(0, cut), "..."]
  }
  return arr
}

/** Converts UTC datetime into local time; returns date as string */
export function localdate(datetime?: string | null): string {
  if (!datetime) return ""
  if (!datetime.includes("T")) datetime += "T12:00:00"
  if (!datetime.endsWith("Z")) datetime += "Z"
  const d = new Date(datetime)
  return d.toLocaleDateString()
}

export function nextSunday(): string {
  const now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), now.getDate() + 7 - now.getDay())
    .toISOString()
    .split("T")[0] as string
}

export function fileToBase64String(file: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => {
      let encoded = reader.result?.toString() || ""
      encoded = encoded.replace(/^data:(.*,)?/, "")
      if (encoded.length % 4 > 0) {
        encoded += "=".repeat(4 - (encoded.length % 4))
      }
      resolve(encoded)
    }
    reader.onerror = reject
  })
}

export function randomId(): string {
  return Math.random().toString(36).slice(2, 9)
}

/**
 * Chord ratio is the ratio of the number of chord-like characters
 *     (upper case, space, number, slash, #, b)
 * in a line to the total number of characters.
 */
export function chordRatio(line: string): number {
  if (line.length === 0) return 0
  const chordCount = (line.match(/[A-Z0-9/#b ]/g) || []).length
  return chordCount / line.length
}
