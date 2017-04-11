#Bitstream Simulation
#Author: Owen Hoffend
#April, 2017

import stochasticUitls as su
import sys

#Functions in this simulator use the True/False functionality of stochasticUtils

def main(argv): #For command-line operation (implement later)
	print(str(argv))

class Circuit():
	def __init__(self, left, right):
		self.left = left
		self.right = right
		self.inputs = []

		if isinstance(left, Input):
			self.inputs.append(left)
		elif isinstance(left, Circuit):
			self.inputs += left.inputs

		if isinstance(right, Input):
			self.inputs.append(right)
		elif isinstance(right, Circuit):
			self.inputs += right.inputs

		self.num_inputs = len(self.inputs)

	def get_inputs(self):
		return [_input.name + " " + str(_input.value) for _input in self.inputs]

class And(Circuit):
	def __init__(self, left, right):
		Circuit.__init__(self, left, right)

	def run(self):
		return self.left.run() and self.right.run()

class Or(Circuit):
	def __init__(self, left, right):
		Circuit.__init__(self, left, right)

	def run(self):
		return self.left.run() or self.right.run()

class Not(Circuit):
	def __init__(self, _input):
		Circuit.__init__(self, _input, None)

	def run(self):
		return not self.left.run()

class Input:
	def __init__(self, name, value = False):
		self.name = name
		self.value = value

	def run(self):
		return self.value

if __name__ == "__main__":
	if sys.argv[1:] == []:
		#Do the default thing
		circuit = And(Or(Input('A', False), Input('B')), Input('C', True))
		xor = Or(And(Input('X'), Not(Input('Y'))), And(Not(Input('X')), Input('Y')))

		_input = xor.inputs

		_input[0].value = False
		_input[1].value = False
		_input[2].value = False
		_input[3].value = False

		_input_str = xor.get_inputs()
		print(_input_str)
		print(xor.run())
		#su.gen_prob()
	else:
		main(sys.argv[1:]) #TODO: Implement parsing of equatons later
