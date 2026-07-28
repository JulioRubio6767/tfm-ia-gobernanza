"""Genera HTML imprimible desde TESIS_COMPLETA.md"""
import os, re, base64

MD_PATH = "C:/Users/julio/Desktop/tesis/capitulos/TESIS_COMPLETA.md"
OUT_PATH = "C:/Users/julio/Desktop/tesis/capitulos/TESIS_COMPLETA.html"
IMG_DIR = "C:/Users/julio/Desktop/tesis/outputs/figures"

with open(MD_PATH, "rb") as f:
    raw = f.read()
if raw[:3] == b"\xef\xbb\xbf":
    raw = raw[3:]
md = raw.decode("utf-8")

CSS = """
@page { margin: 1.5cm 1.8cm 1.5cm 1.8cm; }
body { font-family: 'Times New Roman', Times, serif; font-size: 11pt; line-height: 1.4; max-width: 190mm; margin: auto; padding: 10px 20px; background: white; color: #1a1a1a; }
h1 { font-size: 14pt; font-weight: bold; text-align: center; margin: 15px 0 8px; }
h2 { font-size: 12pt; font-weight: bold; margin: 10px 0 5px; border-bottom: 1px solid #ccc; padding-bottom: 2px; }
h3 { font-size: 11pt; font-weight: bold; margin: 8px 0 4px; }
p { text-align: justify; margin: 4px 0; }
img { max-width: 90%; height: auto; display: block; margin: 10px auto; }
.fig-caption { text-align: center; font-size: 9pt; color: #555; margin: 0 0 12px; font-style: italic; }
table { border-collapse: collapse; width: 100%; margin: 6px 0; font-size: 9pt; }
td, th { border: 1px solid #999; padding: 3px 6px; text-align: center; }
th { background: #f0f0f0; font-weight: bold; }
@media print { body { padding: 0; } }
"""

html_parts = []
html_parts.append('<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">')
html_parts.append('<title>Framework de Gobernanza Proactiva</title>')
html_parts.append(f'<style>{CSS}</style></head><body>')

in_yaml = True
in_table = False

for line in md.split("\n"):
    s = line.strip()
    
    if s == "---" and in_yaml:
        in_yaml = False
        continue
    if in_yaml:
        continue
    if not s:
        if in_table:
            html_parts.append("</table>")
            in_table = False
        continue
    
    # Image
    img_match = re.match(r'!\[(.*?)\]\(([^)]+)\)', s)
    if img_match:
        caption = img_match.group(1)
        rel_path = img_match.group(2)
        abs_path = os.path.normpath(os.path.join(os.path.dirname(MD_PATH), rel_path))
        if os.path.exists(abs_path):
            with open(abs_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            html_parts.append(f'<img src="data:image/png;base64,{img_data}" alt="{caption}">')
        continue
    
    # Figure caption
    if s.startswith("*") and ("Figura" in s or "Fuente" in s):
        clean = s.strip("*").strip()
        html_parts.append(f'<p class="fig-caption">{clean}</p>')
        continue
    
    # Tables
    if s.startswith("|") and s.endswith("|"):
        cells = [c.strip() for c in s.split("|")[1:-1]]
        if all(c in ("---", ":---", ":---:") for c in cells):
            continue
        if not in_table:
            html_parts.append("<table>")
            in_table = True
        html_parts.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
        continue
    else:
        if in_table:
            html_parts.append("</table>")
            in_table = False
    
    # Headings
    if s.startswith("# ") and len(s) > 2:
        html_parts.append(f"<h1>{s[2:].strip()}</h1>")
    elif s.startswith("## ") and len(s) > 3:
        html_parts.append(f"<h2>{s[3:].strip()}</h2>")
    elif s.startswith("### ") and len(s) > 4:
        html_parts.append(f"<h3>{s[4:].strip()}</h3>")
    elif s.startswith("#### ") and len(s) > 5:
        html_parts.append(f"<h4>{s[5:].strip()}</h4>")
    elif s.startswith("---"):
        continue
    else:
        html_parts.append(f"<p>{s}</p>")

if in_table:
    html_parts.append("</table>")
html_parts.append("</body></html>")

with open(OUT_PATH, "wb") as f:
    f.write(b"\xef\xbb\xbf")
    f.write("".join(html_parts).encode("utf-8"))

img_count = len(re.findall(r"img src", "".join(html_parts)))
size_mb = os.path.getsize(OUT_PATH) / (1024 * 1024)
words = len(md.split())

print(f"HTML: {OUT_PATH}")
print(f"Palabras: {words}")
print(f"Imagenes: {img_count}")
print(f"Tamaño: {size_mb:.1f} MB")
