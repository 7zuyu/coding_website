import pandas as pd

# Baca file Excel
file_path = 'data1.xlsx'
df = pd.read_excel(file_path)

# Cetak nama kolom untuk memastikan nama yang benar
print("Nama kolom dalam file Excel:", df.columns)

# Asumsikan nama kolom adalah 'latitude' dan 'longitude', sesuaikan jika berbeda
latitude_col = 'latitude'
longitude_col = 'longitude'

# Pastikan nama kolom sesuai dengan yang ada di file Excel
if latitude_col not in df.columns or longitude_col not in df.columns:
    raise KeyError("Nama kolom tidak ditemukan dalam file Excel. Periksa nama kolom dan coba lagi.")

# Inisialisasi variabel untuk nilai latitude selanjutnya
next_latitude = df[latitude_col].iloc[-1] + 1

# DataFrame baru untuk menyimpan baris tambahan
new_rows = []

# Loop hingga nilai longitude di bawah 10
while df[longitude_col].iloc[-1] < 10:
    # Tambahkan baris baru dengan latitude meningkat dan longitude tetap 1
    new_rows.append({latitude_col: next_latitude, longitude_col: 1})
    next_latitude += 1

# Konversi list of dicts ke DataFrame
new_rows_df = pd.DataFrame(new_rows)

# Gabungkan DataFrame asli dengan DataFrame baru
df = pd.concat([df, new_rows_df], ignore_index=True)

# Simpan hasil ke file Excel baru
df.to_excel('data2.xlsx', index=False)
