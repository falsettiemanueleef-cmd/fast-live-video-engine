from __future__ import annotations
import argparse, json, os, shutil, subprocess, tempfile, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG = (8, 8, 10)
WHITE = (247, 247, 247)
RED = (239, 55, 42)
MUTED = (185, 185, 190)


def font(size: int, bold: bool = False):
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_width):
    words, lines, current = text.split(), [], ''
    for word in words:
        test = (current + ' ' + word).strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
            current = test
        else:
            if current: lines.append(current)
            current = word
    if current: lines.append(current)
    return lines


def draw_scene(title, en, it, index, total, out_path):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    # Minimal cinematic red accent and brand marker.
    d.rounded_rectangle((72, 100, 1008, 112), radius=6, fill=(48, 48, 52))
    d.rounded_rectangle((72, 100, int(72 + 936 * index / max(total, 1)), 112), radius=6, fill=RED)
    d.text((76, 170), 'FAST', font=font(42, True), fill=WHITE)
    d.text((205, 170), 'LIVE', font=font(42, True), fill=RED)
    d.text((76, 300), title.upper(), font=font(34, True), fill=MUTED)
    en_font, it_font = font(76, True), font(48, False)
    y = 610
    for line in wrap(d, en, en_font, 900):
        d.text((76, y), line, font=en_font, fill=WHITE, stroke_width=1, stroke_fill=(20,20,20))
        y += 104
    y += 90
    d.rounded_rectangle((76, y, 1004, y + 8), radius=4, fill=RED)
    y += 65
    for line in wrap(d, it, it_font, 900):
        d.text((76, y), line, font=it_font, fill=(220, 220, 224))
        y += 72
    d.text((76, 1780), 'AI • PRODUCTIVITY • DIGITAL SKILLS', font=font(25, True), fill=MUTED)
    d.text((930, 1780), f'{index:02d}/{total:02d}', font=font(25, True), fill=RED)
    im.save(out_path, quality=95)


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    ap = argparse.ArgumentParser(description='Render a FAST LIVE bilingual vertical short.')
    ap.add_argument('brief', help='Path to JSON brief')
    ap.add_argument('--output', default='fast-live-short.mp4')
    args = ap.parse_args()
    brief = json.loads(Path(args.brief).read_text(encoding='utf-8'))
    scenes = brief.get('scenes', [])
    if not scenes: raise SystemExit('The brief must contain at least one scene.')
    if not shutil.which('ffmpeg') or not shutil.which('espeak-ng'):
        raise SystemExit('ffmpeg and espeak-ng must be installed.')
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        clips = []
        for i, scene in enumerate(scenes, 1):
            image = tmp / f'scene_{i:02d}.png'
            audio = tmp / f'scene_{i:02d}.wav'
            clip = tmp / f'scene_{i:02d}.mp4'
            narration = scene.get('narration') or scene.get('en') or ''
            if not narration.strip(): raise SystemExit(f'Scene {i} has no narration.')
            draw_scene(brief.get('title', 'FAST LIVE'), scene.get('en', ''), scene.get('it', ''), i, len(scenes), image)
            run(['espeak-ng', '-v', brief.get('voice_language', 'en'), '-s', '148', '-w', str(audio), narration])
            run(['ffmpeg', '-y', '-loop', '1', '-i', str(image), '-i', str(audio), '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '128k', '-pix_fmt', 'yuv420p', '-shortest', '-vf', 'scale=1080:1920,fps=30,format=yuv420p', str(clip)])
            clips.append(clip)
        concat = tmp / 'concat.txt'
        concat.write_text(''.join(f"file '{p.as_posix()}'\n" for p in clips), encoding='utf-8')
        run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat), '-c', 'copy', '-movflags', '+faststart', args.output])
    print(f'Render complete: {args.output}')

if __name__ == '__main__':
    main()
