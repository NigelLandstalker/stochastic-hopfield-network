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
		self.input_names = []

		self.run_count = 0

		def __add_input(new_input): #In the future this could work for circuits with > 2 inputs.
			if isinstance(new_input, Input):
				self.inputs.append(new_input)
				self.input_names.append(new_input.name)
			elif isinstance(new_input, Circuit):
				self.inputs += new_input.inputs
				self.input_names += [_input.name for _input in new_input.inputs]
			else:
				raise TypeError("New circuit element is not a circuit element or input.")

		__add_input(left)
		__add_input(right)

		self.num_inputs = len(set(self.inputs))

	def set_input(self, name, value): #Sets the value of an input to this circuit, affecting all inputs of the same name.
		if name in self.input_names:
			for index, current_name in enumerate(self.input_names):
				if current_name == name:
					self.inputs[index].value = value
		else:
			raise ValueError("No variable of name %s exists" % name)

		#return self.run() #Runs the circuit. USE THIS TO RUN EVERY CIRCUIT

	def get_input_string(self): #Just for testing purposes
		return [_input.name + " " + str(_input.value) for _input in self.inputs]

	def run(self):
		pass

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

#BASE LOGIC CLASSES
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
		Circuit.__init__(self, _input, Input('null'))

	def run(self):
		return not self.left.run()

class Input:
	def __init__(self, name, value = False):
		self.name = name
		self.value = value

	def run(self):
		return self.value

#BEGIN LOGIC LIBRARY:

#COMBINATIONAL LOGIC CIRCUITS:
class Xor(Circuit):
	def __init__(self, left, right):
		Circuit.__init__(self, left, right)

	def run(self):
		return Or(And(Not(self.left), self.right), And(self.left, Not(self.right)))

#MEMORY CIRCUITS:
class D_FF(Circuit):
	def __init__(self, left, right):
		Circuit.__init__(self, left, right) #Left = data, right = clock
		self.master_rsnor = Rsnor(And(left, right), And(Not(left), right))
		self.slave_rsnor = Rsnor(And(self.master_rsnor, Not(right)), And(Not(self.master_rsnor), Not(right)))

	def run(self):
		return self.slave_rsnor.run()

class T_FF(Circuit):
	def __init__(self, left):
		Circuit.__init__(self, left, Input('null'))
		self.memory = Input('memory')
		self.memory.value = False

	def run(self):
		if self.left.run():
			self.memory.value = Not(self.memory).run()
		return self.memory.value

class Balancer1(Circuit): #balances the 1s
	def __init__(self, left, right):
		Circuit.__init__(self, left, right)
		self.tff = T_FF(Xor(left, right)) #Toggle the internal memory iff one but not both of the inputs are 1 (if both are true, internal memory "toggles twice," resulting in no change)

	def run(self): #For now I'm just returning a list of the two outputs. In the future maybe want to find a way to specify output count.
		state = Input('state')
		state.value = self.tff.run()
		return [Or(And(state, Or(self.left, self.right)), And(self.left, self.right)).run() , Or(And(Not(state), Or(self.left, self.right)), And(self.left, self.right)).run()]

class AndBalancer(Circuit):
	def __init__(self, left, right):
		Circuit.__init__(self, left, right)
		self.bal = Balancer1(left, right)

	def run(self):
		outputs = self.bal.run() #Run the balancer with the new inputs. 
		top = Input('top')
		bot = Input('bot')

		top.value = outputs[0]
		bot.value = outputs[1]

		return And(top, bot)

def random_bitstream_sim(circuit, input_probs, length):
	streams = {name: su.gen_prob(input_probs[name], length) for name in input_probs}
	return bitstream_sim(circuit, streams, length)

def bitstream_sim(circuit, streams, length): #Runs a stochastic simulation on this circuit
	#input_probs is a dictionary of {'input_name': probability_value}
	stream_width = len(streams)
	if stream_width == circuit.num_inputs:
		outputs = []
		for stream_index in range(length):
			for name in streams:
				circuit.set_input(name, streams[name][stream_index]) #Assign the circuit's inputs for this iteration of the stochastic simulation.
			outputs.append(circuit.run())
		return outputs
	else:
		raise ValueError('Bitstream count: %s does not match circuit input count: %s' % (len(streams), circuit.num_inputs))

if __name__ == "__main__":
	if sys.argv[1:] == []:
		#Do the default thing
		xor = Or(And(Input('X'), Not(Input('Y'))), And(Not(Input('X')), Input('Y')))
		and_test = And(Input('A'), Input('B'))
		_input_probs = {'A': 0.5, 'B': 0.5}
		#output = random_bitstream_sim(and_test, _input_probs, 10000)
		output = bitstream_sim(and_test, {'A': [True, False, True, False], 'B':[True, False, True, False]}, 4)
		#print(su.eval_prob(output))

#		dff = D_FF(Input('data'), Input('clock'))
#		print(dff.set_input('data', True))
#		print(dff.set_input('clock', True))
#		print(dff.set_input('clock', False))
#
#		print(dff.set_input('data', False))
#		print(dff.set_input('clock', True))
#		print(dff.set_input('clock', False))
#
#		tff = T_FF(Input('toggle'))
#		print(tff.set_input('toggle', True))
#		#print(tff.set_input('toggle', False))
#		print(tff.set_input('toggle', True))
#		print(tff.set_input('toggle', True))
#		print(tff.set_input('toggle', True))

		bal = Balancer1(Input('top'), Input('bottom'))

		bal.set_input('top', True)
		bal.set_input('bottom', True)
		print(bal.run())

		_input_probs = {'top': 0.5, 'bottom': 0.5}
		bal_output = random_bitstream_sim(bal, _input_probs, 10)
		transposed_output = list(map(list, zip(*bal_output)))

		print("Single Balancer top: %s" % su.eval_prob(transposed_output[0]))
		print("Single Balancer bot: %s" % su.eval_prob(transposed_output[1]))

		andbal = AndBalancer(Input('top'), Input('bottom'))
		andbal_output = random_bitstream_sim(andbal, _input_probs, 10)
		print("andbal output %s" % su.eval_prob(andbal_output))

	else:
		main(sys.argv[1:]) #TODO: Implement parsing of equations later

#Results:
#It is known that the MUX does scaled addition as follows: sx + (1 - s)y
#The 1 balancer is experimentally shown to compute the function: P_out = 0.5(x + y) (the same probability exists on both outputs. These probabilities are correlated but out of phase)
#TODO: Can out-of-phase probabilities be useful in some way?
#The theoretical n-input counting network therefore produces the function: (1 / n)(sum(x)), where x is the input vector. This is exactly an average function.
#Can a mux
#Or(Balance(x, y)) should be 0 no matter what OR SHOULD IT....
