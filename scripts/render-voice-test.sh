#!/usr/bin/env bash
set -euo pipefail

mkdir -p output models
VOICE="en_US-libritts_r-medium"
BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium"

curl -fL --retry 3 "$BASE/$VOICE.onnx" -o "models/$VOICE.onnx"
curl -fL --retry 3 "$BASE/$VOICE.onnx.json" -o "models/$VOICE.onnx.json"
curl -fL --retry 3 "$BASE/MODEL_CARD" -o "models/$VOICE.MODEL_CARD"

# Do not use this voice unless its upstream card still confirms CC BY 4.0.
grep -qi "CC BY 4.0" "models/$VOICE.MODEL_CARD"

cat > output/narration.txt <<'EOF'
Welcome to FAST LIVE. The world moves fast, and useful ideas should move faster.
Every day brings new technology, new opportunities, and new ways to think.
Stay curious. Think clearly. Move forward.
EOF

python -m pip install --disable-pip-version-check "piper-tts==1.8.0"
piper --model "models/$VOICE.onnx" --config "models/$VOICE.onnx.json" --output_file output/voiceover.wav < output/narration.txt

test -s output/voiceover.wav
ffprobe -v error -show_entries stream=codec_name,sample_rate,channels -of default=noprint_wrappers=1 output/voiceover.wav

ffmpeg -hide_banner -y \
  -f lavfi -i "color=c=0x101820:s=1080x1920:r=30:d=120" \
  -i output/voiceover.wav \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='FAST LIVE':fontcolor=white:fontsize=104:x=(w-text_w)/2:y=h*0.34,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='IDEAS THAT MOVE YOU FORWARD':fontcolor=0x55D6BE:fontsize=42:x=(w-text_w)/2:y=h*0.43" \
  -c:v libx264 -preset veryfast -pix_fmt yuv420p \
  -c:a aac -b:a 128k -shortest -movflags +faststart \
  output/fastlive-voice-render-test.mp4

test -s output/fastlive-voice-render-test.mp4
ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,duration -of default=noprint_wrappers=1 output/fastlive-voice-render-test.mp4
