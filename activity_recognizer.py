# this program recognizes activities
from file_reader import CSVReader
import data_processing
from sklearn.multiclass import OneVsRestClassifier
from sklearn import svm
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd


def data_setup(time_window):
    reader = CSVReader()
    recordings = reader.get_data_files_as_df()
    data_processing.convert_gyro_data(recordings)

    train_recordings, test_recordings = data_processing.split_recordings_to_train_test(
        recordings
    )
    # suggestion from ChatGPT to already split here since train and test data should be normalized
    # only with the scaler fit to the test data

    train_windows = data_processing.create_time_windows(train_recordings, time_window)
    test_windows = data_processing.create_time_windows(test_recordings, time_window)

    classifier_train_data = data_processing.transform_windows_to_features(train_windows)
    classifier_test_data = data_processing.transform_windows_to_features(test_windows)

    standard_scaled_train = data_processing.perform_standard_scaling(
        classifier_train_data, classifier_train_data
    )
    standard_scaled_test = data_processing.perform_standard_scaling(
        classifier_train_data, classifier_test_data
    )

    normalized_train = data_processing.perform_normalization(
        standard_scaled_train, standard_scaled_train
    )
    normalized_test = data_processing.perform_normalization(
        standard_scaled_train, standard_scaled_test
    )

    train_activities = normalized_train["activity"]
    train_features = normalized_train.copy().drop(columns="activity")

    test_activities = normalized_test["activity"]
    test_features = normalized_test.copy().drop(columns="activity")

    return train_activities, train_features, test_activities, test_features


def train_and_evaluate(
    classifier, features_train, classes_train, features_test, classes_test
):
    # function code from notebook by max
    classifier.fit(features_train, classes_train)

    classes_predicted = classifier.predict(features_test)
    # hier eigentlich doch predict auf aufgezeichnete daten

    accuracy = accuracy_score(classes_test, classes_predicted)
    # für was braucht man dann test hier? braucht man das im laufenden recogniizer?
    return classes_predicted, accuracy


def train_classifier(classifier, features_train, train_classes):
    classifier.fit(features_train, train_classes)


def predict_classes(classifier, feature_data):
    classes_predicted = classifier.predict(feature_data)
    return classes_predicted


def plot_classification_report(
    classes_test, classes_predicted
):  # fucntion code from notebook by max
    report = classification_report(classes_test, classes_predicted, output_dict=True)
    df = pd.DataFrame(report)
    return df


def classifier_setup(train_classes, train_features):
    classifier = OneVsRestClassifier(svm.SVC(kernel="rbf"))
    train_classifier(classifier, train_classes, train_features)
    return classifier


TIME_WINDOW = 2

train_classes, train_features, test_classes, test_features = data_setup(TIME_WINDOW)
classifier = classifier_setup(train_features, train_classes)
prediction = predict_classes(classifier, test_features.iloc[[0]])
# hier dann aufgezeichnetes window rein

print(f"Prediction: {prediction}")
print(f"Real: {test_classes.iloc[0]}")
