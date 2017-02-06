#Miscellaneous utilities for stochastic hopfield network optimiser
#Author: Owen Hoffend

import random, math

def eval_prob(bitstream):
	in_len = len(bitstream)
	out_len = len([i for i in bitstream if i == 1])

	return out_len / in_len

#Generates a stochastic bitstream of a specified probability and length
def gen_prob(prob, bitLength, isInt = False):
	if(prob <= 1):
		if isInt:
			return [1  if i <= prob else 0 for i in [random.uniform(0,1) for _ in range(bitLength)]]
		else:
			return [True  if i <= prob else False for i in [random.uniform(0,1) for _ in range(bitLength)]]
	else:
		print("Invalid probability input")

def list_rand_minmax(prob, list_, minmax):
	#[random.uniform(0, 2 * minmax) - minmax if random.uniform(0, 1) <= prob else list_[index] for index in range(len(list_))]
	return [(random.uniform(0, 2 * minmax) - minmax) if random.uniform(0, 1) <= prob else list_[index] for index in range(len(list_))]

def dot_product(list_a, list_b):
	return math.fsum(a * b for a, b in zip(list_a, list_b))
