#Fitness functions for networked stochastic logic neural nets
#Author: Owen Hoffend

import random
import math

#Testcase params
BITSTREAM_LENGTH = 1000

def s_AND_fit(network): #Trains the network to output the correct value on its first output for each iteration
	if network.width >= 2: #Network size
		a_input, b_input = random.uniform(0, 1), random.uniform(0,1)
		network_inputs = [a_input, b_input]
		network_inputs.extend([0 for _ in range(network.width - 2)])

		expected = a_input * b_input
		outputprob = network.stochastic_run(network_inputs, BITSTREAM_LENGTH)[0]
		#print(abs(outputprob - expected))
		return 1 - (abs(expected - outputprob) / expected)
		#print(abs(expected - outputprob))
		#return (1/((expected - outputprob)**2))
	else:
		print("Invalid network size for s_AND operation.")

def scaled_add_fit(network):
	if network.width >= 3: #Network size
		a_input, b_input, c_input = random.uniform(0, 1), random.uniform(0,1), random.uniform(0,1)
		network_inputs = [a_input, b_input, c_input]
		network_inputs.extend([0 for _ in range(network.width - 3)])

		expected = (a_input * c_input) + (1 - c_input) * b_input
		outputprob = network.stochastic_run(network_inputs, BITSTREAM_LENGTH)[0]
		#print(abs(outputprob - expected))
		return 1 - (abs(expected - outputprob) / expected)
		#print(abs(expected - outputprob))
		#return (1/((expected - outputprob)**2))
	else:
		print("Invalid network size for s_AND operation.")
