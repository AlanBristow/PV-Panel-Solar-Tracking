/*
  Title: Steerable Solar (PV) Panels
  Author: Alan Bristow
  Connection: WiFi
  Search: All Axis
  Pin Connections:
    - Power LED
      - Brown D16 G
      - Orange D16 S
    - Wifi LED
      - Green D4 G
      - Yellow D4 S
    - Client LED
      - Blue D2 G
      - Purple D2 S
    - Reference Panel
      - Purple to red
      - Blue to black
      - Purple D32 S
      - Blue D32 G
    - Solar Position Algorithm Panel
      - Yellow to red
      - Green to black
      - Yellow D33 S
      - Green D33 G
    - Tracking Panel
      - White to red
      - Grey to black
      - White D35 S
      - Grey D35 G
    - OLED Screen
      - Red to VDD
      - Black to GND
      - White to SCK
      - Yellow to SDA
      - Red D22 V
      - Black D22 G
      - White D22 S
      - Yellow D21 S
*/

#include <ESP32Servo.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <base64.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include "esp_wpa2.h"
#include "private_details.h"
#include "spa.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Pin definition and assignment
#define servoRotateTrackingPin 14
#define servoTiltTrackingPin 27
#define servoRotateSpaPin 26
#define servoTiltSpaPin 15
#define AdcTrackingPanelPin 35
#define AdcReferencePanelPin 32
#define AdcSpaPanelPin  33
#define powerLedPin 17
#define wifiLedPin 16
#define clientLedPin 4
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// WiFi server creation
WiFiServer server(80);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Solar Position Algorithm Struct
spa_data spa;

// Servo object creation
Servo servoRotateTracking;
Servo servoTiltTracking;
Servo servoRotateSpa;
Servo servoTiltSpa;

// Constant declarations
const int servoFrequency = 50;
const float measureResistorTrackingPanel = 20.2;
const float fixedResistorTrackingPanel = 34.5;
const float measureResistorReferencePanel = 20.2;
const float fixedResistorReferencePanel = 34.7;
const float measureResistorSpaPanel = 20.2;
const float fixedResistorSpaPanel = 34.7;

// Global declarations
unsigned long lastCallTime = 0;
float servoZenith = 0;
float servoAzimuth = 0;
float bestRotateAngle = 0;
float bestTiltAngle = 0;

// Function definitions
void lcdStartup();
void wifiSetup();
void updateGitHub(const String &ipAddress);
void getTime(String &timeStamp);
unsigned long getTimeInSeconds(String timeStamp);
void servoSetup();
void solarPositionAlgorithmUpdate(spa_data *spa,String dateStamp,String timeStamp);
void servoMove(spa_data spa,float &servoZenith,float &servoAzimuth);
void readPanelAndCalculatePower(float &resistorMilliVolts,int panelPin,float &circuitCurrent,float &measureResistor,float &fixedResistor,float &circuitTotalVoltage,float &panelPower);
void trackingCall(float servoZenith,float servoAzimuth,float &bestRotateAngle,float &bestTiltAngle,float &resistorMilliVoltsTrackingPanel,int panelPin,float &circuitCurrentTrackingPanel,float &measureResistorTrackingPanel,float &fixedResistorTrackingPanel,float &circuitTotalVoltageTrackingPanel,float &trackingPanelPower);
void lcdDisplayPower(float trackingPanelPower,float referencePanelPower,float spaPanelPower);
void sendData(String formatedData);
 
void setup()
{ 
  Serial.begin(115200);
  pinMode(powerLedPin, OUTPUT);
  pinMode(wifiLedPin, OUTPUT);
  pinMode(clientLedPin, OUTPUT);
  digitalWrite(powerLedPin, HIGH);
  lcdStartup();
  servoSetup();
  wifiSetup();
}
 
