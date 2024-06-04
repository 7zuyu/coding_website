import cv2
import numpy as np


def hitung_luas_area_keseluruhan(gambar):
    gray = cv2.cvtColor(gambar, cv2.COLOR_BGR2GRAY)

    _, thresholded = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    luas_total = 0
    for contour in contours:
        luas = cv2.contourArea(contour)
        luas_total += luas

    return contours, luas_total

def hitung_luas_area_tertentu(gambar, lower_color, upper_color):

    rgb = cv2.cvtColor(gambar, cv2.COLOR_BGR2RGB)

    # Buat masker untuk warna tertentu
    mask = cv2.inRange(rgb, lower_color, upper_color)

    # Temukan kontur objek berdasarkan masker
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    luas_total = 0
    for contour in contours:
        # Hitung luas setiap kontur
        luas = cv2.contourArea(contour)
        luas_total += luas

    return mask, contours, luas_total


def main():
    # Baca gambar
    gambar = cv2.imread('contoj.png')  # Ganti dengan path gambar yang sesuai

    # Hitung luas area keseluruhan
    contours_keseluruhan, luas_keseluruhan = hitung_luas_area_keseluruhan(gambar)

    # Rentang warna abu-abu dalam ruang warna RGB
    lower_color = np.array([245, 245, 245])  # Nilai minimum RGB untuk abu-abu
    upper_color = np.array([255, 255, 255])  # Nilai maksimum RGB untuk abu-abu

    # Hitung luas area dengan warna abu-abu
    mask, contours_tertentu, luas_tertentu = hitung_luas_area_tertentu(gambar, lower_color, upper_color)

    # Hitung persentase luas area atap bangunan yang tersedia
    if luas_keseluruhan > 0:
        persentase_luas = (luas_tertentu / luas_keseluruhan) * 100
    else:
        persentase_luas = 0

    # Tampilkan hasil persentase luas area yang tersedia
    print("Luas area keseluruhan dalam gambar: {} piksel persegi".format(luas_keseluruhan))
    print("Luas area tertentu dalam gambar: {} piksel persegi".format(luas_tertentu))
    print("Persentase luas area atap bangunan yang tersedia: {:.2f}%".format(persentase_luas))

    # Gambar kontur pada gambar asli untuk visualisasi
    gambar_kontur_keseluruhan = gambar.copy()
    cv2.drawContours(gambar_kontur_keseluruhan, contours_keseluruhan, -1, (0, 255, 0), 2)

    gambar_kontur_tertentu = gambar.copy()
    cv2.drawContours(gambar_kontur_tertentu, contours_tertentu, -1, (255, 0, 0), 2)

    # Tampilkan gambar asli, masker, dan gambar dengan kontur
    cv2.imshow('Gambar Asli', gambar)
    cv2.imshow('Masker Warna Abu-Abu', mask)
    cv2.imshow('Kontur Area Keseluruhan', gambar_kontur_keseluruhan)
    cv2.imshow('Kontur Area Tertentu', gambar_kontur_tertentu)

    # Tunggu hingga tombol ditekan dan tutup semua jendela
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()