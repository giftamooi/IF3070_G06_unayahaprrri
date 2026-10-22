# IF3070_G06_unayahaprrri

Tugas Besar 1 IF3070 Dasar Inteligensi Artifisial 2026/2027: penyelesaian persoalan pemuatan kendaraan ke kapal kargo dengan local search.

## Deskripsi

PT ~~Owen~~ Intim Line perlu menentukan kendaraan mana yang diangkut, serta posisi dan orientasi tiap kendaraan di geladak, agar total shipping fee maksimal. Persoalan ini diselesaikan dengan tiga algoritma local search:

- Hill-climbing (steepest ascent)
- Simulated annealing
- Genetic algorithm

Batasan yang dipakai di ketiga algoritma:

| Komponen | Nilai |
|---|---|
| Geladak kapal | matriks 5 baris × 7 kolom (35 sel) |
| Kapasitas kapal (`shipMaxCapacity`) | total berat ≤ 100 ton |
| Mobil | 1 × 2, 5 ton, 20 juta, 20 unit |
| Minibus | 1 × 3, 12 ton, 30 juta, 7 unit |
| Truk | 2 × 3, 30 ton, 60 juta, 5 unit |

Ukuran kendaraan ditulis untuk orientasi horizontal (baris × kolom). Pada orientasi vertikal, ukurannya ditukar.

Objective function adalah total shipping fee kendaraan yang ada di dalam kapal. Constraint yang berlaku: kendaraan tidak boleh saling tumpang tindih, harus berada di dalam batas geladak, dan total beratnya tidak boleh melebihi kapasitas kapal.

## Struktur repository

```
src/
  hill_climbing.py         Hill-climbing steepest ascent
  simulated_annealing.py   Simulated annealing
  genetic_algorithm.py     Genetic algorithm
output/
  output.hill_climbing/        hasil run hill-climbing
  output.simulated_annealing/  hasil run simulated annealing
  output.genetic_algorithm/    hasil run genetic algorithm (variasi populasi dan iterasi)
docs/                      laporan (.pdf)
```

## Setup

Program hanya memakai library bawaan Python, jadi tidak perlu `pip install`.

1. Pasang Python 3.10 atau lebih baru (sudah diuji dengan Python 3.11).
2. Clone repository:
   ```
   git clone https://github.com/giftamooi/IF3070_G06_unayahaprrri.git
   cd IF3070_G06_unayahaprrri
   ```

## Cara menjalankan

Jalankan dari root repository:

```
python src/hill_climbing.py
python src/simulated_annealing.py
python src/genetic_algorithm.py
```

Semua hasil ditampilkan di CLI: state awal dan state akhir (matriks geladak serta tabel kendaraan PLACED/UNPLACED), value, durasi, dan grafik.

- **Hill-climbing:** tidak meminta input. Program menjalankan 3 run dan menampilkan grafik value terhadap iterasi untuk setiap run.
- **Simulated annealing:** meminta suhu awal, laju pendinginan, suhu minimum, batas iterasi, dan batas iterasi tanpa perbaikan (untuk menghitung stuck). Program menjalankan 3 run (default) menampilkan grafik value dan grafik e^(ΔE/T) terhadap iterasi, dan di akhir ada tabel ringkasan semua run.
- **Genetic algorithm:** meminta jumlah populasi awal (minimal 2) dan jumlah generasi (minimal 1). Program menampilkan grafik fitness maksimum dan rata-rata populasi terhadap iterasi.

Jika karakter garis tabel atau grafik muncul berantakan di terminal Windows, jalankan dengan mode UTF-8:

```
python -X utf8 src/simulated_annealing.py
```

## Pembagian tugas

| Nama | NIM | Tugas |
|---|---|---|
| Endda Tsa Azzahra Syaifur | 18224094 | Genetic algorithm |
| Rafael Sean Hadipranoto | 18224100 | Simulated annealing |
| Gifta Mooira Prasharnissa | 18224106 | Hill-climbing |
