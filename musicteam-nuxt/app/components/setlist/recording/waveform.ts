import { Input, ALL_FORMATS, UrlSource, AudioSampleSink } from "mediabunny"

interface AudioPeak {
  time: number
  max: number
  rms: number
  nsm: number
}

export class WaveformViewer {
  url: string
  duration: number | null
  peaks: AudioPeak[]

  canvas: HTMLCanvasElement | null
  ctx: CanvasRenderingContext2D | null

  constructor(url: string) {
    this.url = url
    this.duration = null
    this.peaks = []
    this.canvas = null
    this.ctx = null
  }

  setCanvas(canvas: HTMLCanvasElement) {
    this.canvas = canvas
    this.ctx = canvas.getContext("2d")
  }

  async load() {
    // note: this process is too slow, relative to the fact that we already need to
    // process the file at upload time. During ingestion, we should calculate the
    // peaks, and store them as a JSON blob in the recording db record.
    const input = new Input({
      formats: ALL_FORMATS,
      source: new UrlSource(this.url),
    })

    this.duration =
      (await input.getDurationFromMetadata()) ?? (await input.computeDuration())
    const audioTrack = await input.getPrimaryAudioTrack()
    if (!audioTrack) {
      throw new Error("no audio track found!")
    }
    const sink = new AudioSampleSink(audioTrack)

    // one peak entry per second
    for (let i = 0; i < this.duration; i++) {
      const peak = { time: i, max: 0, rms: 0, nsm: 0 }
      for await (const sample of sink.samples(i, i + 1)) {
        const bytesNeeded = sample.allocationSize({ format: "f32", planeIndex: 0 })
        const floats = new Float32Array(bytesNeeded / 4)
        sample.copyTo(floats, { format: "f32", planeIndex: 0 })
        sample.close()

        for (let j = 0; j < floats.length; j++) {
          peak.rms += floats[j]! ** 2
          peak.max = Math.max(Math.abs(floats[j]!), peak.max)
        }
        peak.nsm += floats.length
      }
      peak.rms = Math.sqrt(peak.rms / peak.nsm)
      this.peaks.push(peak)

      if (i % 60 == 0) this.draw()
    }
  }

  draw() {
    const ctx = this.ctx
    if (!ctx || !this.canvas) return
    if (this.duration === null) return

    const height = this.canvas.clientHeight
    const width = this.canvas.clientWidth

    ctx.clearRect(0, 0, height, width)

    // draw waveform
    const wave = (peaks: { time: number; v: number }[], maxV: number) => {
      ctx.beginPath()
      const center = height / 2
      ctx.moveTo(0, center)
      const hscale = width / this.duration!
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
      this.peaks.map((p) => ({ time: p.time, v: p.rms * 3 })),
      max,
    )
  }
}
