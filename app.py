"""
Aplikasi Streamlit: Ekstrak Produk & Harga dari Halaman HTML GoFood
--------------------------------------------------------------------
Cara pakai:
1. Buka halaman toko GoFood di browser (Chrome/Edge), tekan Ctrl+S,
   pilih format "Webpage, HTML Only" atau "Complete", simpan sebagai .html
2. Upload file .html tersebut di aplikasi ini (bisa lebih dari satu toko sekaligus)
3. Isi nama tokonya masing-masing
4. Klik "Proses & Buat Excel", lalu download hasilnya

Jalankan dengan:
    streamlit run app.py
"""

import streamlit as st
from gofood_parser import build_dataframe
from excel_writer import dataframe_to_excel_bytes

st.set_page_config(page_title="GoFood HTML ke Excel", page_icon="🛒", layout="centered")

st.title("🛒 GoFood HTML ke Excel")
st.write(
    "Upload file HTML halaman toko GoFood (hasil *Save Page As* dari browser), "
    "aplikasi ini akan mengekstrak **nama produk, kategori, dan harga** ke dalam "
    "satu file Excel. Bisa upload beberapa toko sekaligus."
)

with st.expander("ℹ️ Cara ambil file HTML dari GoFood"):
    st.markdown(
        """
        1. Buka halaman toko GoFood yang ingin diambil datanya di browser (Chrome/Edge).
        2. Tunggu sampai daftar menu produk **selesai dimuat**.
        3. Tekan **Ctrl+S** (Windows) atau **Cmd+S** (Mac).
        4. Pilih format **"Webpage, Complete"** atau **"Webpage, HTML Only"**.
        5. Upload file `.html` yang dihasilkan (bukan folder `_files`-nya) di bawah ini.
        """
    )

uploaded_files = st.file_uploader(
    "Upload file HTML (bisa lebih dari 1 file / toko)",
    type=["html", "htm"],
    accept_multiple_files=True,
)

store_files = {}

if uploaded_files:
    st.subheader("Nama Toko")
    st.caption("Isi nama toko untuk masing-masing file yang diupload.")
    for i, file in enumerate(uploaded_files):
        default_name = file.name.rsplit(".", 1)[0].replace("_", " ")
        store_name = st.text_input(
            f"Nama toko untuk file: `{file.name}`",
            value=default_name,
            key=f"store_name_{i}",
        )
        html_content = file.read().decode("utf-8", errors="ignore")
        store_files[store_name or default_name] = html_content

    st.divider()

    if st.button("🚀 Proses & Buat Excel", type="primary"):
        with st.spinner("Memproses file..."):
            df, failed_stores = build_dataframe(store_files)

        if failed_stores:
            st.warning(
                "⚠️ Toko berikut **gagal diproses** (kemungkinan file HTML tidak "
                "lengkap / bukan halaman GoFood yang valid): "
                + ", ".join(f"`{s}`" for s in failed_stores)
            )

        if df.empty:
            st.error(
                "Tidak ada produk yang berhasil diambil dari file yang diupload. "
                "Pastikan file HTML disimpan setelah daftar menu selesai dimuat."
            )
        else:
            st.success(f"Berhasil! {len(df)} produk ditemukan dari {df['Toko'].nunique()} toko.")

            # Ringkasan per kategori
            st.subheader("Ringkasan per Kategori")
            summary = (
                df.groupby("Kategori")
                .agg(Jumlah_Produk=("Produk", "count"), Harga_Rata2=("Harga", "mean"))
                .reset_index()
                .sort_values("Jumlah_Produk", ascending=False)
            )
            st.dataframe(summary, use_container_width=True, hide_index=True)

            st.subheader("Semua Produk")
            st.dataframe(df, use_container_width=True, hide_index=True)

            excel_bytes = dataframe_to_excel_bytes(df)
            st.download_button(
                label="📥 Download Excel",
                data=excel_bytes,
                file_name="produk_gofood.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
else:
    st.info("Silakan upload minimal 1 file HTML untuk mulai.")
