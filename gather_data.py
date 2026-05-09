from DIPPID import SensorUDP
import pandas as pd
import time
import os
from pathlib import Path

# this program gathers sensor data

PORT = 5700
sensor = SensorUDP(PORT)

name = input("\nPlease enter your name for the file name: ")

placements = {1: "hand", 2: "pocket"}
placement_id = None
placement = None

while placement_id is None or placement is None:
    try:
        placement_id = int(
            input(
                "\nPlease enter the sensor placement you want to record:\n"
                "1 = hand\n"
                "2 = pocket\n"
            )
        )
        placement = placements[placement_id]

    except (KeyError, ValueError):
        print("\nInvalid input. Try again.")


activities = ["running", "rowing", "lifting", "jumpingjacks"]
sampling_rates = [100]
sets_per_activity = 5

activity_idx = 0
sampling_rate_idx = 0
set_counter = 1
is_recording = False
recording_duration = 10

df = pd.DataFrame(
    columns=["id", "timestamp", "acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z"]
)
row_id = 1
recording_start_time = 0
next_sample_time = 0

print(
    "\nReady to start recording. The first set is:\n"
    f"{activities[activity_idx]} with sampling rate {sampling_rates[sampling_rate_idx]} Hz"
    f"\nSet number: {set_counter}\nPress Button 1 to start"
)

while activity_idx < len(activities):  # loop for going through all activities

    while sampling_rate_idx < len(sampling_rates):
        # loop for sampling rates (20 Hz and 100 Hz)

        freq_time_window = 1 / sampling_rates[sampling_rate_idx]
        # time window between samples with current frequencyone sample

        rows = []

        while set_counter <= sets_per_activity:
            # loop for running 5 sets of each sampling rate and acitivity

            if not is_recording:
                # when recording is not running check for button 1 to start recording
                if sensor.has_capability("button_1"):
                    if int(sensor.get_value("button_1")) == 1:
                        is_recording = True
                        rows = []  # clear rows
                        print(
                            "\nButton 1 Pressed\nRecording will start in 3 seconds.\n"
                            "Position the sensor and start the activity now.\n"
                            "Recording will stop after 10 seconds!"
                        )
                        time.sleep(
                            3
                        )  # 3 sec grace for getting ready e.g. putting phone in pocket
                        print("\nStart!")
                        row_id = 1  # reset row_id when starting a new set
                        recording_start_time = time.time()
                        next_sample_time = recording_start_time

                time.sleep(0.01)  # sleep when not recording and button not pressed

            if is_recording:  # when recording was started do the recording
                recording_runtime = time.time() - recording_start_time
                # calculate current runtime

                if not recording_runtime >= recording_duration:
                    if time.time() < next_sample_time:
                        time.sleep(0.0001)  # sleep time time until next iteration
                        continue  # if not enough time has passend simply continue and check again in next iteration

                    next_sample_time += freq_time_window

                    row_data = {}  # dataset for each row as dict
                    row_data["id"] = row_id  # append row_id to row_data
                    row_data["timestamp"] = time.time()
                    # append timestamp to row_data (format from example file)

                    if sensor.has_capability("accelerometer"):
                        acc_data = sensor.get_value("accelerometer")
                        row_data["acc_x"] = acc_data["x"]
                        row_data["acc_y"] = acc_data["y"]
                        row_data["acc_z"] = acc_data["z"]
                        # append accelerometer data to row_data

                    if sensor.has_capability("gyroscope"):
                        gyro_data = sensor.get_value("gyroscope")
                        row_data["gyro_x"] = gyro_data["x"]
                        row_data["gyro_y"] = gyro_data["y"]
                        row_data["gyro_z"] = gyro_data["z"]
                        # append gyroscope data to row_data

                    rows.append(
                        row_data
                    )  # append to list instead of df directly for better performance
                    # df.loc[len(df)] = row_data
                    # transform the row_data dict to real df row (and append)

                    row_id += 1  # update row id for next iteration

                if recording_runtime >= recording_duration:
                    # if runtime longer then specified duration exit recording
                    print(f"\nRecording stopped after {recording_runtime}")

                    file_name = (  # put together the filename in format from assignment
                        f"{name}-"
                        f"{activities[activity_idx]}-"
                        f"{sampling_rates[sampling_rate_idx]}Hz-"
                        f"{placement}-"
                        f"{set_counter}.csv"
                    )
                    path = (
                        f".{os.sep}data{os.sep}{name}{os.sep}"  # set the directory path
                    )
                    Path(path).mkdir(exist_ok=True, parents=True)
                    # create the path if it doesnt exist already
                    # parents True for nested path

                    full_path = path + file_name  # combine for full_path

                    df = pd.DataFrame(rows)
                    df = df.dropna()  # just in case of NaN values
                    df.to_csv(full_path, index=False)  # save the df to file
                    # no pandas index (like in example file)

                    print(f"File saved to {full_path}")

                    is_recording = False  # stop the recording (recording = 1 File)

                    df = df.iloc[0:0]  # clear df data (but keep columns)

                    set_counter += 1  # increase set counter

                    if set_counter > 5:
                        # if set is higher the required go to next sampling rate
                        sampling_rate_idx += 1

                        set_counter = 1
                        # reset set_counter when starting recording with next sampling rate

                        if sampling_rate_idx >= len(sampling_rates):
                            # if all sampling rates done go to next acitvity
                            activity_idx += 1

                            sampling_rate_idx = 0
                            # reset sampling rate idx for starting a new activity

                    if activity_idx < len(activities):
                        print(
                            "Ready to start next recording. The next set is:\n"
                            f"{activities[activity_idx]} with sampling rate {sampling_rates[sampling_rate_idx]} Hz"
                            f"\nSet number: {set_counter}\nPress Button 1 to start"
                        )
                    else:
                        print(
                            f"\nAll recordings for sensor placement {placement} finished!"
                        )
                        sensor.disconnect()
                        exit()
