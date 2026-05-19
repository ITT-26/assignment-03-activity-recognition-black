import pandas as pd
from pathlib import Path
import re


class CSVReader:

    def __init__(self):
        self.data_directory = Path("data")
        self.valid_data_names = [
            # "Daniel", exclude daniel because of wrong samples, 
            "felix",
            "ferdi",
            "georg",
            "lennart",
            "marcel",
            "maximilian",
            "patrick",
            "thu",
            "vanessa",
        ]

    def get_recording_as_df(self, path):
        df = pd.read_csv(path)
        return df

    def get_data_files_as_df(self):

        recordings = []

        NEEDED_TAGS = 5

        for name in self.valid_data_names:
            directory = self.data_directory / name
            for file in directory.glob("*.csv"):
                tags = re.split(r"-", file.stem)
                
                for i, tag in enumerate(tags):
                    if tag == 'jumping_jacks':
                        tags[i] = 'jumpingjacks'
                        
                tag_index = (
                    len(tags) - NEEDED_TAGS
                )  # for more than one name in file name
                recording = {
                    "name": tags[tag_index].lower(),
                    "activity": tags[tag_index + 1].lower(),
                    "sample_rate": tags[tag_index + 2].lower(),
                    "sensor_placement": tags[tag_index + 3].lower(),
                    "set": tags[tag_index + 4],
                    "data": self.get_recording_as_df(file),
                }
                recordings.append(recording)

        return recordings


# reader = CSVReader()
# reader.read_all_data_files()
# print(reader.recordings)
