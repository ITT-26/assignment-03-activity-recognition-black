# this program recognizes activities
from file_reader import CSVReader
import data_processing
from sklearn.multiclass import OneVsOneClassifier
from sklearn import svm
import pandas as pd
import numpy as np
import threading
import time
from DIPPID import SensorUDP
from collections import deque


class ActivityRecognizer:
    def __init__(self, player_name):
        self.TIME_WINDOW = 2
        self.SAMPLE_RATE = 20  # in Hz
        # 20 works better than 100 in test
        
        self.classifier = None
        self.amount_of_samples_for_prediction = self.TIME_WINDOW * self.SAMPLE_RATE

        self.standard_scaler = None
        self.min_max_scaler = None

        self.sample_data = deque(maxlen=self.amount_of_samples_for_prediction)
        self.sample_features = []

        self.sensor_thread = None
        self.interrupt_event_collecting = threading.Event()

        self.recognizer_thread = None
        self.interrupt_event_recognizer = threading.Event()

        self.prediction = None
        self.confidence = None

        self.player = player_name

    def data_setup(self):
        reader = CSVReader()
        recordings = reader.get_data_files_as_df()
        for rec in recordings.copy():
            if rec["sample_rate"] == '100hz':
                recordings.remove(rec)
        # testing showed train only with sample rate 100 for slightly better accuracy
            
        data_processing.convert_gyro_data(recordings)

        data_windows = data_processing.create_time_windows(recordings, self.TIME_WINDOW)
        # all data for  training in live system
        classifier_data = data_processing.transform_windows_to_features(
            data_windows, self.TIME_WINDOW
        )

        self.standard_scaler = data_processing.fit_and_get_standard_scaler(
            classifier_data
        )
        self.min_max_scaler = data_processing.fit_and_get_min_max_scaler(
            classifier_data
        )
        standard_scaled_data = data_processing.perform_scaling(
            self.standard_scaler, classifier_data
        )
        normalized_data = data_processing.perform_scaling(
            self.min_max_scaler, standard_scaled_data
        )

        activities = normalized_data["activity"]
        features = normalized_data.copy().drop(columns="activity")

        return activities, features

    def train_classifier(self, features, activities):
        self.classifier.fit(features, activities)

    def classifier_setup(self, features, activities):
        self.classifier = svm.SVC(kernel="poly", degree=4, gamma="scale",  C=10, coef0=0, probability=True) 
        # testing results hier einsetzen
        self.train_classifier(features, activities)

    def predict_classes(self, feature_data):
        classes_predicted = self.classifier.predict(feature_data)
        return classes_predicted

    def get_decision_data(self, feature_data): 
        # nur für OneVsOne gebraucht
        decision_data = self.classifier.decision_function(feature_data)
        return decision_data
    
    def predict_probabilities(self, feature_data):
        probabilities = self.classifier.predict_proba(feature_data)
        return probabilities

    def collect_sensor_data(self, data_deque, sample_rate, interruption_event):
        PORT = 5700
        sensor = SensorUDP(PORT)
        time_between_samples = 1 / sample_rate
        next_sample = time.time()
        while not interruption_event.is_set():
            if time.time() >= next_sample:
                sample = {
                    "acc_x": 0.0,
                    "acc_y": 0.0,
                    "acc_z": 0.0,
                    "gyro_x": 0.0,
                    "gyro_y": 0.0,
                    "gyro_z": 0.0,
                }
                sample["timestamp"] = time.time()
                if sensor.has_capability("accelerometer"):
                    acc_data = sensor.get_value("accelerometer")
                    sample["acc_x"] = acc_data["x"]
                    sample["acc_y"] = acc_data["y"]
                    sample["acc_z"] = acc_data["z"]
                if sensor.has_capability("gyroscope"):
                    gyro_data = sensor.get_value("gyroscope")
                    sample["gyro_x"] = gyro_data["x"]
                    sample["gyro_y"] = gyro_data["y"]
                    sample["gyro_z"] = gyro_data["z"]
                data_deque.append(sample)
            time.sleep(time_between_samples / 2)

        sensor.disconnect()
        # disconnect sensor bei interrupt event

    def start_data_collection(self):
        self.sensor_thread = threading.Thread(
            target=self.collect_sensor_data,
            args=(self.sample_data, self.SAMPLE_RATE, self.interrupt_event_collecting),
        )
        self.sensor_thread.start()

    def prepare_recognizer(self):
        # das als erstes aus fitness_trainer.py
        acitvities, features = self.data_setup()

        self.classifier_setup(features, acitvities)
        print("Ready to start! Classifier is ready!")

    def run_recognizer(self, interruption_event):
        while not interruption_event.is_set():
            if len(self.sample_data) >= self.amount_of_samples_for_prediction:

                start_time = time.time()
                live_recording = [
                    {
                        "name": self.player,
                        "activity": None,
                        "sample_rate": f"{self.SAMPLE_RATE}hz",
                        "data": pd.DataFrame(self.sample_data),
                    }
                ]
                data_processing.convert_gyro_data(live_recording)
                data_window = data_processing.create_time_windows(
                    live_recording, self.TIME_WINDOW
                )
                classifier_data = data_processing.transform_windows_to_features(
                    data_window, self.TIME_WINDOW
                )

                # print(classifier_data)
                ACC_THRESHHOLD = 1 # for sensor on table (not moving)
                 # GYRO_THRESHHOLD = 0.5 not needed after LOSO testing

                if (
                    classifier_data["acc_strenght_mean"].iloc[0] < ACC_THRESHHOLD
                    #and classifier_data["gyro_strenght_mean"].iloc[0] < GYRO_THRESHHOLD
                ):
                    # No movement so no predicition
                    self.prediction = None
                    self.confidence = 0
                    time.sleep(0.05)
                    continue

                standard_scaled_data = data_processing.perform_scaling(
                    self.standard_scaler, classifier_data
                )
                normalized_data = data_processing.perform_scaling(
                    self.min_max_scaler, standard_scaled_data
                )

                self.sample_features = normalized_data.copy().drop(columns="activity")

                self.prediction = self.predict_classes(self.sample_features)[0]

                # decision data nur für OneVsOne
                # decision_data = self.get_decision_data(self.sample_features)[0]
                # print(decision_data)

                self.confidence = self.predict_probabilities(self.sample_features)[0].max()
                # für OneVsOne: decision_data.max() / decision_data.sum()

                # print(f"Prediction: {self.prediction} in time: {time.time()- start_time}")
            time.sleep(0.05)

    def start_recognizer(self):
        # das in fitness trainer wenn start des trainings sozusagen
        self.start_data_collection()
        self.recognizer_thread = threading.Thread(
            target=self.run_recognizer, args=(self.interrupt_event_collecting,)
        )
        self.recognizer_thread.start()

    def stop_recognizer(self):
        # das bei beedingung des trainings
        self.interrupt_event_collecting.set()
        self.interrupt_event_recognizer.set()
        self.sensor_thread.join()
        self.recognizer_thread.join()

        print("Recognizer stopped!")

    def get_prediction(self):
        return self.prediction

    def get_confidence(self):
        return self.confidence
