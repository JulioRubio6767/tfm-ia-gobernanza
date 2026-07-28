"""
to_html.py — Convierte tesis_completa.md a HTML profesional con imagenes
Uso: python scripts/to_html.py
Genera: tesis_completa.html (~5 MB)
"""

import re, os, base64

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_PATH = os.path.join(ROOT, "capitulos", "tesis_completa.md")
OUT_PATH = os.path.join(ROOT, "tesis_completa.html")
IMG_DIR = os.path.join(ROOT, "outputs", "figures")

with open(MD_PATH, "rb") as f:
    raw = f.read()
if raw[:3] == b"\xef\xbb\xbf":
    raw = raw[3:]
md = raw.decode("utf-8")

# ─── CSS ───
CSS = """
@page { margin: 1cm 1.2cm 1cm 1.2cm; }
body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 12pt;
    line-height: 1.35;
    color: #1a1a1a;
    max-width: 190mm;
    margin: auto;
    padding: 3px 8px;
    background: white;
}
h1 { font-size: 14pt; font-weight: bold; text-align: center; margin-top: 8px; margin-bottom: 4px; }
h2 { font-size: 13pt; font-weight: bold; margin-top: 6px; margin-bottom: 3px; border-bottom: 1px solid #ccc; padding-bottom: 1px; }
h3 { font-size: 12pt; font-weight: bold; margin-top: 5px; margin-bottom: 2px; }
h4 { font-size: 12pt; font-weight: bold; margin-top: 4px; margin-bottom: 2px; }
p { text-align: justify; margin: 1px 0; }
img { max-width: 80%; height: auto; display: block; margin: 4px auto; }
.fig-caption { text-align: center; font-size: 10pt; color: #555; margin: 0 0 5px 0; font-style: italic; }
table { border-collapse: collapse; width: 100%; margin: 3px 0; font-size: 10pt; }
td, th { border: 1px solid #999; padding: 1px 3px; text-align: center; }
th { background: #f0f0f0; font-weight: bold; }
.cover-page { text-align: center; padding: 10px 0 8px 0; }
.cover-page h1 { font-size: 16pt; margin-top: 12px; }
.cover-page .meta { font-size: 12pt; margin-top: 10px; line-height: 1.5; }
"""

