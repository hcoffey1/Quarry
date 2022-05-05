# -*- coding: utf-8 -*-

# TensorFlow and tf.keras
import tensorflow as tf
from sklearn import preprocessing
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization
from sklearn.model_selection import train_test_split
import joblib

# Commonly used modules
import numpy as np
import pandas as pd
import os
import sys

from os import listdir
from os.path import isfile, join

out_columns = ['PST', 'TVD', 'Entropy', 'Swaps']
dataset_path = "../dataSets_V1/dataSets_Noise"
checkpoint_path = "../models_V1/checkpoint_{}"
scaler_path = "../models_V1/scaler.save"


def create_model(input_size, output_size):
    leaky_relu = tf.keras.layers.LeakyReLU(alpha=0.01)

    model = Sequential([
        Dense(512, activation=leaky_relu, input_shape=(input_size,)),
        BatchNormalization(),

        Dense(256, activation=leaky_relu),
        BatchNormalization(),

        Dense(256, activation=leaky_relu),
        BatchNormalization(),

        Dense(128, activation=leaky_relu),
        BatchNormalization(),

        Dense(output_size, activation='linear'),
    ])
    
    return model

def queryModel(csv, out_column):
    """Load in v1 model and make prediction"""
    if out_column not in out_columns:
        # Raise error?
        return None

    df = pd.read_csv(csv)
    min_max_scaler = joblib.load(scaler_path)  
    X = df.drop(columns=out_columns)
    X_scale = min_max_scaler.transform(X)
   
    model = create_model(len(X.columns), 1)
    model.load_weights(checkpoint_path.format(out_column))

    return model(X_scale)


def main():

    files = [join(dataset_path, f) for f in listdir(
        dataset_path) if isfile(join(dataset_path, f))]

    dfs = [pd.read_csv(f) for f in files]
    df = pd.concat(dfs)

    X = df.drop(columns=out_columns)
    Y = df[out_columns]

    # Scaling
    min_max_scaler = preprocessing.MinMaxScaler()
    X_scale = min_max_scaler.fit_transform(X)

    joblib.dump(min_max_scaler, scaler_path)

    X_train, X_val_and_test, Y_train, Y_val_and_test = train_test_split(
        X_scale, Y, test_size=0.3)
    X_val, X_test, Y_val, Y_test = train_test_split(
        X_val_and_test, Y_val_and_test, test_size=0.5)

    # Baseline model
    for out_column in out_columns:
        Y_out = Y[[out_column]]
        Y_train_out = Y_train[[out_column]]
        Y_test_out = Y_test[[out_column]]
        Y_val_out = Y_val[[out_column]]

        model = create_model(len(X.columns), 1)

        optimizer = tf.keras.optimizers.Adam(learning_rate=0.005, decay=5e-4)
        model.compile(optimizer=optimizer,
                      loss='mean_absolute_error',
                      metrics=['MSE'])

        hist = model.fit(X_train, Y_train_out,
                         batch_size=32, epochs=200,
                         validation_data=(X_val, Y_val_out))

        model.save_weights(checkpoint_path.format(out_column))

    # print(model(X_test[0:10]).numpy(), Y_test[0:10])


if __name__ == "__main__":
    main()
