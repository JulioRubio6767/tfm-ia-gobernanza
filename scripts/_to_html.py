"""Convierte tesis_completa.md a HTML con imagenes locales"""
import re, os, html

base = 'C:/Users/julio/Desktop/tesis'

with open(base + '/tesis_completa.md', 'rb') as f:
    raw = f.read()
if raw[:3] == b'\xef\xbb\xbf': raw = raw[3:]
md_text = raw.decode('utf-8')

html_parts = []
html_parts.append('''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>TFM - Framework de Gobernanza Proactiva</title>
<style>
body { font-family: 'Times New Roman', serif; max-width: 900px; margin: auto; padding: 20px; line-height: 1.6; font-size: 12pt; }
h1 { font-size: 18pt; text-align: center; }
h2 { font-size: 14pt; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 25px; }
h3 { font-size: 12pt; margin-top: 20px; }
img { max-width: 100%; height: auto; display: block; margin: 10px auto; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; }
td, th { border: 1px solid #ccc; padding: 5px; font-size: 10pt; }
.fig-caption { text-align: center; font-size: 10pt; color: #555; margin: 5px 0 20px 0; }
.center { text-align: center; }
</style>
</head>
<body>
''')

for line in md_text.split('\n'):
    s = line.strip()
    
    img_m = re.match(r'!\[(.*?)\]\(file:///[^)]+/([^/)]+\.png)\)', line)
    if img_m:
        caption = html.escape(img_m.group(1))
        fname = img_m.group(2)
        ap = 'file:///' + base.replace('\\', '/') + '/outputs/figures/' + fname
        html_parts.append(f'<img src="{ap}" alt="{caption}">')
        html_parts.append(f'<p class="fig-caption">{caption}</p>')
        continue
    
    if s.startswith('*Figura') or s.startswith('*Fuente'):
        html_parts.append(f'<p class="fig-caption">{html.escape(s)}</p>')
        continue
    
    if s.startswith('|') and s.endswith('|'):
        cells = [c.strip() for c in s.split('|')[1:-1]]
        if cells and all(cc in ('---', ':---', ':---:') for cc in cells):
            continue
        html_parts.append('<tr>' + ''.join(f'<td>{html.escape(c)}</td>' for c in cells if c) + '</tr>')
        continue
    
    if line.startswith('### '):
        html_parts.append(f'<h3>{html.escape(line[4:])}</h3>')
    elif line.startswith('## '):
        html_parts.append(f'<h2>{html.escape(line[3:])}</h2>')
    elif line.startswith('# '):
        html_parts.append(f'<h1>{html.escape(line[2:])}</h1>')
    elif s == '---':
        html_parts.append('<hr>')
    elif s == '':
        pass
    else:
        txt = html.escape(line)
        if txt.startswith('|'):
            continue
        html_parts.append(f'<p>{txt}</p>')

html_parts.append('</body></html>')

with open(base + '/tesis_completa.html', 'wb') as f:
    f.write(b'\xef\xbb\xbf')
    f.write(''.join(html_parts).encode('utf-8'))

print('Creado: tesis_completa.html')
print('Abrir en cualquier navegador.')
