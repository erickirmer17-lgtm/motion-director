"""elevenlabs.py — music + SFX generation (key read from System/API KEYS.txt, never printed).

  python3 elevenlabs.py music out.mp3 --prompt "..." --ms 15000
  python3 elevenlabs.py music out.mp3 --plan plan.json           # composition_plan (sections with durations)
  python3 elevenlabs.py sfx jobs.json outdir/                     # [["name","prompt",seconds,prompt_influence], ...]
  python3 elevenlabs.py quota                                     # plan + characters used / limit (credits)

Notes (validated 2026-10):
- music/compose honours tempo words ("112 BPM") well; free prompts tend to fade early.
  A composition_plan with section durations holds a structure, but can come back thin (kick-only);
  the best result so far: rich free-prompt track, then re-cut on its own bar grid with mixer.Mixer.music(bars=...).
- sound-generation: duration_seconds 0.5 … 30 (0.4 errors). One variation per call — run jobs in parallel.
"""
import sys, json, re, os, urllib.request, concurrent.futures as cf

KEYFILE = os.environ.get('MD_API_KEYS_FILE', '/Users/user/Documents/Claude Opp./System/API KEYS.txt')


def key():
    if os.environ.get('ELEVENLABS_API_KEY'): return os.environ['ELEVENLABS_API_KEY']
    if not os.path.exists(KEYFILE): raise SystemExit('set ELEVENLABS_API_KEY (or MD_API_KEYS_FILE)')
    for line in open(KEYFILE):
        if line.startswith('ELEVENLABS'):
            m = re.search(r'(sk_[A-Za-z0-9]+)', line)
            if m: return m.group(1)
    raise SystemExit('ElevenLabs key not found in API KEYS.txt')


def post(url, body, out):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'xi-api-key': key(), 'Content-Type': 'application/json'})
    try:
        d = urllib.request.urlopen(req, timeout=300).read()
        open(out, 'wb').write(d); return f'ok {out} {len(d)}'
    except urllib.error.HTTPError as e:
        return f'ERR {out} {e.code} {e.read()[:300]}'


def music(out, prompt=None, ms=15000, plan=None):
    body = {'composition_plan': json.load(open(plan))} if plan else {'prompt': prompt, 'music_length_ms': ms}
    print(post('https://api.elevenlabs.io/v1/music/compose', body, out))


def sfx(jobs, outdir):
    os.makedirs(outdir, exist_ok=True)
    def one(j):
        name, text, dur, pi = j
        return post('https://api.elevenlabs.io/v1/sound-generation',
                    {'text': text, 'duration_seconds': max(0.5, float(dur)), 'prompt_influence': pi}, f'{outdir}/{name}.mp3')
    with cf.ThreadPoolExecutor(4) as ex:
        for r in ex.map(one, jobs): print(r)


def quota():
    req = urllib.request.Request('https://api.elevenlabs.io/v1/user/subscription', headers={'xi-api-key': key()})
    try: d = json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        print(f'quota unavailable ({e.code}): this key probably lacks the user_read scope; check elevenlabs.io → Subscription'); return
    print(f"tier {d.get('tier')}  used {d.get('character_count')} / {d.get('character_limit')}  resets {d.get('next_character_count_reset_unix')}")


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'quota': quota()
    if mode == 'music':
        args = sys.argv[2:]; out = args[0]
        p = args[args.index('--prompt') + 1] if '--prompt' in args else None
        ms = int(args[args.index('--ms') + 1]) if '--ms' in args else 15000
        plan = args[args.index('--plan') + 1] if '--plan' in args else None
        music(out, p, ms, plan)
    elif mode == 'sfx':
        sfx(json.load(open(sys.argv[2])), sys.argv[3])
