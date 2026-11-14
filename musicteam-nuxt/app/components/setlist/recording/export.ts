import {
  Input,
  UrlSource,
  ALL_FORMATS,
  Output,
  Mp4OutputFormat,
  BufferTarget,
  Conversion,
} from "mediabunny"

export async function trimRecording(
  url: string,
  start: number,
  end: number | undefined,
) {
  const input = new Input({
    source: new UrlSource(url),
    formats: ALL_FORMATS,
  })

  const output = new Output({
    format: new Mp4OutputFormat(),
    target: new BufferTarget(),
  })

  const conversion = await Conversion.init({
    input,
    output,
    trim: { start, end },
  })

  if (!conversion.isValid) {
    for (const track of conversion.discardedTracks) {
      if (track.reason === "no_encodable_target_codec") {
        throw new Error(
          `This web browser doesn't support encoding to the target codec.`,
        )
      } else if (track.reason === "unknown_source_codec") {
        throw new Error(
          `This web browser doesn't know the codec of the source recording.`,
        )
      } else if (track.reason === "undecodable_source_codec") {
        throw new Error(
          `This web browser can't decode the codec of the source recording.`,
        )
      }
    }
    console.error(conversion.discardedTracks)
    throw new Error("Sorry, could not prepare mark for download")
  }

  await conversion.execute()

  return output.target.buffer
}
