# media-processing

## Purpose

Hephaestus turns uploaded media into derivatives that consoles can display.

## Requirements

### Requirement: Eager video transcode

Hephaestus SHALL produce a 720p h264 transcode for every video it processes.

#### Scenario: video upload

- **WHEN** a video is processed
- **THEN** a `transcode-720p` derivative is produced

### Requirement: Poster frame

Hephaestus SHALL produce a `poster` derivative (a still frame) for every video.

#### Scenario: poster for video

- **WHEN** a video is processed
- **THEN** a `poster` derivative is produced alongside the transcode
