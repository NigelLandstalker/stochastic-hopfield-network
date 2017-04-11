#Fitness functions for networked stochastic logic neural nets
#Author: Owen Hoffend

import random
import math
import statistics

#Testcase params
BITSTREAM_LENGTH = 100
TRIALS = 50
TRIAL_FITNESS_ABORT_THRESHOLD = 0.01
MAX_MISTAKES = 50

def AND_fit(network): #Trains the network to output the correct value on its first output for each iteration
	if network.width >= 2: #Network size
		trial_fitnesses = []
		mistakes = 0
		for _ in range(TRIALS):
			a_input, b_input = random.uniform(0, 1), random.uniform(0,1)
			network_inputs = [a_input, b_input]
			network_inputs.extend([0 for _ in range(network.width - 2)])

			expected = a_input * b_input
			outputprob = network.stochastic_run(network_inputs, BITSTREAM_LENGTH)[0]
			trial_fitness = 1 - (abs((expected - outputprob) / expected))
			trial_fitnesses.append(trial_fitness)

			if trial_fitness < TRIAL_FITNESS_ABORT_THRESHOLD:
				mistakes += 1
				if mistakes > MAX_MISTAKES:
					break
		return statistics.mean(trial_fitnesses)
	else:
		print("Invalid network size for s_AND operation.")

def sine_fit(network):
	if network.width >= 1: #I do not know a good network size for the sine function
		trial_fitnesses = []
		mistakes = 0
		for _ in range(TRIALS):
			network_input = [random.uniform(0, 1)]
			network_input.extend([0 for _ in range(network.width - 1)])

			expected = (math.sin(2*math.pi*network_input[0]) + 1) / 2 #+1 and /2 so that it outputs in the range from 0 to 1
			outputprob = network.stochastic_run(network_input, BITSTREAM_LENGTH)[0]
			trial_fitness = 1 - (abs((expected - outputprob) / expected))
			trial_fitnesses.append(trial_fitness)
			if trial_fitness < TRIAL_FITNESS_ABORT_THRESHOLD:
				mistakes += 1
				if mistakes > MAX_MISTAKES:
					break
		return statistics.mean(trial_fitnesses)
	else:
		print("Invalid network size for sine fit operation.")

def scaled_add_fit(network):
	if network.width >= 3: #Network size
		trial_fitnesses = []
		mistakes = 0
		for _ in range(TRIALS):
			a_input, b_input, c_input = random.uniform(0, 1), random.uniform(0,1), random.uniform(0,1)
			network_inputs = [a_input, b_input, c_input]
			network_inputs.extend([0 for _ in range(network.width - 3)])

			expected = (a_input * c_input) + (1 - c_input) * b_input
			outputprob = network.stochastic_run(network_inputs, BITSTREAM_LENGTH)[0]
			trial_fitness = 1 - (abs(expected - outputprob) / expected)
			trial_fitnesses.append(trial_fitness)
			if trial_fitness < TRIAL_FITNESS_ABORT_THRESHOLD:
				mistakes += 1
				if mistakes > MAX_MISTAKES:
					break
		return trial_fitnesses
	else:
		print("Invalid network size scaled add fit operation.")
