#!/usr/bin/env python3
"""Arma el video final de Elielle Detalles: caja de regalo $600."""
import os, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 720, 1280, 30
BURG = (122, 42, 74)
CREAM = (251, 243, 239)
os.chdir(S)
os.makedirs('build', exist_ok=True)

# ---------- linea de tiempo del video ----------
# (archivo, inicio, fin, velocidad)
SEGS = [
    ('armado.mp4', 2.0, 8.0, 1.0),    # intro + caja vacia
    ('armado.mp4', 8.0, 20.0, 2.0),   # relleno
    ('armado.mp4', 22.0, 30.0, 1.25), # mascarilla
    ('armado.mp4', 30.0, 38.0, 1.25), # pinza flor
    ('armado.mp4', 38.0, 48.0, 1.5),  # parches
    ('armado.mp4', 48.0, 56.0, 1.25), # collar y aretes
    ('final.mp4', 0.0, 11.42, 1.0),   # resultado final
]
OUTRO = 3.6
seg_start = []
t = 0
for f, a, b, sp in SEGS:
    seg_start.append(t)
    t += (b - a) / sp
MAIN_END = t
TOTAL = MAIN_END + OUTRO
print('segment starts', [round(x, 2) for x in seg_start], 'main end', round(MAIN_END, 2), 'total', round(TOTAL, 2))

# ---------- narracion: (inicio en voz1, fin, momento en el video, subtitulos) ----------
VO = [
    (0.00, 4.62, 0.45, ['¡Hola! Hoy te enseño', 'cómo armamos esta', 'linda caja de regalo']),
    (6.10, 10.80, seg_start[1] + 0.3, ['Primero, llenamos la caja', 'con papel picado rosado,', 'bien esponjoso']),
    (12.45, 15.62, seg_start[2] + 0.5, ['Luego colocamos una', 'mascarilla facial hidratante']),
    (17.05, 20.17, seg_start[3] + 0.5, ['Agregamos una pinza para', 'el cabello en forma de flor']),
    (21.50, 24.10, seg_start[4] + 0.6, ['Después, unos parches', 'para los ojos']),
    (25.24, 29.60, seg_start[5] + 0.3, ['Y para completar, un set', 'de collar y aretes', 'de acero inoxidable']),
    (30.72, 34.94, seg_start[6] + 0.4, ['¡Y así queda!', 'Perfecta para sorprender', 'a quien más quieres']),
    (35.63, 38.27, seg_start[6] + 5.6, ['Llévatela por solo', '600 pesos']),
    (39.15, 41.10, MAIN_END + 0.5, ['¡Escríbenos y', 'haz tu pedido!']),
]
for a, b, at, _ in VO:
    assert at + (b - a) <= TOTAL, (a, at)

# ---------- logo ----------
logo = Image.open('logo.png').convert('RGB')
badge = logo.crop((420, 560, 1740, 1660)).convert('RGBA')  # 1320x1100
bw0, bh0 = badge.size
mask = Image.new('L', badge.size, 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw0 - 1, bh0 - 1), radius=110, fill=255)
badge.putalpha(mask)

BIG_W = 640
SMALL_W = 150
MARGIN = 20
big_pos = ((W - BIG_W) / 2, (H - BIG_W * bh0 / bw0) / 2 - 40)
small_pos = (W - MARGIN - SMALL_W, MARGIN + 6)
WM_ALPHA = 0.88

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def badge_at(width, alpha):
    h = round(width * bh0 / bw0)
    b = badge.resize((round(width), h), Image.LANCZOS)
    if alpha < 1:
        a = b.getchannel('A').point(lambda v: int(v * alpha))
        b.putalpha(a)
    return b

def shadow_for(b, radius=6, opacity=0.35):
    sh = Image.new('RGBA', (b.width + radius * 4, b.height + radius * 4), (0, 0, 0, 0))
    m = b.getchannel('A').point(lambda v: int(v * opacity))
    blk = Image.new('RGBA', b.size, (60, 20, 35, 255)); blk.putalpha(m)
    sh.paste(blk, (radius * 2, radius * 2 + 2), blk)
    return sh.filter(ImageFilter.GaussianBlur(radius))

