import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split


def convert_gyro_data(recordings):
    need_gyro_conversion = ["lennart", "maximilian"]
    for recording in recordings:
        if recording["name"] in need_gyro_conversion:
            recording["data"]["gyro_x"] = np.deg2rad(recording["data"]["gyro_x"])
            recording["data"]["gyro_y"] = np.deg2rad(recording["data"]["gyro_y"])
            recording["data"]["gyro_z"] = np.deg2rad(recording["data"]["gyro_z"])


def split_recordings_to_train_test(recordings):
    # not needed in live system was only needed for model testing
    training, test = train_test_split(
        recordings,
        test_size=0.2,
        stratify=[
            f"{r['activity']}_{r['name']}_{r['sensor_placement']}_{r['sample_rate']}"
            for r in recordings
        ],
    )
    return training, test


def create_time_windows(recordings, window_length):
    windows = []

    for rec in recordings:
        data = rec["data"]
        activity = rec["activity"]
        sample_rate = int(rec["sample_rate"].replace("hz", ""))
        window_size = sample_rate * window_length

        window_start = 0
        window_end = window_size

        while window_end <= len(data):
            window = data.iloc[window_start:window_end].copy()
            window["activity"] = activity
            windows.append(window)

            window_start += window_size
            window_end += window_size

    return windows


def transform_windows_to_features(windows):
    feature_rows = []

    for window in windows:
        feature_row = {}

        feature_row["activity"] = window["activity"].iloc[0]

        for acc_col in ["acc_x", "acc_y", "acc_z"]:
            feature_row[f"{acc_col}_mean"] = window[acc_col].mean()
            feature_row[f"{acc_col}_std"] = window[acc_col].std()
            feature_row[f"{acc_col}_min"] = window[acc_col].min()
            feature_row[f"{acc_col}_max"] = window[acc_col].max()

        for gyro_col in ["gyro_x", "gyro_y", "gyro_z"]:
            feature_row[f"{gyro_col}_mean"] = window[gyro_col].mean()
            feature_row[f"{gyro_col}_std"] = window[gyro_col].std()
            feature_row[f"{gyro_col}_min"] = window[gyro_col].min()
            feature_row[f"{gyro_col}_max"] = window[gyro_col].max()

        acc_strengths = np.sqrt(
            window["acc_x"] ** 2 + window["acc_y"] ** 2 + window["acc_z"] ** 2
        )
        gyro_strengths = np.sqrt(
            window["gyro_x"] ** 2 + window["gyro_y"] ** 2 + window["gyro_z"] ** 2
        )

        feature_row["acc_strenght_mean"] = acc_strengths.mean()
        feature_row["acc_strenght_std"] = acc_strengths.std()

        feature_row["gyro_strenght_mean"] = gyro_strengths.mean()
        feature_row["gyro_strenght_std"] = gyro_strengths.std()

        acc_strengths_hamming = acc_strengths * np.hamming(len(acc_strengths))
        acc_fft = np.fft.rfft(acc_strengths_hamming)
        acc_freqs = np.fft.rfftfreq(len(acc_strengths_hamming), 1 / len(window))
        feature_row["acc_dom_freq"] = acc_freqs[np.argmax(np.abs(acc_fft))]

        gyro_strengths_hamming = gyro_strengths * np.hamming(len(gyro_strengths))
        gyro_fft = np.fft.rfft(gyro_strengths_hamming)
        gyro_freqs = np.fft.rfftfreq(len(gyro_strengths_hamming), 1 / len(window))
        feature_row["dom_gyro_freq"] = gyro_freqs[np.argmax(np.abs(gyro_fft))]

        feature_rows.append(feature_row)

    classifier_data = pd.DataFrame(feature_rows)
    return classifier_data


def fit_and_get_standard_scaler(train_df):
    scaler = StandardScaler()
    scaler.fit(train_df[[col for col in train_df.columns if col != "activity"]])
    return scaler


def fit_and_get_min_max_scaler(train_df):
    scaler = MinMaxScaler()
    scaler.fit(train_df[[col for col in train_df.columns if col != "activity"]])
    return scaler


def perform_scaling(scaler, df_to_scale):
    scaled_samples = scaler.transform(
        df_to_scale[[col for col in df_to_scale.columns if col != "activity"]]
    )
    df_scaled = df_to_scale.copy()
    df_scaled[[col for col in df_scaled.columns if col != "activity"]] = scaled_samples
    return df_scaled
