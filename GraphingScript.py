import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import os

# Directory containing Excel files
directory = r' '

# List of specific filenames you want to process
specific_filenames = ['2024-04-16_data.xlsx']

def DataAveraged(directory,filename):
    filepath = os.path.join(directory, filename)
    df = pd.read_excel(filepath)
    datetime_objects = pd.to_datetime(df['Time Logged'], format="%H:%M:%S")
    df['Timestamp'] = datetime_objects
    df['MinuteTimestamp'] = df['Timestamp'].dt.round('min')
    df['HourlyTimestamp'] = df['Timestamp'].dt.round('h')
    df['15MinTimestamp'] = df['Timestamp'].dt.round('15min')
    df['30MinTimestamp'] = df['Timestamp'].dt.round('30min')
    plt.plot(df['Timestamp'], df['SPA Panel Power(W)'], label='Raw Data')
    minute_averaged_data = df.groupby('MinuteTimestamp')['SPA Panel Power(W)'].mean()
    hourly_averaged_data = df.groupby('HourlyTimestamp')['SPA Panel Power(W)'].mean()
    fifteen_min_averaged_data = df.groupby('15MinTimestamp')['SPA Panel Power(W)'].mean()
    thirty_min_averaged_data = df.groupby('30MinTimestamp')['SPA Panel Power(W)'].mean()
    plt.plot(minute_averaged_data.index, minute_averaged_data.values, label='Minute Averaged Data')
    plt.plot(fifteen_min_averaged_data.index, fifteen_min_averaged_data.values, label='15-Min Averaged Data')
    plt.plot(thirty_min_averaged_data.index, thirty_min_averaged_data.values, label='30-Min Averaged Data')
    plt.plot(hourly_averaged_data.index, hourly_averaged_data.values, label='Hourly Averaged Data')
    plt.xlabel('Time')
    plt.ylabel('SPA Panel Power(W)')
    plt.title('SPA Panel Power vs Time')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.show()

def PowerVsAngle(directory,filename):
    filepath = os.path.join(directory, filename)
    df = pd.read_excel(filepath)
    datetime_objects = pd.to_datetime(df['Time Logged'], format="%H:%M:%S")
    df['Timestamp'] = datetime_objects
    df['MinuteTimestamp'] = df['Timestamp'].dt.round('15min')
    minute_averaged_data_spa = df.groupby('MinuteTimestamp')['SPA Panel Power(W)'].mean()
    minute_averaged_data_fix = df.groupby('MinuteTimestamp')['Fixed Panel Power(W)'].mean()
    minute_averaged_data_tra = df.groupby('MinuteTimestamp')['Tracking Panel Power(W)'].mean()
    minute_averaged_data_spr = df.groupby('MinuteTimestamp')['Spa Panel Rotate'].mean()
    minute_averaged_data_tpr = df.groupby('MinuteTimestamp')['Tracking Panel Rotate'].mean()
    minute_averaged_data_spt = df.groupby('MinuteTimestamp')['Spa Panel Tilt'].mean()
    minute_averaged_data_tpt = df.groupby('MinuteTimestamp')['Tracking Panel Tilt'].mean()
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(minute_averaged_data_fix.index, minute_averaged_data_fix.values, color='m', label='Fixed Panel Power')
    ax1.plot(minute_averaged_data_spa.index, minute_averaged_data_spa.values, color='orange', label='SPA Panel Power')
    ax1.plot(minute_averaged_data_tra.index, minute_averaged_data_tra.values, color='g', label='Tracking Panel Power')
    ax1.set_xlabel('Time (Hours)')
    ax1.set_ylabel('Power (Watts)')
    ax1.tick_params(axis='y')
    ax2 = ax1.twinx()
    ax2.scatter(minute_averaged_data_spr.index, minute_averaged_data_spr.values, color='blue', label='SPA Rotate Servo Angle', s=10, marker='o')
    ax2.scatter(minute_averaged_data_tpr.index, minute_averaged_data_tpr.values, color='red', label='Tracking Rotate Servo Angle', s=10, marker='o')
    ax2.scatter(minute_averaged_data_spt.index, minute_averaged_data_spt.values, color='purple', label='SPA Tilt Servo Angle',  s=10,marker='o')
    ax2.scatter(minute_averaged_data_tpt.index, minute_averaged_data_tpt.values, color='green', label='Tracking Tilt Servo Angle', s=10, marker='o')
    ax2.set_ylabel('Servo Angle (Degrees)')
    ax2.set_zorder(1)
    ax1.set_zorder(2)
    ax1.patch.set_visible(False)
    ax2.patch.set_visible(False)
    plt.title('Panels Power and Servo Angle vs Time - Averaged over 15 minutes')
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper left')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.show()

