#!/usr/bin/env python3
# student_manager.py
# Simple Student Grade Manager — single-file, no external libs required

import csv
import os
from typing import List, Dict

CSV_FILE = "students_data.csv"
FIELDNAMES = ["nim", "name", "prodi", "scores"]  # scores stored as "matkul1:score1;matkul2:score2"


# ---------- Utilities ----------
def clear_screen():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass


def parse_scores(scores_str: str) -> Dict[str, float]:
    """Parse 'matkul:score;matkul2:score2' -> dict"""
    d = {}
    if not scores_str:
        return d
    for part in scores_str.split(";"):
        if not part.strip():
            continue
        if ":" not in part:
            continue
        matkul, val = part.split(":", 1)
        matkul = matkul.strip()
        try:
            valf = float(val.strip())
        except ValueError:
            continue
        d[matkul] = valf
    return d


def scores_to_string(d: Dict[str, float]) -> str:
    return ";".join(f"{k}:{v}" for k, v in d.items())


# ---------- CSV I/O ----------
def load_all() -> List[Dict]:
    items = []
    if not os.path.exists(CSV_FILE):
        return items
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, fieldnames=FIELDNAMES)
        for row in reader:
            # if file has header row matching FIELDNAMES, skip header detection
            # We assume rows all map to fields
            nim = row.get("nim", "").strip()
            if nim == "" or nim.lower() == "nim":
                # skip malformed/header
                continue
            item = {
                "nim": nim,
                "name": row.get("name", "").strip(),
                "prodi": row.get("prodi", "").strip(),
                "scores": parse_scores(row.get("scores", "").strip())
            }
            items.append(item)
    return items


def save_all(items: List[Dict]):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        # write rows (no header to keep simple)
        for it in items:
            writer.writerow({
                "nim": it["nim"],
                "name": it["name"],
                "prodi": it["prodi"],
                "scores": scores_to_string(it["scores"])
            })


# ---------- CRUD and helpers ----------
def find_by_nim(items: List[Dict], nim: str):
    for i, it in enumerate(items):
        if it["nim"] == nim:
            return i, it
    return -1, None


def add_student(items: List[Dict]):
    nim = input("Masukkan NIM: ").strip()
    if not nim:
        print("NIM kosong. Batal.")
        return
    idx, _ = find_by_nim(items, nim)
    if idx != -1:
        print("NIM sudah ada.")
        return
    name = input("Nama: ").strip()
    prodi = input("Prodi: ").strip()
    # optionally add first score
    add_first = input("Tambah nilai mata kuliah sekarang? (y/n): ").strip().lower()
    scores = {}
    if add_first == "y":
        matkul = input("Nama mata kuliah: ").strip()
        try:
            nilai = float(input("Nilai (angka): ").strip())
            scores[matkul] = nilai
        except ValueError:
            print("Nilai tidak valid, diabaikan.")
    items.append({"nim": nim, "name": name, "prodi": prodi, "scores": scores})
    save_all(items)
    print("Mahasiswa ditambahkan.")


def add_score(items: List[Dict]):
    nim = input("Masukkan NIM: ").strip()
    idx, it = find_by_nim(items, nim)
    if idx == -1:
        print("Mahasiswa tidak ditemukan.")
        return
    matkul = input("Nama mata kuliah: ").strip()
    if not matkul:
        print("Nama mata kuliah kosong.")
        return
    try:
        nilai = float(input("Nilai (angka): ").strip())
    except ValueError:
        print("Nilai harus angka.")
        return
    # gunakan set behavior: matkul unik (overwrite jika sama)
    it["scores"][matkul] = nilai
    save_all(items)
    print("Nilai ditambahkan/diupdate.")


def edit_score(items: List[Dict]):
    nim = input("Masukkan NIM: ").strip()
    idx, it = find_by_nim(items, nim)
    if idx == -1:
        print("Mahasiswa tidak ditemukan.")
        return
    if not it["scores"]:
        print("Belum ada mata kuliah untuk mahasiswa ini.")
        return
    print("Daftar mata kuliah:")
    for m in it["scores"]:
        print(" -", m, ":", it["scores"][m])
    matkul = input("Pilih mata kuliah yang akan diubah: ").strip()
    if matkul not in it["scores"]:
        print("Mata kuliah tidak ditemukan.")
        return
    try:
        nilai = float(input("Masukkan nilai baru: ").strip())
    except ValueError:
        print("Nilai harus angka.")
        return
    it["scores"][matkul] = nilai
    save_all(items)
    print("Nilai diupdate.")


def delete_student(items: List[Dict]):
    nim = input("Masukkan NIM yang akan dihapus: ").strip()
    before = len(items)
    items[:] = [it for it in items if it["nim"] != nim]
    if len(items) < before:
        save_all(items)
        print("Mahasiswa dan semua nilainya dihapus.")
    else:
        print("NIM tidak ditemukan.")


def search_student(items: List[Dict]):
    nim = input("Masukkan NIM untuk dicari: ").strip()
    idx, it = find_by_nim(items, nim)
    if idx == -1:
        print("Tidak ditemukan.")
        return
    print_student(it)


def print_student(it: Dict):
    print(f"NIM: {it['nim']}")
    print(f"Nama: {it['name']}")
    print(f"Prodi: {it['prodi']}")
    if not it["scores"]:
        print("Belum ada nilai.")
    else:
        print("Nilai:")
        for m, v in it["scores"].items():
            print(f"  - {m}: {v}")
        avg = sum(it["scores"].values()) / len(it["scores"]) if it["scores"] else 0
        print(f"Rata-rata: {avg:.2f}")


def list_all(items: List[Dict]):
    if not items:
        print("Data kosong.")
        return
    for it in items:
        print("-" * 30)
        print_student(it)
    print("-" * 30)


# ---------- Main loop ----------
def main():
    items = load_all()
    while True:
        print("\n=== Student Grade Manager ===")
        print("1) Tambah Mahasiswa")
        print("2) Tambah/Update Nilai Mata Kuliah")
        print("3) Edit Nilai Mata Kuliah")
        print("4) Hapus Mahasiswa (beserta nilai)")
        print("5) Cari Mahasiswa (NIM)")
        print("6) Tampilkan Semua")
        print("7) Keluar")
        choice = input("Pilih (1-7): ").strip()
        if choice == "1":
            add_student(items)
        elif choice == "2":
            add_score(items)
        elif choice == "3":
            edit_score(items)
        elif choice == "4":
            delete_student(items)
        elif choice == "5":
            search_student(items)
        elif choice == "6":
            list_all(items)
        elif choice == "7":
            print("Selesai. Data tersimpan ke:", CSV_FILE)
            break
        else:
            print("Pilihan tidak valid. Coba lagi.")


if __name__ == "__main__":
    main()
