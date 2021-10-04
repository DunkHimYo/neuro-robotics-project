import pandas as pd
import datetime
import numpy as np

class frame_calculator:
    def __init__(self, client, sub: list):
        self.client = client  
        self.sub = sub
        self.sub_data = client.subscribe(streams=sub)
        self.columns = {}
        for i in range(len(self.sub_data['success'])):
            self.columns[self.sub_data['success'][i]['streamName']] = self.sub_data['success'][i]['cols']
        self.title_chk = {}

        for key in self.columns.keys():
            self.title_chk[key] = 1


    def requests_to_data_frame(self, data_values,time=None):
        data_sample_frames=None

        data_values=np.array(data_values,dtype=np.object)
        if len(data_values.shape)>1:
            data_sample_frames = pd.DataFrame(
                data=data_values,
                columns=self.columns[self.sub[0]])
        else:
            data_sample_frames = pd.DataFram(
                data=data_values[np.newaxis],
                columns=self.columns[self.sub[0]])

        if time is not None:
            data_sample_frames.index=[datetime.datetime.fromtimestamp(i) for i in time]

        return data_sample_frames
