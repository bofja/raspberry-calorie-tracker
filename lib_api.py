# Digunakan saat mengirim dan menerima data ke FatSecret dan Node-RED
# Masukan untuk FatSecret berupa jenis makanan yang diklasifikasi TFLite
# TODO: Masukan untuk Node-RED berupa informasi gizi makanan dari FatSecret

# FatSecret
import requests
import requests.auth as rauth
# Node-RED
import time
import csv

class FatSecret:
    def __init__(self, client_id, client_secret, token_file = None):
        self.client_id = client_id
        self.client_secret = client_secret
        # Gunakan token dari file bila sudah ada
        if token_file: self.baca_token(token_file)
        # Minta token baru bila token kosong dan simpan ke file
        if not self.token: self.autentikasi(token_file)

    def baca_token(self, file):
        try:
            with open(file, "r") as f:
                # Simpan akses token dan hilangkan newline
                self.token = f.readline().rstrip()
            # Jangan pakai akses token bila sudah dihapus
            if self.token == "REMOVED": self.token = None
        except Exception:
            print("Terjadi kesalahan saat mengakses file token...")
            self.token = None

    def tulis_token(self, file, token):
        try:
            with open(file, "w") as f:
                # Tulis token ke dalam file
                f.write(token)
            return True
        except Exception:
            print("Terjadi kesalahan saat menulis file token...")
            return False
    
    def autentikasi(self, token_file = None):
        # Cek dokumentasi pada https://platform.fatsecret.com/api/Default.aspx?screen=rapih
        url = "https://oauth.fatsecret.com/connect/token"
        auth = rauth.HTTPBasicAuth(self.client_id, self.client_secret)
        data = { "grant_type": "client_credentials", "scope": "basic" }
        # Minta akses token baru ke server FatSecret
        respons = requests.post(url = url, auth = auth, data = data)
        if respons.status_code == 200:
            # Simpan akses token untuk digunakan nanti
            self.token = respons.json()["access_token"]
            # Simpan akses token ke file bila diperlukan
            if token_file: self.tulis_token(token_file, self.token)
        else:
            # Cek kode error pada https://platform.fatsecret.com/api/Default.aspx?screen=rapiec
            raise ConnectionError(f"Error {respons.status_code} saat meminta akses token...")

    def cari_makanan(self, nama_makanan, jumlah_maks = 20, ambil_pertama = False):
        url = "https://platform.fatsecret.com/rest/server.api"
        headers = { "Authorization": f"Bearer {self.token}" }
          # Lihat metode yang tersedia pada https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2
        data = { "method": "foods.search", "search_expression": nama_makanan, "format": "json" }
        respons = requests.post(url = url, headers = headers, data = data)
        if respons.status_code == 200:
            list_makanan = respons.json()["foods"]["food"]
            # Cukup tampilkan X buah makanan bila diminta
            list_makanan = list_makanan[:jumlah_maks] if jumlah_maks > 0 else list_makanan
            if ambil_pertama == False:
                # Pilih makanan berdasarkan hasil pencarian (menghasilkan id makanan)
                for makanan in list_makanan:
                    if makanan["food_type"] == "Brand": print(makanan["brand_name"], end = ": ")
                    print(f'{makanan["food_name"]} [id: {makanan["food_id"]}]')
                    print(f'{makanan["food_url"]}\n')
                return int(input("Ketikkan id makanan yang dipilih: "))
            else:
                # Ambil id makanan terkecil yang didapat dari list makanan
                # Id makanan terkecil umumnya merupakan makanan asli (bukan brand tertentu)
                return min([ int(makanan["food_id"]) for makanan in list_makanan ])
        else:
            # Cek kode error pada https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2&method=foods.search
            raise ConnectionError(f"Error {respons.status_code} saat memanggil foods.search...")

    def info_makanan(self, id_makanan):
        url = "https://platform.fatsecret.com/rest/server.api"
        headers = { "Authorization": f"Bearer {self.token}" }
        # Lihat metode yang tersedia pada https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2
        data = { "method": "food.get.v2", "food_id": id_makanan, "format": "json" }
        respons = requests.post(url = url, headers = headers, data = data)
        if respons.status_code == 200:
            return respons.json()["food"]
        else:
            # Cek kode error pada https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2&method=food.get.v2
           raise ConnectionError(f"Error {respons.status_code} saat memanggil food.get.v2...")
    
    # Dapatkan estimasi kalori per gram pada makanan
    def estimasi_kalori(self, id_makanan):
        info_makanan = self.info_makanan(id_makanan)
        if info_makanan:
            kalori = []
            # Dapatkan kalori untuk tiap-tiap takaran (ukuran) saji makanan
            for takaran in info_makanan["servings"]["serving"]:
                if takaran["metric_serving_unit"] == "g":
                    # Dapatkan estimasi kalori per gram jika satuan berupa gram
                    kalori.append(float(takaran["calories"]) / takaran["metric_serving_amount"])
            # Rata-ratakan kalori dari tiap-tiap takaran
            kalori = round(sum(kalori) / len(kalori), 3)
            return int(kalori) if kalori.is_integer() else kalori