# ─── Build HTML ───
html = []
html.append(f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Framework de Gobernanza Proactiva para Sistemas de IA Auditables</title>
<style>{CSS}</style>
</head>
<body>
""")

# ─── TOC placeholder ───
html.append('<div class="toc" id="toc">')
html.append('<h2 style="text-align:center;">INDICE</h2>')
toc_entries = []

# ─── Process markdown ───
lines = md.split("\n")
in_yaml = True
in_table = False
in_code = False
skip_hr = False
toc_counter = 0

def img_to_base64(img_path):
    """Convert image to base64 data URI."""
    if not os.path.exists(img_path):
        return None
    with open(img_path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(img_path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def process_inline(text):
    """Convert **bold** and *italic* to HTML."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


for line in lines:
    s = line.strip()
    
    # Skip YAML
    if s == "---" and in_yaml:
        in_yaml = False
        continue
    if in_yaml:
        continue
    
    # Empty lines
    if not s:
        continue
    
    # Skip YAML metadata lines
    if ":" in s and not s.startswith("#") and not s.startswith("|") and not s.startswith("*") and not s.startswith("!") and not s.startswith("##"):
        if in_yaml and any(k in s for k in ["title:", "autor:", "director:", "tipo:", "dataset:", "referencias:", "figuras:", "kpis:", "fecha:"]):
            continue
    
    in_yaml = False
    
    # Horizontal rules
    if s == "---" and not in_yaml:
        html.append('</div><hr class="page-break"><div>')
        continue
    
    # Image: ![Figura X.Y - Desc](path)
    img_match = re.match(r"!\[(.*?)\]\(.*?([^/]+\.png)\)", s)
    if img_match:
        caption = img_match.group(1)
        fname = img_match.group(2)
        img_path = os.path.join(IMG_DIR, fname)
        b64 = img_to_base64(img_path)
        if b64:
            html.append(f'<img src="{b64}" alt="{caption}" loading="lazy">')
        else:
            html.append(f'<p style="color:red;">[Imagen no encontrada: {fname}]</p>')
        continue
    
    # Figure caption
    if s.startswith("*Figura") or s.startswith("*Fuente"):
        html.append(f'<p class="fig-caption">{process_inline(s.strip("*"))}</p>')
        continue
    
    # Headings
    if s.startswith("# ") and len(s) > 2:
        text = s[2:].strip()
        toc_entries.append((1, text))
        if "CAPÍTULO" in text.upper() or "CAPITULO" in text.upper():
            html.append(f'<h1 style="margin-top:15px;">{process_inline(text)}</h1>')
        elif text.lower() in ("resumen", "abstract"):
            html.append(f'<h1>{process_inline(text)}</h1>')
        else:
            html.append(f'<h1>{process_inline(text)}</h1>')
        continue
    
    if s.startswith("## ") and len(s) > 3:
        text = s[3:].strip()
        toc_entries.append((2, text))
        html.append(f'<h2>{process_inline(text)}</h2>')
        continue
    
    if s.startswith("### ") and len(s) > 4:
        text = s[4:].strip()
        toc_entries.append((3, text))
        html.append(f'<h3>{process_inline(text)}</h3>')
        continue
    
    if s.startswith("#### ") and len(s) > 5:
        text = s[5:].strip()
        html.append(f'<h4>{process_inline(text)}</h4>')
        continue
    
    # Tables
    if s.startswith("|") and s.endswith("|"):
        cells = [c.strip() for c in s.split("|")[1:-1]]
        
        # Skip separator lines
        if cells and all(c in ("---", ":---", ":---:", "" ) for c in cells):
            continue
        
        if not in_table:
            html.append('<table>')
            in_table = True
        
        is_header = False
        html.append('<tr>')
        for cell in cells:
            tag = "th" if is_header else "td"
            html.append(f'<{tag}>{process_inline(cell)}</{tag}>')
        html.append('</tr>')
        is_header = False
        continue
    else:
        if in_table:
            html.append('</table>')
            in_table = False
    
    # Bold lines (like **Palabras clave:**, **Keywords:**)
    if s.startswith("**") and ":**" in s:
        parts = s.split(":**", 1)
        html.append(f'<p><b>{parts[0]}:</b>{process_inline(parts[1]) if len(parts) > 1 else ""}</p>')
        continue
    
    # Regular paragraph
    html.append(f'<p>{process_inline(s)}</p>')

# Close any open table
if in_table:
    html.append('</table>')

# Close TOC placeholder
html.append('</div>')

# ─── Generate TOC ───
toc_html = ['<div id="toc-container"><h2 style="text-align:center;">INDICE DE CONTENIDOS</h2>']
for level, text in toc_entries:
    cls = f"toc-h{level}"
    toc_html.append(f'<p class="{cls}">{text}</p>')
toc_html.append('</div>')

# Replace TOC placeholder
full_html = "".join(html)
full_html = full_html.replace(
    '<div class="toc" id="toc">\n<h2 style="text-align:center;">INDICE</h2>',
    "".join(toc_html)
)

# ─── Add cover page ───
cover = f"""
<div class="cover-page">
    <p style="font-size:12pt;">Universidad Internacional de La Rioja</p>
    <p style="font-size:10pt;">Escuela Superior de Ingeniería y Tecnología</p>
    <p style="font-size:9pt; margin-top:15px;">Máster Universitario en Big Data y Visual Analytics</p>
    <h1 style="margin-top:30px;">Framework de Gobernanza Proactiva para Sistemas de IA Auditables</h1>
    <p style="font-size:10pt; margin-top:20px;">Metodología Integrada para el Diseño, Implementación y Evaluación<br>
    de Modelos de Decisión Automatizada Conformes con la Normativa Europea</p>
    <div class="meta" style="margin-top:30px;">
        <p><b>Autor:</b> Julio Andrés Rubio Echeverria</p>
        <p><b>Director:</b> Ricardo Andres Fonseca Perdomo</p>
        <p><b>Tipo:</b> Tipo 3 — Desarrollo de Metodología</p>
        <p><b>Fecha:</b> Julio 2026</p>
    </div>
</div>
"""

full_html = cover + full_html

# ─── Add closing tag ───
full_html += "\n</body></html>"

# ─── Write ───
with open(OUT_PATH, "wb") as f:
    f.write(full_html.encode("utf-8"))

size_mb = os.path.getsize(OUT_PATH) / (1024 * 1024)
print(f"HTML generado: {OUT_PATH}")
print(f"Tamaño: {size_mb:.1f} MB")
print(f"Imagenes incluidas: {len([l for l in full_html.split(chr(10)) if 'img src' in l])}")
print(f"Paginas estimadas: ~{len(full_html)//5000}")
