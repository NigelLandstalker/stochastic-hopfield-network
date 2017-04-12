#Bitstream Simulation
#Author: Owen Hoffend
#April, 2017

import stochasticUitls as su
import sys

#Functions in this simulator use the True/False functionality of stochasticUtils

MAX_RUNS = 1000 #Maximum iterations of a top-level circuit

def main(argv): #For command-line operation (implement later)
	print(str(argv))

class Circuit():
	def __init__(self, left, right):
		self.left = left
		self.right = right
		self.inputs = []
		self.input_names = []

		self.run_count = 0

		def __add_input(new_input): #In the future this could work for circuits with > 2 inputs.
			if isinstance(new_input, Input):
				self.inputs.append(new_input)
				self.input_names.append(new_input.name)
			elif isinstance(new_input, Circuit):
				self.inputs += new_input.inputs
				self.input_names += [_input.name for _input in new_input.inputs]

		__add_input(left)
		__add_input(right)

		self.num_inputs = len(self.inputs)

#	def replace_input(self, name_to_replace, new_input): #Used for building circuits with feedback
#		index = self.input_names.index(name_to_replace)
#		self.input_names[index] = name_to_replace
#		self.inputs[index] = new_input
#
#		if name_to_replace in self.left.input_names:
#			self.left = new_input
#		else:
#			self.right = new_input

	def set_input(self, name, value):
		if name in self.input_names:
			for index, current_name in enumerate(self.input_names):
				if current_name == name:
					self.inputs[index].value = value
		else:
			raise ValueError("No variable of name %s exists" % name)

	def get_inputs(self):
		return [_input.name + " " + str(_input.value) for _input in self.inputs]

class Rsnor(Circuit): #Internal memory element instead of dealing with feedback within the recursion tree.
	def __init__(self, left, right):
		Circuit.__init__(self, left, right) #left = S, right = R
		self.memory = False

	def run(self):
		s = self.left.run()
		r = self.right.run()
		if s and r:
			raise ValueError("RS Nor is in an invalid state")
		elif s and (not r):
			self.memory = True
		elif (not s) and r:
			self.memory = False

		return self.memory

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
		xor.set_input('X', True)
		xor.set_input('Y', True)

		rsnor = Rsnor(Input('S'), Input('R'))
		rsnor.set_input('S', True)
		print(rsnor.run())
		rsnor.set_input('S', False)
		print(rsnor.run())
		rsnor.set_input('R', True)
		print(rsnor.run())
		rsnor.set_input('R', False)
		print(rsnor.run())

		_input_str = xor.get_inputs()
		print(_input_str)
		print(xor.run())

	else:
		main(sys.argv[1:]) #TODO: Implement parsing of equatons later
