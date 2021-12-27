# Digunakan saat mengirim dan menerima data ke FatSecret dan Node-RED
# Masukan untuk FatSecret berupa jenis makanan yang diklasifikasi TFLite
# Masukan untuk Node-RED berupa informasi gizi makanan dari FatSecret

import requests
import requests.auth as rauth

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
            print("Terjadi kesalahan saat mengakses file token")
            self.token = None

    def tulis_token(self, file, token):
        try:
            with open(file, "w") as f:
                # Tulis token ke dalam file
                f.write(token)
            return True
        except Exception:
            print("Terjadi kesalahan saat menulis file token")
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
            raise ConnectionError(f"Error {respons.status_code} saat meminta akses token")

    def cari_makanan(self, nama_makanan, jumlah_maks = 20):
        url = "https://platform.fatsecret.com/rest/server.api"
        headers = { "Authorization": f"Bearer {self.token}" }
          # Lihat metode yang tersedia pada https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2
        data = { "method": "foods.search", "search_expression": nama_makanan, "format": "json" }
        respons = requests.post(url = url, headers = headers, data = data)
        if respons.status_code == 200:
            list_makanan = respons.json()["foods"]["food"]
            # Cukup tampilkan X buah makanan bila diminta
            list_makanan = list_makanan[:jumlah_maks] if jumlah_maks > 0 else list_makanan
            # Pilih makanan berdasarkan hasil pencarian (menghasilkan id makanan)
            for makanan in list_makanan:
                if makanan["food_type"] == "Brand": print(makanan["brand_name"], end = ": ")
                print(f'{makanan["food_name"]} [id: {makanan["food_id"]}]')
                print(f'{makanan["food_url"]}\n')
            return int(input("Ketikkan id makanan yang dipilih: "))
        else:
            # Cek kode error pada https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2&method=foods.search
            raise ConnectionError(f'Error {respons.status_code} saat memanggil "foods.search"')

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
           raise ConnectionError(f'Error {respons.status_code} saat memanggil "food.get.v2"')
    
    # Dapatkan estimasi kalori per gram pada makanan
    def estimasi_kalori(self, id_makanan):
        info_makanan = self.info_makanan(id_makanan)
        if info_makanan:
            kalori = []
            # Dapatkan kalori untuk tiap-tiap takaran (ukuran) saji makanan
            for takaran in info_makanan["servings"]["serving"]:
                if takaran["metric_serving_unit"] == "g":
                    # Dapatkan estimasi kalori per gram jika satuan berupa gram
                    kalori.append(float(takaran["calories"]) / float(takaran["metric_serving_amount"]))
            # Rata-ratakan kalori dari tiap-tiap takaran
            kalori = round(sum(kalori) / len(kalori), 3)
            return int(kalori) if kalori.is_integer() else kalori