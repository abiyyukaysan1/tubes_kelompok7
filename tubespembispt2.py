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
# Premium Career Logic
# -------------------------
def career_recommendation(scores: Dict[str, float]) -> str:
    """Analisis nilai untuk memetakan potensi karier."""

    if not scores:
        return "Belum ada data nilai."

    # Mapping sederhana (bisa dikembangkan)
    avg = sum(scores.values()) / len(scores)

    if avg >= 85:
        return "Software Engineer / AI Engineer"
    elif avg >= 75:
        return "Data Analyst / Web Developer"
    elif avg >= 65:
        return "UI/UX Designer / QA Tester"
    else:
        return "Business Analyst / Customer Support"


# -------------------------
# Streamlit
# -------------------------
st.title("📘 Student Management System + Business Concept (Premium Feature)")

items = load_all()

# Initialize premium status
if "premium" not in st.session_state:
    st.session_state["premium"] = False

menu = st.sidebar.radio(
    "Menu",
    [
        "Tambah Mahasiswa",
        "Tambah/Update Nilai",
        "Edit Nilai",
        "Hapus Mahasiswa",
        "Cari Mahasiswa",
        "Tampilkan Semua",
        "Premium Center",
        "Career Recommendation (Premium)"
    ]
)


# --------------------- MENU UTAMA ---------------------

# Tambah Mahasiswa
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
        idx, _ = next(((i, x) for i, x in enumerate(items) if x["nim"] == nim), (-1, None))
        if idx != -1:
            st.error("NIM sudah ada!")
        else:
            items.append({"nim": nim, "name": name, "prodi": prodi, "scores": scores})
            save_all(items)
            st.success("Mahasiswa ditambahkan.")


# Tambah/Update Nilai
elif menu == "Tambah/Update Nilai":
    st.header("📝 Tambah / Update Nilai")

    nim = st.text_input("Masukkan NIM")
    data = next((x for x in items if x["nim"] == nim), None)

    if data:
        matkul = st.text_input("Nama Mata Kuliah")
        nilai = st.number_input("Nilai", min_value=0.0, max_value=100.0)

        if st.button("Simpan Nilai"):
            data["scores"][matkul] = nilai
            save_all(items)
            st.success("Nilai berhasil ditambah / diupdate.")
    else:
        if nim:
            st.warning("Mahasiswa tidak ditemukan.")


# Edit Nilai
elif menu == "Edit Nilai":
    st.header("✏️ Edit Nilai Mata Kuliah")

    nim = st.text_input("Masukkan NIM")
    data = next((x for x in items if x["nim"] == nim), None)

    if data:
        if not data["scores"]:
            st.info("Mahasiswa belum punya nilai.")
        else:
            matkul = st.selectbox("Pilih Mata Kuliah", list(data["scores"].keys()))
            nilai_baru = st.number_input("Nilai Baru", value=data["scores"][matkul])

            if st.button("Update"):
                data["scores"][matkul] = nilai_baru
                save_all(items)
                st.success("Nilai berhasil diupdate.")
    else:
        if nim:
            st.warning("Mahasiswa tidak ditemukan.")


# Hapus Mahasiswa
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


# Cari Mahasiswa
elif menu == "Cari Mahasiswa":
    st.header("🔍 Cari Mahasiswa")

    nim = st.text_input("Masukkan NIM")
    data = next((x for x in items if x["nim"] == nim), None)

    if data:
        st.subheader("Data Mahasiswa")
        st.write(f"**NIM:** {data['nim']}")
        st.write(f"**Nama:** {data['name']}")
        st.write(f"**Prodi:** {data['prodi']}")

        if data["scores"]:
            st.write("### Nilai")
            st.table([{"Mata Kuliah": m, "Nilai": v} for m, v in data["scores"].items()])
            avg = sum(data["scores"].values()) / len(data["scores"])
            st.write(f"**Rata-rata:** {avg:.2f}")
        else:
            st.info("Belum ada nilai.")
    else:
        if nim:
            st.warning("Data tidak ditemukan.")


# Tampilkan Semua
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


# --------------------- PREMIUM CENTER ---------------------
elif menu == "Premium Center":
    st.header("💎 Premium Center")

    if st.session_state.premium:
        st.success("Anda adalah pengguna PREMIUM! 🎉")
    else:
        st.warning("Anda belum premium.")

        if st.button("Upgrade ke Premium (Rp 49.000)"):
            st.session_state.premium = True
            st.success("Upgrade berhasil! Anda sekarang pengguna PREMIUM.")


# --------------------- CAREER RECOMMENDATION ---------------------
elif menu == "Career Recommendation (Premium)":
    st.header("🚀 Career Recommendation (Premium Feature)")

    if not st.session_state.premium:
        st.error("Akses ditolak. Anda harus menjadi pengguna PREMIUM untuk mengakses fitur ini.")
        st.stop()

    # Jika sudah premium:
    nim = st.text_input("Masukkan NIM")
    data = next((x for x in items if x["nim"] == nim), None)

    if data:
        st.subheader("Analisis Karier Berdasarkan Nilai")
        rec = career_recommendation(data["scores"])
        st.success(f"Rekomendasi Karier: **{rec}**")
    else:
        if nim:
            st.warning("Mahasiswa tidak ditemukan.")
