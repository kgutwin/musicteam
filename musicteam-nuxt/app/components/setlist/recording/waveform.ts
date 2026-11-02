import { Input, ALL_FORMATS, UrlSource, AudioSampleSink } from "mediabunny"
import { timeString } from "@/utils"

export interface AudioPeak {
  time: number
  max: number
  rms: number
  nsm: number
}

export interface WaveformMark {
  time: number
  label: string
  color: string
}

export class WaveformViewer {
  duration: number
  peaks: AudioPeak[]
  cursor: number
  marks: WaveformMark[]

  canvas: HTMLCanvasElement | null
  ctx: CanvasRenderingContext2D | null

  constructor(duration: number, peaks: AudioPeak[]) {
    this.duration = duration
    this.peaks = peaks
    this.cursor = -1
    this.marks = []
    this.canvas = null
    this.ctx = null
  }

  setCanvas(canvas: HTMLCanvasElement) {
    this.canvas = canvas
    this.ctx = canvas.getContext("2d")
    this.draw()
  }

  setMarks(marks: WaveformMark[]) {
    this.marks = marks
    this.draw()
  }

  offset(time: number) {
    if (!this.canvas || !this.duration) return 0
    const hscale = this.canvas.clientWidth / this.duration
    return Math.round(time * hscale)
  }

  draw() {
    const ctx = this.ctx
    if (!ctx || !this.canvas) return
    if (this.duration === null) return

    const height = this.canvas.clientHeight
    const width = this.canvas.clientWidth
    const ruler = 18
    const hscale = width / this.duration!

    ctx.fillStyle = "white"
    ctx.fillRect(0, 0, width, height)

    // todo: auto scale tick rate based on duration
    const tick = 600.0 // ten minutes

    // draw ruler
    ctx.fillStyle = "rgb(148 163 184)" // bg-slate-400
    ctx.fillRect(0, 0, width, ruler)
    ctx.fillStyle = "white"
    ctx.font = "13px monospace"
    ctx.textAlign = "start"
    ctx.strokeStyle = "rgb(71 85 105)" // bg-slate-600
    ctx.setLineDash([3, 2])
    ctx.lineWidth = 1
    for (let x = 0; x < this.duration; x += tick) {
      const offset = Math.round(x * hscale) - 0.5
      ctx.fillText(timeString(x), offset + 3, 12)
      if (x > 0) {
        ctx.beginPath()
        ctx.moveTo(offset, 1)
        ctx.lineTo(offset, height)
        ctx.stroke()
      }
    }
    ctx.setLineDash([])

    // draw waveform
    const wave = (peaks: { time: number; v: number }[], maxV: number) => {
      ctx.beginPath()
      const center = height / 2 + ruler / 2
      ctx.moveTo(0, center)
      const vscale = (height - ruler) / 2 / maxV

      // starting at the left center, draw peaks going upwards
      for (const peak of peaks) {
        ctx.lineTo(peak.time * hscale, center - peak.v * vscale)
      }
      // then, going backwards, draw symmetrical peaks going downwards
      for (const peak of peaks.toReversed()) {
        ctx.lineTo(peak.time * hscale, center + peak.v * vscale)
      }

      ctx.fill()
    }

    const max = Math.max(...this.peaks.map((p) => Math.max(p.max, p.rms)))

    ctx.fillStyle = "rgb(96 165 250)" // bg-blue-400
    wave(
      this.peaks.map((p) => ({ time: p.time, v: p.max })),
      max,
    )

    ctx.fillStyle = "rgb(59 130 246)" // bg-blue-500
    wave(
      this.peaks.map((p) => ({ time: p.time, v: p.rms * 2 })),
      max,
    )

    // draw marks
    let lastLabelEnd = 0
    let lastLabelRow = 0
    ctx.font = "14px sans-serif"
    for (const mark of this.marks) {
      ctx.fillStyle = mark.color
      const offset = Math.round(mark.time * hscale)
      ctx.fillRect(offset - 0.5, ruler, 1, height - ruler)
    }
    for (const mark of this.marks) {
      ctx.fillStyle = mark.color
      const offset = Math.round(mark.time * hscale)
      const labelSize = ctx.measureText(mark.label)
      const labelEnd = offset + labelSize.width + 3
      const labelRow = offset < lastLabelEnd ? (lastLabelRow + 1) % 2 : 0
      const labelTop = ruler + 17 * labelRow

      ctx.fillRect(offset - 0.5, labelTop, labelEnd - offset, 16)
      ctx.fillStyle = "white"
      ctx.fillText(mark.label, offset + 1, labelTop + 12)

      lastLabelEnd = labelEnd
      lastLabelRow = labelRow
    }

    // draw cursor
    if (this.cursor >= 0 && this.cursor <= this.duration) {
      ctx.fillStyle = "red"
      const offset = Math.round(this.cursor * hscale)
      ctx.beginPath()
      ctx.moveTo(offset - 3, ruler)
      ctx.lineTo(offset + 3, ruler)
      ctx.lineTo(offset + 0.5, ruler + 3)
      ctx.lineTo(offset + 0.5, height)
      ctx.lineTo(offset - 0.5, height)
      ctx.lineTo(offset - 0.5, ruler + 3)
      ctx.lineTo(offset - 3, ruler)
      ctx.fill()
    }
  }
}
