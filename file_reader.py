import pandas as pd
from pathlib import Path
import re

class CSVReader: 
    
    def __init__(self):
        self.data_directory = Path("data")
        self.valid_data_names = ["Daniel", "felix", "ferdi", "georg", "lennart", "marcel", "maximilian", "patrick", "thu", "vanessa"]
        self.needs_gyro_conversion = ["lennart", "maximilian"]
        
        self.recordings = []
    
    def get_recording_as_df(self, path):
        df = pd.read_csv(path)
        return df
    
    def read_all_data_files(self):
        for name in self.valid_data_names:
            directory = self.data_directory / name
            for file in directory.glob("*.csv"):
                tags = re.split(r"-", file.stem)
                recording = {
                    "name" : tags[0].lower(),
                    "activity" : tags[1].lower(),
                    "frequency": tags[2].lower(),
                    "sensor_placement": tags[3].lower(),
                    "set" : tags[4],
                    "data": self.get_recording_as_df(file)
                }
                self.recordings.append(recording)


#reader = CSVReader()
#reader.read_all_data_files()
#print(reader.recordings)
