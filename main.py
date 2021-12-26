import lib_classifier as classify
import lib_component as comp

def setup():
    # Set sebagai variabel global agar dapat diakses dari luar
    global kamera, load_cell, buzzer, lcd
    # Inisialisasi sensor dan aktuator
    kamera = comp.Kamera(server = "http://172.16.0.12")
    load_cell = comp.LoadCell(dout_pin = 5, sck_pin = 6, rasio = 221.33)
    #lcd = comp.LCD(kolom = 16, baris = 2, alamat = 0x27)
    buzzer = comp.Buzzer(pin = 13)

def loop():
    # Berat minimum dimana timbangan dianggap berisi (gram)
    berat_minimum = 2
    # Berat hasil pengukuran sebelumnya
    berat_sebelum = 0

    while True:
        berat_sekarang = load_cell.timbang()
        if berat_sebelum < berat_minimum <= berat_sekarang:
            print(f"Berat timbangan (berisi): {berat_sekarang}")
            buzzer.bunyi()
            #kamera.potret()
        else:
            print(f"Berat timbangan (kosong): {berat_sekarang}")

if __name__ == "__main__":
    setup()
    loop()