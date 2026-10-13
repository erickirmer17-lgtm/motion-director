"""sfx_scan.py — decode candidate SFX, measure features, draw a spectrogram contact sheet.
usage: python3 sfx_scan.py out.jpg file1 file2 ...   (prints a table)"""
import sys, subprocess, numpy as np, os
from PIL import Image, ImageDraw, ImageFont
FF=os.environ.get('FFMPEG','/Users/user/Library/Python/3.9/lib/python/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1')
def load(p, sr=44100):
    r=subprocess.run([FF,'-v','error','-i',p,'-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True)
    return np.frombuffer(r.stdout,np.float32), sr
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',12)
out=sys.argv[1]; files=sys.argv[2:]
tiles=[]
for p in files:
    x,sr=load(p)
    if len(x)<10: print('FAIL',p); continue
    dur=len(x)/sr; pk=np.max(np.abs(x))+1e-9
    env=np.sqrt(np.convolve(x**2,np.ones(441)/441,'same'))
    tpk=np.argmax(env)/sr
    # spectral centroid over the loud part
    n=2048; seg=x[max(0,int(tpk*sr)-n//2):int(tpk*sr)+n//2]
    if len(seg)<n: seg=np.pad(seg,(0,n-len(seg)))
    S=np.abs(np.fft.rfft(seg*np.hanning(n))); f=np.fft.rfftfreq(n,1/sr); cen=float((S*f).sum()/(S.sum()+1e-9))
    rms_db=20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
    print(f"{dur:6.2f}s peak@{tpk:5.2f}s cent={cen:6.0f}Hz rms={rms_db:6.1f}dB  {os.path.basename(p)}")
    # spectrogram tile
    hop=256; frames=max(1,(len(x)-n)//hop); frames=min(frames,600)
    hop=max(1,(len(x)-n)//frames) if frames>0 else hop
    spec=np.array([np.abs(np.fft.rfft(x[i*hop:i*hop+n]*np.hanning(n)))[:600] if i*hop+n<=len(x) else np.zeros(600) for i in range(frames)]).T
    spec=20*np.log10(spec+1e-6); spec=np.clip((spec+20)/80,0,1)
    im=Image.fromarray((255*(1-spec[::-1])).astype(np.uint8)).resize((300,90)).convert('RGB')
    t=Image.new('RGB',(300,128),'white'); t.paste(im,(0,0)); d=ImageDraw.Draw(t)
    wv=np.abs(x[::max(1,len(x)//300)][:300])/pk
    for i,v in enumerate(wv): d.line([(i,108-int(v*16)),(i,108)],fill=(40,40,200))
    d.text((2,112),f"{os.path.basename(p)[:44]} {dur:.2f}s",fill=(200,0,0),font=font)
    tiles.append(t)
cols=5; rows=(len(tiles)+cols-1)//cols
s=Image.new('RGB',(cols*300,rows*128),'white')
for i,t in enumerate(tiles): s.paste(t,((i%cols)*300,(i//cols)*128))
s.save(out,quality=85)
