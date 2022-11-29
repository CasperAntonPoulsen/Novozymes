from datetime import datetime, timedelta
import pandas as pd

from libcomcat.dataframes import get_summary_data_frame
from libcomcat.search import  search

class EarthquakeData:
    def __init__(self, filePath=None):
        self.filePath = filePath

        self.coordinates = dict(
            europe = {
                "maxlat":72,
                "minlat":34,
                "minlon":-25,
                "maxlon":46
            },
            us = {
                "maxlat":50,
                "minlat":25,
                "minlon":-125,
                "maxlon":-65
            }
        )

    def loadFromFile(self, deltaYears, region):
        if self.filePath is None:
            raise OSError("No filepath is present")
        else:
            df = pd.read_json(region + "_" + self.filePath)

            starttime=datetime.now()-timedelta(days=365*deltaYears)
            
            return df[df["time"] > starttime.timestamp()]

    def loadFromAPI(self, deltaYears, region):
        df = get_summary_data_frame(search(starttime=datetime.now()-timedelta(days=365*deltaYears), 
                                           endtime=datetime.now(),
                                           minlatitude=self.coordinates[region]["minlat"], 
                                           maxlatitude=self.coordinates[region]["maxlat"], 
                                           minlongitude=self.coordinates[region]["minlon"], 
                                           maxlongitude=self.coordinates[region]["maxlon"]))
        return df

    def loadData(self, deltaYears, region): 
        try:
            df = self.loadFromFile(deltaYears, region)
        except OSError:
            df = self.loadFromAPI(deltaYears, region)

        if df.empty:
            raise OSError("Could not load dataset, no file is present and API does not respond")
        return df

