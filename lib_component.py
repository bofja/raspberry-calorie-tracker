# Used when accessing sensor and actuator components
# Input can be GPIO pin numbers, etc.

import requests
import RPi.GPIO as GPIO
import time

# Requires RPi.GPIO (pip)
from hx711_multi import HX711
# Requires python-smbus (apt) or smbus2 (pip)
from RPLCD.i2c import CharLCD

class Camera:
   def __init__(self, server, save_folder = "capture", format_file = "%Y-%m-%d %H:%M:%S"):
      # Camera web server address
      self.server = server
      # Directory to save images
      self. save_folder = save_folder
      # Image file naming format
      self. format_file = format_file

   def __time(self):
     # Give the current time according to the image file name format
     return time. strftime(self. format_file)

   def portrait(self, delay = 0):
     # Wait X seconds before taking a portrait
     if delay > 0: time.sleep(depa)
        # Capture an image from the camera's web server
        image = requests.get(f"{self.server}/capture")
     if image.status_code == 200:
        # Save the image to the destination folder in the name format
        destination = f"{self.save_folder}/{self.__time()}.jpg"
            with open(destination, "wb") as file:
        try: file.write(image.content)
        except Exception:
           # Notify the user if the image save fails
           print("Image destination cannot be accessed or written to...")
        return None
        # Return the path to the saved image file
        return destination
     else:
        # Notify the user if the server cannot be accessed
         print(f"Camera server cannot be accessed (error {image.status_code})...")
         return None

class Buzzer:
   def __init__(self, pin):
      self.pin = pin
      # GPIO number (not pin number) as reference
      GPIO.setmode(GPIO.BCM)
      # Set buzzer pin as output
      GPIO.setup(self.pin, GPIO.OUT)

   def __del__(self):
      # Clean GPIO after finished
      try: GPIO.cleanup()
      except Exception: pass

   def suara(self, ulang = 1, jeda_nyalai = 0.5, jeda_mati = 0.3):
      # Turn on buzzer repeatedly (if needed)
      for _ in range(ulang):
      # Turn on buzzer according to on interval
      GPIO.output(self.pin, GPIO.HIGH)
      time.sleep(jeda_nyalai)
      # Turn off buzzer according to off interval
      GPIO.output(self.pin, GPIO.LOW)
      time.sleep(jeda_mati)

class LoadCell:
   def __init__(self, dout_pin, sck_pin, ratio = 0):
      # GPIO number (not pin number) as reference
      GPIO.setmode(GPIO.BCM)
      # Initialize HX711 module
      self.hx711 = HX711(dout_pin, sck_pin, 128, "A", False, "CRITICAL")
      # Reset SCK pin before starting reading
      self.hx711.reset()
      # Set current reading weight as zero
      input("Unload the scale and press ENTER...")
      self.hx711.zero()

      if ratio == 0:
         # Calibrate weight sensor if ratio is unknown
         calibration = str(input("Want to calibrate weight sensor (Y/N)? "))
         if calibration == "Y" or calibration == "y": self.calibration()
         else:
             # Set the calibration ratio if it is known
             self.hx711.set_weight_multiples(ratio)

   def __del__(self):
      # Clean GPIO after completion
      try: GPIO.cleanup()
      except Exception: pass

   def __timbang_mentah(self, hitung = 30):
      # Calculate the performance (time) of the weight measurement
      mulai = time.perf_counter()
      # Measure the raw weight of the current load until it is read
      while self.hx711.read_raw(hitung) == None:
         duration = int(round(time.perf_counter() - mulai))
         print(f"Weight not read ({duration} seconds), retrying...")

   def calibration(self):
      # Ask the user to place a load of known weight
      input("Place the load on the scale and press ENTER...")
      # Measure the raw weight of the current load this until it is read
      self.__raw_weight()
      # Get the last raw weight measurement result
      raw_weight = self.hx711.get_raw()
      print(f"Raw weight: {raw_weight}")
      # Ask the user to enter the actual weight of the load
      original_weight = float(input("Enter the actual weight (grams): "))
      # Calibrate the weight value for the next measurement
      ratio = round(raw_weight / original_weight, 3)
      self.hx711.set_weight_multiples(ratio)
      print(f"Calibration ratio: {ratio}")

   def weigh(self):
      # Measure the raw weight of the current load until it is read
      self.__raw_weight()
      # Give the last weight measurement result (raw weight divided by ratio)
      return round(self.hx711.get_weight(), 3)

class LCD:
# The type used is generally PCF8574 (see the I2C chip section)
   def __init__(self, column = 16, row = 2, address = 0x27, type = "PCF8574"):
      self.lcd = CharLCD(type, address, None, 1, column, row, backlight_enabled = False)

   def __del__(self):
      # Clear the screen and close the connection
      self.lcd.close(True)

   def write(self, text, row = 1):
      # Write text on the appropriate row
      self.lcd.cursor_pos = (row - 1, 0)
      self.lcd.write_string(text)

   def write_on(self, text, row = 1, pause = 5, delete = True):
      # Write text on the appropriate row
      self.lcd.cursor_pos = (row - 1, 0)
      self.lcd.write_string(text)
      # Turn on the screen backlight for X seconds
      self.nyala(pause)
      # Clear the screen again when requested
      if clear: self.lcd.clear()

   def nyala(self, paus = 0):
      # Turn on the screen backlight
      self.lcd.backlight_enabled = True
      # Turn it off again after a certain delay (seconds)
      if paus > 0:
         time.sleep(pause)
         self.lcd.backlight_enabled = False

   def mati(self, lupa = False):
      # Turn off the screen backlight
      self.lcd.backlight_enabled = False
      if lupa: self.lcd.clear()
