import { Input, ALL_FORMATS, UrlSource, AudioSampleSink } from "mediabunny"

export interface AudioPeak {
  time: number
  max: number
  rms: number
  nsm: number
}

export class WaveformViewer {
  duration: number
  peaks: AudioPeak[]

  canvas: HTMLCanvasElement | null
  ctx: CanvasRenderingContext2D | null

  constructor(duration: number, peaks: AudioPeak[]) {
    this.duration = duration
    this.peaks = peaks
    this.canvas = null
    this.ctx = null
  }

  setCanvas(canvas: HTMLCanvasElement) {
    this.canvas = canvas
    this.ctx = canvas.getContext("2d")
    this.draw()
  }

  draw() {
    const ctx = this.ctx
    if (!ctx || !this.canvas) return
    if (this.duration === null) return

    const height = this.canvas.clientHeight
    const width = this.canvas.clientWidth
    const hscale = width / this.duration!

    ctx.clearRect(0, 0, height, width)

    // draw time ticks
    // ctx.strokeStyle = "gray"
    // const tick = 600.0 // ten minutes
    // for (let x = tick; x < this.duration; x += tick) {
    //   ctx.strokeRect(x * hscale, 0, 0, height)
    // }

    // draw waveform
    const wave = (peaks: { time: number; v: number }[], maxV: number) => {
      ctx.beginPath()
      const center = height / 2
      ctx.moveTo(0, center)
      const vscale = height / 2 / maxV

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
  }
}
