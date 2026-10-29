package hephaestus

/** The derivative vocabulary. The wire token is what producers put in `want`. */
enum DerivativeKind(val token: String):
  case Thumb extends DerivativeKind("thumb")
  case Sample extends DerivativeKind("sample")
  /** 720p h264 MP4, produced for video media only. */
  case Transcode extends DerivativeKind("transcode-720p")

object DerivativeKind:
  def fromToken(t: String): Option[DerivativeKind] =
    DerivativeKind.values.find(_.token == t)
