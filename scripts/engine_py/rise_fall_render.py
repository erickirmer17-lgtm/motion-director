"""usage:
  python3 render.py sheet  <scale> <out.jpg> [f0 f1 step]   — contact sheet of frames
  python3 render.py frames <scale> <outdir> f0 f1           — individual jpgs
  python3 render.py video  <scale> <out.mp4> [workers] [mb]  — full render piped to ffmpeg (silent)
"""
import sys, os, time, subprocess
import numpy as np, cv2
from multiprocessing import Pool

FF = '/Users/user/Library/Python/3.9/lib/python/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
_SCALE = None; _MB = None


def _init(scale, mb):
    global _SCALE, _MB
    import core
    core.init(scale); _SCALE = scale; _MB = mb


def _work(f):
    import shots
    return f, shots.render_frame(f, _MB)


def main():
    mode, scale = sys.argv[1], float(sys.argv[2]); out = sys.argv[3]
    import core
    core.init(scale)
    if mode in ('sheet', 'frames'):
        f0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        f1 = int(sys.argv[5]) if len(sys.argv) > 5 else core.NF - 1
        step = int(sys.argv[6]) if len(sys.argv) > 6 else 1
        frames = list(range(f0, f1 + 1, step))
        with Pool(min(10, len(frames)), initializer=_init, initargs=(scale, None)) as pool:
            res = dict(pool.imap_unordered(_work, frames))
        if mode == 'frames':
            os.makedirs(out, exist_ok=True)
            for f in frames:
                cv2.imwrite(f'{out}/f{f:03d}.jpg', cv2.cvtColor(res[f], cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
            return
        tiles = []
        for f in frames:
            im = cv2.cvtColor(res[f], cv2.COLOR_RGB2BGR).copy()
            cv2.putText(im, f'f{f}', (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            tiles.append(im)
        cols = 6
        while len(tiles) % cols:
            tiles.append(np.zeros_like(tiles[0]))
        rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
        cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
        return
    if mode == 'video':
        workers = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        mb = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5] != 'x' else None
        W, H = core.W, core.H
        cmd = [FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24000/1001', '-i', '-',
               '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-tune', 'grain', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        with Pool(workers, initializer=_init, initargs=(scale, mb)) as pool:
            for i, (f, img) in enumerate(pool.imap(_work, range(core.NF), chunksize=1)):
                p.stdin.write(img.tobytes())
                if i % 24 == 0:
                    print(f'frame {f}/{core.NF}  {time.time() - t0:.0f}s', flush=True)
        p.stdin.close(); p.wait()
        print('done', out, f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
