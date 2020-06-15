# Making functions in other directories accesible to this file by
# inserting into sis path
import sys

from predictionQueries import text_classification_query, get_summary, summarization_query, predict_text_sentiment

sys.path.insert(1, './preprocessing')
sys.path.insert(1, './data_generation')
sys.path.insert(1, './modeling')
sys.path.insert(1, './plotting')

from keras_preprocessing import sequence
import os
import warnings
from pandas.core.common import SettingWithCopyWarning
import numpy as np
import pandas as pd
from tabulate import tabulate
from scipy.spatial.distance import cosine
from sklearn.model_selection import cross_val_score
from pandas import DataFrame
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn import preprocessing, svm
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from dataset_labelmatcher import get_similar_column, get_similar_model
from tensorflow.keras.callbacks import EarlyStopping
from matplotlib import pyplot
from grammartree import get_value_instruction
from prediction_model_creation import get_keras_model_reg, get_keras_text_class
from prediction_model_creation import get_keras_model_class
from keras.utils import to_categorical
from keras.utils import np_utils
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import tensorflow as tf
from data_reader import DataReader
from dimensionality_red_queries import dimensionality_reduc
from os import listdir

from NLP_preprocessing import text_clean_up, lemmatize_text, encode_text
from keras.preprocessing.image import ImageDataGenerator
from termcolor import colored
from keras.models import model_from_json
from feedforward_nn import regression_ann, classification_ann, convolutional
from supplementaries import tune_helper, stats
from classification_models import k_means_clustering, train_svm, nearest_neighbors, decision_tree
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from keras.layers import (Dense, Conv2D, Flatten, MaxPooling2D, )
from NLP_preprocessing import text_clean_up, lemmatize_text, get_target_values

import torch
from torch.utils.data import DataLoader

# Importing the T5 modules from huggingface/transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration

from keras_preprocessing import sequence

from huggingfaceModelRetrainHelper import train, CustomDataset, inference

warnings.simplefilter(action='error', category=FutureWarning)
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# function imports from other files

currLog = ""
counter = 0
number = 0


# # current_dir=os.getcw()

# # allows for all columns to be displayed when printing()
# pd.options.display.width = None


# # clears the log when new process is started up


def clearLog():
    global currLog
    global counter

    currLog = ""
    counter = 0


# logging function that creates hierarchial display of the processes of
# different functions. Copied into different python files to maintain
# global variable parallels


def logger(instruction, found="", slash=''):
    global currLog
    global counter
    if counter == 0:
        currLog += (" " * 2 * counter) + str(instruction) + str(found)
    elif instruction == "->":
        counter = counter - 1
        if slash == '|':
            currLog += (" " * 2 * counter) + slash + str(found)
        else:
            currLog += (" " * 2 * counter) + str(instruction) + str(found)
    else:
        currLog += (" " * 2 * counter) + "|"
        currLog += "\n"
        currLog += (" " * 2 * counter) + "|- " + str(instruction) + str(found)
        if instruction == "done...":
            currLog += "\n"
            currLog += "\n"

    counter += 1
    if instruction == "->":
        print(currLog, end="")
    else:
        print(currLog)
    currLog = ""


# class to store all query information


