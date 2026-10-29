package artemis

import hephaestus.client.{DerivativeRequest, HephaestusClient}

final class UploadService(hephaestus: HephaestusClient, store: MediaStore):

  /** Derivatives requested for every upload, image or video. */
  private val want = List("thumb", "sample")

  def onUpload(media: Media): Unit =
    store.save(media)
    hephaestus.request(DerivativeRequest(media.id, media.blobRef, want))

  /** Re-runs derivative generation for existing media (same list). */
  def reprocess(media: Media): Unit =
    hephaestus.request(DerivativeRequest(media.id, media.blobRef, want))