def PowVsCloud(directory,filename):
    filepath = os.path.join(directory, filename)
    df = pd.read_excel(filepath)
    fixPower = df['Fixed Panel Power(W)']
    spaPower = df['SPA Panel Power(W)']
    traPower = df['Tracking Panel Power(W)']
    cloPer = df['Cloud Coverage']
    timestamps = df['Time Logged']
    datetime_objects = [datetime.strptime(ts, "%H:%M:%S") for ts in timestamps]
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(datetime_objects, fixPower, color='k', label="Fixed")
    ax1.plot(datetime_objects, spaPower, color='m', label="SPA")
    ax1.plot(datetime_objects, traPower, color='g', label="Tracking")
    ax1.set_xlabel('Time (Hours)')
    ax1.set_ylabel('Power (Watts)')
    ax1.tick_params(axis='y')
    ax2 = ax1.twinx()
    ax2.bar(datetime_objects, cloPer, color='skyblue', width=0.0004, label = "Cloud Coverage")
    ax2.plot(datetime_objects, cloPer)
    ax2.set_ylabel('Cloud Coverage (Percentage)')
    ax2.tick_params(axis='y')
    ax2.set_zorder(1)
    ax1.set_zorder(2)
    ax1.patch.set_visible(False)
    plt.title('Panels Power and Cloud Coverage vs Time')
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper left')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.tight_layout()
    plt.show()

def MinutePowVsCloud(directory,filename):
    filepath = os.path.join(directory, filename)
    df = pd.read_excel(filepath)
    datetime_objects = pd.to_datetime(df['Time Logged'], format="%H:%M:%S")
    df['Timestamp'] = datetime_objects
    df['MinuteTimestamp'] = df['Timestamp'].dt.round('min')
    minute_averaged_data_spa = df.groupby('MinuteTimestamp')['SPA Panel Power(W)'].mean()
    minute_averaged_data_fix = df.groupby('MinuteTimestamp')['Fixed Panel Power(W)'].mean()
    minute_averaged_data_tra = df.groupby('MinuteTimestamp')['Tracking Panel Power(W)'].mean()
    minute_averaged_data_clo = df.groupby('MinuteTimestamp')['Cloud Coverage'].mean()
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(minute_averaged_data_fix.index, minute_averaged_data_fix.values, color='m', label='Fixed Panel Power')
    ax1.plot(minute_averaged_data_spa.index, minute_averaged_data_spa.values, color='orange', label='SPA Panel Power')
    ax1.plot(minute_averaged_data_tra.index, minute_averaged_data_tra.values, color='g', label='Tracking Panel Power')
    ax1.set_xlabel('Time (Hours)')
    ax1.set_ylabel('Power (Watts)')
    ax1.tick_params(axis='y')
    ax2 = ax1.twinx()
    ax2.bar(minute_averaged_data_clo.index,minute_averaged_data_clo.values, color='skyblue', width=1/1440, label = "Cloud Coverage")
    ax2.plot(minute_averaged_data_clo.index,minute_averaged_data_clo.values)
    ax2.set_xlabel('Time (Hours)')
    ax2.set_ylabel('Cloud Coverage (Percentage)')
    ax2.tick_params(axis='y')
    ax2.set_zorder(1)
    ax1.set_zorder(2)
    ax1.patch.set_visible(False)
    plt.title('Panels Power and Cloud Coverage vs Time - Averaged over a minute')
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper left')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.show()

def FifteenMinutePowVsCloud(directory,filename):
    filepath = os.path.join(directory, filename)
    df = pd.read_excel(filepath)
    datetime_objects = pd.to_datetime(df['Time Logged'], format="%H:%M:%S")
    df['Timestamp'] = datetime_objects
    df['MinuteTimestamp'] = df['Timestamp'].dt.round('15min')
    minute_averaged_data_spa = df.groupby('MinuteTimestamp')['SPA Panel Power(W)'].mean()
    minute_averaged_data_fix = df.groupby('MinuteTimestamp')['Fixed Panel Power(W)'].mean()
    minute_averaged_data_tra = df.groupby('MinuteTimestamp')['Tracking Panel Power(W)'].mean()
    minute_averaged_data_clo = df.groupby('MinuteTimestamp')['Cloud Coverage'].mean()
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(minute_averaged_data_fix.index, minute_averaged_data_fix.values, color='m', label='Fixed Panel Power')
    ax1.plot(minute_averaged_data_spa.index, minute_averaged_data_spa.values, color='orange', label='SPA Panel Power')
    ax1.plot(minute_averaged_data_tra.index, minute_averaged_data_tra.values, color='g', label='Tracking Panel Power')
    ax1.set_xlabel('Time (Hours)')
    ax1.set_ylabel('Power (Watts)')
    ax1.tick_params(axis='y')
    ax2 = ax1.twinx()
    ax2.bar(minute_averaged_data_clo.index, minute_averaged_data_clo.values, edgecolor='b', color='skyblue', width=15/1440, label="Cloud Coverage")
    ax2.set_xlabel('Time (Hours)')
    ax2.set_ylabel('Cloud Coverage (Percentage)')
    ax2.tick_params(axis='y')
    ax2.set_zorder(1)
    ax1.set_zorder(2)
    ax1.patch.set_visible(False)
    ax2.patch.set_visible(False)
    plt.title('Panels Power and Cloud Coverage vs Time - Averaged over 15 minutes')
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper left')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.show()

