from matplotlib import pyplot as plt
from collections import deque
from threading import Lock, Thread

import myo
import numpy as np

import matplotlib
import sklearn.datasets
import pandas as pd
import os
import glob
from sklearn import decomposition
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA as RandomizedPCA
from scipy.fftpack import dct
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import _pickle as cPickle
import sys
import matplotlib.pyplot as plt
import seaborn as sns


class EmgCollector(myo.DeviceListener):
  """
  Collects EMG data in a queue with *n* maximum number of elements.
  """

  def __init__(self, n):
    self.n = n
    self.lock = Lock()
    self.emg_data_queue = deque(maxlen=n)

  def get_emg_data(self):
    with self.lock:
      return list(self.emg_data_queue)

  # myo.DeviceListener

  def on_connected(self, event):
    event.device.stream_emg(True)

  def on_emg(self, event):
    with self.lock:
      self.emg_data_queue.append((event.timestamp, event.emg))


class Plot(object):

  def __init__(self, listener):
    self.n = listener.n
    self.listener = listener
    self.fig = plt.figure()
    self.axes = [self.fig.add_subplot('81' + str(i)) for i in range(1, 9)]
    [(ax.set_ylim([-100, 100])) for ax in self.axes]
    self.graphs = [ax.plot(np.arange(self.n), np.zeros(self.n))[0] for ax in self.axes]
    plt.ion()

  def update_plot(self):
    emg_data = self.listener.get_emg_data()
    emg_data = np.array([x[1] for x in emg_data]).T
    self.emg_data = emg_data
    for g, data in zip(self.graphs, emg_data):
      if len(data) < self.n:
        # Fill the left side with zeroes.
        data = np.concatenate([np.zeros(self.n - len(data)), data])
      g.set_ydata(data)
    plt.draw()

  def main(self):  
    for count in range(1,4):
            print(str(count)+"......")
            for num in range(1,10):
                self.update_plot()
                plt.pause(0.01)
    with open('PKSVMClassifier', 'rb') as f:
        rf = cPickle.load(f)
        while True:
            self.update_plot()
            plt.pause(0.5)
            data = self.emg_data[:,0:199]
            print(data)
            input_pattern_frequency = np.array([])
            for elm in data:
                channel_in_frequency = np.fft.rfft(elm).real
                input_pattern_frequency = np.concatenate([channel_in_frequency, input_pattern_frequency])
            input_pattern_frequency = input_pattern_frequency.reshape(1,input_pattern_frequency.size)
            frame = pd.DataFrame.from_records(input_pattern_frequency)
            predictions = rf.predict(frame)
            print(predictions)
            sys.stdout.flush()


def main():
  myo.init()
  hub = myo.Hub()
  listener = EmgCollector(500)
  with hub.run_in_background(listener.on_event):
    Plot(listener).main()


if __name__ == '__main__':
  main()