# Intro: 0 -> 3.3 s
INTRO = 3.3
os.makedirs('build/intro', exist_ok=True)
n = int(INTRO * FPS)
for i in range(n):
    tt = i / FPS
    fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bg_a = 1 - ease((tt - 2.1) / 0.7)
    if bg_a > 0:
        fr.paste(Image.new('RGBA', (W, H), CREAM + (int(255 * bg_a),)), (0, 0))
    # entrada: aparece + crece levemente
    fin = ease(tt / 0.6)
    k = ease((tt - 2.1) / 1.0)  # movimiento a la esquina
    width = (BIG_W * (0.9 + 0.1 * fin)) * (1 - k) + SMALL_W * k
    cx_big = big_pos[0] + BIG_W / 2
    cy_big = big_pos[1] + BIG_W * bh0 / bw0 / 2
    cx_s = small_pos[0] + SMALL_W / 2
    cy_s = small_pos[1] + SMALL_W * bh0 / bw0 / 2
    cx = cx_big * (1 - k) + cx_s * k
    cy = cy_big * (1 - k) + cy_s * k
    alpha = fin * (1 - k) + WM_ALPHA * k
    b = badge_at(width, alpha)
    x, y = round(cx - b.width / 2), round(cy - b.height / 2)
    if k > 0:
        sh = shadow_for(b, opacity=0.35 * k)
        fr.alpha_composite(sh, (x - 12, y - 12))
    fr.alpha_composite(b, (x, y))
    fr.save(f'build/intro/{i:04d}.png')

# Marca de agua fija
wm = Image.new('RGBA', (W, H), (0, 0, 0, 0))
b = badge_at(SMALL_W, WM_ALPHA)
wm.alpha_composite(shadow_for(b, opacity=0.35), (small_pos[0] - 12, small_pos[1] - 12))
wm.alpha_composite(b, small_pos)
wm.save('build/watermark.png')

# ---------- Outro (tarjeta final) ----------
fXB = 'fonts/ElielleSansXB.ttf'
fMD = 'fonts/ElielleSansMd.ttf'
os.makedirs('build/outro', exist_ok=True)
logo_out = badge_at(470, 1.0)
font_price = ImageFont.truetype(fXB, 120)
font_small = ImageFont.truetype(fMD, 30)
font_cta = ImageFont.truetype(fXB, 40)
n = int(OUTRO * FPS)
for i in range(n):
    tt = i / FPS
    fr = Image.new('RGBA', (W, H), CREAM + (255,))
    d = ImageDraw.Draw(fr)
    a1 = ease(tt / 0.5)
    lb = badge_at(470 * (0.92 + 0.08 * a1), a1)
    fr.alpha_composite(lb, (round((W - lb.width) / 2), round(330 - lb.height / 2)))
    # "Caja de regalo"
    a2 = ease((tt - 0.35) / 0.4)
    txt = 'CAJA DE REGALO'
    tw = d.textlength(txt, font=font_small)
    tl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(tl).text(((W - tw) / 2, 600), txt, font=font_small, fill=BURG + (int(255 * a2),)); fr.alpha_composite(tl)
    # pastilla de precio con "pop"
    a3 = ease((tt - 0.5) / 0.35)
    if a3 > 0:
        pop = 1 + 0.12 * math.sin(min(1, max(0, (tt - 0.5) / 0.5)) * math.pi)
        ptxt = '$600'
        pw = d.textlength(ptxt, font=font_price)
        pill = Image.new('RGBA', (int(pw) + 100, 170), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pill)
        pd.rounded_rectangle((0, 0, pill.width - 1, 169), radius=85, fill=BURG + (255,))
        pd.text((50, 8), ptxt, font=font_price, fill=(255, 255, 255, 255))
        s = 0.85 + 0.15 * a3
        pill = pill.resize((round(pill.width * s * pop), round(pill.height * s * pop)), Image.LANCZOS)
        pill.putalpha(pill.getchannel('A').point(lambda v: int(v * a3)))
        fr.alpha_composite(pill, (round((W - pill.width) / 2), round(750 - pill.height / 2)))
    a4 = ease((tt - 0.9) / 0.4)
    for j, line in enumerate(['¡Escríbenos y', 'haz tu pedido!']):
        lw = d.textlength(line, font=font_cta)
        tl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(tl).text(((W - lw) / 2, 900 + j * 56), line, font=font_cta, fill=BURG + (int(255 * a4),)); fr.alpha_composite(tl)
    fr.convert('RGB').save(f'build/outro/{i:04d}.png')

# ---------- Subtitulos ASS ----------
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f'{h}:{m:02d}:{s:05.2f}'

