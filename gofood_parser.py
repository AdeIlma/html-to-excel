"""
gofood_parser.py
-----------------
Fungsi-fungsi untuk mengekstrak daftar produk (nama, kategori, harga) dari
file HTML halaman restoran/toko GoFood (hasil "Save Page As" dari browser),
lalu mengelompokkannya ke dalam kategori sederhana (Anggur, Bir, Whisky, dst).

Sumber data: GoFood menyimpan seluruh data toko (termasuk katalog produk)
di dalam tag <script id="__NEXT_DATA__" type="application/json">...</script>
pada halaman. Fungsi di sini mencari tag tersebut, mem-parsing JSON-nya, lalu
mengambil outlet -> catalog -> sections -> items.
"""

import re
import json
import pandas as pd

# ---------------------------------------------------------------------------
# ATURAN KATEGORISASI
# ---------------------------------------------------------------------------
# Setiap kategori punya daftar pola regex (huruf kecil) yang dicocokkan ke
# nama produk. Urutan penting: aturan di atas dicek lebih dulu.
# Silakan tambah/ubah sendiri sesuai jenis produk toko kamu.
CATEGORY_RULES = [
    ("Anggur", [
        r"anggur", r"newport", r"tomi stanley", r"alimi bintang kuntul",
    ]),
    ("Soju", [r"soju"]),
    ("Bir", [
        r"\bbeer\b", r"\bbir\b", r"guinness", r"heineken", r"radler", r"stout",
    ]),
    ("Whisky", [r"whisky", r"whiskey", r"jameson", r"red label"]),
    ("Vodka", [r"vodka"]),
    ("Rum", [r"\brum\b", r"bacardi", r"captain morgan"]),
    ("Gin", [r"\bgin\b", r"gordons"]),
    ("Brandy", [r"brandy"]),
    ("Liqueur / RTD", [r"jagermeister", r"\bvibe\b"]),
    ("Gelas", [r"sloki", r"\bglass\b", r"\bshoot\b", r"\bshot\b"]),
]


def categorize(product_name: str) -> str:
    """Tentukan kategori produk berdasarkan nama produk (best-effort)."""
    name = product_name.lower()
    for category, patterns in CATEGORY_RULES:
        for pattern in patterns:
            if re.search(pattern, name):
                return category
    return "Lainnya"


def extract_products_from_html(html_content: str):
    """
    Ambil daftar produk unik (nama & harga) dari isi HTML halaman GoFood.

    Mengembalikan list of dict: [{"name": ..., "price": ...}, ...]
    Mengembalikan None kalau tidak ditemukan data __NEXT_DATA__ (berarti file
    HTML bukan hasil simpan halaman GoFood yang lengkap).
    """
    match = re.search(
        r'__NEXT_DATA__"\s*type="application/json">(.*?)</script>',
        html_content,
        re.DOTALL,
    )
    if not match:
        return None

    try:
        data = json.loads(match.group(1))
        outlet = data["props"]["pageProps"]["outlet"]
        sections = outlet.get("catalog", {}).get("sections", [])
    except (KeyError, json.JSONDecodeError, TypeError):
        return None

    seen_uids = set()
    products = []
    for section in sections:
        for item in section.get("items", []):
            uid = item.get("uid")
            # Lewati duplikat: GoFood sering menampilkan ulang item terlaris
            # di section "populer" selain di section aslinya (mis. "Drinks").
            if uid in seen_uids:
                continue
            seen_uids.add(uid)

            name = item.get("displayName", "").strip()
            price = item.get("price", {}).get("units", 0)
            if not name:
                continue

            products.append({"name": name, "price": price})

    return products


def build_dataframe(store_files: dict) -> pd.DataFrame:
    """
    store_files: dict {nama_toko: isi_html_string}
    Mengembalikan DataFrame gabungan semua toko dengan kolom:
    Toko, Produk, Kategori, Harga
    Toko yang gagal di-parse akan dilewati (bukan error) dan nama-namanya
    dikembalikan lewat parameter kedua (failed_stores).
    """
    rows = []
    failed_stores = []

    for store_name, html_content in store_files.items():
        products = extract_products_from_html(html_content)
        if products is None:
            failed_stores.append(store_name)
            continue
        for p in products:
            rows.append({
                "Toko": store_name,
                "Produk": p["name"],
                "Kategori": categorize(p["name"]),
                "Harga": p["price"],
            })

    df = pd.DataFrame(rows, columns=["Toko", "Produk", "Kategori", "Harga"])
    return df, failed_stores
