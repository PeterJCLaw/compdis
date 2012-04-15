
import os.path
import sys

# Hack the path..

p = os.path.abspath(os.path.dirname(__file__))
p = os.path.join(p, '../bin')
sys.path.insert(0, p)

del p

# External
import unittest

# Local
import scores
import util

simple_data = { '0': 3, '1': 2, '2': 1, '3': 0 }
simple_pos = { 1: ['0'], 2: ['1'], 3: ['2'], 4: ['3'] }
simple_points = { '0': 4.0, '1': 3.0, '2': 2.0, '3': 1.0 }

dsq_data = { '0': 3, '1': 2, '2': 1, '3': 0 }
dsq_dsq = [ '0', '2' ]
dsq_pos = { 1: ['1'], 2: ['3'], 3: ['0', '2'] }
dsq_points = { '0': 0.0, '1': 4.0, '2': 0.0, '3': 3.0 }

tie1_data = { '0': 3, '1': 3, '2': 0, '3': 0 }
tie1_pos = { 1: ['1', '0'], 3: ['3', '2'] }
tie1_points = { '0': 3.5, '1': 3.5, '2': 1.5, '3': 1.5 }

tie2_data = { '0': 3, '1': 3, '2': 0, '3': 0 }
tie2_dsq = [ '0', '2' ]
tie2_pos = { 1: ['1'], 2: ['3'], 3: ['0', '2'] }
tie2_points = { '0': 0.0, '1': 4.0, '2': 0.0, '3': 3.0 }

class PositionsTests(unittest.TestCase):

	def test_simple(self):
		pos = scores.calc_positions(simple_data, [])
		util.assertEqual(simple_pos, pos, "Wrong positions")

	def test_tie(self):
		pos = scores.calc_positions(tie1_data, [])
		util.assertEqual(tie1_pos, pos, "Wrong positions")

	def test_dsq(self):
		pos = scores.calc_positions(dsq_data, dsq_dsq)
		util.assertEqual(dsq_pos, pos, "Wrong positions")

	def test_dsq_tie(self):
		pos = scores.calc_positions(tie2_data, tie2_dsq)
		util.assertEqual(tie2_pos, pos, "Wrong positions")

class LeaguePointsTests(unittest.TestCase):

	def test_simple(self):
		points = scores.calc_league_points(simple_pos, [])
		util.assertEqual(simple_points, points, "Wrong points")

	def test_tie(self):
		points = scores.calc_league_points(tie1_pos, [])
		util.assertEqual(tie1_points, points, "Wrong points")

	def test_dsq_tie(self):
		points = scores.calc_league_points(tie2_pos, tie2_dsq)
		util.assertEqual(tie2_points, points, "Wrong points")

if __name__ == '__main__':
	unittest.main(buffer=True)
