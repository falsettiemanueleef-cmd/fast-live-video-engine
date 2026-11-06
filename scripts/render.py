from __future__ import annotations
import argparse, json, os, shutil, subprocess, tempfile, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 720, 1280, 15
BG=(7,8,12); WHITE=(248,248,250); RED=(242,54,39); MUTED=(165,169,180)

def font(size, bold=False):
    paths=[
      '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
      '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, width):
    lines=[]; cur=''
    for word in text.split():
        test=(cur+' '+word).strip()
        if draw.textbbox((0,0),test,font=fnt)[2] <= width: cur=test
        else:
            if cur: lines.append(cur)
            cur=word
    if cur: lines.append(cur)
    return lines

def run(cmd):
    subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

def render_frame(scene, title, idx, total, frame, frames, out):
    t=frame/max(frames,1)
    im=Image.new('RGB',(W,H),BG)
    # Atmospheric vertical gradient and animated glow.
    px=im.load()
    for y in range(H):
        v=int(9+8*(1-y/H))
        for x in range(W):
            px[x,y]=(v, v, min(22,v+8))
    glow=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    cx=int(W*(0.76-0.22*t)); cy=int(H*(0.28+0.12*math.sin(t*math.pi*2)))
    radius=int(230+22*math.sin(t*math.pi*2))
    gd.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=(220,32,24,30))
    glow=glow.filter(ImageFilter.GaussianBlur(85)); im=Image.alpha_composite(im.convert('RGBA'),glow)
    d=ImageDraw.Draw(im)
    # Fine grid and drifting particles.
    for x in range(28,W,56): d.line((x,0,x,H),fill=(255,255,255,8),width=1)
    for y in range(20,H,56): d.line((0,y,W,y),fill=(255,255,255,7),width=1)
    for j in range(18):
        x=int((j*97+frame*2.2)%W); y=int((j*173+frame*1.1)%H)
        d.ellipse((x,y,x+3,y+3),fill=(255,75,58,100))
    # Animated orbital rings.
    d.arc((cx-150,cy-150,cx+150,cy+150),start=int(frame*3)%360,end=int(frame*3)%360+235,fill=(242,54,39,150),width=3)
    d.arc((cx-190,cy-190,cx+190,cy+190),start=int(-frame*2)%360,end=int(-frame*2)%360+160,fill=(255,255,255,45),width=2)
    # Header and progress.
    d.text((48,54),'FAST',font=font(31,True),fill=WHITE)
    d.text((143,54),'LIVE',font=font(31,True),fill=RED)
    d.text((W-170,64),'IDEAS IN MOTION',font=font(12,True),fill=MUTED)
    d.rounded_rectangle((48,112,W-48,119),radius=4,fill=(55,57,65))
    d.rounded_rectangle((48,112,48+int((W-96)*(idx/total)),119),radius=4,fill=RED)
    # Oversized scene index as a visual anchor.
    d.text((46,210),f'{idx:02d}',font=font(118,True),fill=(255,255,255,22),stroke_width=1,stroke_fill=(242,54,39,90))
    # Text block with a subtle entrance.
    title_y=440
    en=scene.get('en','')
    en_font=font(48,True)
    lines=wrap(d,en,en_font,610)
    line_h=62
    total_h=len(lines)*line_h
    y=title_y+(1-t)*24
    for line in lines:
        d.text((50,int(y)),line,font=en_font,fill=WHITE,stroke_width=1,stroke_fill=(10,10,12))
        y+=line_h
    y+=28
    d.rounded_rectangle((50,int(y),W-50,int(y)+6),radius=3,fill=RED)
    y+=34
    it_font=font(29,False)
    for line in wrap(d,scene.get('it',''),it_font,610):
        d.text((50,int(y)),line,font=it_font,fill=(205,208,216))
        y+=42
    # Footer.
    d.text((50,H-76),'AI  /  PRODUCTIVITY  /  DIGITAL SKILLS',font=font(14,True),fill=MUTED)
    d.text((W-105,H-76),f'{idx}/{total}',font=font(15,True),fill=RED)
    im.convert('RGB').save(out,quality=90)

def main():
    ap=argparse.ArgumentParser(description='Render an animated bilingual FAST LIVE vertical short.')
    ap.add_argument('brief'); ap.add_argument('--output',default='fast-live-short.mp4')
    args=ap.parse_args()
    brief=json.loads(Path(args.brief).read_text(encoding='utf-8'))
    scenes=brief.get('scenes',[])
    if not scenes: raise SystemExit('The brief must contain at least one scene.')
    if not shutil.which('ffmpeg') or not shutil.which('espeak-ng') or not shutil.which('ffprobe'):
        raise SystemExit('ffmpeg, ffprobe and espeak-ng must be installed.')
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td); clips=[]
        for i,scene in enumerate(scenes,1):
            narration=(scene.get('narration') or scene.get('en') or '').strip()
            if not narration: raise SystemExit(f'Scene {i} has no narration.')
            audio=tmp/f'audio_{i:02d}.wav'; clip=tmp/f'scene_{i:02d}.mp4'
            run(['espeak-ng','-v',brief.get('voice_language','en'),'-s',str(brief.get('voice_speed',165)),'-p','38','-a','175','-w',str(audio),narration])
            probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(audio)],text=True)
            duration=float(probe.strip())+0.45
            frames=max(45,math.ceil(duration*FPS))
            frame_dir=tmp/f'frames_{i:02d}'; frame_dir.mkdir()
            for n in range(frames):
                render_frame(scene,brief.get('title','FAST LIVE'),i,len(scenes),n,frames,frame_dir/f'frame_{n:04d}.jpg')
            run(['ffmpeg','-y','-framerate',str(FPS),'-i',str(frame_dir/'frame_%04d.jpg'),'-i',str(audio),'-t',f'{duration:.3f}','-vf','scale=1080:1920:flags=lanczos,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','21','-c:a','aac','-b:a','128k','-shortest',str(clip)])
            clips.append(clip)
        concat=tmp/'concat.txt'
        concat.write_text(''.join(f"file '{p.as_posix()}'\\n" for p in clips),encoding='utf-8')
        run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',args.output])
    print(f'Render complete: {args.output}')

if __name__=='__main__': main()
