import os
import pandas as pd
from datetime import datetime
import serial
import time
import requests
import details

url_base = "http://api.openweathermap.org/data/2.5/weather?"
assembledUrl = url_base + "appid=" + details.API_KEY + "&q=" + details.LOCATION

def sendESPTime():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    timeMessage = current_time+"\n"
    ser.write(timeMessage.encode())

def generate_file_name():
    today_date = datetime.today().strftime("%Y-%m-%d")
    file_path = os.path.join(details.BASE_PATH, f"{today_date}_data.xlsx")
    return file_path

def check_and_update_excel(data):
    file_name = generate_file_name()

    if os.path.isfile(file_name):
        existing_data = pd.read_excel(file_name)
        if isinstance(data, dict):
            data = {key: [value] if not isinstance(value, list) else value for key, value in data.items()}
            data = pd.DataFrame.from_dict(data)
        updated_data = pd.concat([existing_data, data], ignore_index=True)
    else:
        if isinstance(data, dict):
            data = {key: [value] if not isinstance(value, list) else value for key, value in data.items()}
            updated_data = pd.DataFrame.from_dict(data)
        else:
            updated_data = pd.DataFrame(data)

    updated_data.to_excel(file_name, index=False)
    print(f"Data saved to {file_name}")

def read_esp32():
    received_data = ser.readline().decode().strip()
    values = received_data.split(',')
    time.sleep(0.2)
    timeLog = str(values[0])
    calc = int(values[1])
    fixPow = float(values[2])
    spaPow = float(values[3])
    traPow = float(values[4])
    fixTotVol = float(values[5])
    spaTotVol = float(values[6])
    traTotVol = float(values[7])
    fixMilVol = float(values[8])
    spaMilVol = float(values[9])
    traMilVol = float(values[10])
    fixCur = float(values[11])
    spaCur = float(values[12])
    traCur = float(values[13])
    spaAzi = float(values[14])
    spaZen = float(values[15])
    serAzi = float(values[16])
    serZen = float(values[17])
    besRot = float(values[18])
    besTil = float(values[19])
    return timeLog,calc,fixPow,spaPow,traPow,fixTotVol,spaTotVol,traTotVol,fixMilVol,spaMilVol,traMilVol,fixCur,spaCur,traCur,spaAzi,spaZen,serAzi,serZen,besRot,besTil

def get_openweathermap_data(assembledUrl):
    response = requests.get(assembledUrl).json()
    temp = response['main']['temp']
    weat = response['weather'][0]['main']
    des = response['weather'][0]['description']
    clo = response['clouds']['all']
    pres = response['main']['pressure']
    hum = response['main']['humidity']
    return temp, weat, des, clo, pres, hum

if __name__ == "__main__":
    try:
        ser = serial.Serial(details.COM_PORT, 115200, timeout=1)
        print(f"Connected to {details.COM_PORT}")
    except serial.SerialException:
        print(f"Error: Could not connect to {details.COM_PORT}")
        exit()

    try:
        while True:
            sendESPTime()
            timeLog,calc,fixPow,spaPow,traPow,fixTotVol,spaTotVol,traTotVol,fixMilVol,spaMilVol,traMilVol,fixCur,spaCur,traCur,spaAzi,spaZen,serAzi,serZen,besRot,besTil = read_esp32()
            timeRecieved = datetime.now()
            temp, weat, des, clo, pres, hum = get_openweathermap_data(assembledUrl)
            data_to_add = {
                "Time Recieved": timeRecieved,
                "Time Logged": timeLog,
                "Just Calculated": calc,
                "Fixed Panel Power(W)": fixPow,
                "SPA Panel Power(W)": spaPow,
                "Tracking Panel Power(W)": traPow,
                "Fixed Panel Total Voltage(V)": fixTotVol,
                "SPA Panel Total Voltage(V)": spaTotVol,
                "Tracking Total Voltage(V)": traTotVol,
                "Fixed Panel Millivoltage(V)": fixMilVol,
                "SPA Panel Millivoltage(V)": spaMilVol,
                "Tracking Millivoltage(V)": traMilVol,
                "Fixed Panel Current(C)": fixCur,
                "SPA Panel Current(C)": spaCur,
                "Tracking Current(C)": traCur,
                "SPA Azimuth": spaAzi,
                "SPA Zenith": spaZen,
                "Spa Panel Rotate": serAzi,
                "Spa Panel Tilt": serZen,
                "Tracking Panel Rotate": besRot,
                "Tracking Panel Tilt": besTil,
                "Temperature": temp,
                "Weather": weat,
                "Description": des,
                "Cloud Coverage": clo,
                "Pressure": pres,
                "Humidity": hum
            }
            check_and_update_excel(data_to_add)
            
    except KeyboardInterrupt:
        print("\nCommunication and logging terminated.")