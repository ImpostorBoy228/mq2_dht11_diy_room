#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <DHT.h>

// Provide the token generation process info.
#include <addons/TokenHelper.h>

// Provide the RTDB payload printing info and other helper functions.
#include <addons/RTDBHelper.h>

/* 1. Define the WiFi credentials */
#define WIFI_SSID "Shamoni_14"
#define WIFI_PASSWORD "57075707"

/* 2. Define the API Key */
#define API_KEY "AIzaSyAMa9C2EXcZ9ULgLq0tYUuK3ftCviA3Hj0"

/* 3. Define the RTDB URL */
#define DATABASE_URL "https://sus-iot-default-rtdb.asia-southeast1.firebasedatabase.app/" 

/* 4. Define the user Email and password that already registered or added in your project */
#define USER_EMAIL "susman209290@gmail.com"
#define USER_PASSWORD "linux/etc"

// Define Firebase Data object
FirebaseData fbdo;

FirebaseAuth auth;
FirebaseConfig config;

unsigned long sendDataPrevMillis = 0;

const int gasPin = 36;
DHT dht(4, DHT11);

void setup()
{
  pinMode(gasPin, INPUT);
  dht.begin();

  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  /* Assign the api key (required) */
  config.api_key = API_KEY;

  /* Assign the user sign in credentials */
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  /* Assign the RTDB URL (required) */
  config.database_url = DATABASE_URL;

  /* Assign the callback function for the long running token generation task */
  config.token_status_callback = tokenStatusCallback; // see addons/TokenHelper.h

  Firebase.reconnectNetwork(true);

  fbdo.setBSSLBufferSize(4096, 1024);

  fbdo.setResponseSize(2048);

  Firebase.begin(&config, &auth);

  Firebase.setDoubleDigits(5);

  config.timeout.serverResponse = 10 * 1000;
}

void loop()
{
  if (Firebase.ready() && (millis() - sendDataPrevMillis > 10 || sendDataPrevMillis == 0))
  {
    sendDataPrevMillis = millis();

    // Считываем аналоговое значение с gasPin
    int gasValue = analogRead(gasPin);
    Serial.printf("Gas Value: %d\n", gasValue);
    Serial.printf("Firebase update status: %s\n", Firebase.RTDB.setInt(&fbdo, F("/house/gas-value"), gasValue) ? "ok" : fbdo.errorReason().c_str());

    delay(100);

    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(h) || isnan(t)) {
      Serial.println(F("Failed to read from DHT sensor!"));
      return;
    }
    Serial.printf("Temperature: %s\n", Firebase.RTDB.setFloat(&fbdo, F("/house/temp"), t) ? "ok" : fbdo.errorReason().c_str());
    Serial.printf("Humidity: %s\n", Firebase.RTDB.setFloat(&fbdo, F("/house/humidity"), h) ? "ok" : fbdo.errorReason().c_str());
  }
}
