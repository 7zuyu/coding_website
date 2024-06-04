// Mendefinisikan elemen hasil
const resultDiv = document.getElementById("result");

// Menangani peristiwa klik pada peta
function onMapClick(e) {
    const latitude = e.latlng.lat;
    const longitude = e.latlng.lng;

    // Kirim data latitude dan longitude ke server
    sendDataToServer(latitude, longitude);
}

// Fungsi untuk mengirim data ke server
function sendDataToServer(latitude, longitude) {
    // Buat objek XMLHttpRequest
    const xhr = new XMLHttpRequest();

    // Tentukan URL endpoint Anda di sini
    const url = "file:///D:/Tugas%20Akhir/coding_website/luasatapbangunan.html";

    // Tentukan metode dan URL endpoint
    xhr.open("POST", url, true);

    // Tentukan tindakan yang akan diambil setelah permintaan selesai
    xhr.onload = function () {
        if (xhr.status === 200) {
            // Tanggapan dari server
            const response = xhr.responseText;
            // Tampilkan hasil di dalam div
            resultDiv.innerHTML = response;
        } else {
            // Tanggapan dari server gagal
            resultDiv.innerHTML = "Gagal mengirim data ke server.";
        }
    };

    // Atur header permintaan
    xhr.setRequestHeader("Content-Type", "application/json");

    // Data yang akan dikirim ke server
    const data = JSON.stringify({ latitude: latitude, longitude: longitude });

    // Kirim permintaan
    xhr.send(data);
}

// Memasang event listener untuk klik pada peta
map.on('click', onMapClick);
