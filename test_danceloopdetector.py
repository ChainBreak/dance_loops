#!/usr/bin/env python3
import unittest
import math
from danceloopdetector import DanceLoopDetector

class TestDanceLoopDetector(unittest.TestCase):
    def test_autocorrelation(self):

        period = 10
        dld = DanceLoopDetector({"frames_per_beat":period})

        for i in range(period*5):
            v = math.sin(i/period * math.pi*2)
            
            auto_correlation, max_auto_correlation = dld.calc_lagged_product(v)
            
            if i > period:

                self.assertAlmostEqual(auto_correlation, max_auto_correlation)

if __name__ == "__main__":
    unittest.main()