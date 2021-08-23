from matplotlib import pyplot as plt
from collections import deque
from threading import Lock, Thread
import time
import struct
import serial

import myo
import numpy as np

ser=serial.Serial("com6",9600,timeout=1)
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
        data = np.concatenate([np.zeros(self.n - len(data)), data])
      g.set_ydata(data)
    plt.draw()

  def main(self):
    print("Relax state:")
    for count in range(1,6):
            print(str(count)+"......")
            for num in range(1,10):
                self.update_plot()
                plt.pause(0.01)
    n_c = 20
    am_min = 0
    for m in range(0,n_c):
            print(m)
            self.update_plot()
            plt.pause(0.01)
            for column in range(0,200):
                for row in range(0,8):
                    am_min+=abs(self.emg_data[row][column])
    am_min = am_min/n_c
    print(am_min)    
    print("Maximum grip strength:")
    for count in range(1,6):
            print(str(count)+"......")
            for num in range(1,10):
                self.update_plot()
                plt.pause(0.01)
    am_max = 0
    for m in range(0,n_c):
            print(m)
            self.update_plot()
            plt.pause(0.01)
            for column in range(0,200):
                for row in range(0,8):
                    am_max+=abs(self.emg_data[row][column])
    am_max = am_max/n_c
    print(am_max)    
    
    while True:
        am_test = 0
        self.update_plot()
        plt.pause(0.2)
        for column in range(0,200):
                for row in range(0,8):
                    am_test+=abs(self.emg_data[row][column])
        strength = (am_test-am_min)/(am_max-am_min)
        print(strength)
        if strength <= 0:
            p0 = int(1500)
            p1 = int(1500)
        else:
            if strength >= 1:
                p0 = int(2000)
                p1 = int(900)
            else:
                p0 = int(500*strength+1500)
                p1 = int(1500-600*strength)
        pose0 = struct.pack('<H',p0)
        pose1 = struct.pack('<H',p1)
        data = b'\x55\x55\x14\x03\x05\xC8\x00\x01'+ pose0 +b'\x02' + pose1 + b'\x03' + pose1 + b'\x04' + pose1 + b'\x05' + pose1        
        ser.write(data)
       
        
def main():
  myo.init()
  hub = myo.Hub()
  listener = EmgCollector(500)
  with hub.run_in_background(listener.on_event):
    Plot(listener).main()


if __name__ == '__main__':
  main()
