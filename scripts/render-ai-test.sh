#!/usr/bin/env bash
set -euo pipefail

OUT="output"
VOICE_DIR="assets/voice"
VOICE="en_US-libritts_r-medium"
BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium"
mkdir -p "$OUT" "$VOICE_DIR"

# Fetch the model, its configuration, and the upstream model card for review/attribution.
curl -fL "$BASE/$VOICE.onnx" -o "$VOICE_DIR/$VOICE.onnx"
curl -fL "$BASE/$VOICE.onnx.json" -o "$VOICE_DIR/$VOICE.onnx.json"
curl -fL "https://huggingface.co/rhasspy/piper-voices/raw/main/en/en_US/libritts_r/medium/MODEL_CARD" -o "$VOICE_DIR/MODEL_CARD.txt"

python -m pip install --user --upgrade pip
python -m pip install --user piper-tts
export PATH="$HOME/.local/bin:$PATH"

cat > "$OUT/narration.txt" <<'TEXT'
The world moves fast. Ideas travel farther when they are clear, useful, and made to be shared. FAST LIVE brings you concise stories, practical insights, and fresh perspectives from around the world. Stay curious. Stay informed. Live fast.
TEXT

piper --model "$VOICE_DIR/$VOICE.onnx" --config "$VOICE_DIR/$VOICE.onnx.json" --output_file "$OUT/voiceover.wav" < "$OUT/narration.txt"

# Fit a simple vertical visual to the exact narration duration.
DURATION="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT/voiceover.wav")"
ffmpeg -hide_banner -y \
  -f lavfi -i "color=c=0x101820:s=1080x1920:r=30" \
  -i "$OUT/voiceover.wav" \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='FAST LIVE':fontcolor=white:fontsize=100:x=(w-text_w)/2:y=h*0.40,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='GLOBAL STORIES  •  FRESH PERSPECTIVES':fontcolor=0x55D6BE:fontsize=38:x=(w-text_w)/2:y=h*0.53" \
  -map 0:v:0 -map 1:a:0 -t "$DURATION" \
  -c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 160k -shortest -movflags +faststart \
  "$OUT/fastlive-voiceover-test.mp4"

ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height -of default=noprint_wrappers=1 "$OUT/fastlive-voiceover-test.mp4"
