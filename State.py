import math
import random
import copy

class State:

    def __init__(self, parent_state, to_index, cities):
        if parent_state != None:
            self.matrix = copy.deepcopy(parent_state.matrix)
            self.parent_state_lower_bound = parent_state.lower_bound
            self.depth = parent_state.depth + 1

            self.route_set_indices = copy.deepcopy(parent_state.route_set_indices)
            self.route = copy.deepcopy(parent_state.route)

            self.visited_rows = copy.deepcopy(parent_state.visited_rows)
            self.visited_columns = copy.deepcopy(parent_state.visited_columns)

            # to_index represents the index of the city we are visiting
            self.to_index = to_index
            self.visit_next_city_and_reduce(parent_state.to_index, to_index, cities)

    def set_state_zero_matrix(self, matrix, cities, randStartCityIndex):
        self.matrix = copy.deepcopy(matrix)
        self.parent_state_lower_bound = 0
        self.depth = 1

        # keep track of the cities that we have visited
        self.route_set_indices = set()
        self.route = []

        # when we travel between two cities, we will infinite-out the column and row
        # we will keep track of which columns and rows are infinited-out with these sets
        self.visited_columns = set()
        self.visited_rows = set()

        # select arbitrary start city

        # save the start city as the to_index
        # ( this will become the from index when we start visiting cities )
        self.to_index = randStartCityIndex
        # add the index to the set of visited city indices so that we don't have our route
        self.route_set_indices.add(randStartCityIndex)
        self.route.append(cities[randStartCityIndex])

        self.reduce_state_zero_matrix()

    def visit_next_city_and_reduce(self, from_city_index, to_city_index, cities):
        # lower bound = parent state lower bound + cost of path + cost of reduction
        # get cost of path at row = from_city_index , column = to_city_index
        cost_of_path = self.matrix[from_city_index][to_city_index]

        # infinite out row from_city_index
        for i in range(len(self.matrix)):
            self.matrix[from_city_index][i] = math.inf
        # add row to visited_rows
        self.visited_rows.add(from_city_index)

        # infinite out column to_city_index
        for i in range(len(self.matrix)):
            self.matrix[i][to_city_index] = math.inf
        # add column to visited_columns
        self.visited_columns.add(to_city_index)

        # infinite out backwards path
        self.matrix[to_city_index][from_city_index] = math.inf

        # reduce the matrix and keep track of the cost of reduction
        cost_of_reduction = 0

        # reduce rows not in visited_rows and add cost
        for i in range(len(self.matrix)):
            if i not in self.visited_rows:
                cost_of_reduction += self.reduce_row(i)
        # reduce columns not in visited_columns and add cost
        for i in range(len(self.matrix)):
            if i not in self.visited_columns:
                cost_of_reduction += self.reduce_col(i)

        # lower bound = parent state lower bound + cost of path + cost of reduction
        self.lower_bound = self.parent_state_lower_bound + cost_of_path + cost_of_reduction

        # update route and route_set
        # add the index to the set of visited city
        self.route_set_indices.add(to_city_index)
        self.route.append(cities[to_city_index])

    def get_key(self):
        return (self.lower_bound * 2) / self.depth

    def reduce_state_zero_matrix(self):
        # lower bound = previous lower bound + cost of path + cost of reduction
        self.lower_bound = self.parent_state_lower_bound
        # reduce each row and add the cost of reduction to the lower bound
        for i in range(len(self.matrix)):
            self.lower_bound += self.reduce_row(i)
        # reduce each column and add the cost of reduction to the lower bound
        for i in range(len(self.matrix)):
            self.lower_bound += self.reduce_col(i)

    # return the amount to add to the lower bound ( cost of reduction )
    def reduce_row(self, rowIndex):
        minimum = math.inf
        for i in range(len(self.matrix)):
            if self.matrix[rowIndex][i] < minimum:
                minimum = self.matrix[rowIndex][i]
        # we will not modify the matrix if minimum is 0 or infinity
        if minimum == 0 or minimum == math.inf:
            return minimum
        else:
            for i in range(len(self.matrix)):
                self.matrix[rowIndex][i] = self.matrix[rowIndex][i] - minimum
            return minimum

    # return the amount to add to the lower bound ( cost of reduction )
    def reduce_col(self, columnIndex):
        minimum = math.inf
        for i in range(len(self.matrix)):
            if self.matrix[i][columnIndex] < minimum:
                minimum = self.matrix[i][columnIndex]
        # we will not modify the matrix if minimum is 0 or infinity
        if minimum == 0 or minimum == math.inf:
            return minimum
        else:
            for i in range(len(self.matrix)):
                self.matrix[i][columnIndex] = self.matrix[i][columnIndex] - minimum
            return minimum