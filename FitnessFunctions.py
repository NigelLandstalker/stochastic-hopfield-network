#Fitness functions for networked stochastic logic neural nets
#Author: Owen Hoffend

import random

#Testcase params
BITSTREAM_LENGTH = 10
TESTCASE_LENGTH = 5
PROBABILITY_RANGE = 0.01

def s_AND_fit(network): #Trains the network to output the correct value on its first output for each iteration
	if network.width >= 2: #Network size requirement
		correct_count = 0
		for _ in range(TESTCASE_LENGTH):
			a_input, b_input = random.uniform(0, 1), random.uniform(0,1)
			network_inputs = [a_input, b_input]
			network_inputs.extend([0 for _ in range(network.width - 2)])

			expected = a_input * b_input
			outputprob = network.stochastic_run(network_inputs, BITSTREAM_LENGTH)[0]
			if expected - PROBABILITY_RANGE <= outputprob <= expected + PROBABILITY_RANGE:
				correct_count += 1
		return (correct_count / TESTCASE_LENGTH) * 100
	else:
		print("Invalid network size for s_AND operation.")