# TODO: Baca statistik untuk Node-RED
class CsvHelper:
    def __init__(self, file_csv):
        # File CSV untuk operasi baca tulis
        self.file_csv = file_csv

    def impor_csv(self, lewati_satu = True):
        list_data = []
        # Buka file CSV sebagai input
        with open(self.file_csv, "r") as file:
            # Lewati baris pertama (header) bila diminta
            if lewati_satu: reader = list(csv.reader(file))[1:]
            else: reader = list(csv.reader(file))
            for bar in range(len(reader)):
                # Baca kolom-kolm tiap baris
                for kol in range(len(reader[bar])):
                    try:
                        if reader[bar][kol] in ("None", "NaN", ""):
                            # Konversi string kosong menjadi null
                            reader[bar][kol] = None
                        else:
                            # Konversi string lainnya menjadi float atau integer
                            reader[bar][kol] = float(reader[bar][kol])
                            if reader[bar][kol].is_integer():
                                reader[bar][kol] = int(reader[bar][kol])
                    except ValueError:
                        # Jangan konversi string bila tidak memungkinkan
                        pass
                # Tambahkan baris saat ini ke list data
                list_data.append(reader[bar])
        # Kembalikan data dalam bentuk list 2 dimensi
        return list_data

    def ekspor_csv(self, list_data, label = True, on_linux = False):
        # Hilangkan baris tambahan (\r\n) pada Windows
        nl = "\n" if on_linux else ""
        # Buka file CSV sebagai output (mode tulis)
        with open(self.file_csv, "w", newline = nl) as file:
            # Tulis nilai null (None) dan string kosong sebagai ""
            writer = csv.writer(file, delimiter = ",", quoting = csv.QUOTE_NONNUMERIC)
            # Tambahkan label (header) bila diminta
            if label: writer.writerow(["Waktu", "Nama", "Berat", "Kalori"])
            # Tulis data ke CSV berdasarkan list data
            writer.writerows(list_data)

    # Tambah baris baru ke file csv
    def tambah_csv(self, nama, berat, kalori_total, waktu = None, on_linux = False):
        # Hilangkan baris tambahan (\r\n) pada Windows
        nl = "\n" if on_linux else ""
        # Buka file CSV sebagai output (mode tulis)
        with open(self.file_csv, "a", newline = nl) as file:
            # Tulis nilai null (None) dan string kosong sebagai ""
            writer = csv.writer(file, delimiter = ",", quoting = csv.QUOTE_NONNUMERIC)
            # Dapatkan waktu saat ini bila waktu kosong
            if not waktu: waktu = int(time.time())
            # Tulis data ke CSV berdasarkan list data
            writer.writerow([waktu, nama, berat, kalori_total])