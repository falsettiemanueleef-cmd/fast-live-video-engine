#!/usr/bin/env bash
set -euo pipefail

OUT="output/short"
VOICE_DIR="assets/voice"
VOICE="en_US-libritts_r-medium"
BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium"
FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

mkdir -p "$OUT" "$VOICE_DIR"
curl -fL "$BASE/$VOICE.onnx" -o "$VOICE_DIR/$VOICE.onnx"
curl -fL "$BASE/$VOICE.onnx.json" -o "$VOICE_DIR/$VOICE.onnx.json"
curl -fL "https://huggingface.co/rhasspy/piper-voices/raw/main/en/en_US/libritts_r/medium/MODEL_CARD" -o "$VOICE_DIR/MODEL_CARD.txt"

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install piper-tts

cat > "$OUT/narration.txt" <<'TEXT'
The world moves fast, and the stories shaping our lives move with it. New ideas cross borders, technology changes how we work, and small decisions can open unexpected doors. Understanding what is happening helps us choose what comes next. Stay curious, look beyond the headlines, and keep moving forward. This is FAST LIVE.
TEXT

.venv/bin/piper --model "$VOICE_DIR/$VOICE.onnx" --config "$VOICE_DIR/$VOICE.onnx.json" --output_file "$OUT/voiceover.wav" < "$OUT/narration.txt"
DURATION="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT/voiceover.wav")"
SEGMENT="$(awk -v d="$DURATION" 'BEGIN { printf "%.3f", d/4 }')"

# Four original motion-graphic scenes. No stock footage or third-party visual assets.
make_scene() {
  local index="$1" title="$2" subtitle="$3" bg="$4"
  local start
  start="$(awk -v n="$index" -v s="$SEGMENT" 'BEGIN { printf "%.3f", n*s }')"
  ffmpeg -hide_banner -loglevel error -y \
    -f lavfi -i "color=c=$bg:s=1080x1920:r=30:d=$SEGMENT" \
    -vf "drawbox=x=70:y=250:w=940:h=1420:color=white@0.045:t=3,drawbox=x=70:y=250:w=14:h=1420:color=0x55D6BE@0.95:t=fill,drawtext=fontfile=$FONT_BOLD:text='FAST LIVE':fontcolor=0x55D6BE:fontsize=44:x=100:y=310,drawtext=fontfile=$FONT_BOLD:text='$title':fontcolor=white:fontsize=52:line_spacing=18:x=(w-text_w)/2+sin(t*1.2)*8:fix_bounds=true:y=h*0.43:box=1:boxcolor=black@0.08:boxborderw=24,drawtext=fontfile=$FONT_REG:text='$subtitle':fontcolor=0xD9E4EA:fontsize=38:x=(w-text_w)/2:y=h*0.59,drawtext=fontfile=$FONT_REG:text='STAY CURIOUS  •  LIVE FAST':fontcolor=white@0.65:fontsize=28:x=(w-text_w)/2:y=h-230" \
    -t "$SEGMENT" -an -c:v libx264 -preset veryfast -pix_fmt yuv420p "$OUT/scene-$index.mp4"
}

make_scene 0 "THE WORLD MOVES FAST" "The stories shaping our lives move with it." "0x101820"
make_scene 1 "IDEAS CROSS BORDERS" "Technology changes how we work and connect." "0x172A3A"
make_scene 2 "UNDERSTANDING MATTERS" "Knowledge helps us choose what comes next." "0x202B35"
make_scene 3 "KEEP MOVING FORWARD" "Fresh perspectives. One world. FAST LIVE." "0x132B2B"

cat > "$OUT/scenes.txt" <<'LIST'
file 'scene-0.mp4'
file 'scene-1.mp4'
file 'scene-2.mp4'
file 'scene-3.mp4'
LIST
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$OUT/scenes.txt" -i "$OUT/voiceover.wav" \
  -map 0:v:0 -map 1:a:0 -shortest -c:v copy -c:a aac -b:a 160k -movflags +faststart \
  "$OUT/fastlive-four-scene-short.mp4"

# Fail if the final file is not a portrait video with both audio and video streams.
test -s "$OUT/fastlive-four-scene-short.mp4"
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height -of csv=p=0 "$OUT/fastlive-four-scene-short.mp4"
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of csv=p=0 "$OUT/fastlive-four-scene-short.mp4"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT/fastlive-four-scene-short.mp4"
