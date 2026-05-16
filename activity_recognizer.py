# this program recognizes activities
from file_reader import CSVReader
from data_processing import DataPreprocessser
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier
from sklearn import svm

TIME_WINDOW = 2

strategies = {
    "normal": lambda kernel: svm.SVC(kernel=kernel),
    "one_vs_one": lambda kernel: OneVsOneClassifier(svm.SVC(kernel=kernel)),
    "one_vs_rest": lambda kernel: OneVsRestClassifier(svm.SVC(kernel=kernel)),
}

classifiers = []
predictions_list = []

def data_setup(time_window):
    reader = CSVReader()
    recordings = reader.get_data_files_as_df()
    preprocessor = DataPreprocessser()
    preprocessor.convert_gyro_data(recordings)
    
    train_recordings, test_recordings = preprocessor.split_recordings_to_train_test(recordings)
    # suggestion from ChatGPT to already split here since train and test data should be normalized
    # only with the scaler fit to the test data
    
    train_windows = preprocessor.create_time_windows(train_recordings, time_window)
    test_windows =  preprocessor.create_time_windows(test_recordings, time_window)
    
        
    classifier_train_data = preprocessor.transform_windows_to_features(train_windows)
    classifier_test_data = preprocessor.transform_windows_to_features(test_windows)
    
    standard_scaled_train = preprocessor.perform_standard_scaling(classifier_train_data, classifier_train_data)
    standard_scaled_test = preprocessor.perform_standard_scaling(classifier_train_data, classifier_test_data)
    
    normalized_train = preprocessor.perform_normalization(standard_scaled_train, standard_scaled_train )
    normalized_test = preprocessor.perform_normalization(standard_scaled_train, standard_scaled_test)

def model_train()
    pass
def capure_data_continuosly():
    pass

data_setup(TIME_WINDOW)
 