void loop()
{
  Serial.begin(115200);
  WiFiClient client = server.available();

  // Variable declarations
  float resistorMilliVoltsTrackingPanel = 0;
  float resistorMilliVoltsReferencePanel = 0;
  float resistorMilliVoltsSpaPanel = 0;
  float circuitCurrentTrackingPanel = 0;
  float circuitCurrentReferencePanel = 0;
  float circuitCurrentSpaPanel = 0;
  float circuitTotalVoltageTrackingPanel = 0;
  float circuitTotalVoltageReferencePanel = 0;
  float circuitTotalVoltageSpaPanel = 0;
  float trackingPanelPower = 0;
  float referencePanelPower = 0;
  float spaPanelPower = 0;
  int calculated = 0;
  int result = 0;
  String dateStamp;
  String timeStamp;

  getTime(dateStamp,timeStamp);
  unsigned long timeInSeconds = getTimeInSeconds(timeStamp);
  if((timeInSeconds - lastCallTime) >= 300)
  {
    solarPositionAlgorithmUpdate(&spa,dateStamp,timeStamp);
    result = spa_calculate(&spa);
    servoMove(spa,servoZenith,servoAzimuth);
    trackingCall(servoZenith,servoAzimuth,bestRotateAngle,bestTiltAngle,resistorMilliVoltsTrackingPanel,3,circuitCurrentTrackingPanel,circuitTotalVoltageTrackingPanel,trackingPanelPower);
    lastCallTime = timeInSeconds;
    calculated = 1;
  }
  readPanelAndCalculatePower(resistorMilliVoltsReferencePanel,1,circuitCurrentReferencePanel,circuitTotalVoltageReferencePanel,referencePanelPower);
  readPanelAndCalculatePower(resistorMilliVoltsSpaPanel,2,circuitCurrentSpaPanel,circuitTotalVoltageSpaPanel,spaPanelPower);
  readPanelAndCalculatePower(resistorMilliVoltsTrackingPanel,3,circuitCurrentTrackingPanel,circuitTotalVoltageTrackingPanel,trackingPanelPower);
  lcdDisplayPower(trackingPanelPower,referencePanelPower,spaPanelPower);
  String formatedData= " ";
  formatedData = String(timeStamp)+","+String(calculated)+","+String(referencePanelPower,5)+","+String(spaPanelPower,5)+","+String(trackingPanelPower,5)+","+String(circuitTotalVoltageReferencePanel,5)+","+String(circuitTotalVoltageSpaPanel,5)+","+String(circuitTotalVoltageTrackingPanel,5);
  formatedData = formatedData+","+String(resistorMilliVoltsReferencePanel,5)+","+String(resistorMilliVoltsSpaPanel,5)+","+String(resistorMilliVoltsTrackingPanel,5)+","+String(circuitCurrentReferencePanel,5)+","+String(circuitCurrentSpaPanel,5)+","+String(circuitCurrentTrackingPanel,5);
  formatedData = formatedData+","+String(spa.azimuth,5)+","+String(spa.zenith,5)+","+String(servoAzimuth,5)+","+String(servoZenith,5)+","+String(bestRotateAngle,5)+","+String(bestTiltAngle,5);
  sendData(formatedData);
}