ass = [
    '[Script Info]', 'ScriptType: v4.00+', f'PlayResX: {W}', f'PlayResY: {H}', 'WrapStyle: 0', '',
    '[V4+ Styles]',
    'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
    'Style: Sub,ElielleSansXB,58,&H00FFFFFF,&H00FFFFFF,&H004A2A7A,&H64000000,0,0,0,0,100,100,0,0,1,5,2,2,40,40,230,1',
    'Style: Price,ElielleSansXB,80,&H00FFFFFF,&H00FFFFFF,&H004A2A7A,&H004A2A7A,0,0,0,0,100,100,0,0,3,14,0,5,40,40,0,1',
    '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text',
]
for a, b, at, chunks in VO:
    if at >= MAIN_END:  # la tarjeta final ya muestra el texto
        continue
    dur = b - a
    total_chars = sum(len(c) for c in chunks)
    cur = at
    for c in chunks:
        d = dur * len(c) / total_chars
        ass.append(f'Dialogue: 0,{ts(cur)},{ts(cur + d - 0.01)},Sub,,0,0,0,,{{\\fad(60,60)}}{c}')
        cur += d
# etiqueta de precio sobre el resultado final
p0 = seg_start[6] + 5.5
ass.append(f'Dialogue: 1,{ts(p0)},{ts(MAIN_END)},Price,,0,0,0,,{{\\pos(360,400)\\fad(200,150)\\t(0,180,\\fscx118\\fscy118)\\t(180,360,\\fscx100\\fscy100)}}Solo $600')
open('build/subs.ass', 'w', encoding='utf-8').write('\n'.join(ass) + '\n')

# ---------- Render ----------
def run(cmd):
    print('+', ' '.join(cmd)[:300]); subprocess.run(cmd, check=True)

# 1) cuerpo principal: cortes + velocidad
inputs = []
parts = []
for i, (f, a, b, sp) in enumerate(SEGS):
    inputs += ['-i', f]
    parts.append(f'[{i}:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},fps={FPS},'
                 f'scale={W}:-2:flags=lanczos,crop={W}:{H},setsar=1,eq=saturation=1.08:contrast=1.03[v{i}]')
concat = ''.join(f'[v{i}]' for i in range(len(SEGS))) + f'concat=n={len(SEGS)}:v=1:a=0[body]'
run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(parts) + ';' + concat,
     '-map', '[body]', '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'build/body.mp4'])

# 2) cuerpo + intro + marca de agua + subtitulos
run(['ffmpeg', '-v', 'error', '-y', '-i', 'build/body.mp4',
     '-framerate', str(FPS), '-i', 'build/intro/%04d.png',
     '-loop', '1', '-i', 'build/watermark.png',
     '-filter_complex',
     f"[0:v][1:v]overlay=0:0:eof_action=pass[a];"
     f"[a][2:v]overlay=0:0:shortest=1:enable='gte(t,{INTRO - 1 / FPS:.3f})'[b];"
     f"[b]subtitles=build/subs.ass:fontsdir=fonts[v]",
     '-map', '[v]', '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'build/body_fx.mp4'])

# 3) outro
run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', 'build/outro/%04d.png',
     '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', 'build/outro.mp4'])

# 4) audio: voz (con ducking de musica) + musica
vo_in = []
vo_f = []
for i, (a, b, at, _) in enumerate(VO):
    ms = int(at * 1000)
    vo_f.append(f'[1:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={b - a - 0.06:.3f}:d=0.06,adelay={ms}|{ms}[s{i}]')
mix_vo = ''.join(f'[s{i}]' for i in range(len(VO))) + f'amix=inputs={len(VO)}:normalize=0,apad,atrim=0:{TOTAL:.3f}[vo]'
music = (f'[2:a]atrim=0:{TOTAL:.3f},asetpts=PTS-STARTPTS,volume=0.30,'
         f'afade=t=in:d=0.8,afade=t=out:st={TOTAL - 2.0:.3f}:d=2.0[mus]')
af = ';'.join(vo_f) + ';' + mix_vo + ';[vo]asplit[vo1][vo2];' + music + ';' + \
     '[mus][vo2]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=500[duck];' + \
     '[vo1]loudnorm=I=-16:TP=-1.5:LRA=11,volume=1.0[von];' + \
     '[duck][von]amix=inputs=2:normalize=0,alimiter=limit=0.95[aout]'

# 5) unir video + audio
run(['ffmpeg', '-v', 'error', '-y', '-i', 'build/body_fx.mp4', '-i', 'audio/voz1.mp3', '-i', 'audio/musica1.mp3',
     '-i', 'build/outro.mp4',
     '-filter_complex', af + ';[0:v][3:v]concat=n=2:v=1:a=0[v]',
     '-map', '[v]', '-map', '[aout]', '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p',
     '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-t', f'{TOTAL:.3f}',
     'Elielle_caja_regalo_600.mp4'])
print('OK')
