# Automatic Food Calorie Tracker
Automatic food calorie tracker using Raspberry Pi, sensors, and FatSecret API. This was originally made for my "Embedded System" final project, feel free to use and modify.

|||
|-|-|
|119140218|Andhika Wibawa|
|119140134|Muhammad Yahya|
|14117174|Ishak Fikri Taufiq|

## Design and schematic

### System Schematic
<img src="docs/System Schematic.png" height="300">

**Note:** The NodeRED part is still partially done

### Prototype Design
<img src="docs/Prototype Design.png" height="300">

## Hardwares used
1. 📶 Modem/router (for internet connection)
2. 🖥️ Raspberry Pi 3B (use at least 16 GB MicroSD to be safe)
3. 📷 ESP32-CAM (with FTDI or downloader module)
4. 📟 LCD (with I2C PCF8574 module)
5. ⚖️ Load cell 10 KG (with HX711 module)
6. 🔊 Piezo buzzer

## Softwares used
1. Raspberry Pi OS (full desktop + software)
2. Visual Studio Code (or any text editor)
3. TensorFlow Lite (ARM32 version)
4. Arduino IDE (for ESP32-CAM)
5. Python (version > 2)

See more detail on instructions...

## Technical instructions

### Setting-up ESP32-CAM for capturing images ([ref](https://randomnerdtutorials.com/esp32-cam-video-streaming-face-recognition-arduino-ide))
1. Install Arduino IDE on your PC (preferred) or Raspberry Pi
2. Install ESP32 (ESP32-CAM) add-on on Arduino IDE
3. Plug (to PC/RPi), flash, and run ESP32-CAM C++ code using Arduino IDE
4. Save ESP32-CAM camera server IP address by any means
5. Unplug ESP32-CAM (if plugged to PC) and plug it to Raspberry Pi (see prototype design)
5. Capture food images (the more the better) of at least 2 food types (use different angles/rotations, etc.)
6. Save the images for later (machine learning training purpose)

### Setting-up Python libraries and machine learning
1. Install Python libraries using `pip install -r requirements.txt`
2. Install [TFLite runtime](https://www.tensorflow.org/lite/guide/python) (I use the one from [GitHub releases](https://github.com/google-coral/pycoral/releases/))
3. Train your ML model using the captured food images, use [Teachable Machine](https://teachablemachine.withgoogle.com/) (preferred) or [EdgeImpulse](https://studio.edgeimpulse.com/)
4. Change the class name of each food type with the food name (as close as possible to [FatSecret](https://www.fatsecret.com/calories-nutrition/) food name)
5. Export your model as `.tflite` file and save it for later use

### Setting-up FatSecret REST API ([ref](https://platform.fatsecret.com/api/Default.aspx?screen=rapih))
1. Register an application [here](https://platform.fatsecret.com/api/Default.aspx?screen=r). Don't register it as web application unless you want to use JavaScript API
2. After registration complete, save your `client_id` and `client_secret` (treat them like username and password)
3. Add your internet IP (not your local IP) to FatSecret `Allowed IP Addresses` (on FatSecret web settings)
4. You should be able to make REST API calls now ([ref](https://platform.fatsecret.com/api/Default.aspx?screen=rapiref2))

## Use instructions
1. Make sure you complete all steps in technical instructions
2. Clone this repo code using `git clone` (non-collaborator) or `git remote add` (collaborator)
3. Read the code and make some changes if needed (including `client_id`, `client_secret`, GPIO pin, ESP32-CAM IP address, etc.)
4. ???
5. Profit

## References
* [Automatic Calorie Tracking Scale](https://www.hackster.io/lezwon/automatic-calorie-tracking-scale-31d780) (primary)
* [ESP32-CAM Streaming Web Server](https://randomnerdtutorials.com/esp32-cam-video-streaming-face-recognition-arduino-ide)
* [RPLCD (LCD Library) Documentation](https://rplcd.readthedocs.io/en/stable/)
* [Python "hx711-multi" Library Documentation](https://github.com/Morrious/hx711-multi)
* [Python "requests" Library Documentation](https://docs.python-requests.org/en/latest/)
* [Official FatSecret REST API Guide](https://platform.fatsecret.com/api/Default.aspx?screen=rapiauth2)
* [TensorFlow Lite Image Classification Examples](https://github.com/tensorflow/examples/tree/master/lite/examples/image_classification)

## Todo
* Push daily calorie statistics to NodeRED (from CSV file)
* Prevent food stats logging when the image classification accuracy is bad