def FifteenMinutePowVsSunElevationAngle(directory, filename):
    filepath = os.path.join(directory, filename)
    df = pd.read_excel(filepath)
    datetime_objects = pd.to_datetime(df['Time Logged'], format="%H:%M:%S")
    df['Timestamp'] = datetime_objects
    df['MinuteTimestamp'] = df['Timestamp'].dt.round('15min')
    df['ZenTimestamp'] = df['Timestamp'].dt.round('min')
    minute_averaged_data_spa = df.groupby('MinuteTimestamp')['SPA Panel Power(W)'].mean()
    minute_averaged_data_fix = df.groupby('MinuteTimestamp')['Fixed Panel Power(W)'].mean()
    minute_averaged_data_tra = df.groupby('MinuteTimestamp')['Tracking Panel Power(W)'].mean()
    minute_averaged_data_zen = df.groupby('MinuteTimestamp')['SPA Zenith'].mean()
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(minute_averaged_data_fix.index, minute_averaged_data_fix.values, color='m', label='Fixed Panel Power')
    ax1.plot(minute_averaged_data_spa.index, minute_averaged_data_spa.values, color='orange', label='SPA Panel Power')
    ax1.plot(minute_averaged_data_tra.index, minute_averaged_data_tra.values, color='g', label='Tracking Panel Power')
    ax1.set_xlabel('Time (Hours)')
    ax1.set_ylabel('Power (Watts)')
    ax1.set_ylim(0,0.6)
    ax1.tick_params(axis='y')
    ax2 = ax1.twinx()
    ax2.plot(minute_averaged_data_zen.index, 90-minute_averaged_data_zen.values, color='k', label="Elevation Angle of the Sun")
    ax2.set_xlabel('Time (Hours)')
    ax2.set_ylabel('Elevation Angle of the Sun (Degrees)')
    ax2.tick_params(axis='y')
    ax2.set_zorder(1)
    ax1.set_zorder(2)
    ax1.patch.set_visible(False)
    ax2.patch.set_visible(False)
    plt.title('Panels Power and Sun Elevation Angle vs Time - Averaged over 15 minutes')
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper left')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.show()

def TotalPower(directory, filename):
    filepath = os.path.join(directory, filename)
    df = pd.read_excel(filepath)
    datetime_objects = pd.to_datetime(df['Time Logged'], format="%H:%M:%S")
    df['Timestamp'] = datetime_objects
    df['HourlyTimestamp'] = df['Timestamp'].dt.round('15min')
    hour_averaged_data_spa = df.groupby('HourlyTimestamp')['SPA Panel Power(W)'].mean()
    hour_averaged_data_fix = df.groupby('HourlyTimestamp')['Fixed Panel Power(W)'].mean()
    hour_averaged_data_tra = df.groupby('HourlyTimestamp')['Tracking Panel Power(W)'].mean()
    SpaTotPower = (hour_averaged_data_spa.values).sum()
    FixTotPower = (hour_averaged_data_fix.values).sum()
    TraTotPower = (hour_averaged_data_tra.values).sum()
    hours = len(hour_averaged_data_spa.index)
    first_timestamp = df['Timestamp'].iloc[0]
    last_timestamp = df['Timestamp'].iloc[-1]
    totalTime = (last_timestamp - first_timestamp).total_seconds()
    algRuns = totalTime//300
    print("How many 15 minute windows = "+str(hours))
    print("How many seconds = "+str(totalTime))
    print("How many times did the algorithm run = "+str(algRuns))
    print("Solar Position Algorithm panel total power when averaged per 15 minutes= "+str(SpaTotPower))
    print("Fixed panel total power when averaged per 15 minutes = "+str(FixTotPower))
    print("Tracking total power when averaged per 15 minutes = "+str(TraTotPower))
    print("Solar Position Algorithm panel average power = "+str((SpaTotPower/hours)-(algRuns*0.000094)*2))
    print("Fixed panel average power = "+str((FixTotPower/hours)))
    print("Tracking average power = "+str((TraTotPower/hours)-(algRuns*0.000094)*2))
    

def list_functions():
    print("Functions:")
    print("1. Data Averaged")
    print("2. Power Vs Angle")
    print("3. Power Vs Cloud")
    print("4. Minute Power Vs Cloud")
    print("5. Fifteen Minute Power Vs Cloud")
    print("6. Fifteen Minute Power Vs Sun Elevation Angle")
    print("7. Power Generated")

def main():
    list_functions()
    choice = input("Enter the corresponding number to choose a function: ")

    if choice == '1':
        for filename in specific_filenames:
            DataAveraged(directory, filename)
    elif choice == '2':
        for filename in specific_filenames:
            PowerVsAngle(directory, filename)
    elif choice == '3':
        for filename in specific_filenames:
            PowVsCloud(directory, filename)
    elif choice == '4':
        for filename in specific_filenames:
            MinutePowVsCloud(directory, filename)
    elif choice == '5':
        for filename in specific_filenames:
            FifteenMinutePowVsCloud(directory, filename)
    elif choice == '6':
        for filename in specific_filenames:
            FifteenMinutePowVsSunElevationAngle(directory, filename)
    elif choice == '7':
        for filename in specific_filenames:
            TotalPower(directory, filename)
    else:
        print("Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()