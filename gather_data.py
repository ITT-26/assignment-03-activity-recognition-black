from DIPPID import SensorUDP
import pandas as pd
import time
import os
from pathlib import Path

# this program gathers sensor data

PORT = 5700
sensor = SensorUDP(PORT)

name = "test"
placement = "hand"


activities = ["running", "rowing", "lifting", "jumpingjacks"]
sampling_rates = [20, 100]
sets_per_activity = 5

activity_idx = 0
sampling_rate_idx = 0
set_counter = 1
is_recording = False


df = pd.DataFrame(
    columns=["id", "timestamp", "acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z"]
)
row_id = 1

while activity_idx < len(activities):  # loop for going through all activities
    sampling_rate_idx = 0  # reset sampling rate idx when starting a new activity
    while sampling_rate_idx < len(
        sampling_rates
    ):  # loop for sampling rates (20 Hz and 100 Hz)
        set_counter = (
            1  # reset set_counter when starting recording with next sampling rate
        )

        while (
            set_counter <= 5
        ):  # loop for running 5 sets of each sampling rate and acitivity

            if (
                not is_recording
            ):  # when recording is not running check for button 1 to start recording
                if sensor.has_capability("button_1"):
                    if int(sensor.get_value("button_1")) == 1:
                        is_recording = True
                        print(
                            "Start recording for "
                            f"activity {activities[activity_idx]} "
                            f"sampling rate {sampling_rates[sampling_rate_idx]} Hz "
                            f"Set {set_counter}"
                        )

            if is_recording:  # when recording was started do the recording obv
                row_data = {}  # dataset for each row  as dict
                row_data["id"] = row_id  # append row_id to row_data
                row_data["timestamp"] = (
                    time.time()
                )  # append timestamp to row_data (format from example file)

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

                df.loc[len(df)] = (
                    row_data  # transform the row_data dict to real df row (and append)
                )

                row_id += 1

                if sensor.has_capability(
                    "button_2"
                ):  # check for button 2 click to stop recording of the set
                    if int(sensor.get_value("button_2")) == 1:
                        print(
                            "Stop recording for "
                            f"activity {activities[activity_idx]} "
                            f"sampling rate {sampling_rates[sampling_rate_idx]} Hz "
                            f"Set {set_counter}"
                        )

                        file_name = (  # put together the filename in format from assignment
                            f"{name}-"
                            f"{activities[activity_idx]}-"
                            f"{sampling_rates[sampling_rate_idx]}Hz-"
                            f"{placement}-"
                            f"{set_counter}.csv"
                        )
                        path = f".{os.sep}gathered_data{os.sep}{name}{os.sep}"  # set the directory path
                        Path(path).mkdir(
                            exist_ok=True, parents=True  # create the path if it doesnt exist already
                        ) # parents True for nested path
                        full_path = path + file_name  # combine for full_path
                        df.dropna()  # just in case of NaN values
                        df.to_csv(full_path, index=False)  # save the df to file
                        # no pandas index (like in example file)

                        print(f"File saved to {full_path}")

                        is_recording = False  # stop the recording (recording = 1 File)

                        df = df.iloc[0:0]  # clear df data (but keep columns)

                        set_counter += 1  # increase set counter
                        row_id = 1  # reset row_id when starting a new set
                        if (
                            set_counter > 5
                        ):  # if set is higher the required go to next sampling rate
                            sampling_rate_idx += 1
                            if sampling_rate_idx >= len(
                                sampling_rates
                            ):  # if all sampling rates done go to next acitvity
                                activity_idx += 1

            time.sleep(0.01)
           

sensor.disconnect()
