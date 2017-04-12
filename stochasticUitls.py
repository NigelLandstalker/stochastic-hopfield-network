#Miscellaneous utilities for stochastic hopfield network optimiser
#Author: Owen Hoffend

import random, math

def eval_prob(bitstream, isBoolean = False):
	in_len = len(bitstream)
	if isBoolean:
		out_len = len([i for i in bitstream if i == True])
	else:
		out_len = len([i for i in bitstream if i == 1])

	return out_len / in_len

#Generates a stochastic bitstream of a specified probability and length
def gen_prob(prob, bitLength, isInt = False):
	if(prob <= 1):
		if isInt:
			return [1 if i <= prob else 0 for i in [random.uniform(0,1) for _ in range(bitLength)]]
		else:
			return [True if i <= prob else False for i in [random.uniform(0,1) for _ in range(bitLength)]]
	else:
		print("Invalid probability input")

def list_rand_minmax(prob, list_, minmax):
	#return [(list_[index] + (quantized_rand(minmax * 2, len(list_)) - minmax)) / 2 if random.uniform(0, 1) <= prob else list_[index] for index in range(len(list_))]
	return [(quantized_rand(minmax * 2, len(list_)) - minmax) if random.uniform(0, 1) <= prob else list_[index] for index in range(len(list_))]

def quantized_rand(minmax, length):
	#Divide the minmax (usually 1) up by the number of inputs that the node receives. This should be implementable with digital hardware.
	quantization_interval = minmax / length
	return random.randint(0, length) * quantization_interval

def dot_product(list_a, list_b):
	return math.fsum(a * b for a, b in zip(list_a, list_b))
