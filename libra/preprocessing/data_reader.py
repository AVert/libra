import os
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.python.client import device_lib


class DataReader():
    def __init__(self, filepath, trim=False, trim_format='random', trim_ratio=0.20, strat_col_index=0):
        '''
        Constructor for the DataReader class.

        The DataReader class creates a Pandas DataFrame object
        based off of the datset's file extension, the format of trimming that needs to be applied to the
        dataset (i.e. random sampling or stratified sampling), how much of the dataset needs to be trimmed,
        and the index of the column that the dataset will be sampled against using the stratified sampling technique.

        :param filepath: The file path to the dataset (str)
        :param trim: Whether the dataset should be trimmed or not (bool)
        :param trim_format: The format/type of trimming (str)
        :param trim_ratio: The proportion of the dataset that needs to be trimmed (float)
        :param strat_col_index: The index of the column that the dataset will be sampled against using the
        stratified sampling technique (int)
        '''
        self.filepath = filepath
        self.trim = trim
        self.trim_format = trim_format
        self.trim_ratio = trim_ratio
        self.strat_col_index = strat_col_index

    def retrieve_file_size(self):
        '''
        Returns the size of the dataset in megabytes

        :return: the size of the dataset in megabytes (float)
        '''
        file_stats = os.stat(self.filepath)
        return (file_stats.st_size / (1024 ** 2))

    def retrieve_extension(self):
        '''
        Returns the dataset's file extension (i.e. .csv, .json, .xlsx, etc.)

        :return: the dataset's file extension (str)
        '''
        ext_index = self.filepath.rindex('.')
        return self.filepath[ext_index:]

    # Creates a Pandas DataFrame object based off of what the inputted
    # dataset's extension is
    def data_generator(self):
        '''
        Creates a Pandas DataFrame object based off of the dataset's file extension, whether a GPU is available or not,
        whether the user wants the dataset to be trimmed or not, and the format of trimming specified by the user.

        NOTE: This function currently only supports .csv (comma-separated values file),
        .xlsx (Microsoft Excel Open XML Spreadsheet), and .json (JavaScript Object Notation) files

        If the user's device contains a GPU, the dataset won't be trimmed unless the user specifies so. If the user's
        device doesn't contain a GPU, the dataset will automatically be trimmed regardless of whether the user specified
        for the dataset to be trimmed or not in order to ensure efficient processing by the CPU.

        If the user doesn't specify a specific form of trimming they want to apply to the dataset, random sampling will
        be applied by default.

        If the user doesn't specify a proportion/ratio of how much of the dataset needs to be trimmed, 20% of the
        dataset will be trimmed by default.

        If the user specifies that they want to apply "stratified sampling" to the dataset and they haven't specified a
        column's index that they want to stratify against, the first column (index of 0) will be chosen by default.

        :return: The dataset after being trimmed/pre-processed (Pandas DataFrame)
        '''
        if self.retrieve_extension() == '.csv':
            df = pd.read_csv(self.filepath)
        elif self.retrieve_extension() == '.xlsx':
            df = pd.read_excel(self.filepath)
            for data in df:
                if df[data].dtype.name == 'int64':
                    df[data] = df[data].astype(float)
        elif self.retrieve_extension() == '.json':
            df = pd.read_json(self.filepath)

        if self.is_gpu_available() == False:
            self.trim = True
        if self.trim == True:
            if self.trim_format == 'random':
                df = df.sample(frac=(1.0 - self.trim_ratio))
            elif self.trim_format == 'stratify':
                # ADD STRATIFYING TECHNIQUE HERE
                y = df[df.columns[self.strat_col_index]]
                del df[df.columns[self.strat_col_index]]

                x_train, x_test, y_train, y_test = train_test_split(df, y, stratify=y, test_size=self.trim_ratio, random_state=0)

                df = pd.concat([x_test, y_test])

        return df

    def get_available_gpus(self):
        '''
        Returns a list of available GPUs on the current device running the program

        :return: List of available GPUs on the current device (list of Strings)
        '''
        local_device_protos = device_lib.list_local_devices()
        return [device.name for device in local_device_protos
                if device.device_type == 'GPU']

    def is_gpu_available(self):
        '''
        Returns a boolean value representing whether the current device has a GPU or not

        :return: Whether the current device has a GPU or not (bool)
        '''
        return tf.test.gpu_device_name() != ''

# print(len(pd.read_csv("./tools/data/structured_data/housing.csv")))

# dataReader = DataReader("./tools/data/structured_data/housing.csv", trim=False, trim_format='stratify', trim_ratio=0.5)
# data = dataReader.data_generator()

# print(data)

############################

# data_reader = DataReader('./data/housing.csv', trim=True, trim_ratio=0.5)

# print("Is GPU Available:", data_reader.is_gpu_available())
# print("Available GPUs:", data_reader.get_available_gpus())

# print("Before Trimming:", data_reader.data_generator().shape)
# print("After Trimming:", data_reader.trim_gpu().shape)