# Used when sending and receiving data to FatSecret and NodeRED
# The input for FatSecret is a type of food classified by TFLite
# TODO: Input to NodeRED is food nutritional information from FatSecret

# FatSecret
import requests
import requests.auth as rauth
# NodeRED
import time
import csv

class FatSecret:
    def __init__(self, client_id, client_secret, token_file = None):
        self.client_id = client_id
        self.client_secret = client_secret
        # Use the token from the file if it already exists
        if token_file: self.baca_token(token_file)
        # Request a new token when the token is empty and save it to file
        if not self.token: self.autentikasi(token_file)

    def baca_token(self, file):
        try:
            with open(file, "r") as f:
                # Keep the access token and remove the newline
                self.token = f.readline().rstrip()
            # Keep the access token and remove the newline
            if self.token == "REMOVED": self.token = None
        except Exception:
            print("An error occurred while accessing the token file...")
            self.token = None

    def tulis_token(self, file, token):
        try:
            with open(file, "w") as f:
                # Write the token into a file
                f.write(token)
            return True
        except Exception:
            print("An error occurred while writing the token file...")
            return False
    
    def autentikasi(self, token_file = None):
        # Check the documentation on https://platform.fatsecret.com/api/Default.aspx?screen=rapih
        url = "https://oauth.fatsecret.com/connect/token"
        auth = rauth.HTTPBasicAuth(self.client_id, self.client_secret)
        data = { "grant_type": "client_credentials", "scope": "basic" }
        # Request a new access token to the FatSecret server
        respons = requests.post(url = url, auth = auth, data = data)
        if respons.status_code == 200:
            # Save the access token for later use
            self.token = respons.json()["access_token"]
            # Save token access to files when needed
            if token_file: self.tulis_token(token_file, self.token)
        else:
            # Check the error code on https://platform.fatsecret.com/api/Default.aspx?screen=rapiec
            raise ConnectionError(f"Error {respons.status_code} when requesting token access...")
     // cari_food      food_name max_count ambil_pertama
    def search_food(self, food_name, max_count = 20, take_first = False):
        url = "https://platform.fatsecret.com/rest/server.api"
        headers = { "Authorization": f"Bearer {self.token}" }
          # See available methods on https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2
        data = { "method": "foods.search", "search_expression": food_name, "format": "json" }
        respons = requests.post(url = url, headers = headers, data = data)
        if respons.status_code == 200:
            list_food = respons.json()["foods"]["food"]
            # Just display X items of food when prompted
            list_food = list_food[:max_count] if max_count > 0 else list_food
            if take_first == False:
                # Select food based on search results (generate food id)
                for food in list_food:
                    if food["food_type"] == "Brand": print(food["brand_name"], end = ": ")
                    print(f'{food["food_name"]} [id: {food["food_id"]}]')
                    print(f'{food["food_url"]}\n')
                return int(input("Type the selected food id: "))
            else:
                # Take the smallest food ID obtained from the food list
                # The smallest food ID is generally real food (not a particular brand)
                return min([ int(food["food_id"]) for food in list_food ])
        else:
            # Check the error code on https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2&method=foods.search
            raise ConnectionError(f"Error {respons.status_code} when calling foods.search...")

    def info_food(self, id_food):
        url = "https://platform.fatsecret.com/rest/server.api"
        headers = { "Authorization": f"Bearer {self.token}" }
        # See available methods on https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2
        data = { "method": "food.get.v2", "food_id": id_food, "format": "json" }
        respons = requests.post(url = url, headers = headers, data = data)
        if respons.status_code == 200:
            return respons.json()["food"]
        else:
            # Check the error code on https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2&method=food.get.v2
           raise ConnectionError(f"Error {respons.status_code} when calling food.get.v2...")
    
    # Get an estimate of the calories per gram of food
    def calorie_estimation(self, id_food):
        info_food = self.info_food(id_food)
        if info_food:
            kalori = []
            # Get calories for each serving size (size) of food
            for dose in info_food["servings"]["serving"]:
                if dose["metric_serving_unit"] == "g":
                    # Get an estimate of calories per gram if the units are grams
                    kalori.append(float(dose["calories"]) / float(dose["metric_serving_amount"]))
            # Average the calories from each serving
            kalori = round(sum(kalori) / len(kalori), 3)
            return int(kalori) if kalori.is_integer() else kalori

# TODO:Read the statistics for NodeRED
class CsvHelper:
    def __init__(self, file_csv):
        # CSV file for read write operations
        self.file_csv = file_csv

    def impor_csv(self, skip_one = True):
        list_data = []
        # Open a CSV file as input
        with open(self.file_csv, "r") as file:
            # Skip the first line (header) if requested
            if skip_one: reader = list(csv.reader(file))[1:]
            else: reader = list(csv.reader(file))
            for bar in range(len(reader)):
                # Read the columns of each row
                for kol in range(len(reader[bar])):
                    try:
                        if reader[bar][kol] in ("None", "NaN", ""):
                            # Convert empty string to null
                            reader[bar][kol] = None
                        else:
                            # Convert other strings to float or integer
                            reader[bar][kol] = float(reader[bar][kol])
                            if reader[bar][kol].is_integer():
                                reader[bar][kol] = int(reader[bar][kol])
                    except ValueError:
                        # Do not convert strings if this is not possible
                        pass
                # Add the current row to the data list
                list_data.append(reader[bar])
        # Return data in the form of a 2-dimensional list
        return list_data

    def ekspor_csv(self, list_data, label = True, on_linux = False):
        # Remove extra lines (\r\n) in Windows
        nl = "\n" if on_linux else ""
        # Open CSV file as output (write mode)
        with open(self.file_csv, "w", newline = nl) as file:
            # Write null values ​​(None) and empty strings as ""
            writer = csv.writer(file, delimiter = ",", quoting = csv.QUOTE_NONNUMERIC)
            # add a label (header) if requested
            if label: writer.writerow(["Time", "Name", "Heavy", "Kalori"])
            # Write data to CSV based on the data list
            writer.writerows(list_data)

    # Add new row to csv file
    def tambah_csv(self, name, heavy, kalori_total, time = None, on_linux = False):
        # Remove extra lines (\r\n) in Windows
        nl = "\n" if on_linux else ""
        # Open CSV file as output (write mode)
        with open(self.file_csv, "a", newline = nl) as file:
            # Write null values ​​(None) and empty strings as ""
            writer = csv.writer(file, delimiter = ",", quoting = csv.QUOTE_NONNUMERIC)
            # Get the current time if time is free
            if not Time: Time = int(time.time())
            # Write data to CSV based on the data list
            writer.writerow([time, name, heavy, kalori_total])
