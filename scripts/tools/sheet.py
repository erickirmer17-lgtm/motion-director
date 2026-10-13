import sys,glob
from PIL import Image, ImageDraw, ImageFont
d=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3]); step=int(sys.argv[4]); out=sys.argv[5]
cols=int(sys.argv[6]) if len(sys.argv)>6 else 10
fs=[f"{d}/f{i:04d}.jpg" for i in range(a,b+1,step)]
ims=[Image.open(f) for f in fs]
tw=216; th=int(ims[0].height*tw/ims[0].width)
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',14)
rows=(len(ims)+cols-1)//cols
s=Image.new('RGB',(cols*tw,rows*th),'white')
for k,(f,im) in enumerate(zip(range(a,b+1,step),ims)):
    t=im.resize((tw,th)); ImageDraw.Draw(t).text((3,3),str(f),fill=(255,0,0),font=font)
    ImageDraw.Draw(t).rectangle([0,0,tw-1,th-1],outline=(200,200,200))
    s.paste(t,((k%cols)*tw,(k//cols)*th))
s.save(out,quality=88)
