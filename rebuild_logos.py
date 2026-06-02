"""
Re-extract the missing logos with smaller dilation + embed ALL logos as base64 in the HTML.
"""
from PIL import Image
import numpy as np
from scipy.ndimage import label, binary_dilation
import os, json, base64, re

BASE  = "/Users/i755892/Desktop/Claude/Videos/"
LOGOS = "/Users/i755892/Desktop/Claude/logos/"
HTML  = "/Users/i755892/Desktop/Claude/customer-library.html"

# ── Re-extract the 6 missing from screenshot 3 (bottom row) ──────────────────
def extract_region(img_path, y_start_frac, y_end_frac, names, dilation=10):
    img = Image.open(img_path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]
    y0 = int(h * y_start_frac)
    y1 = int(h * y_end_frac)
    region_arr = arr[y0:y1, :]
    mask = ~((region_arr[:,:,0] > 242) & (region_arr[:,:,1] > 242) & (region_arr[:,:,2] > 242))
    dilated = binary_dilation(mask, iterations=dilation)
    labeled, n = label(dilated)
    bboxes = []
    for i in range(1, n+1):
        rows = np.where((labeled==i).any(axis=1))[0]
        cols = np.where((labeled==i).any(axis=0))[0]
        if len(rows)==0: continue
        r0,r1,c0,c1 = rows[0],rows[-1],cols[0],cols[-1]
        if (r1-r0)*(c1-c0) < 500: continue
        bboxes.append((r0,r1,c0,c1))
    bboxes.sort(key=lambda b: (b[2]+b[3])//2)
    img_region = Image.fromarray(arr[y0:y1, :])
    pad = 8
    crops = []
    for r0,r1,c0,c1 in bboxes:
        crops.append(img_region.crop((max(0,c0-pad), max(0,r0-pad),
                                      min(w,c1+pad), min(y1-y0,r1+pad))))
    print(f"  Found {len(crops)} logos, expected {len(names)}")
    return crops

def slug(name):
    t = name.lower()
    for a,b in [(" ","_"),("·",""),("İ","i"),("ı","i"),("ğ","g"),("ü","u"),
                ("ş","s"),("ö","o"),("ç","c"),("(",""),(")",""),(". ","_"),(".",""),(",","")]:
        t = t.replace(a,b)
    return t

print("Re-extracting missing logos from original screenshots...")

# Screenshot 3 – last row (Tırsan already done; need TKG→Turktex = 6 logos)
print("Screenshot 3 last row:")
crops = extract_region(BASE+"Screenshot 2026-05-28 at 11.19.59.png", 0.83, 1.0,
    ["TKG Otomotiv","Toksan Otomotiv","Trakya Döküm","Trendyol","Turka","Turktex"], dilation=8)
missing3 = ["TKG Otomotiv","Toksan Otomotiv","Trakya Döküm","Trendyol","Turka","Turktex"]
for crop, name in zip(crops, missing3):
    crop.save(LOGOS + slug(name) + ".png")
    print(f"  Saved {name}")

# Screenshot 3 – also try to recover Tırsan row fully (skip first if already exists)
# Actually Tırsan is already done.

# Screenshot 4 – last row (Volta, Yemek Hane, Yeşilyurt Demir Çelik)
print("Screenshot 4 last row:")
crops4 = extract_region(BASE+"Screenshot 2026-05-28 at 11.20.05.png", 0.83, 1.0,
    ["TYÖ","Vergo","Vestel","Yapı Merkezi","Volta","Yemek Hane","Yeşilyurt Demir Çelik"], dilation=8)
# TYÖ, Vergo, Vestel, Yapı Merkezi already extracted. Only need last 3.
missing4 = ["TYÖ","Vergo","Vestel","Yapı Merkezi","Volta","Yemek Hane","Yeşilyurt Demir Çelik"]
for crop, name in zip(crops4, missing4):
    out = LOGOS + slug(name) + ".png"
    if not os.path.exists(out):
        crop.save(out)
        print(f"  Saved {name}")
    else:
        print(f"  Skip {name} (exists)")

# Screenshot 1 – ebebek (last item, row 6 col 7)
print("Screenshot 1 last row:")
crops1 = extract_region(BASE+"Screenshot 2026-05-28 at 11.19.33.png", 0.82, 1.0,
    ["DeFacto","Dimes","Doğan Trend","Doğanlar Mobilya","Dönmez Hammer","Drogsan","ebebek"], dilation=8)
missing1 = ["DeFacto","Dimes","Doğan Trend","Doğanlar Mobilya","Dönmez Hammer","Drogsan","ebebek"]
for crop, name in zip(crops1, missing1):
    out = LOGOS + slug(name) + ".png"
    if not os.path.exists(out) or name == "ebebek":
        crop.save(out)
        print(f"  Saved {name}")

# Screenshot 5 – Enerjisa (bottom row, 3rd item)
print("Screenshot 5 bottom row:")
crops5 = extract_region(BASE+"Screenshot 2026-05-28 at 11.20.11.png", 0.5, 1.0,
    ["Yücel Boru","Zeren Group","Enerjisa"], dilation=10)
missing5 = ["Yücel Boru","Zeren Group","Enerjisa"]
for crop, name in zip(crops5, missing5):
    out = LOGOS + slug(name) + ".png"
    if not os.path.exists(out) or name == "Enerjisa":
        crop.save(out)
        print(f"  Saved {name}")

# ── Rebuild logo_map with ALL companies ──────────────────────────────────────
all_companies = [
    "A·101","Abalifish","Abdi İbrahim","Agrobest","Ahlatcı Holding","Akedaş","Akçadağ Grup",
    "Akdeniz Chemson","Aktek","Alisan + Meram Un","Alpet","Altay Otomotiv","Alvimedica",
    "Anadolu Efes","ARCA","Arçelik","Aromsa","Art Holding","Arzum","Askale Çimento",
    "Aster Textile","Astor","ATM İstanbul","Aunde Teknik","Aves","Aydınlı","Balsu Gıda",
    "Beta Enerji","Betek","Beymen","Beşiktaş (BJK)","BİM","Bizle","Blue Projects",
    "Bordrill","Borusan Boru","Bozankaya","Boyner","Bülbim","Civil","Coşkunöz Holding",
    "Çelebi","Çelik Halat","Çetaş","Çimsa","DAP Yapı","DeFacto","Demirören","Dimes",
    "Doğan Trend","Doğanlar Mobilya","Dönmez Hammer","Döksan","Dream","Drogsan","ebebek",
    "EMAX","Enerjisa","Enpay","Er-Bakır","Eren Enerji","Eren Perakende","Ermaş","ETİ",
    "Europower Enerji","Farmasi","Fassan","Federal Mogul","Fenerbahçe","FLO",
    "Fraport TAV Antalya","Gabba Home","Gen","Genvera Enerji","Getir","Göltaş",
    "Gümüş Grup","Gümüşdoğa","Hassan","Havaş","Haver","HEMA Endüstri","Hesapçıoğlu",
    "Horoz Lojistik","IDO","İlbak","İnci GS Yuasa","Karbosan","Kombi Klima Shop",
    "Konveyor","Mapa","Mapeks Organics","Maritaş","Martaş","Martur Fompak","Mavi",
    "Maya","Med Lojistik","Mega","Meysu","MGM Ceramics","Migros","Mogul","Murat Lojistik",
    "Netaş","Nobel","Noordzee","Norm Civata","Odelo","OnBT","Orhan Holding","Orzax","OTC",
    "Paket Mutfak","Partsmax","Petrol Ofisi","Polimetal Madencilik","Sabancı Üniversitesi",
    "Sadal","Sahibinden.com","Sancak Inflight","Sarper","Savronik","Setas Color Center",
    "Shell","Sistem Alüminyum","Smart Güneş Teknolojileri","Standard Profil","Taha Giyim",
    "Tanoto","Tat Gıda","Tavuk Dünyası","Teknik Malzeme","Termoteknik","Tırsan",
    "TKG Otomotiv","Toksan Otomotiv","Trakya Döküm","Trendyol","Turka","Turktex",
    "Türkiye Sigorta","TYÖ","Unifree Duty Free","Venus","Vergo","Vestel","Volta",
    "Yapı Merkezi","Yaşar","Yemek Hane","Yeşilyurt Demir Çelik","Yiğitoğlu",
    "Yıldırım Group","Yilport Holding","Yörpaş","Yücel Boru","Zeren Group","Zorlu Enerji",
]

logo_map = {}
for name in all_companies:
    path = LOGOS + slug(name) + ".png"
    if os.path.exists(path):
        logo_map[name] = path

print(f"\nLogos available: {len(logo_map)} / {len(all_companies)}")
missing = [c for c in all_companies if c not in logo_map]
if missing:
    print("Still missing:", missing)

# ── Embed all logos as base64 in the HTML ────────────────────────────────────
print("\nEmbedding logos as base64 in HTML...")

b64_map = {}
for name, path in logo_map.items():
    with open(path, "rb") as f:
        b64_map[name] = "data:image/png;base64," + base64.b64encode(f.read()).decode()

# Build JS object string
js_entries = ",\n".join(f'  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v)}' for k,v in b64_map.items())
js_block = f"const LOGO_MAP = {{\n{js_entries}\n}};"

with open(HTML, "r", encoding="utf-8") as f:
    html = f.read()

# Replace the existing LOGO_MAP block
html = re.sub(
    r'// Local logos extracted from screenshots\nconst LOGO_MAP = \{.*?\};',
    js_block,
    html,
    flags=re.DOTALL
)

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Done! HTML updated with {len(b64_map)} base64 logos.")
