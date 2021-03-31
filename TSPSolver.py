#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))




import time
import numpy as np
from TSPClasses import *
import heapq
import itertools



class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''
	
	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

	# starts from an arbitrary city, picks the shortest path available to an unvisited city,
	# then picks the shortest path from that city to an unvisited city, etc., until it returns to the origin city.
	# Note that for Hard problems, it is possible to reach a city which has no paths to any remaining unvisited cities
	# (don't forget to check for a path from the last city back to the first to complete the cycle).
	# In such cases, just restart with a different random seed.

	def greedy( self,time_allowance=60.0 ):
		# start timer
		start_time = time.time()
		# choose arbitrary index to start from
		randStartCityIndex = random.randint(0 , len(self._scenario.getCities()) - 1)
		# keep track of randomStartIndices in a set
		randIndexSet = set()
		# intialize helper_result to false to enter the while loop
		helper_result = False
		# if initial attempt is
		while helper_result == False and time.time()-start_time < time_allowance:
			# choose arbitrary index to start from
			randStartCityIndex = random.randint(0, len(self._scenario.getCities()) - 1)
			# if the random index is in the set, select a new random index
			while randStartCityIndex in randIndexSet:
				randStartCityIndex = random.randint(0, len(self._scenario.getCities()) - 1)
			# add the random index to the set
			randIndexSet.add(randStartCityIndex)
			# call helper function
			helper_result = self.greedy_helper(randStartCityIndex, start_time, time_allowance)

		end_time = time.time()
		results = {}
		# if we did not get a result back, set cost to infinity
		if helper_result == False:
			results['cost'] = math.inf
			results['count'] = 0
			results['soln'] = None
		# if we did get a valid result, get cost, soln from TSPSolution object
		else:
			results['cost'] = helper_result.cost
			results['count'] = 1
			results['soln'] = helper_result
		# the remainder of our result set will be the same regardless of whether we received a successful result
		results['time'] = end_time - start_time
		results['max'] = None
		results['total'] = None
		results['pruned'] = None

		return results


	def greedy_helper( self, randStartCityIndex, start_time, time_allowance=60.0 ):
		# get cities
		cities = self._scenario.getCities()
		# starting from arbitrary city
		currCity = cities[randStartCityIndex]
		# boolean to keep track of whether we have visited all cities
		foundTour = False
		# set to make sure that we don't visit a city twice
		citySet = set()
		# route
		route = []
		# keep looping until path to all cities is found
		while not foundTour and time.time()-start_time < time_allowance:
			# variables to keep track of closest city and the distance to closest city
			closestCity = None
			costToClosestCity = math.inf

			route.append(currCity)
			citySet.add(currCity)

			# if the set contains all cities, then we check to make sure the cost from the last city to the first city
			if len(citySet) == len(cities):
				if currCity.costTo(cities[randStartCityIndex]) != math.inf:
					foundTour = True
					# we do not add the first city to the route because TSPSolver._costOfRoute
					# will automatically add the cost from the last city to the first
					break
				else:
					break
			# loop through all cities, looking for closest city
			for city in cities:
				if city not in citySet:
					costToCity = currCity.costTo(city)
					if (costToCity < costToClosestCity):
						costToClosestCity = costToCity
						closestCity = city

			# after the loop, if the math.inf
			if costToClosestCity == math.inf:
				break

			# set currCity equal to the closestCity for next iteration of while loop
			currCity = closestCity

		# if we have set tourFound equal to true in the while loop, we will return the TSPSolution object for that route
		if foundTour == True:
			bssf = TSPSolution(route)
			return bssf
		else:
			return False
	
	
	
	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints: 
		max queue size, total number of states created, and number of pruned states.</returns> 
	'''
		
	def branchAndBound( self, time_allowance=60.0 ):
		pass



	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	'''
		
	def fancy( self,time_allowance=60.0 ):
		pass
		



