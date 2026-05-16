# this program recognizes activities
from file_reader import CSVReader
from data_processing import DataPreprocessser
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier
from sklearn import svm
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd


TIME_WINDOW = 2

strategies = { # das hier wird eigentlich auch nicht gebracuht nur im notebook für testing
    "normal": lambda kernel: svm.SVC(kernel=kernel),
    "one_vs_one": lambda kernel: OneVsOneClassifier(svm.SVC(kernel=kernel)),
    "one_vs_rest": lambda kernel: OneVsRestClassifier(svm.SVC(kernel=kernel)),
}

kernels = {"linear", "poly", "rbf", "sigmoid"}

classifiers = []
predictions_list = []


def data_setup(time_window):
    reader = CSVReader()
    recordings = reader.get_data_files_as_df()
    preprocessor = DataPreprocessser()
    preprocessor.convert_gyro_data(recordings)

    train_recordings, test_recordings = preprocessor.split_recordings_to_train_test(
        recordings
    )
    # suggestion from ChatGPT to already split here since train and test data should be normalized
    # only with the scaler fit to the test data

    train_windows = preprocessor.create_time_windows(train_recordings, time_window)
    test_windows = preprocessor.create_time_windows(test_recordings, time_window)

    classifier_train_data = preprocessor.transform_windows_to_features(train_windows)
    classifier_test_data = preprocessor.transform_windows_to_features(test_windows)

    standard_scaled_train = preprocessor.perform_standard_scaling(
        classifier_train_data, classifier_train_data
    )
    standard_scaled_test = preprocessor.perform_standard_scaling(
        classifier_train_data, classifier_test_data
    )

    normalized_train = preprocessor.perform_normalization(
        standard_scaled_train, standard_scaled_train
    )
    normalized_test = preprocessor.perform_normalization(
        standard_scaled_train, standard_scaled_test
    )

    train_activities = normalized_train["activity"]
    train_features = normalized_train.copy().drop(columns="activity")

    test_activities = normalized_test["activity"]
    test_features = normalized_test.copy().drop(columns="activity")

    return train_activities, train_features, test_activities, test_features

def train_and_evaluate(classifier, features_train, classes_train, features_test, classes_test): # function code from notebook by max
    classifier.fit(features_train, classes_train)

    classes_predicted = classifier.predict(features_test) #hier eigentlich doch predict auf aufgezeichnete daten
     
    accuracy = accuracy_score(classes_test, classes_predicted) # für was braucht man dann test hier? braucht man das im laufenden recogniizer?
    return classes_predicted, accuracy

def plot_classification_report(classes_test, classes_predicted): # fucntion code from notebook by max
    report = classification_report(classes_test, classes_predicted, output_dict=True)
    df = pd.DataFrame(report)
    return df



def capture_data_continously():
    pass


train_labels, train_features, test_labels, test_features = data_setup(TIME_WINDOW)

classifier = function(kernels[0])
classifiers.append(classifier)
predictions, accuracy = train_and_evaluate(classifier, train_features, train_labels, test_features, train_labels)
