#Hopfield network main structure code
#Author: Owen Hoffend

import json
import FitnessFunctions
import math
from Timer import Timer
from copy import copy
from stochasticUitls import *
#Network parameters
DEFAULT_THRESHOLD = 1
DEFAULT_BIAS = 0
DEFAULT_OUTPUT = 0
DEFAULT_INTERNAL_WEIGHT = 1
DEFAULT_INPUT_WEIGHT = 1

#Evolution parameters
INITIAL_POPULATION_SIZE = 100
#Population-based evolutionary algorithm:
#Generate a set of random networks to serve as the seed population.
#Run the required test function on each network and save the network's performance as a percentage value

class hopfield_network():
	def __init__(self, width, mutate_on_instantiation=False, **kwargs):
		self.width = width
		self.output = [DEFAULT_OUTPUT for _ in range(width)]
		self.biases = [DEFAULT_BIAS for _ in range(width)]
		self.thresholds = [DEFAULT_THRESHOLD for _ in range(width)]
		self.input_weights = [DEFAULT_INPUT_WEIGHT for _ in range(width)]
		self.internal_weights = [[DEFAULT_INTERNAL_WEIGHT for i in range(width)] for j in range(width)]

		self.fitness = 0

		if mutate_on_instantiation:
			self.mutate(**kwargs)

	def mutate(self, **kwargs):
		if "threshold_prob" and "threshold_minmax" in kwargs:
			self.thresholds = list_rand_minmax(kwargs["threshold_prob"], self.thresholds, kwargs["threshold_minmax"])

		if "bias_prob" and "bias_minmax" in kwargs:
			self.biases = list_rand_minmax(kwargs["bias_prob"], self.biases, kwargs["bias_minmax"])

		if "input_weight_prob" and "input_weight_minmax" in kwargs:
			self.input_weights = list_rand_minmax(kwargs["input_weight_prob"], self.input_weights, kwargs["input_weight_minmax"])

		if "internal_weight_prob" and "internal_weight_minmax" in kwargs:
			self.internal_weights = [list_rand_minmax(kwargs["internal_weight_prob"], sublist, kwargs["internal_weight_minmax"]) for sublist in self.internal_weights]

	def run_once(self, inputs):
		if len(inputs) == self.width:
			pre_threshold = [inputs[index] * self.input_weights[index] + dot_product(self.internal_weights[index], self.output) + self.biases[index] for index in range(self.width)]
			self.output = [1 if pre_threshold[index] > self.thresholds[index] else 0 for index in range(self.width)]
			return list(self.output) #SHOULDN'T return the pointer to self.output itself. Make sure of this!
		else:
			print("invalid input lengths")

	def stochastic_run(self, probabilities, bitlength):
		inputs = [list(i) for i in zip(*[gen_prob(prob, bitlength, True) for prob in probabilities])]
		outputs = zip(*[self.run_once(inputs[index]) for index in range(len(inputs))])
		output_probs = [eval_prob(out_i) for out_i in outputs]
		return output_probs #returns the probability of encountering a 1

	def exportJSON(self, filename):
		with open(filename, 'w') as outfile:
			json.dump(self.__dict__, outfile)
			outfile.close()

def importJSON(filename):
	with open(filename, 'r') as infile:
		data = json.load(infile)
		infile.close()
		net = hopfield_network(data["width"])
		net.thresholds, net.internal_weights, net.output, net.biases, net.input_weights = data["thresholds"], data["internal_weights"], data["output"], data["biases"], data["input_weights"]
		return net

def run_evolution(generation_cnt, operation, **params):
	#Runs an entire evolution cycle from start to finish
	#generation_cnt defines the number of generations in the evolution cycle
	#The initial population size is specified outside the function (for now)
	function = getattr(FitnessFunctions, operation)
	current_population = [hopfield_network(params["network_size"], True, **params) for _ in range(INITIAL_POPULATION_SIZE)]
	net_timer_avg = 0
	for _ in range(generation_cnt):
		with Timer() as gen_timer:
			for network in current_population:
				with Timer() as network_timer:
					network.fitness = function(network)
				net_timer_avg = (network_timer.secs + net_timer_avg) / 2

			current_population.sort(key = lambda x: x.fitness, reverse=True)
			current_population = current_population[:math.ceil(len(current_population) / 4)]
			print([n.fitness for n in current_population])

		print("Average network test time was %s" % net_timer_avg)
		print("Generation time was: %s" % gen_timer.secs)

		with Timer() as mutation_timer:
			for network in current_population:
				if len(current_population) < INITIAL_POPULATION_SIZE:
					mutation_prob = 1 - (network.fitness / 100)
					params["internal_weight_prob"] = mutation_prob
					params["input_weight_prob"] = mutation_prob
					params["bias_prob"] = mutation_prob

					for _ in range(3):
						child_network = copy(network)
						child_network.mutate(**params)
						current_population.append(child_network)
				else:
					break

		print("Mutation time was: %s" % mutation_timer.secs)

	return current_population

	#Evolution improvement ideas:
	#Change the mutation chance to depend on the fitness level of the network. - CHECK
	#Instead of completely random mutations, use a random plus/minus factor
	#Alter the testcase length iteratively to safe on cycles
	#Figure out how to use GPU to parallelize the testing!

def test_fitness_randomly():
	fitnesslevel = 0
	maxfitlevel = 0
	cycles = 0
	while fitnesslevel < 100:
		network = hopfield_network(2)
		#network = importJSON("test.txt")
		network.mutate(internal_weight_prob=1, internal_weight_minmax=1, bias_prob=1, bias_minmax=1, input_weight_prob=1, input_weight_minmax=1)
		fitnesslevel = FitnessFunctions.s_AND_fit(network)
		cycles += 1
		if fitnesslevel > maxfitlevel:
			maxfitlevel = fitnesslevel
			network.exportJSON("test.txt")
			print(str(maxfitlevel) + " " + str(cycles))
			cycles = 0


if __name__ == "__main__":
	run_evolution(1000, "s_AND_fit", network_size=4, internal_weight_prob=1, internal_weight_minmax=1, bias_prob=1, bias_minmax=1, input_weight_prob=1, input_weight_minmax=1)
