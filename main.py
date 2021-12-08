import lib_komponen as comp

def setup():
    # Set sebagai variabel global agar dapat diakses dari luar
    global kamera, load_cell, buzzer, lcd
    # Inisialisasi sensor dan aktuator
    kamera = comp.Kamera(server = "http://172.16.0.12")
    load_cell = comp.LoadCell(dout_pin = 5, sck_pin = 6)
    #lcd = comp.LCD(kolom = 16, baris = 2, alamat = 0x27)
    buzzer = comp.Buzzer(pin = 13)

def loop():
    berat_minimum = 3
    berat_sebelum = 0

    while True:
        berat_sekarang = load_cell.timbang()
        if berat_sebelum < berat_minimum <= berat_sekarang:
            print(f"Berat makanan: {berat_sekarang}")
            buzzer.bunyi()
        else:
            print(f"Berat kosong: {berat_sekarang}")

    # menimbang = False
    # while True:
    #     berat = load_cell.timbang()
    #     if berat > 10 and menimbang == False:
    #         menimbang = True
    #         print(f"Berat makanan: {berat}")
    #         buzzer.bunyi()
    #         #kamera.potret()
    #     else:
    #         menimbang = False
    #         print("Timbangan kosong...")

if __name__ == "__main__":
    setup()
    loop()