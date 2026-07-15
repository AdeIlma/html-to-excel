# GoFood HTML ke Excel

Aplikasi Streamlit untuk mengubah file HTML halaman toko GoFood menjadi file
Excel berisi daftar produk, kategori, dan harga. Bisa upload beberapa toko sekaligus.

## Cara Install & Jalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Nanti akan terbuka otomatis di browser (biasanya http://localhost:8501).

## Cara Ambil File HTML dari GoFood

1. Buka halaman toko GoFood di browser (Chrome/Edge), tunggu sampai daftar
   menu selesai dimuat.
2. Tekan Ctrl+S (Windows) / Cmd+S (Mac).
3. Pilih format "Webpage, Complete" atau "Webpage, HTML Only".
4. Upload file `.html` yang tersimpan (bukan folder `_files`) ke aplikasi ini.

## Struktur File

- `app.py` — halaman utama Streamlit (UI: upload, input nama toko, tombol proses, download)
- `gofood_parser.py` — logika ekstraksi data produk dari HTML + aturan kategorisasi
- `excel_writer.py` — logika menulis DataFrame ke file Excel yang rapi (format Rupiah, warna header, dst)

## Menyesuaikan Kategori

Aturan kategori ada di `gofood_parser.py`, variabel `CATEGORY_RULES` di bagian
atas file. Tambahkan kata kunci (regex) sesuai jenis produk toko kamu kalau
ada produk yang masuk kategori "Lainnya" tapi seharusnya masuk kategori lain.
