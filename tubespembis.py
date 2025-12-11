import streamlit as st
import csv
import os
from typing import Dict, List

CSV_FILE = "students_data.csv"
FIELDNAMES = ["nim", "name", "prodi", "scores"]


# -------------------------
# Utilities
# -------------------------
def parse_scores(scores_str: str) -> Dict[str, float]:
    d = {}
    if not scores_str:
        return d
    for part in scores_str.split(";"):
        if ":" not in part:
            continue
        matkul, val = part.split(":", 1)
        try:
            d[matkul.strip()] = float(val.strip())
        except:
            pass
    return d


def scores_to_string(d: Dict[str, float]) -> str:
    return ";".join(f"{k}:{v}" for k, v in d.items())


# -------------------------
# Load & Save CSV
# -------------------------
def load_all() -> List[Dict]:
    items = []
    if not os.path.exists(CSV_FILE):
        return items
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, fieldnames=FIELDNAMES)
        for row in reader:
            nim = row.get("nim", "").strip()
            if nim == "" or nim.lower() == "nim":
                continue
            items.append({
                "nim": nim,
                "name": row.get("name", "").strip(),
                "prodi": row.get("prodi", "").strip(),
                "scores": parse_scores(row.get("scores", "").strip())
            })
    return items


def save_all(items: List[Dict]):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        for it in items:
            writer.writerow({
                "nim": it["nim"],
                "name": it["name"],
                "prodi": it["prodi"],
                "scores": scores_to_string(it["scores"])
            })


# -------------------------
# Helper
# -------------------------
def find_by_nim(items, nim):
    for idx, it in enumerate(items):
        if it["nim"] == nim:
            return idx, it
    return -1, None


# -------------------------
# Streamlit App
# -------------------------
st.title("📘 Student Grade Manager (Streamlit Version)")

items = load_all()

menu = st.sidebar.radio(
    "Menu",
    ["Tambah Mahasiswa", "Tambah/Update Nilai", "Edit Nilai", "Hapus Mahasiswa", "Cari Mahasiswa", "Tampilkan Semua"]
)

# ===============================
# 1) Tambah Mahasiswa
# ===============================
if menu == "Tambah Mahasiswa":
    st.header("➕ Tambah Mahasiswa")

    nim = st.text_input("NIM")
    name = st.text_input("Nama")
    prodi = st.text_input("Prodi")

    add_score_now = st.checkbox("Tambah nilai sekarang?")
    scores = {}

    if add_score_now:
        matkul = st.text_input("Nama Mata Kuliah")
        nilai = st.number_input("Nilai", min_value=0.0, max_value=100.0)

        if matkul:
            scores[matkul] = nilai

    if st.button("Simpan"):
        idx, _ = find_by_nim(items, nim)
        if idx != -1:
            st.error("NIM sudah ada!")
        else:
            items.append({"nim": nim, "name": name, "prodi": prodi, "scores": scores})
            save_all(items)
            st.success("Mahasiswa ditambahkan.")


# ===============================
# 2) Tambah/Update Nilai
# ===============================
elif menu == "Tambah/Update Nilai":
    st.header("📝 Tambah / Update Nilai")

    nim = st.text_input("Masukkan NIM")
    idx, it = find_by_nim(items, nim)

    if it:
        matkul = st.text_input("Nama Mata Kuliah")
        nilai = st.number_input("Nilai", min_value=0.0, max_value=100.0)

        if st.button("Simpan Nilai"):
            it["scores"][matkul] = nilai
            save_all(items)
            st.success("Nilai berhasil ditambah / diupdate.")
    else:
        if nim:
            st.warning("Mahasiswa tidak ditemukan.")


# ===============================
# 3) Edit Nilai
# ===============================
elif menu == "Edit Nilai":
    st.header("✏️ Edit Nilai Mata Kuliah")

    nim = st.text_input("Masukkan NIM")
    idx, it = find_by_nim(items, nim)

    if it:
        if not it["scores"]:
            st.info("Mahasiswa belum punya nilai.")
        else:
            matkul = st.selectbox("Pilih Mata Kuliah", list(it["scores"].keys()))
            nilai_baru = st.number_input("Nilai Baru", value=it["scores"][matkul])

            if st.button("Update"):
                it["scores"][matkul] = nilai_baru
                save_all(items)
                st.success("Nilai berhasil diupdate.")
    else:
        if nim:
            st.warning("Mahasiswa tidak ditemukan.")


# ===============================
# 4) Hapus Mahasiswa
# ===============================
elif menu == "Hapus Mahasiswa":
    st.header("🗑️ Hapus Mahasiswa")

    nim = st.text_input("Masukkan NIM yang akan dihapus")
    if st.button("Hapus"):
        before = len(items)
        items = [it for it in items if it["nim"] != nim]
        if len(items) < before:
            save_all(items)
            st.success("Mahasiswa dihapus.")
        else:
            st.error("NIM tidak ditemukan.")


# ===============================
# 5) Cari Mahasiswa
# ===============================
elif menu == "Cari Mahasiswa":
    st.header("🔍 Cari Mahasiswa")

    nim = st.text_input("Masukkan NIM")
    idx, it = find_by_nim(items, nim)

    if it:
        st.subheader("Data Mahasiswa")
        st.write(f"**NIM:** {it['nim']}")
        st.write(f"**Nama:** {it['name']}")
        st.write(f"**Prodi:** {it['prodi']}")

        if it["scores"]:
            st.write("### Nilai")
            st.table([{"Mata Kuliah": m, "Nilai": v} for m, v in it["scores"].items()])
            avg = sum(it["scores"].values()) / len(it["scores"])
            st.write(f"**Rata-rata:** {avg:.2f}")
        else:
            st.info("Belum ada nilai.")
    else:
        if nim:
            st.warning("Data tidak ditemukan.")


# ===============================
# 6) Tampilkan Semua
# ===============================
elif menu == "Tampilkan Semua":
    st.header("📚 Semua Data Mahasiswa")

    if not items:
        st.info("Data kosong.")
    else:
        table = []
        for it in items:
            avg = (sum(it["scores"].values()) / len(it["scores"])) if it["scores"] else 0
            table.append({
                "NIM": it["nim"],
                "Nama": it["name"],
                "Prodi": it["prodi"],
                "Jumlah Mata Kuliah": len(it["scores"]),
                "Rata-rata": f"{avg:.2f}"
            })

        st.table(table)
