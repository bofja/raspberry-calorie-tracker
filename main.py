import lib_component as comp
import lib_classifier as model
import lib_api as api

# User dan password autentikasi FatSecret
fs_client_id = "REMOVED"
fs_client_secret = "REMOVED"

def setup():
    # Set sebagai variabel global agar dapat diakses dari luar
    global kamera, load_cell, buzzer, lcd, tflite, fatsecret
    # Inisialisasi sensor dan aktuator
    kamera = comp.Kamera(server = "http://172.16.0.12", folder_simpan = "capture")
    load_cell = comp.LoadCell(dout_pin = 5, sck_pin = 6, rasio = 221.33)
    lcd = comp.LCD(kolom = 16, baris = 2, alamat = 0x27)
    buzzer = comp.Buzzer(pin = 13)
    # Inisialisasi model klasifikasi dari file
    tflite = model.Classifier("config/model_unquant.tflite")
    # Inisialisasi FatSecret API dan simpan akses token ke dalam file
    fatsecret = api.FatSecret(fs_client_id, fs_client_secret, "config/fatsecret_token.txt")

def loop():
    # Berat minimum dimana timbangan dianggap berisi (gram)
    berat_minimum = 2
    # Berat hasil pengukuran sebelumnya
    berat_sebelum = 0

    while True:
        berat_sekarang = load_cell.timbang()
        # Bila timbangan berisi maka...
        if berat_sebelum < berat_minimum <= berat_sekarang:
            print(f"Berat timbangan (berisi): {berat_sekarang}")
            # Potret dan klasifikasi gambar
            file_gambar = kamera.potret()
            jenis_makanan = tflite.klasifikasi(file_gambar)
            # Dapatkan estimasi kalori per gram
            kalori = fatsecret.estimasi_kalori(fatsecret.cari_makanan(jenis_makanan))
            # Tulis hasil akhir estimasi ke LCD dan nyalakan buzzer
            lcd.tulis(f"{jenis_makanan}\nKalori: {round(kalori * berat_sekarang)}")
            lcd.nyala(3) # Nyalakan LCD selama X detik (non-async)
            # Wkwk gabut
            buzzer.bunyi()
        else:
            print(f"Berat timbangan (kosong): {berat_sekarang}")

if __name__ == "__main__":
    setup()
    loop()