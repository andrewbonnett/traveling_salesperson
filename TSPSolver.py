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
from State import *
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
		# keep track of randomStartIndices in a set
		randIndexSet = set()
		# intialize helper_result to false to enter the while loop
		helper_result = False
		# continue to run the helper function until we receive a valid result (within time constraint)
		# TIME: O(n^3)
		# worst case the while loop will run n times (n  = number of cities)
		# worst case the inner while loop will run n times to find index of city we haven't started from
		# greedy_helper is O(n^2) time, which is called n times in the worst case.
		# SPACE: O(n)
		# greedy_helper is O(n) space, which is called n times in the worst case,
		# but each time the old solution is erase, so the space is just O(n)
		while helper_result == False and time.time()-start_time < time_allowance:
			if not len(randIndexSet) < len(self._scenario.getCities()):
				break
			# choose arbitrary index to start from
			randStartCityIndex = random.randint(0, len(self._scenario.getCities()) - 1)
			# if the random index is in the set, select a new random index
			while randStartCityIndex in randIndexSet:
				randStartCityIndex = random.randint(0, len(self._scenario.getCities()) - 1)
			# add the random index to the set
			randIndexSet.add(randStartCityIndex)
			# call helper function
			# TIME: O(n^2) SPACE: O(n)
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

	# Time Complexity is O(n^2). For each city in our partial path (n cities)
	# we look at every other city to find the smallest cost
	# Space Complexity is O(n) to store the route as an ordered array of cities
	def greedy_helper( self, randStartCityIndex, start_time, time_allowance=60.0 ):
		# get cities
		cities = self._scenario.getCities()
		# starting from arbitrary city
		currCity = cities[randStartCityIndex]
		# boolean to keep track of whether we have found a valid tour
		foundTour = False
		# set to make sure that we don't visit a city twice
		citySet = set()
		# route
		# SPACE O(n)
		route = []
		# keep looping until path to all cities is found
		# TIME while loop will run max n times, space is O(n)
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
					# we do not add the first city to the route here because TSPSolver._costOfRoute
					# will automatically add the cost from the last city to the first
					break
				else:
					break
			# loop through all cities, looking for closest city
			# TIME O(n)
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
			# TIME O(n)
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
		# start timer
		start_time = time.time()

		# initialize variables that we will keep track of / return
		self.number_of_solutions_found = 0 # YUP
		self.max_queue_size = 0 # YUP
		self.number_of_states_created = 0 # YUP
		self.number_of_pruned_states = 0 # YUP

		# run greedy to get an initial solution
		# we will use bssf to keep track of the cost of the best solution and the cost
		self.bssf = self.greedy()['soln']

		# get cities
		cities = self._scenario.getCities()

		# initialize empty matrix of size (number of cities x number of cities)
		unreduced_cost_matrix = [[math.inf for i in range(len(cities))] for j in range(len(cities))]
		# initialize state 0 by constructing 2D matrix
		# TIME O(n^2)
		# SPACE O(n^2)
		for i in range(len(cities)):
			for j in range(len(cities)):
				unreduced_cost_matrix[i][j] = cities[i].costTo(cities[j])

		# state zero is the only state that does not inherit from a parent state, so we pass in None
		state_zero = State(None, None, None)
		# select arbitrary start city
		randStartCityIndex = random.randint(0, len(cities) - 1)
		# ( this will become the from index when we start visiting cities )
		state_zero.set_state_zero_matrix(unreduced_cost_matrix, cities, randStartCityIndex)
		# increment number of states created
		self.number_of_states_created += 1
		# create a heap queue
		self.heap_list = []
		heapq.heapify(self.heap_list)
		# push state zero on the queue
		heapq.heappush(self.heap_list, (state_zero.get_key(), state_zero))

		# while the length of our queue is not zero
		while len(self.heap_list) != 0 and time.time()-start_time < time_allowance:
			# update max queue size
			if len(self.heap_list) > self.max_queue_size:
				self.max_queue_size = len(self.heap_list)
			# call our pop_off function
			key, state = heapq.heappop(self.heap_list)
			self.pop_off(state)

		# if not all states are dequeued because of termination
		# those states will be counted as pruned
		self.number_of_pruned_states += len(self.heap_list)

		# stop time
		end_time = time.time()
		# organize results and return
		results = {}
		results['cost'] = self.bssf.cost
		results['count'] = self.number_of_solutions_found
		results['soln'] = self.bssf
		results['time'] = end_time - start_time
		results['max'] = self.max_queue_size
		results['total'] = self.number_of_states_created
		results['pruned'] = self.number_of_pruned_states

		return results


	def pop_off(self, parent_state):
		# if the state has all cities in the route
		if len(parent_state.route_set_indices) == len(self._scenario.getCities()):
			# check that that the cost from the last to the first is not infinity
			if parent_state.route[-1].costTo(parent_state.route[0]) != math.inf:
				solution = TSPSolution(parent_state.route)
				# if the cost of the solution is less than the solution we have saved, update it
				if solution.cost < self.bssf.cost:
					self.bssf = solution
					# increment number of solutions found
					self.number_of_solutions_found += 1
					# prune states
					self.prune()

		else:
			# for all cities
			for i in range(len(self._scenario.getCities())):
				# if the city is not already part of the route
				if i not in parent_state.route_set_indices:
					# create new state
					new_state = State(parent_state, i, self._scenario.getCities())
					# increment number of states created
					self.number_of_states_created += 1
					# if the new state's lower bound is not infinity and is not more than bssf, then add it to the queue
					if new_state.lower_bound != math.inf and new_state.lower_bound < self.bssf.cost:
						new_state_key = new_state.get_key()
						heapq.heappush(self.heap_list, (new_state.get_key(), new_state))
					# if the new state is not added to the queue, then it counts as "pruned"
					else:
						self.number_of_pruned_states += 1


	def prune(self):
		# for each tuple in the heap_list
		for tuple in self.heap_list:
			# extract the key and state object
			key, state = tuple
			# if the state's lower bound is greater than or equal to  the new bssf cost
			if state.lower_bound >= self.bssf.cost:
				# remove the tuple from the list
				self.heap_list.remove(tuple)
				# increment the number of pruned states
				self.number_of_pruned_states += 1


	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	'''
		
	def fancy( self,time_allowance=60.0 ):
		# start timer
		start_time = time.time()
		# call greedy
		self.bssf = self.greedy()['soln']
		# get cities
		cities = self._scenario.getCities()
		route_changed = True
		while route_changed:
			route_changed = False
			for i in range(len(cities)):
				for j in range(len(cities)):
					if i != j:
						new_solution = self.two_opt_swap(self.bssf, i, j)
						if new_solution.cost < self.bssf.cost:
							self.bssf = new_solution
							route_changed = True

		end_time = time.time()

		results = {}
		results['cost'] = self.bssf.cost
		results['count'] = 0
		results['soln'] = self.bssf
		results['time'] = end_time - start_time
		results['max'] = 0
		results['total'] = 0
		results['pruned'] = 0

		return results



	def two_opt_swap(self, path, i, j):
		swapped_path = path.route[:i] + path.route[i:j][::-1] + path.route[j:]
		swapped_path_solution = TSPSolution(swapped_path)
		return swapped_path_solution



		



