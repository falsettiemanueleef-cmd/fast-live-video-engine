#!/usr/bin/env bash
set -euo pipefail
mkdir -p output
ffmpeg -hide_banner -y \
  -f lavfi -i "color=c=0x101820:s=1080x1920:d=15:r=30" \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='FAST LIVE':fontcolor=white:fontsize=92:x=(w-text_w)/2:y=(h-text_h)/2-90,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='CLOUD RENDER TEST':fontcolor=0x55D6BE:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2+45" \
  -c:v libx264 -pix_fmt yuv420p -movflags +faststart \
  output/fastlive-cloud-test.mp4
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 output/fastlive-cloud-test.mp4
