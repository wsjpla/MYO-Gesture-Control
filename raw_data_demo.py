from matplotlib import pyplot as plt
from collections import deque
from threading import Lock, Thread

import myo
import numpy as np


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
    for n in range(1,6):
        print("\nGesture " + str(n))
        for count in range(1,6):
            print(str(count)+"......")
            for num in range(1,10):
                self.update_plot()
                plt.pause(0.02)
        for m in range(1,10):   
            self.update_plot()
            plt.pause(0.02)
            filename = "emg_data/Gesture_"+str(n)+"_"+str(m)+".txt"
            self.f = open(filename,"w+")
            for column in range(0,200):
                self.f.write(str(self.emg_data[:,column]))
                #for row in range(0,8):
                #    self.f.write(str(self.emg_data[row][column]) + " ")
                self.f.write("\n")

            

def main():
  myo.init()
  hub = myo.Hub()
  listener = EmgCollector(500)
  with hub.run_in_background(listener.on_event):
    Plot(listener).main()


if __name__ == '__main__':
  main()
