import sys
sys.stdout.reconfigure(encoding='utf-8')

OLD_LB_JS = """  // ── Lightbox ────────────────────────────────────────────────────
  (function () {
    var lb    = document.getElementById('lightbox');
    var lbImg = document.getElementById('lb-img');
    var lbCap = document.getElementById('lb-caption');
    function openLb(src, caption) {
      lbImg.src = src;
      lbCap.textContent = caption || '';
      lb.classList.add('lb-open');
      document.body.style.overflow = 'hidden';
    }
    function closeLb() {
      lb.classList.remove('lb-open');
      document.body.style.overflow = '';
      setTimeout(function () { lbImg.src = ''; }, 250);
    }
    document.getElementById('lb-close').addEventListener('click', closeLb);
    lb.addEventListener('click', function (e) { if (e.target === lb) closeLb(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && lb.classList.contains('lb-open')) closeLb();
    });
    // Expose so page-specific code can call openLb
    window._openLightbox = openLb;
  }());"""

NEW_LB_JS = """  // ── Lightbox ────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    var lb    = document.getElementById('lightbox');
    var lbImg = document.getElementById('lb-img');
    var lbCap = document.getElementById('lb-caption');
    if (!lb) return;
    function openLb(src, caption) {
      lbImg.src = src;
      lbCap.textContent = caption || '';
      lb.classList.add('lb-open');
      document.body.style.overflow = 'hidden';
    }
    function closeLb() {
      lb.classList.remove('lb-open');
      document.body.style.overflow = '';
      setTimeout(function () { lbImg.src = ''; }, 250);
    }
    document.getElementById('lb-close').addEventListener('click', closeLb);
    lb.addEventListener('click', function (e) { if (e.target === lb) closeLb(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && lb.classList.contains('lb-open')) closeLb();
    });
    window._openLightbox = openLb;
  });"""

OLD_BTT_JS = """  // ── Back to top ─────────────────────────────────────────────────
  (function () {
    var btn = document.getElementById('btt');
    window.addEventListener('scroll', function () {
      btn.classList.toggle('btt-show', window.scrollY > 420);
    }, { passive: true });
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }());"""

NEW_BTT_JS = """  // ── Back to top ─────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('btt');
    if (!btn) return;
    window.addEventListener('scroll', function () {
      btn.classList.toggle('btt-show', window.scrollY > 420);
    }, { passive: true });
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });"""

for fname in ['cctv-components.html', 'index.html']:
    with open(fname, 'r', encoding='utf-8') as f:
        html = f.read()

    if OLD_LB_JS not in html:
        print(f"ERROR: lightbox JS not found in {fname}")
        continue
    if OLD_BTT_JS not in html:
        print(f"ERROR: BTT JS not found in {fname}")
        continue

    html = html.replace(OLD_LB_JS, NEW_LB_JS, 1)
    html = html.replace(OLD_BTT_JS, NEW_BTT_JS, 1)

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Fixed: {fname}")
