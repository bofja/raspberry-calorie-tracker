import lib_component as comp
import lib_classifier as model
import lib_api as api

# FatSecret authentication username and password
fs_client_id = "REMOVED"
fs_client_secret = "REMOVED"

def setup():
   # Set as global variables to be accessible from outside
   global kamera, load_cell, buzzer, lcd, tflite, fatsecret, stats
   # Initialize sensors and actuators
   kamera = comp.Kamera(server = "http://172.16.0.11", folder_simpan = "capture")
   load_cell = comp.LoadCell(dout_pin = 5, sck_pin = 6, ratio = 221.33)
   lcd = comp.LCD(column = 16, row = 2, address = 0x27)
   buzzer = comp.Buzzer(pin = 19)
   # Initialize model classification from file
   tflite = model.Classifier("config/model_unquant.tflite", "config/food_label.txt")
   # Initialize FatSecret API and save access token to file
   fatsecret = api.FatSecret(fs_client_id, fs_client_secret, "config/fatsecret_token.txt")
   # Food statistics file to read from NodeRED
   #stats = api.CsvHelper("config/food_stats.csv")

def loop():
   # Minimum weight at which scale is considered loaded (grams)
   minimum_weight = 2
   # Previous weight
   previous_weight = 0

   while True:
      current_weight = load_cell.weigh()
      # If scale is loaded then...
      if previous_weight < minimum_weight <= current_weight:
         print(f"Weight of scale (filled): {current_weight}")
         # Wait X seconds then take picture and classify food
         image_file = camera.portrait(3)
         food_type = tflite.classification(image_file)
         # Get estimated calories per gram from the most relevant food id
         calories = fatsecret.estimation_calories(fatsecret.search_food(food_type, 20, True))
         # Save food type and estimated total calories
         food_info = f"{food_type}\nCalories: {round(calories * current_weight)}"
         # Display food info and weight to terminal
         print(food_info + f"\nWeight: {current_weight}")
         # Turn on buzzer to indicate success
         buzzer.sound()
         # Display food info to LCD for X seconds
         lcd.write_on(food_info, 1, 5)
         # Write current food info results to NodeRED statistics file
         #stats.add_csv(food_type, current_weight, calories * current_weight)
      elif minimum_weight < previous_weight:
         print(f"Weight of the scale (contents have not changed): {current_weight}")
      else:
         print(f"Weight of the scale (empty): {current_weight}")
      # Save the current weight for the next loop
      previous_weight = current_weight

if __name__ == "__main__":
   # while True:
   # # For initial training purposes of food types
   # camera = comp.Camera(server = "http://172.16.0.11", save_folder = "training")
   # ask = input("Press ENTER to take a photo...")
   # camera.portret()

   # Main program
   setup()
   loop()
