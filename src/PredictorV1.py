# -*- coding: utf-8 -*-

# TensorFlow and tf.keras
import tensorflow as tf
from sklearn import preprocessing
from keras.models import Sequential, save_model, load_model
from keras.layers import Dense, BatchNormalization
from keras.activations import sigmoid
from sklearn.model_selection import train_test_split
import joblib

# Commonly used modules
import pandas as pd

from os import listdir
from os.path import isfile, join

out_columns = {'PST': None, 'TVD': None, 'Entropy': None, 'Swaps': None}
out_columns_sig = ['PST', 'TVD']
dataset_path = "./dataSets_V1/dataSets_Noise"
checkpoint_path = "./models_V1/checkpoint_{}"
img_path = "./models_V1/img/checkpoint_{}.png"
scaler_path = "./models_V1/scaler.save"

#Graphviz breaks other dependencies
#def plot_models():
#    load_models()
#    for out in out_columns:
#        plot_model(out_columns[out], to_file=img_path.format(out), show_shapes=True)

def load_models():
    for out in out_columns:
        out_columns[out] = load_model(checkpoint_path.format(out))


def create_model(input_size, output_size):
    leaky_relu = tf.keras.layers.LeakyReLU(alpha=0.01)
    relu = tf.keras.layers.ReLU()

    model = Sequential([
        Dense(512, activation=relu, input_shape=(input_size,)),
        BatchNormalization(),

        Dense(256, activation=relu),
        BatchNormalization(),

        Dense(256, activation=relu),
        BatchNormalization(),

        Dense(128, activation=sigmoid),
        BatchNormalization(),

        Dense(output_size, activation=relu),
    ])

    return model


def create_model_sigmoid(input_size, output_size):
    leaky_relu = tf.keras.layers.LeakyReLU(alpha=0.01)
    relu = tf.keras.layers.ReLU()

    model = Sequential([
        Dense(512, activation=relu, input_shape=(input_size,)),
        BatchNormalization(),

        Dense(256, activation=relu),
        BatchNormalization(),

        Dense(256, activation=relu),
        BatchNormalization(),

        Dense(128, activation=sigmoid),
        BatchNormalization(),

        Dense(output_size, activation=sigmoid),
    ])

    return model


def queryModel(X: pd.DataFrame, out_column: str):
    """Load in v1 model and make prediction"""
    if out_column not in out_columns:
        # Raise error?
        return None

    min_max_scaler = joblib.load(scaler_path)
    X = X[min_max_scaler.feature_names_in_]
    X_scale = min_max_scaler.transform(X)

    model = out_columns[out_column]

    return model(X_scale)


def main():

    files = [join(dataset_path, f) for f in listdir(
        dataset_path) if isfile(join(dataset_path, f))]

    dfs = [pd.read_csv(f) for f in files]
    df = pd.concat(dfs)

    X = df.drop(columns=out_columns.keys())
    Y = df[out_columns.keys()]

    # Scaling
    min_max_scaler = preprocessing.MinMaxScaler()
    X_scale = min_max_scaler.fit_transform(X)

    joblib.dump(min_max_scaler, scaler_path)

    X_train, X_val_and_test, Y_train, Y_val_and_test = train_test_split(
        X_scale, Y, test_size=0.3)
    X_val, X_test, Y_val, Y_test = train_test_split(
        X_val_and_test, Y_val_and_test, test_size=0.5)

    # Baseline model
    for out_column in out_columns.keys():
        Y_out = Y[[out_column]]
        Y_train_out = Y_train[[out_column]]
        Y_test_out = Y_test[[out_column]]
        Y_val_out = Y_val[[out_column]]

        if out_column in out_columns_sig:
            model = create_model_sigmoid(len(X.columns), 1)
        else:
            model = create_model(len(X.columns), 1)

        optimizer = tf.keras.optimizers.Adam(learning_rate=0.005, decay=5e-4)
        model.compile(optimizer=optimizer,
                      loss='mean_absolute_error',
                      metrics=['MSE'])

        hist = model.fit(X_train, Y_train_out,
                         batch_size=32, epochs=200,
                         validation_data=(X_val, Y_val_out))

        save_model(model=model, filepath=checkpoint_path.format(out_column))
        #plot_model(out_columns[out_column], to_file=img_path.format(out_column), show_shapes=True)


if __name__ == "__main__":
    main()
