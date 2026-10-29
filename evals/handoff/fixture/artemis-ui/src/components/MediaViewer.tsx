import { Media, derivativeUrl } from "../lib/media";

type Props = { media: Media };

// Renders a post's media. Images show the sample derivative; videos play
// the 720p h264 transcode produced by Hephaestus.
export function MediaViewer({ media }: Props) {
  if (media.kind === "video") {
    const src = derivativeUrl(media, "transcode-720p");
    return (
      <video controls preload="metadata" poster={derivativeUrl(media, "thumb")}>
        <source src={src} type="video/mp4" />
      </video>
    );
  }
  return <img src={derivativeUrl(media, "sample")} alt={media.title} />;
}