void lcdStartup()
{
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
  {
    for(;;);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(5, 23);
  display.println("Steerable Solar (PV) Panels");
  display.drawRoundRect(1, 15, 126, 32, 10, WHITE);
  display.display(); 
  delay(2000);
}

void wifiSetup()
{
  WiFi.begin(WIFI_SSID, WPA2_AUTH_PEAP, WIFI_IDENTITY, WIFI_USERNAME, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
  }
  // Get the IP address
  String ipAddress = WiFi.localIP().toString();
  // Update GitHub with the IP address
  updateGitHub(ipAddress);
  server.begin();
  timeClient.begin();
  timeClient.setTimeOffset(0);
  digitalWrite(wifiLedPin, HIGH);
}

void updateGitHub(const String &ipAddress)
{
  HTTPClient http;
  String apiUrl = "https://api.github.com/repos/" + String(REPOOWNER) + "/" + String(REPONAME) + "/contents/" + String(FILEPATH);
  String base64EncodedIP = base64::encode(ipAddress);

  // Retrieve the SHA of the existing file
  http.begin(apiUrl);
  http.addHeader("Authorization", "token " + String(GITHUBTOKEN));
  int httpResponseCode = http.GET();

  if(httpResponseCode == HTTP_CODE_OK)
  {
    DynamicJsonDocument jsonDocument(1024);
    DeserializationError error = deserializeJson(jsonDocument, http.getString());
    if(!error)
    {
      String sha = jsonDocument["sha"].as<String>();

      // Update the file with the SHA
      String postData = "{\"message\":\"Update IP address\",\"content\":\"" + base64EncodedIP + "\",\"sha\":\"" + sha + "\"}";

      http.begin(apiUrl);
      http.addHeader("Content-Type", "application/json");
      http.addHeader("Authorization", "token " + String(GITHUBTOKEN));

      httpResponseCode = http.PUT(postData);
    }
  }
  http.end();
}

void getTime(String &dateStamp, String &timeStamp)
{
  while(!timeClient.update())
  {
    timeClient.forceUpdate();
  }
  String formattedDate = timeClient.getFormattedDate();
  int splitT = formattedDate.indexOf("T");
  dateStamp = formattedDate.substring(0, splitT);
  timeStamp = formattedDate.substring(splitT+1, formattedDate.length()-1);
}

unsigned long getTimeInSeconds(String timeStamp)
{
  int hour = timeStamp.substring(0, 2).toInt();
  int minute = timeStamp.substring(3, 5).toInt();
  int second = timeStamp.substring(6).toInt();
  return hour * 3600 + minute * 60 + second;
}

void servoSetup()
{
  servoRotateTracking.setPeriodHertz(servoFrequency);
  servoTiltTracking.setPeriodHertz(servoFrequency);
  servoRotateSpa.setPeriodHertz(servoFrequency);
  servoTiltSpa.setPeriodHertz(servoFrequency);
  servoRotateTracking.attach(servoRotateTrackingPin);
  servoTiltTracking.attach(servoTiltTrackingPin);
  servoRotateSpa.attach(servoRotateSpaPin);
  servoTiltSpa.attach(servoTiltSpaPin);
  servoRotateTracking.write(map(90, 0, 180, 20, 180));
  servoTiltTracking.write(map(55, 0, 90, 21, 101));
  servoRotateSpa.write(map(90, 0, 180, 25, 175));
  servoTiltSpa.write(map(55, 0, 90, 18, 98));
  delay(200);
}

void solarPositionAlgorithmUpdate(spa_data *spa,String dateStamp,String timeStamp)
{
  spa->year          = dateStamp.substring(0,4).toInt();
  spa->month         = dateStamp.substring(5,7).toInt();
  spa->day           = dateStamp.substring(8,10).toInt();
  spa->hour          = timeStamp.substring(0,2).toInt();
  spa->minute        = timeStamp.substring(3,5).toInt();
  spa->second        = timeStamp.substring(6).toInt();
  spa->timezone      = 0.0;
  spa->delta_ut1     = 0;
  spa->delta_t       = 67;
  spa->longitude     = -6.36080;
  spa->latitude      = 53.23041;
  spa->elevation     = 70;
  spa->pressure      = 1013;
  spa->temperature   = 9.4;
  spa->slope         = 0;
  spa->azm_rotation  = -10;
  spa->atmos_refract = 0.5667;
  spa->function      = SPA_ALL;
}

void servoMove(spa_data spa,float &servoZenith,float &servoAzimuth)
{
  float zenith = spa.zenith;
  float azimuth = spa.azimuth;
  servoZenith = 90-zenith;
  servoAzimuth = azimuth-90;
  if(servoAzimuth < 0)
  {
    servoAzimuth = 0;
  }
  if(servoAzimuth > 180)
  {
    servoAzimuth = 180;
  }
  servoRotateTracking.write(map((int)servoAzimuth, 0, 180, 20, 180));
  servoTiltTracking.write(map((int)servoZenith, 0, 90, 21, 101));
  servoRotateSpa.write(map((int)servoAzimuth, 0, 180, 25, 175));
  servoTiltSpa.write(map((int)servoZenith, 0, 90, 18, 98));
}

void readPanelAndCalculatePower(float &resistorMilliVolts,int panelPin,float &circuitCurrent,float &circuitTotalVoltage,float &panelPower)
{
  if(panelPin == 1)
  {
    resistorMilliVolts = analogReadMilliVolts(AdcReferencePanelPin);
    circuitCurrent = (resistorMilliVolts/1000)/measureResistorReferencePanel;
    circuitTotalVoltage = circuitCurrent*(measureResistorReferencePanel+fixedResistorReferencePanel);
  }
  else if(panelPin == 2)
  {
    resistorMilliVolts = analogReadMilliVolts(AdcSpaPanelPin);
    circuitCurrent = (resistorMilliVolts/1000)/measureResistorSpaPanel;
    circuitTotalVoltage = circuitCurrent*(measureResistorSpaPanel+fixedResistorSpaPanel);
  }
  else if(panelPin == 3)
  {
    resistorMilliVolts = analogReadMilliVolts(AdcTrackingPanelPin);
    circuitCurrent = (resistorMilliVolts/1000)/measureResistorTrackingPanel;
    circuitTotalVoltage = circuitCurrent*(measureResistorTrackingPanel+fixedResistorTrackingPanel);
  }
  panelPower = circuitTotalVoltage*circuitCurrent;
}

void trackingCall(float servoZenith,float servoAzimuth,float &bestRotateAngle,float &bestTiltAngle,float &resistorMilliVoltsTrackingPanel,int panelPin,float &circuitCurrentTrackingPanel,float &circuitTotalVoltageTrackingPanel,float &trackingPanelPower)
{
  float bestPower = 0;
  // Iterate through the 3x3 grid
  for (int i = -1; i <= 1; i++) {
    for (int j = -1; j <= 1; j++) {
      // Calculate new positions
      float targetRotate = servoAzimuth + (i*10);
      float targetTilt = servoZenith + (j*10);

      // Ensure the values are within the servo limits (0 to 180 degrees)
      targetRotate = constrain(targetRotate, 0, 180);
      targetTilt = constrain(targetTilt, 0, 90);

      // Move the servos to the new positions
      servoRotateTracking.write(map((int)targetRotate, 0, 180, 20, 180));
      servoTiltTracking.write(map((int)targetTilt, 0, 90, 21, 101));
      delay(2000);
      readPanelAndCalculatePower(resistorMilliVoltsTrackingPanel,panelPin,circuitCurrentTrackingPanel,circuitTotalVoltageTrackingPanel,trackingPanelPower);
      if(trackingPanelPower > bestPower)
      {
        bestRotateAngle = targetRotate;
        bestTiltAngle = targetTilt;
        bestPower = trackingPanelPower;
      }
    }
  }
  servoRotateTracking.write(map((int)bestRotateAngle, 0, 180, 20, 180));
  servoTiltTracking.write(map((int)bestTiltAngle, 0, 90, 21, 101));
  trackingPanelPower = bestPower;
}

void lcdDisplayPower(float trackingPanelPower,float referencePanelPower,float spaPanelPower)
{
  display.clearDisplay();
  display.setCursor(30, 0);
  display.println("Panel Power");
  display.drawRoundRect(8, 10, 34, 53, 5, WHITE);
  display.drawRoundRect(47, 10, 34, 53, 5, WHITE);
  display.drawRoundRect(86, 10, 34, 53, 5, WHITE);
  display.setCursor(15, 20);
  display.println("Tra:");
  display.setCursor(10, 36);
  display.print(trackingPanelPower);
  display.println("W");
  display.setCursor(54, 20);
  display.println("Ref:");
  display.setCursor(49, 36);
  display.print(referencePanelPower);
  display.println("W");
  display.setCursor(93, 20);
  display.println("Spa:");
  display.setCursor(88, 36);
  display.print(spaPanelPower);
  display.println("W");
  display.display(); 
}

void sendData(String formatedData)
{
  WiFiClient client = server.available(); 
  digitalWrite(clientLedPin, HIGH);
  while(!client)
  {
    client = server.available();
  }
  client.println(formatedData);
  client.stop();
  digitalWrite(clientLedPin, LOW);
}