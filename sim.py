#!/usr/local/Cellar/python@3.9/3.9.1/bin/python3

import matplotlib.pyplot as plt
import itertools
import networkx as nx
import numpy as np
import random
import simpy

from numpy.random import default_rng
from scipy.stats import norm
from scipy.stats import shapiro


class microservice:
  DISTRIBUTIONS = ['normal', 'gamma', 'exponential']
  MAX_LATENCY = 1000000
  def __init__(self, distribution_type="normal", seed=None, central=100, stddev=30):
    if distribution_type not in microservice.DISTRIBUTIONS:
      raise Exception("Distribution type %s unknown, no sensible way to proceed",
        distribution_type)
    else:
      self.distribution_type = distribution_type
      if seed == None:
        self.rng = default_rng()
      else:
        self.rng = default_rng(seed)
    self.dependencies = []
    self.bestof_dependencies = []
    self.worstof_dependencies = []
    self.last_latency = 0
    self.latency_history = []
    self.central = central
    self.stddev = stddev

  def add_serial_dependency(self, thing):
    self.dependencies.append(thing)

  def add_bestof_dependency(self, thing):
    self.bestof_dependencies.append(thing)

  def add_worstof_dependency(self, thing):
    self.worstof_dependencies.append(thing)

  def return_self_latency(self):
    if self.distribution_type == "normal":
      return self.rng.normal(self.central, self.stddev)
    elif self.distribution_type == "gamma":
      return self.rng.gamma(self.central, self.stddev)
    elif self.distribution_type == "exponential":
      return self.rng.exponential(self.central)
    else:
      return 1 # This is bad

  def calculate_latency(self):
    self.last_latency = 0
    # Calculate serialised latency for explicit dependencies, if any
    for x in self.dependencies:
      self.last_latency += x.calculate_latency()
    # Calculate "best of" latency for explicit dependencies, i.e. LB
    group_best_latency = microservice.MAX_LATENCY
    for x in self.bestof_dependencies:
      _ = x.calculate_latency()
      if _ < group_best_latency:
        group_best_latency = _
    if group_best_latency != microservice.MAX_LATENCY:
      self.last_latency += group_best_latency
    # Calculate "worst of" latency for explicit dependencies, i.e. storage
    group_worst_latency = 0
    for x in self.worstof_dependencies:
      _ = x.calculate_latency()
      if _ > group_worst_latency:
        group_worst_latency = _
    self.last_latency += group_worst_latency
    # Self latency
    self.last_latency += self.return_self_latency()
    self.latency_history.append(self.last_latency)
    return self.last_latency

  def is_normally_distributed(self):
    mydata = pd.Series(self.latency_history)
    if (shapiro(mydata).pvalue > 0.05):
      return True
    else:
      return False

class macroservice:
  def __init__(self, node_size = 10, probability = 0.3, k = 3, until=10):
    #self.graph = networkx.generators.random_graphs.erdos_renyi_graph(
    #  node_size, probability
    #)
    #self.graph = networkx.generators.random_graphs.connected_watts_strogatz_graph(
    self.until = until
    # Create the connected graph, supposed to roughly correspond to 'real' systems
    self.graph = networkx.generators.random_graphs.dual_barabasi_albert_graph(
      node_size, k, 1, probability
    )
    # Create the distributed system microservices. 1:1 mapping with graph nodes.
    self.env = simpy.Environment()
    for x in range(node_size):
      self.env.process(self.microservice())

  def microservice(self):
    while True:
      print('start at %d' % self.env.now)
      yield self.env.timeout(1)

  def run(self):
    self.env.run(until=self.until)

  def plot(self):
    pos = nx.spring_layout(self.graph)
    nx.draw_networkx(self.graph, pos)
    plt.title("Random Graph Generation Example")
    plt.show()

def main():
  ms = macroservice(20, 0.3, 3, 10)
  #ms.plot()
  ms.run()

if __name__ == "__main__":
    main()
