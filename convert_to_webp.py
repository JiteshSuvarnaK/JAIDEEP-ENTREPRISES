import os, re, base64, sys
from PIL import Image
from io import BytesIO

sys.stdout.reconfigure(encoding='utf-8')
BASE = 'D:/Jaideep Enterprises/new1'

def to_webp(src_path, dst_path, is_jpeg=False):
    img = Image.open(src_path)
    if is_jpeg:
        img.save(dst_path, 'WEBP', quality=88, method=6)
    else:
        img.save(dst_path, 'WEBP', lossless=True, method=6)
    before = os.path.getsize(src_path)
    after  = os.path.getsize(dst_path)
    print(f'  {os.path.basename(src_path):55s} {before//1024:5d} KB -> {after//1024:4d} KB  ({100-after*100//before}% saved)')

print('=== Converting root-level images ===')
ROOT_IMGS = [f for f in os.listdir(BASE)
             if f.lower().endswith(('.png','.jpg','.jpeg'))
             and f != 'main_logo_img.png']  # logo handled separately
for fname in ROOT_IMGS:
    src = f'{BASE}/{fname}'
    ext = os.path.splitext(fname)[1].lower()
    dst = src.rsplit('.', 1)[0] + '.webp'
    to_webp(src, dst, is_jpeg=(ext in ('.jpg','.jpeg')))

print('\n=== Converting main_logo_img.png ===')
to_webp(f'{BASE}/main_logo_img.png', f'{BASE}/main_logo_img.webp', is_jpeg=False)

print('\n=== Converting CCTV product images ===')
for root, dirs, files in os.walk(f'{BASE}/CCTV Product Categories'):
    for f in files:
        if f.lower().endswith(('.png','.jpg','.jpeg')):
            src = os.path.join(root, f)
            dst = src.rsplit('.', 1)[0] + '.webp'
            to_webp(src, dst, is_jpeg=f.lower().endswith(('.jpg','.jpeg')))

print('\n=== Converting Brand logos ===')
for root, dirs, files in os.walk(f'{BASE}/Brand logos'):
    for f in files:
        if f.lower().endswith(('.png','.jpg','.jpeg')):
            src = os.path.join(root, f)
            dst = src.rsplit('.', 1)[0] + '.webp'
            to_webp(src, dst, is_jpeg=f.lower().endswith(('.jpg','.jpeg')))

# ── Extract base64 images from index.html and replace with external WebP ───
print('\n=== Extracting base64 images from index.html ===')
with open(f'{BASE}/index.html', 'r', encoding='utf-8') as f:
    brass = f.read()

b64_pattern = re.compile(r"url\('data:image/(jpeg|png);base64,([A-Za-z0-9+/=]+)'\)")
NAMES = ['Hero_img.webp', 'about_img.webp']
found = list(b64_pattern.finditer(brass))
print(f'  Found {len(found)} base64 background images')

for i, m in enumerate(found):
    img_type, b64data = m.group(1), m.group(2)
    name = NAMES[i] if i < len(NAMES) else f'extracted_bg_{i}.webp'
    raw  = base64.b64decode(b64data)
    img  = Image.open(BytesIO(raw))
    out  = f'{BASE}/{name}'
    img.save(out, 'WEBP', quality=88, method=6)
    size_kb = os.path.getsize(out) // 1024
    print(f'  Extracted -> {name}  ({len(b64data)//1024} KB b64 -> {size_kb} KB WebP)')
    brass = brass[:m.start()] + f"url('{name}')" + brass[m.end():]

# ── Update all .png / .jpg / .jpeg references in index.html ────────────────
print('\n=== Updating image references in index.html ===')
def replace_refs(html):
    # src="file.png"  src="file.jpg"  data-img="file.png"  url('file.jpg')
    html = re.sub(r'(src=["\'])((?!data:)[^"\']+?)\.(png|jpg|jpeg)(["\'])', r'\1\2.webp\4', html, flags=re.IGNORECASE)
    html = re.sub(r'(data-img=["\'])((?!data:)[^"\']+?)\.(png|jpg|jpeg)(["\'])', r'\1\2.webp\4', html, flags=re.IGNORECASE)
    html = re.sub(r"(url\(')((?!data:)[^']+?)\.(png|jpg|jpeg)('\))", r'\1\2.webp\4', html, flags=re.IGNORECASE)
    html = re.sub(r'(content=["\']https?://[^"\']+?)\.(png|jpg|jpeg)(["\'])', r'\1.webp\3', html, flags=re.IGNORECASE)
    return html

brass = replace_refs(brass)
with open(f'{BASE}/index.html', 'w', encoding='utf-8') as f:
    f.write(brass)
print('  index.html updated')

# ── Update all references in cctv-components.html ──────────────────────────
print('\n=== Updating image references in cctv-components.html ===')
with open(f'{BASE}/cctv-components.html', 'r', encoding='utf-8') as f:
    cctv = f.read()
cctv = replace_refs(cctv)
with open(f'{BASE}/cctv-components.html', 'w', encoding='utf-8') as f:
    f.write(cctv)
print('  cctv-components.html updated')

# ── Final size report ───────────────────────────────────────────────────────
print('\n=== Final size report ===')
def dir_size(path):
    total = 0
    for r, d, files in os.walk(path):
        for f in files:
            if f.lower().endswith('.webp'):
                total += os.path.getsize(os.path.join(r, f))
    return total

root_webp   = sum(os.path.getsize(f'{BASE}/{f}') for f in os.listdir(BASE) if f.lower().endswith('.webp'))
cctv_webp   = dir_size(f'{BASE}/CCTV Product Categories')
logos_webp  = dir_size(f'{BASE}/Brand logos')
html_sizes  = os.path.getsize(f'{BASE}/index.html') + os.path.getsize(f'{BASE}/cctv-components.html')
grand_webp  = root_webp + cctv_webp + logos_webp + html_sizes

def mb(b): return f'{b/1_048_576:.2f} MB'
print(f'  Root WebP images          {mb(root_webp)}')
print(f'  CCTV product WebP images  {mb(cctv_webp)}')
print(f'  Brand logo WebP images    {mb(logos_webp)}')
print(f'  HTML files                {mb(html_sizes)}')
print(f'  TOTAL both pages          {mb(grand_webp)}')
print(f'  Netlify 100GB = ~{100*1024/grand_webp*1_048_576:.0f} full visits/month')
