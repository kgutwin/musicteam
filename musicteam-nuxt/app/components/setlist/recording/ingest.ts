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

export async function audioEncode(file: Blob, progress: (progress: number) => void) {
  const input = new Input({
    source: new BlobSource(file),
    formats: ALL_FORMATS,
  })

  // const { readable, writable } = new TransformStream()

  const outputFormat = new Mp4OutputFormat()
  const outputMimeType = "audio/mp4" // force audio mime type

  const direct = await api.objects.uploadFileDirectPut({
    content_type: outputMimeType,
  })

  const output = new Output({
    format: outputFormat,
    target: new BufferTarget({
      onFinalize: async (buffer) => {
        await fetch(direct.data.url, {
          method: "PUT",
          headers: { "Content-Type": outputMimeType },
          body: buffer,
        })
      },
    }),
  })

  const conversion = await Conversion.init({
    input,
    output,
    audio: {
      codec: "opus",
      // async process(sample: AudioSample): Promise<AudioSample> {
      // },
    },
  })
  conversion.onProgress = progress

  return {
    conversion,
    newRecording: {
      audio_object_id: direct.data.fields.key!,
      audio_object_type: outputMimeType,
    },
  }
}
