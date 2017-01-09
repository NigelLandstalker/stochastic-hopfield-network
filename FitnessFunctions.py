#Fitness functions for networked stochastic logic neural nets
#Author: Owen Hoffend

import random

BITSTREAM_LENGTH = 10
TESTCASE_LENGTH = 100
PROBABILITY_RANGE = 0.1

def s_AND_fit(network):
	if network.width >= 2: #Network size requirement
		correct_count = 0
		for _ in range(TESTCASE_LENGTH):
			a_input, b_input = random.uniform(0, 1), random.uniform(0,1)
			expected = a_input * b_input
			outputprob = network.stochastic_run([a_input, b_input,0,0], BITSTREAM_LENGTH)[0] #Trains the network to output the correct value on its first output for each iteration
			if expected - PROBABILITY_RANGE <= outputprob <= expected + PROBABILITY_RANGE:
				correct_count += 1

		return correct_count
	else:
		print("Invalid network size for s_AND operation.")
