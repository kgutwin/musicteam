import {
  Input,
  ALL_FORMATS,
  BlobSource,
  Output,
  BufferTarget,
  FlacOutputFormat,
  canEncodeAudio,
  Conversion,
  AudioSample,
} from "mediabunny"
import { registerFlacEncoder } from "@mediabunny/flac-encoder"
import { api } from "@/services"

export async function flacEncode(file: Blob, progress: (progress: number) => void) {
  const contentType = "audio/flac"

  if (!(await canEncodeAudio("flac"))) {
    registerFlacEncoder()
  }

  const input = new Input({
    source: new BlobSource(file),
    formats: ALL_FORMATS,
  })

  // const { readable, writable } = new TransformStream()

  const direct = await api.objects.uploadFileDirectPut({ content_type: contentType })

  const output = new Output({
    format: new FlacOutputFormat(),
    target: new BufferTarget({
      onFinalize: async (buffer) => {
        await fetch(direct.data.url, {
          method: "PUT",
          headers: { "Content-Type": contentType },
          body: buffer,
        })
      },
    }),
  })

  const conversion = await Conversion.init({
    input,
    output,
    audio: {
      // async process(sample: AudioSample): Promise<AudioSample> {
      // },
    },
  })
  conversion.onProgress = progress

  await conversion.execute()
  await output.finalize()

  // const response =

  // const direct = await api.objects.uploadFileDirect({ content_type: contentType })
  //
  // const formData = new FormData()
  // for (const field in direct.data.fields) {
  //   if (direct.data.fields[field]) formData.append(field, direct.data.fields[field])
  // }
  // formData.append("file", file)
  //
  // const response = await fetch(direct.data.url, { method: "POST", body: formData })

  const mediaObjectId = direct.data.fields.key

  return mediaObjectId
}
