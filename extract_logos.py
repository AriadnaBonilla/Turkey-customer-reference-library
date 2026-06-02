from PIL import Image
import numpy as np
from scipy.ndimage import label, binary_dilation
import os, json

BASE  = "/Users/i755892/Desktop/Claude/Videos/"
OUT   = "/Users/i755892/Desktop/Claude/logos/"
os.makedirs(OUT, exist_ok=True)

# Company name for every extracted logo, in reading order (left→right, top→bottom)
MAPPINGS = {
    "Screenshot 2026-05-28 at 11.19.33.png": [
        "Abalifish", "Abdi İbrahim", "Beşiktaş (BJK)", "Agrobest", "Akçadağ Grup", "Akdeniz Chemson", "Aktek",
        "Alpet", "Alisan + Meram Un", "Altay Otomotiv", "Alvimedica", "Anadolu Efes", "ARCA", "Arçelik",
        "Aromsa", "Art Holding", "Arzum", "Fassan", "Aster Textile", "Astor", "Aunde Teknik",
        "Aves", "Aydınlı", "Bülbim", "Balsu Gıda", "Beta Enerji", "Betek", "Beymen",
        "BİM", "Borusan Boru", "Boyner", "Bozankaya", "Coşkunöz Holding", "Çelebi", "Çelik Halat",
        "DeFacto", "Dimes", "Doğan Trend", "Doğanlar Mobilya", "Dönmez Hammer", "Drogsan", "ebebek",
    ],
    "Screenshot 2026-05-28 at 11.19.40.png": [
        "Enpay", "Er-Bakır", "Eren Enerji", "ETİ", "Federal Mogul", "Fenerbahçe",
        "FLO", "Fraport TAV Antalya", "Gabba Home", "Gen", "Genvera Enerji", "Getir", "Göltaş",
        "Gümüş Grup", "Hassan", "Havaş", "Haver", "HEMA Endüstri", "Horoz Lojistik",
        "IDO", "İlbak", "İnci GS Yuasa",
        "Karbosan",
        "Konveyor",
    ],
    "Screenshot 2026-05-28 at 11.19.59.png": [
        "Mapa", "Maritaş", "Martaş", "Martur Fompak", "Mavi", "Med Lojistik", "Mega",
        "MGM Ceramics", "Migros", "Mogul", "Çimsa", "Netaş", "Nobel", "Norm Civata",
        "OnBT", "Orhan Holding", "Orzax", "OTC", "Partsmax", "Petrol Ofisi", "Polimetal Madencilik",
        "Zorlu Enerji", "Sahibinden.com", "Sarper", "Setas Color Center", "Sistem Alüminyum", "Shell", "Smart Güneş Teknolojileri",
        "Standard Profil", "Taha Giyim", "Tanoto", "Tat Gıda", "Tavuk Dünyası", "Teknik Malzeme", "Termoteknik",
        "Tırsan", "TKG Otomotiv", "Toksan Otomotiv", "Trakya Döküm", "Trendyol", "Turka", "Turktex",
    ],
    "Screenshot 2026-05-28 at 11.20.05.png": [
        "A·101", "Ahlatcı Holding", "Akedaş", "Askale Çimento", "ATM İstanbul", "Bizle", "Blue Projects",
        "Bordrill", "Civil", "Çetaş", "DAP Yapı", "Demirören", "Döksan", "Dream",
        "EMAX", "Eren Perakende", "Ermaş", "Europower Enerji", "Farmasi", "Gümüşdoğa", "Hesapçıoğlu",
        "Kombi Klima Shop", "Mapeks Organics", "Maya", "Meysu", "Murat Lojistik", "Noordzee", "Odelo",
        "Paket Mutfak", "Sadal", "Sancak Inflight", "Savronik", "Sabancı Üniversitesi", "Türkiye Sigorta",
        "TYÖ", "Vergo", "Vestel", "Yapı Merkezi", "Volta", "Yemek Hane", "Yeşilyurt Demir Çelik",
    ],
    "Screenshot 2026-05-28 at 11.20.11.png": [
        "Unifree Duty Free", "Venus", "Yaşar", "Yıldırım Group", "Yilport Holding", "Yiğitoğlu", "Yörpaş",
        "Yücel Boru", "Zeren Group", "Enerjisa",
    ],
}

def slug(name):
    return name.lower().replace(" ", "_").replace("·","").replace("İ","i").replace("ı","i").replace("ğ","g").replace("ü","u").replace("ş","s").replace("ö","o").replace("ç","c").replace("(","").replace(")","").replace(".","").replace(",","")

def extract_logos(img_path, row_thresh=60, dilation=18, min_area=800):
    img = Image.open(img_path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]

    # mask = not background (white/near-white)
    mask = ~((arr[:,:,0] > 242) & (arr[:,:,1] > 242) & (arr[:,:,2] > 242))

    # dilate to merge nearby parts of same logo
    dilated = binary_dilation(mask, iterations=dilation)

    labeled, n = label(dilated)
    bboxes = []
    for i in range(1, n + 1):
        rows = np.where((labeled == i).any(axis=1))[0]
        cols = np.where((labeled == i).any(axis=0))[0]
        if len(rows) == 0: continue
        r0, r1, c0, c1 = rows[0], rows[-1], cols[0], cols[-1]
        if (r1 - r0) * (c1 - c0) < min_area: continue
        bboxes.append((r0, r1, c0, c1))

    # group into visual rows
    rows_grouped = []
    for bbox in bboxes:
        cy = (bbox[0] + bbox[1]) // 2
        placed = False
        for row in rows_grouped:
            row_cy = sum((b[0]+b[1])//2 for b in row) / len(row)
            if abs(cy - row_cy) < row_thresh:
                row.append(bbox); placed = True; break
        if not placed:
            rows_grouped.append([bbox])

    rows_grouped.sort(key=lambda row: sum((b[0]+b[1])//2 for b in row) / len(row))
    for row in rows_grouped:
        row.sort(key=lambda b: (b[2]+b[3])//2)

    crops = []
    pad = 8
    for r0, r1, c0, c1 in (b for row in rows_grouped for b in row):
        cropped = img.crop((max(0,c0-pad), max(0,r0-pad), min(w,c1+pad), min(h,r1+pad)))
        crops.append(cropped)

    return crops

# --- run ---
name_to_file = {}
for fname, names in MAPPINGS.items():
    fpath = BASE + fname
    crops = extract_logos(fpath)
    print(f"{fname}: extracted {len(crops)} logos, expected {len(names)}")
    for i, (crop, name) in enumerate(zip(crops, names)):
        sname = slug(name) + ".png"
        crop.save(OUT + sname)
        name_to_file[name] = "logos/" + sname

# save mapping for HTML use
with open("/Users/i755892/Desktop/Claude/logo_map.json", "w") as f:
    json.dump(name_to_file, f, ensure_ascii=False, indent=2)
print("Done. Saved", len(name_to_file), "logos.")
