import streamlit as st 
import pandas as pd
#import seaborn as sns
import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from nicegui import events, ui
from io import StringIO
import io

def csv_file_handler(e: events.UploadEventArguments):

    x = "xlsx"

    filename = e.name
    filename = filename.split(".")[-1].lower() 

    if filename == x:
        xlsx = io.BytesIO(e.content.read())
        df = pd.read_excel(xlsx, engine='openpyxl')
        df.columns = ['Benämningar', 'Date', 'Time', 'Measurement']
        df = df.dropna()
        df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), format='%Y-%m-%d' + ' ' + '%H:%M:%S')
        print(df)
        df['Measurement'] = df['Measurement'].astype(str).replace(',', '.').astype(float)
        #remove measurements with value 0 just to make the graphs nicer
        df = df[df['Measurement'] != 0]
        #interpolate missing values
        df.drop(['Date', 'Time'], axis=1, inplace=True)
        df.set_index('Datetime', inplace=True)
        df = df.pivot(columns='Benämningar', values='Measurement')
        df.interpolate(method='time', limit_direction='both', inplace=True)
        plt.figure()
        #ax1 = sns.lineplot(data=df, dashes=False) #look at data
        #apply savgol filter to to each column to smoothen out the data
        df = df.apply(lambda x: savgol_filter(x, 100, 3), axis=0)
        plt.figure()
        #ax2 = sns.lineplot(data=df, dashes=False)
        #get the hourly measurement for each day
        h = df.groupby([df.index.day, df.index.hour]).first()
        h.reset_index(inplace=True, drop=True)
        #apply np.gradient to each column
        h = h.apply(lambda x: np.gradient(x), axis=0)
        h *= 100
        plt.figure()
        # ax_h = sns.lineplot(data=h, dashes=False)
        # ax_h.set_xticks(np.linspace(0, len(h), 7))
        # ax_h.set_xticklabels(ax2.get_xticklabels())
        # ax_h.set_ylabel('Temperature change [%/h]')
        # ax_h.set_xlabel('Time [M-D H]')
        plt.show()
    else:
        with StringIO(e.content.read().decode("utf-8")) as f:
            df = pd.read_csv(f, header = None, delimiter = ';')
            df.columns = ['Benämningar', 'Date', 'Time', 'Measurement']
            df['Datetime'] = pd.to_datetime(df['Date'] + df['Time'], format='%Y-%m-%d%H:%M:%S')
            df['Measurement'] = df['Measurement'].str.replace(',', '.').astype(float)
            #remove measurements with value 0 just to make the graphs nicer
            df = df[df['Measurement'] != 0]
            #interpolate missing values
            df.drop(['Date', 'Time'], axis=1, inplace=True)
            df.set_index('Datetime', inplace=True)
            df = df.pivot(columns='Benämningar', values='Measurement')
            df.interpolate(method='time', limit_direction='both', inplace=True)
            plt.figure()
            # ax1 = sns.lineplot(data=df, dashes=False) #look at data
            #apply savgol filter to to each column to smoothen out the data
            df = df.apply(lambda x: savgol_filter(x, 100, 3), axis=0)
            plt.figure()
            #ax2 = sns.lineplot(data=df, dashes=False)
            #get the hourly measurement for each day
            h = df.groupby([df.index.day, df.index.hour]).first()
            h.reset_index(inplace=True, drop=True)
            #apply np.gradient to each column
            h = h.apply(lambda x: np.gradient(x), axis=0)
            h *= 100
            plt.figure()
            # ax_h = sns.lineplot(data=h, dashes=False)
            # ax_h.set_xticks(np.linspace(0, len(h), 7))
            # ax_h.set_xticklabels(ax2.get_xticklabels())
            # ax_h.set_ylabel('Temperature change [%/h]')
            # ax_h.set_xlabel('Time [M-D H]')
            plt.show()

uploaded_files = st.file_uploader("Choose CSV files", type="csv")
