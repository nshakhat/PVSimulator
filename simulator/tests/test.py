#!/usr/bin/env python
# encoding: utf-8

import datetime as dt
import unittest
from argparse import ArgumentTypeError

from simulator import simulate
from simulator.pvsimulator import get_perfect_voltage_for_a_day as get_voltage


class TestPVSimulator(unittest.TestCase):

    def test_simulate_hourly(self):
        d = dt.datetime.strptime("2017-04-22 00:00:00", '%Y-%m-%d %H:%M:%S')
        res = get_voltage(d, "3600s")
        self.assertTrue(res.__len__(), 24)

    def test_simulate_30min(self):
        d = dt.datetime.strptime("2017-04-22 00:00:00", '%Y-%m-%d %H:%M:%S')
        res = get_voltage(d, "1800s")
        self.assertTrue(res.__len__(), 48)

    def test_valid_date(self):
        d = dt.datetime.strptime("2017-04-22 00:00:00", '%Y-%m-%d %H:%M:%S')
        self.assertEquals(d, simulate.valid_date("2017-04-22 00:00:00"))
        # check that leading zero doesn't matter
        d = dt.datetime.strptime("2017-04-22 01:00:00", '%Y-%m-%d %H:%M:%S')
        self.assertEquals(d, simulate.valid_date("2017-04-22 1:00:00"))
        self.assertEquals(d, simulate.valid_date("2017-04-22 1:0:0"))
        with self.assertRaises(ArgumentTypeError):
            simulate.valid_date("2017-04-0 00:00:00")
        with self.assertRaises(ArgumentTypeError):
            simulate.valid_date("2017-04-000:00:00")

    def test_valid_freq(self):
        with self.assertRaises(ArgumentTypeError):
            simulate.valid_frq("str")
        with self.assertRaises(ArgumentTypeError):
            simulate.valid_frq(400000)
        with self.assertRaises(ArgumentTypeError):
            simulate.valid_frq(-1)
        self.assertEquals(1, simulate.valid_frq(1))
        self.assertEquals(3600, simulate.valid_frq(3600))


if __name__ == '__main__':
    unittest.main()
