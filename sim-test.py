import sim

import matplotlib.pyplot as plt
import pandas as pd
import pylab
import statsmodels.api as sm
import unittest

from scipy.stats import norm
from scipy.stats import shapiro
from unittest.mock import patch

class TestSimMethods(unittest.TestCase):
  def setUp(self):
    self.ms = sim.microservice('normal', 100, 30)
    self.ms2 = sim.microservice('normal', 100, 30)
    self.ms3 = sim.microservice('normal', 100, 30)

  def test_unitary_static_micro_latency(self):
    with patch.object(sim.microservice, 'return_self_latency', return_value=100):
      self.assertEqual(self.ms.calculate_latency(), 100)

  def test_unitary_nonstatic_micro_latency(self):
    self.assertGreater(self.ms.calculate_latency(), 0)

  def test_serial_static_micro_latency(self):
   with patch.object(sim.microservice, 'return_self_latency', return_value=100):
      self.ms.add_serial_dependency(self.ms2)
      self.assertEqual(self.ms.calculate_latency(), 200)

  def test_serial_nonstatic_micro_latency(self):
    self.ms.add_serial_dependency(self.ms2)
    self.assertGreater(self.ms.calculate_latency(), 0)

  def test_bestof_static_micro_latency(self):
    with patch.object(self.ms, 'return_self_latency', return_value=25):
      with patch.object(self.ms2, 'return_self_latency', return_value=100):
        with patch.object(self.ms3, 'return_self_latency', return_value=50):
          self.ms.add_bestof_dependency(self.ms2)
          self.ms.add_bestof_dependency(self.ms3)
          self.assertEqual(self.ms.calculate_latency(), 75)

  def test_bestof_nonstatic_micro_latency(self):
    self.ms.add_bestof_dependency(self.ms2)
    self.ms.add_bestof_dependency(self.ms3)
    self.assertGreater(self.ms.calculate_latency(), 0)

  def test_worstof_static_micro_latency(self):
    with patch.object(self.ms, 'return_self_latency', return_value=25):
      with patch.object(self.ms2, 'return_self_latency', return_value=100):
        with patch.object(self.ms3, 'return_self_latency', return_value=50):
          self.ms.add_worstof_dependency(self.ms2)
          self.ms.add_worstof_dependency(self.ms3)
          self.assertEqual(self.ms.calculate_latency(), 125)

  def test_bestof_nonstatic_micro_latency(self):
    self.ms.add_bestof_dependency(self.ms2)
    self.ms.add_bestof_dependency(self.ms3)
    self.assertGreater(self.ms.calculate_latency(), 0)

  def test_plot_distrib(self):
    for x in range(1,2500):
      self.ms.calculate_latency()
    mydata = pd.Series(self.ms.latency_history)
    self.assertGreater(shapiro(mydata).pvalue, 0.05)

          
if __name__ == '__main__':
    unittest.main()
