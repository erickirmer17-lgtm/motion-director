#!/bin/bash
# encode.sh <frames_dir> <mix.wav> <out.mp4> [fps=60] [poster_frame=last]
# master (CRF 14, 320k AAC, faststart) + a lighter _share copy (CRF 21) for messaging
# + <out>_poster.png, lossless from the frame folder (the last frame unless a frame number is given).
FF=${FFMPEG:-/Users/user/Library/Python/3.9/lib/python/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1}
F="$1"; A="$2"; O="$3"; R="${4:-60}"; P="${5:-last}"
EXT=$(ls "$F" | head -1 | sed 's/.*\.//')
"$FF" -y -v error -framerate "$R" -i "$F/f%04d.$EXT" -i "$A" -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p \
  -profile:v high -movflags +faststart -c:a aac -b:a 320k -shortest "$O"
"$FF" -y -v error -i "$O" -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k "${O%.mp4}_share.mp4"
if [ "$P" = "last" ]; then PF="$F/$(ls "$F" | grep -E "^f[0-9]+\.$EXT$" | sort | tail -1)"; else PF="$F/$(printf 'f%04d' "$P").$EXT"; fi
"$FF" -y -v error -i "$PF" "${O%.mp4}_poster.png" && echo "poster: ${O%.mp4}_poster.png ($(basename "$PF"))"
"$FF" -i "$O" 2>&1 | grep -E "Duration|Stream"
