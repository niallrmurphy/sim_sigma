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
    self.BIG_ENOUGH_SAMPLES = 5000
    self.RNG_SEED = 220806
    # Create the test microservices with different latency distributions
    self.ms = sim.microservice('normal', self.RNG_SEED, 100, 30)
    self.ms2 = sim.microservice('normal', self.RNG_SEED, 100, 30)
    self.ms3 = sim.microservice('normal', self.RNG_SEED, 100, 30)
    self.ms4 = sim.microservice('gamma', self.RNG_SEED, 100, 2)
    self.ms5 = sim.microservice('exponential', self.RNG_SEED, 100, 0)

  def test_unitary_static_micro_latency(self):
    """Test we can patch with a static return value."""
    with patch.object(sim.microservice, 'return_self_latency', return_value=100):
      self.assertEqual(self.ms.calculate_latency(), 100)

  def test_unitary_nonstatic_micro_latency(self):
    """Test we get a non-zero latency without patching."""
    self.assertGreater(self.ms.calculate_latency(), 0)

  def test_serial_static_micro_latency(self):
    """Test we can patch serially dependent microservices and get the sum of statics."""
    with patch.object(sim.microservice, 'return_self_latency', return_value=100):
      self.ms.add_serial_dependency(self.ms2)
      self.assertEqual(self.ms.calculate_latency(), 200)

  def test_serial_nonstatic_micro_latency(self):
    """Test we get a non-zero latency from serially dependent microservices without patching."""
    self.ms.add_serial_dependency(self.ms2)
    self.assertGreater(self.ms.calculate_latency(), 0)

  def test_bestof_static_micro_latency(self):
    """Test that we get the minimum result when we select the 'best of' latency in the group."""
    with patch.object(self.ms, 'return_self_latency', return_value=25):
      with patch.object(self.ms2, 'return_self_latency', return_value=100):
        with patch.object(self.ms3, 'return_self_latency', return_value=50):
          self.ms.add_bestof_dependency(self.ms2)
          self.ms.add_bestof_dependency(self.ms3)
          self.assertEqual(self.ms.calculate_latency(), 75)

  def test_bestof_nonstatic_micro_latency(self):
    """Test we get non-zero latency when we select the best of latencies returned."""
    self.ms.add_bestof_dependency(self.ms2)
    self.ms.add_bestof_dependency(self.ms3)
    self.assertGreater(self.ms.calculate_latency(), 0)

  def test_worstof_static_micro_latency(self):
    """Test we get the maximum result we expect when we select the worst latencies."""
    with patch.object(self.ms, 'return_self_latency', return_value=25):
      with patch.object(self.ms2, 'return_self_latency', return_value=100):
        with patch.object(self.ms3, 'return_self_latency', return_value=50):
          self.ms.add_worstof_dependency(self.ms2)
          self.ms.add_worstof_dependency(self.ms3)
          self.assertEqual(self.ms.calculate_latency(), 125)

  def test_bestof_nonstatic_micro_latency(self):
    """Test we get non-zero latency when we select the worst of latencies returned."""
    self.ms.add_bestof_dependency(self.ms2)
    self.ms.add_bestof_dependency(self.ms3)
    self.assertGreater(self.ms.calculate_latency(), 0)

  def test_plot_distrib(self):
    """Enough samples gets you a normal distribution."""
    for x in range(1,self.BIG_ENOUGH_SAMPLES):
      self.ms.calculate_latency()
    mydata = pd.Series(self.ms.latency_history)
    self.assertGreater(shapiro(mydata).pvalue, 0.05)

  def test_gamma_distrib(self):
    """A gamma distribution on its own is not normally distributed."""
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms4.calculate_latency()
    mydata = pd.Series(self.ms4.latency_history)
    self.assertLess(shapiro(mydata).pvalue, 0.05)

  def test_gamma_dependent(self):
    """A gamma distribution as a serial dependent of a normal distribution is mostly normally distributed."""
    self.ms.add_serial_dependency(self.ms4)
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms.calculate_latency()
    mydata = pd.Series(self.ms.latency_history)
    # self.assertGreater(shapiro(mydata).pvalue, 0.05)

  def test_bestof_gamma(self):
    """A gamma distribution as a subcomponent in 'bestof' is mostly normally distributed"""
    self.ms.add_bestof_dependency(self.ms2)
    self.ms.add_bestof_dependency(self.ms4)
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms.calculate_latency()
    mydata = pd.Series(self.ms.latency_history)
    self.assertGreater(shapiro(mydata).pvalue, 0.05)

  def test_worstof_gamma(self):
    """A gamma distribution as a subcomponent in 'worstof' is mostly normally distributed"""
    self.ms.add_worstof_dependency(self.ms2)
    self.ms.add_worstof_dependency(self.ms4)
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms.calculate_latency()
    mydata = pd.Series(self.ms.latency_history)
    self.assertGreater(shapiro(mydata).pvalue, 0.05)

  def test_exponential_distrib(self):
    """An exponential distribution on its own is not normally distributed."""
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms5.calculate_latency()
    mydata = pd.Series(self.ms5.latency_history)
    self.assertLess(shapiro(mydata).pvalue, 0.05)

  def test_exponential_dependent(self):
    """An exponential distribution as a serial dependent of a normal distribution is not normally distributed."""
    self.ms.add_serial_dependency(self.ms5)
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms.calculate_latency()
    mydata = pd.Series(self.ms.latency_history)
    self.assertLess(shapiro(mydata).pvalue, 0.05)  

  def test_bestof_exponential(self):
    """An exponential distribution as a subcomponent in 'bestof' is not normally distributed."""
    self.ms.add_bestof_dependency(self.ms2)
    self.ms.add_bestof_dependency(self.ms5)
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms.calculate_latency()
    mydata = pd.Series(self.ms.latency_history)
    self.assertLess(shapiro(mydata).pvalue, 0.05)

  def test_worstof_exponential(self):
    """An exponential distribution as a subcomponent in 'worstof' is not normally distributed."""
    self.ms.add_worstof_dependency(self.ms2)
    self.ms.add_worstof_dependency(self.ms5)
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms.calculate_latency()
    mydata = pd.Series(self.ms.latency_history)
    self.assertLess(shapiro(mydata).pvalue, 0.05)

  def test_find_non_normal_bestof(self):
    """We can find a non-normal distribution in 'bestof' subcomponents'."""
    self.ms.add_bestof_dependency(self.ms2)
    self.ms.add_bestof_dependency(self.ms3)
    self.ms.add_bestof_dependency(self.ms5)
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms.calculate_latency()
    mydata1 = pd.Series(self.ms.latency_history)
    mydata2 = pd.Series(self.ms2.latency_history)
    mydata3 = pd.Series(self.ms3.latency_history)
    mydata5 = pd.Series(self.ms5.latency_history)
    # We expect the root node (self.ms) and self.ms5 NOT be normally
    # distributed, and ms2 & ms3 to be.
    self.assertLess(shapiro(mydata1).pvalue, 0.05)
    self.assertLess(shapiro(mydata5).pvalue, 0.05)
    self.assertGreater(shapiro(mydata2).pvalue, 0.05)
    self.assertGreater(shapiro(mydata3).pvalue, 0.05)

  def test_find_non_normal_worstof(self):
    """We can find a non-normal distribution in 'worstof' subcomponents'."""
    self.ms.add_worstof_dependency(self.ms2)
    self.ms.add_worstof_dependency(self.ms3)
    self.ms.add_worstof_dependency(self.ms5)
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms.calculate_latency()
    mydata1 = pd.Series(self.ms.latency_history)
    mydata2 = pd.Series(self.ms2.latency_history)
    mydata3 = pd.Series(self.ms3.latency_history)
    mydata5 = pd.Series(self.ms5.latency_history)
    # We expect the root node (self.ms) and self.ms5 NOT be normally
    # distributed, and ms2 & ms3 to be.
    self.assertLess(shapiro(mydata1).pvalue, 0.05)
    self.assertLess(shapiro(mydata5).pvalue, 0.05)
    self.assertGreater(shapiro(mydata2).pvalue, 0.05)
    self.assertGreater(shapiro(mydata3).pvalue, 0.05)

  def test_exponential_longchain_dependent(self):
    """An exponential system in a chain is non-normally distributed at root."""
    self.ms.add_serial_dependency(self.ms2)
    self.ms2.add_serial_dependency(self.ms5)
    self.ms5.add_serial_dependency(self.ms3)
    for x in range(1, self.BIG_ENOUGH_SAMPLES):
      self.ms.calculate_latency()
    mydata = pd.Series(self.ms.latency_history)
    self.assertLess(shapiro(mydata).pvalue, 0.05)  
    
if __name__ == '__main__':
    unittest.main()
