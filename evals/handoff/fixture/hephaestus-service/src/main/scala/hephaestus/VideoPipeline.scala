package hephaestus

/** Produces every requested derivative for one video. */
final class VideoPipeline(ffmpeg: Ffmpeg, store: BlobStore):

  def run(req: DerivativeRequest): Unit =
    req.want.flatMap(DerivativeKind.fromToken).foreach {
      case DerivativeKind.Thumb     => store.put(req.id, "thumb", ffmpeg.frameAt(req.blob, 1.0))
      case DerivativeKind.Sample    => store.put(req.id, "sample", ffmpeg.scale(req.blob, 1280))
      case DerivativeKind.Transcode => store.put(req.id, "transcode-720p", ffmpeg.h264(req.blob, 720))
    }
