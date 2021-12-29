import lib_component as comp
import lib_classifier as model
import lib_api as api

# User dan password autentikasi FatSecret
fs_client_id = "REMOVED"
fs_client_secret = "REMOVED"

def setup():
    # Set sebagai variabel global agar dapat diakses dari luar
    global kamera, load_cell, buzzer, lcd, tflite, fatsecret, stats
    # Inisialisasi sensor dan aktuator
    kamera = comp.Kamera(server = "http://172.16.0.11", folder_simpan = "capture")
    load_cell = comp.LoadCell(dout_pin = 5, sck_pin = 6, rasio = 221.33)
    lcd = comp.LCD(kolom = 16, baris = 2, alamat = 0x27)
    buzzer = comp.Buzzer(pin = 19)
    # Inisialisasi model klasifikasi dari file
    tflite = model.Classifier("config/model_unquant.tflite", "config/food_label.txt")
    # Inisialisasi FatSecret API dan simpan akses token ke dalam file
    fatsecret = api.FatSecret(fs_client_id, fs_client_secret, "config/fatsecret_token.txt")
    # File statistik makanan untuk dibaca NodeRED
    #stats = api.CsvHelper("config/food_stats.csv")

def loop():
    # Berat minimum dimana timbangan dianggap berisi (gram)
    berat_minimum = 2
    # Berat hasil pengukuran sebelumnya
    berat_sebelum = 0

    while True:
        berat_sekarang = load_cell.timbang()
        # Bila timbangan berisi maka...
        if berat_sebelum < berat_minimum <= berat_sekarang:
            print(f"Berat timbangan (telah diisi): {berat_sekarang}")
            # Tunggu X detik lalu potret dan klasifikasi makanan
            file_gambar = kamera.potret(3)
            jenis_makanan = tflite.klasifikasi(file_gambar)
            # Dapatkan estimasi kalori per gram dari id makanan paling relevan
            kalori = fatsecret.estimasi_kalori(fatsecret.cari_makanan(jenis_makanan, 20, True))
            # Simpan jenis makanan dan estimasi kalori total
            info_makanan = f"{jenis_makanan}\nKalori: {round(kalori * berat_sekarang)}"
            # Tampilkan info dan berat makanan ke terminal
            print(info_makanan + f"\nBerat: {berat_sekarang}")
            # Nyalakan buzzer sebagai indikasi berhasil
            buzzer.bunyi()
            # Tampilkan info makanan ke LCD selama X detik
            lcd.tulis_nyala(info_makanan, 1, 5)
            # Tulis hasil info makanan saat ini ke file statistik NodeRED
            #stats.tambah_csv(jenis_makanan, berat_sekarang, kalori * berat_sekarang)
        elif berat_minimum < berat_sebelum:
            print(f"Berat timbangan (isi belum berubah): {berat_sekarang}")
        else:
            print(f"Berat timbangan (kosong): {berat_sekarang}")
        # Simpan berat saat ini untuk perulangan selanjutnya
        berat_sebelum = berat_sekarang

if __name__ == "__main__":
    # while True:
    #     # Untuk keperluan training awal jenis makanan
    #     kamera = comp.Kamera(server = "http://172.16.0.11", folder_simpan = "training")
    #     tanya = input("Tekan ENTER untuk memotret foto...")
    #     kamera.potret()

    # Program utama
    setup()
    loop()