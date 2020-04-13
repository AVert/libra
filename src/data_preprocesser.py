import keras
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from tensorflow import keras
from tensorflow.python.keras.layers import Dense, Input
from keras.callbacks import EarlyStopping
from matplotlib import pyplot

def singleRegDataPreprocesser(data):
    data.fillna(0, inplace=True)
        
    categorical_columns = data.select_dtypes(exclude=["number"]).columns
    numeric_columns = data.columns[data.dtypes.apply(lambda c: np.issubdtype(c, np.number))]

    if(len(categorical_columns) != 0):

        categorical_feature_mask = data.dtypes==object
        categorical_cols = data.columns[categorical_feature_mask].tolist()
        labeled_df = data[categorical_cols]

        enc = OneHotEncoder()
        enc.fit(labeled_df)
        onehotlabels = enc.transform(labeled_df).toarray()
            
        new_columns=list()
        for col, values in zip(labeled_df.columns, enc.categories_):
            new_columns.extend([col + '_' + str(value) for value in values])

        data = pd.concat([data, pd.DataFrame(onehotlabels, columns=new_columns)], axis='columns')

        for x in categorical_cols: del data[x]

    if(len(numeric_columns) != 0):
        scaler = StandardScaler()
        data[numeric_columns] = scaler.fit_transform(data[numeric_columns])

    return data