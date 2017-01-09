#Hopfield network main structure code
#Author: Owen Hoffend

import json
import FitnessFunctions
from stochasticUitls import *
#Network parameters
DEFAULT_THRESHOLD = 1
DEFAULT_BIAS = 0
DEFAULT_OUTPUT = 0
DEFAULT_INTERNAL_WEIGHT = 1
DEFAULT_INPUT_WEIGHT = 1

class hopfield_network():
	def __init__(self, width):
		self.width = width
		self.output = [DEFAULT_OUTPUT for _ in range(width)]
		self.biases = [DEFAULT_BIAS for _ in range(width)]
		self.thresholds = [DEFAULT_THRESHOLD for _ in range(width)]
		self.input_weights = [DEFAULT_INPUT_WEIGHT for _ in range(width)]
		self.internal_weights = [[DEFAULT_INTERNAL_WEIGHT for i in range(width)] for j in range(width)]

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

if __name__ == "__main__":

	fitnesslevel = 0
	maxfitlevel = 0
	cycles = 0
	while fitnesslevel < 100:
		network = hopfield_network(4)
		#network = importJSON("test.txt")
		network.mutate(internal_weight_prob=1, internal_weight_minmax=1, bias_prob=1, bias_minmax=1, input_weight_prob=1, input_weight_minmax=1)
		fitnesslevel = FitnessFunctions.s_AND_fit(network)
		cycles += 1
		if fitnesslevel > maxfitlevel:
			maxfitlevel = fitnesslevel
			network.exportJSON("test.txt")
			print(str(maxfitlevel) + " " + str(cycles))
			cycles = 0