class client:
    def __init__(self, data):
        logger("creating object...")
        self.dataset = data
        logger("loading dataset...")
        self.models = {}
        self.old_models = {}
        logger("done...")
        clearLog()

    # returns models with a specific string
    def get_models(self, model_requested):
        logger("Getting model...")
        return get_similar_model(model_requested, self.models.keys())
        clearLog()

        # save the model in the current directory

    def save(self, model, save_model, save_path=os.getcwd()):
        model_json = model.to_json()
        with open(save_path + "/model" + str(number) + ".json", "w") as json_file:
            json_file.write(model_json)
            # serialize weights to HDF5
            model.save_weights(save_path + str(number) + ".h5")
            logger("->", "Saved model to disk as model" + str(number))

    # param modelKey: string representation of the model to make prediction
    # param data: dataframe version of desired prediction set
    def predict(self, modelKey, data):
        modeldict = self.models[modelKey]
        data = modeldict['preprocesser'].transform(data)
        print(data)
        predictions = modeldict['model'].predict(data)
        if modeldict.get('interpreter'):
            predictions = modeldict['interpreter'].inverse_transform(
                predictions)
        return predictions

    def neural_network_query(self,
                             instruction,
                             drop=None,
                             preprocess=True,
                             test_size=0.2,
                             random_state=49,
                             epochs=50,
                             generate_plots=True,
                             callback_mode='min',
                             maximizer="val_loss",
                             save_model=True,
                             save_path=os.getcwd()):

        data = pd.read_csv(self.dataset)

        if preprocess:

            remove = get_similar_column(
                get_value_instruction(instruction), data)
            if (data[remove].dtype.name == 'object'):
                callback_mode = 'max'
                maximizer = "val_accuracy"
                self.classification_query_ann(
                    instruction,
                    preprocess=preprocess,
                    test_size=test_size,
                    random_state=random_state,
                    epochs=epochs,
                    generate_plots=generate_plots,
                    callback_mode=callback_mode,
                    maximizer=maximizer,
                    save_model=save_model,
                    save_path=save_path)
            else:
                self.regression_query_ann(
                    instruction,
                    preprocess=preprocess,
                    test_size=test_size,
                    random_state=random_state,
                    epochs=epochs,
                    generate_plots=generate_plots,
                    callback_mode=callback_mode,
                    maximizer=maximizer,
                    drop=None,
                    save_model=save_model,
                    save_path=save_path)

    # single regression query using a feed-forward neural network
    # instruction should be the value of a column
    def regression_query_ann(
            self,
            instruction,
            drop=None,
            preprocess=True,
            test_size=0.2,
            random_state=49,
            epochs=50,
            generate_plots=True,
            callback_mode='min',
            maximizer="val_loss",
            save_model=True,
            save_path=os.getcwd()):

        self.models['regression_ANN'] = regression_ann(
            instruction=instruction,
            dataset=self.dataset,
            drop=drop,
            preprocess=preprocess,
            test_size=test_size,
            random_state=random_state,
            epochs=epochs,
            generate_plots=generate_plots,
            callback_mode=callback_mode,
            maximizer=maximizer,
            save_model=save_model,
            save_path=save_path)

    # query for multilabel classification query, does not work for
    # binaryclassification, fits to feed-forward neural network
    def classification_query_ann(
            self,
            instruction,
            preprocess=True,
            callback_mode='min',
            drop=None,
            random_state=49,
            test_size=0.2,
            epochs=5,
            generate_plots=True,
            maximizer="val_loss",
            save_model=True,
            save_path=os.getcwd()):

        self.models['classification_ANN'] = classification_ann(
            instruction=instruction,
            dataset=self.dataset,
            drop=drop,
            preprocess=preprocess,
            test_size=test_size,
            random_state=random_state,
            epochs=epochs,
            generate_plots=generate_plots,
            callback_mode=callback_mode,
            maximizer=maximizer,
            save_model=save_model,
            save_path=save_path)

    def kmeans_clustering_query(self,
                                preprocess=True,
                                generate_plots=True,
                                drop=None,
                                base_clusters=1):

        self.models['k_means_clustering'] = k_means_clustering(
            dataset=self.dataset,
            preprocess=preprocess,
            generate_plots=generate_plots,
            drop=drop,
            base_clusters=base_clusters)

    def svm_query(self,
                  instruction,
                  test_size=0.2,
                  kernel='linear',
                  preprocess=True,
                  drop=None,
                  cross_val_size=0.3):

        self.models['svm'] = train_svm(instruction,
                                       dataset=self.dataset,
                                       test_size=test_size,
                                       kernel=kernel,
                                       preprocess=preprocess,
                                       drop=drop,
                                       cross_val_size=cross_val_size)

    def nearest_neighbor_query(
            self,
            instruction=None,
            preprocess=True,
            drop=None,
            min_neighbors=3,
            max_neighbors=10):
        self.models['nearest_neigbor'] = nearest_neighbors(
            instruction=instruction,
            dataset=self.dataset,
            preprocess=preprocess,
            drop=drop,
            min_neighbors=min_neighbors,
            max_neighbors=max_neighbors)

    def decision_tree_query(
            self,
            instruction,
            preprocess=True,
            test_size=0.2,
            drop=None):

        self.models['decision_tree'] = decision_tree(instruction,
                                                     dataset=self.dataset,
                                                     preprocess=True,
                                                     test_size=0.2,
                                                     drop=None)

    def tune(self, model_to_tune):
        self.models = tune_helper(
            model_to_tune=model_to_tune,
            dataset=self.dataset,
            models=self.models,
        )

    def stat_analysis(self, column_name="none", drop=None):
        stats(
            dataset=self.dataset,
            drop=drop,
            column_name=column_name
        )

        return

    def convolutional_query(self, data_path=None, new_folders=True):

        # storing values the model dictionary
        self.models["convolutional_NN"] = convolutional(data_path=data_path, new_folders=new_folders)

    # Sentiment analysis predict wrapper
    def predict_text_sentiment(self, text):
        return predict_text_sentiment(text)

    # sentiment analysis query
    def text_classification_query(self, instruction):

        # storing values the model dictionary
        self.models["Text Classification LSTM"] = text_classification_query(instruction)

    # Document summarization predict wrapper
    def get_summary(self, text):
        return get_summary(text)

    # text summarization query
    def summarization_query(self, instruction,
                            preprocess=True,
                            test_size=0.2,
                            random_state=49,
                            epochs=1,
                            generate_plots=True):

        self.models["Document Summarization"] = summarization_query(instruction)

    def dimensionality_reducer(self, instruction):
        dimensionality_reduc(instruction, self.dataset)

    def show_plots(self, model):
        print(self.models[model]['plots'].keys())


# Easier to comment the one you don't want to run instead of typing them
# out every time
newClient = client('./data/housing.csv').stat_analysis()

# newClient = client('./data/landslides_after_rainfall.csv').neural_network_query(instruction='Model distance',
# drop=['id', 'geolocation', 'source_link', 'source_name'])
