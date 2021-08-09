from random import sample
from matplotlib import pyplot as plt
import numpy as np


class DifferentialEvolution:
    def __init__(self, cost_function, bounds, max_iterations,
                 population_size, mutation, crossover, strategy, population_initialization):
        self.cost_function = cost_function
        self.max_iterations = max_iterations
        self.population_size = population_size
        self.mutation = mutation
        self.crossover = crossover
        self.bounds = bounds
        self.population = []
        self.strategy = strategy
        self.generation = 0
        self.generation_best_individual = None
        self.generation_best_individual_idx = None
        self.best_individual_history = []
        self.generation_fitness = []
        self.initial_population = population_initialization

    def initialize(self):
        if self.initial_population == "random":
            for _ in range(self.population_size):
                individual = []
                for bound in self.bounds:
                    individual.append(np.random.uniform(bound[0], bound[1]))
                self.population.append(individual)
        elif self.initial_population == "OBL":
            # oppositional based learning
            population_ext = []
            for _ in range(self.population_size):
                individual = []
                opposite_individual = []
                for bound in self.bounds:
                    x_i = np.random.uniform(bound[0], bound[1])
                    individual.append(x_i)
                    opposite_individual.append(min(bound) + max(bound) - x_i)

                population_ext.append(individual)
                population_ext.append(opposite_individual)
            population_ext.sort(key=self.cost_function)
            self.population = population_ext[:self.population_size]
        elif self.initial_population == "tent":
            x = np.random.uniform(0, 1)
            for _ in range(self.population_size):
                individual = []
                for bound in self.bounds:
                    if x < 0.5:
                        x = 2 * x
                    else:
                        x = 2 * (1 - x)
                    individual.append((bound[1] - bound[0]) * x + bound[0])
                self.population.append(individual)
        elif self.initial_population == "QOBL":
            # quasi-oppositional differential evolution
            population_ext = []
            for _ in range(self.population_size):
                individual = []
                quasi_opposite_individual = []
                for bound in self.bounds:
                    x_i = np.random.uniform(bound[0], bound[1])
                    individual.append(x_i)
                    opposite_individual = min(bound) + max(bound) - x_i
                    m = (min(bound) + max(bound)) / 2
                    if x_i < m:
                        quasi_opposite_individual.append(m + (opposite_individual - m) * np.random.uniform(0, 1))
                    else:
                        quasi_opposite_individual.append(opposite_individual + (m - opposite_individual) * np.random.uniform(0, 1))

                population_ext.append(individual)
                population_ext.append(quasi_opposite_individual)
            population_ext.sort(key=self.cost_function)
            self.population = population_ext[:self.population_size]
            # print(self.population)

    def evolve(self):
        self.generation = 0
        while self.generation < self.max_iterations:
            self.generation_fitness = []
            self.generation += 1
            self.get_best()
            self.best_individual_history.append(self.generation_best_individual)
            for idx, individual in enumerate(self.population):
                crossover_candidates = self.generate_crossover_candidates(idx)
                new_individual = []
                random_dimension = np.random.randint(0, len(individual))
                for dimension in range(len(individual)):
                    cr = np.random.uniform(0, 1)
                    if cr > self.crossover or random_dimension != dimension:
                        new_individual.append(individual[dimension])
                    else:
                        # check boundaries, if violation, random generate new one
                        new_individual.append(self.mutate(crossover_candidates, dimension))

                if self.cost_function(new_individual) < self.cost_function(individual):
                    self.population[idx] = new_individual
                self.generation_fitness.append(self.cost_function(self.population[idx]))
                # measure diversity here?

    def generate_crossover_candidates(self, idx):
        crossover_candidates = [idx]
        while idx in crossover_candidates:
            crossover_candidates = sample(range(self.population_size - 1), 6)
        if self.strategy == "DE/rand/1":
            return crossover_candidates[:3]
        elif self.strategy == "DE/rand/2":
            return crossover_candidates
        elif self.strategy == "DE/best/1":
            crossover_candidates[0] = self.generation_best_individual_idx
            return crossover_candidates[:3]
        elif self.strategy == "DE/best/2":
            crossover_candidates[0] = self.generation_best_individual_idx
            return crossover_candidates
        elif self.strategy == "DE/current-to-best/1":
            crossover_candidates[0] = self.generation_best_individual_idx
            crossover_candidates[1] = idx
            return crossover_candidates[:4]
        elif self.strategy == "DE/current-to-best/2":
            crossover_candidates[0] = self.generation_best_individual_idx
            crossover_candidates[1] = idx
            return crossover_candidates
        elif self.strategy == "DE/current-to-rand/1":
            crossover_candidates[0] = idx
            return crossover_candidates[:4]

    def mutate(self, crossover_candidates, dimension):
        if self.strategy == "DE/rand/1" or self.strategy == "DE/best/1":
            return self.population[crossover_candidates[0]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[1]][dimension] -
                                    self.population[crossover_candidates[2]][dimension])
        elif self.strategy == "DE/rand/2" or self.strategy == "DE/best/2":
            return self.population[crossover_candidates[0]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[1]][dimension] -
                                    self.population[crossover_candidates[2]][dimension]) + \
                   self.mutation[0] * (self.population[crossover_candidates[3]][dimension] -
                                    self.population[crossover_candidates[4]][dimension])
        elif self.strategy == "DE/current-to-best/1":
            return self.population[crossover_candidates[1]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[0]][dimension] -
                                       self.population[crossover_candidates[1]][dimension]) +\
                   self.mutation[1] * (self.population[crossover_candidates[2]][dimension] -
                                       self.population[crossover_candidates[3]][dimension])
        elif self.strategy == "DE/current-to-best/2":
            return self.population[crossover_candidates[1]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[0]][dimension] -
                                       self.population[crossover_candidates[1]][dimension]) + \
                   self.mutation[1] * (self.population[crossover_candidates[2]][dimension] -
                                       self.population[crossover_candidates[3]][dimension]) + \
                   self.mutation[1] * (self.population[crossover_candidates[4]][dimension] -
                                       self.population[crossover_candidates[5]][dimension])
        elif self.strategy == "DE/current-to-rand/1":
            return self.population[crossover_candidates[0]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[1]][dimension] -
                                       self.population[crossover_candidates[0]][dimension]) + \
                   self.mutation[1] * (self.population[crossover_candidates[2]][dimension] -
                                       self.population[crossover_candidates[3]][dimension])

    def get_best(self):
        best_cost = np.inf
        best = np.inf
        best_idx = np.inf
        for idx, individual in enumerate(self.population):
            cost = self.cost_function(individual)
            if cost < best_cost:
                best = individual
                best_cost = cost
                best_idx = idx
        self.generation_best_individual = best
        self.generation_best_individual_idx = best_idx
        return best

    def filter_history(self, dimension):
        solutions = [solution[dimension] for solution in self.best_individual_history]
        return solutions

    def measure_diversity(self, measure):
        if measure == "std-fitness":
            return np.std(self.generation_fitness)


def function_to_minimize(x):
    return x[0] ** 2 + x[1] ** 2


if __name__ == '__main__':
    from testing_functions import schaffer_n2_function as sphere_function

    diff_evolution = DifferentialEvolution(sphere_function, bounds=[[-100, 100], [-100, 100]], max_iterations=100,
                                           population_size=1000,  mutation=[0.7, 0.7], crossover=0.7,
                                           strategy="DE/best/1", population_initialization="QOBL")
    diff_evolution.initialize()
    diff_evolution.evolve()
    print("the best solution: ", diff_evolution.get_best)
    fig, (ax1, ax2) = plt.subplots(2)
    fig.suptitle("Error")
    optimal_value = [512, 404.2319]
    ax1.plot(np.log10(np.abs(np.asarray(diff_evolution.filter_history(0)) - optimal_value[0])))
    ax2.plot(np.log10(np.abs(np.asarray(diff_evolution.filter_history(1)) - optimal_value[1])))
    plt.show()
    print(diff_evolution.get_best())
