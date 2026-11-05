import {
  Input,
  ALL_FORMATS,
  BlobSource,
  Output,
  BufferTarget,
  canEncodeAudio,
  Conversion,
  AudioSample,
  Mp4OutputFormat,
} from "mediabunny"
import { api } from "@/services"

import type { AudioPeak } from "./waveform"

export async function audioEncode(
  file: Blob,
  progress: (progress: number, processedTime: number) => void,
) {
  const input = new Input({
    source: new BlobSource(file),
    formats: ALL_FORMATS,
  })

  const duration =
    (await input.getDurationFromMetadata()) ?? (await input.computeDuration())

  const outputFormat = new Mp4OutputFormat()
  const outputMimeType = "audio/mp4" // force audio mime type

  const direct = await api.objects.uploadFileDirectPut({
    content_type: outputMimeType,
  })

  const output = new Output({
    format: outputFormat,
    target: new BufferTarget({
      onFinalize: async (buffer) => {
        progress(0.99, -1) // how to signal upload progress - negative second arg
        await fetch(direct.data.url, {
          method: "PUT",
          headers: { "Content-Type": outputMimeType },
          body: buffer,
        })

        // I'm skipping this for now, simply because while it "worked", it didn't
        // achieve what I wanted, which was showing upload progress. I'm not going
        // to troubleshoot it now because I'm still only in local dev and the
        // progress may simply be going past too fast.
        // const xhr = new XMLHttpRequest()
        // return new Promise((resolve, reject) => {
        //   xhr.onload = () => resolve()
        //   xhr.onerror = () => reject(xhr.response ?? new Error("Network error"))
        //   xhr.onabort = () => reject(new Error("Cancelled"))
        //   xhr.upload.addEventListener("progress", (e) =>
        //     progress(e.loaded / e.total, -1),
        //   )
        //   xhr.open("PUT", direct.data.url)
        //   xhr.setRequestHeader("Content-Type", outputMimeType)
        //   xhr.send(buffer)
        // })
      },
    }),
  })

  const peaks: AudioPeak[] = []
  let partial = { time: 0, max: 0, rms: 0, nsm: 0 }

  const conversion = await Conversion.init({
    input,
    output,
    audio: {
      codec: "opus",
      process(sample: AudioSample): AudioSample {
        // we're not actually changing the audio data, we are instead just
        // parsing it to get the waveform info
        const lastPeakTime = peaks.length > 0 ? peaks[peaks.length - 1]!.time : 0
        if (Math.floor(partial.time) > Math.floor(lastPeakTime)) {
          partial.rms = Math.sqrt(partial.rms / partial.nsm)
          peaks.push(partial)
          partial = { time: partial.time, max: 0, rms: 0, nsm: 0 }
        }

        const bytesNeeded = sample.allocationSize({ format: "f32", planeIndex: 0 })
        const floats = new Float32Array(bytesNeeded / 4)
        sample.copyTo(floats, { format: "f32", planeIndex: 0 })

        for (let i = 0; i < floats.length; i++) {
          partial.rms += floats[i]! ** 2
          partial.max = Math.max(Math.abs(floats[i]!), partial.max)
        }
        partial.nsm += floats.length
        partial.time += sample.duration

        return sample
      },
    },
  })
  conversion.onProgress = progress

  // fixme: "Error: Cannot execute this conversion because its output configuration is invalid. Make sure to always check the isValid field before executing a conversion. Due to discarded tracks, this conversion could not be executed. Tracks were discarded because your environment is not able to encode 'opus' with the provided parameters."

  return {
    conversion,
    peaks,
    newRecording: {
      object_id: direct.data.fields.key!,
      object_type: outputMimeType,
      duration,
    },
  }
}
