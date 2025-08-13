# MQ2_DHT11_DIY_Room

This project is designed to monitor the temperature, humidity, and gas levels in a room using DHT11 and MQ-2 sensors. It allows you to collect data from these sensors and display it through a Telegram bot, with the ability to update information in real-time.

## Description

The project uses the ESP8266 to connect to Wi-Fi and read data from the DHT11 (for temperature and humidity) and MQ-2 (for gas detection) sensors. These data are then transferred to the Firebase Realtime Database and displayed in the Telegram bot.

### Features:
- Reading temperature, humidity, and gas data.
- Sending data to Firebase.
- Using a Telegram bot to display data that can be updated via buttons.
- Editing Telegram messages every 0.1 seconds to keep data up-to-date.

## Requirements

- **Hardware**:
  - ESP8266 (or similar Wi-Fi board)
  - DHT11 temperature and humidity sensor
  - MQ-2 gas sensor
  
- **Software**:
  - Arduino IDE for programming ESP8266
  - Firebase account
  - Python 3.x
  - Libraries: `aiogram`, `firebase-admin`, `asyncio`

## Installation

1. **Setting up Firebase**:
   - Create a project in the [Firebase Console](https://console.firebase.google.com/).
   - Add the Firebase Realtime Database to the project.
   - Create a service account and get the `google-services.json` file.

2. **Connecting and configuring the ESP8266**:
   - Install the Arduino IDE and add support for the ESP8266.
   - Connect the DHT11 and MQ-2 to the ESP8266.
   - Upload a sketch for the ESP8266 that will read data from the sensors and send it to Firebase.

3. **Configuring the Python bot**:
   - Install all the dependencies:
     ```bash
     pip install aiogram firebase-admin
     ```
   - Place the `google-services.json` file in the same folder as the Python script.
   - Enter your **Telegram bot token** in the Python bot code.
   - Run the Python script:
     ```bash
     python bot.py
     ```

## Usage

1. Launch the Telegram bot.
2. Click on the "Get Data 💾" button to get information about the current status:
   - Humidity
   - Temperature
   - Gas level
3. The data will be updated every 0.1 seconds.

## Project structure

- `bot.py` - Python script for working with Telegram bot and Firebase.
- `google-services.json` - Configuration for Firebase (required to work with the Firebase SDK).
- `esp8266_sketch.ino` - Arduino sketch for ESP8266 that reads data from sensors and sends it to Firebase.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
