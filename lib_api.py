# Digunakan saat mengirim dan menerima data ke FatSecret dan Node-RED
# Masukan untuk FatSecret berupa jenis makanan yang diklasifikasi TFLite
# Masukan untuk Node-RED berupa informasi gizi makanan dari FatSecret

import requests
import requests.auth as rauth

user = "REMOVED"
password = "REMOVED"

class FatSecret:
    def __init__(self, client_id, client_secret, token_file = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.baca_token()
    
    def baca_token(self, file):
        try:
            with open(file, "r") as f:
                # Simpan akses token dan hilangkan newline
                self.token = f.readline().rstrip()
        except Exception:
            print("Terjadi kesalahan saat mengakses file token")
            self.token = None

    def tulis_token(self, file, token):
        try:
            with open(file, "w") as f:
                f.write(token)
            return True
        except Exception:
            print("Terjadi kesalahan saat menulis file token")
            return False
    
    def autentikasi(self, token_file = None):
        # Cek dokumentasi pada https://platform.fatsecret.com/api/Default.aspx?screen=rapih
        token_url = "https://oauth.fatsecret.com/connect/token"
        auth = rauth.HTTPBasicAuth(self.client_id, self.client_secret)
        data = { "grant_type": "client_credentials", "scope": "basic" }
        # Minta akses token baru ke server FatSecret
        respons = requests.post(url = token_url, auth = auth, data = data)
        if respons.status_code == 200:
            # Simpan akses token untuk digunakan nanti
            self.token = respons.json()["access_token"]
            # Simpan akses token ke file bila diperlukan
            if token_file: self.tulis_token(token_file, self.token)
        else:
            # Cek kode error pada https://platform.fatsecret.com/api/Default.aspx?screen=rapiec
            raise ConnectionError(f"Error {respons.status_code} saat menerima respons")
    
    def cari_makanan(self, nama):
        pass

Test = FatSecret(user, password)
Test.autentikasi()