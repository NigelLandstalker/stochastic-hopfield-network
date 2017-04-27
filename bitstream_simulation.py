#Bitstream Simulation
#Author: Owen Hoffend
#April, 2017

import stochasticUitls as su
import sys
#Functions in this simulator use the True/False functionality of stochasticUtils

def logical_xor(A, B): #Computes the logical xor of boolean values A and B
	return (A and (not B)) or ((not A) and B)

def main(argv): #For command-line operation (implement later)
	print(str(argv))

class Circuit():
	def __init__(self, size=2, *inputs):
		if size != len(inputs):
			raise ValueError("Input count is not equal to input size")
		self.sub_circuits = inputs #Contains only the circuit's direct subcircuits
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

		for circuit in self.sub_circuits:
			__add_input(circuit)

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
		Circuit.__init__(self, 2, left, right) #left = S, right = R
		self.memory = False

	def run(self):
		s = self.sub_circuits[0].run()
		r = self.sub_circuits[1].run()
		if s and r:
			raise ValueError("RS Nor is in an invalid state")
		elif s and (not r):
			self.memory = True
		elif (not s) and r:
			self.memory = False

		return self.memory

#BASE LOGIC CLASSES
class And(Circuit): #AND an arbitrary number of inputs
	def __init__(self, *inputs):
		Circuit.__init__(self, len(inputs), *inputs)

	def run(self):
		result = True
		for circuit in self.sub_circuits:
			result = result and circuit.run()

		return result

class Or(Circuit):
	def __init__(self, *inputs):
		Circuit.__init__(self, len(inputs), *inputs)

	def run(self):
		result = True
		for circuit in self.sub_circuits:
			result = result or circuit.run()

		return result

class Not(Circuit):
	def __init__(self, _input):
		Circuit.__init__(self, 1, _input)

	def run(self):
		return not self.sub_circuits[0].run()

class Input:
	def __init__(self, name, value = False):
		self.name = name
		self.value = value

	def run(self):
		return self.value

#BEGIN LOGIC LIBRARY:
#COMBINATIONAL LOGIC CIRCUITS:
class Xor(Circuit):
	def __init__(self, *inputs):
		Circuit.__init__(self, len(inputs), *inputs)

	def run(self):
		result = False
		for circuit in self.sub_circuits:
			result = logical_xor(result, circuit.run())

		return result

#MEMORY CIRCUITS:
class D_FF(Circuit):
	def __init__(self, data, clock):
		Circuit.__init__(self, 2, data, clock)
		self.master_rsnor = Rsnor(And(data, clock), And(Not(data), clock))
		self.slave_rsnor = Rsnor(And(self.master_rsnor, Not(clock)), And(Not(self.master_rsnor), Not(clock)))

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

class Balancer0(Circuit): #balances the 0s
	def __init__(self, left, right):
		Circuit.__init__(self, left, right)
		self.tff = T_FF(Xor(left, right)) #Toggle the internal memory iff one but not both of the inputs are 1 (if both are true, internal memory "toggles twice," resulting in no change)

	def run(self): #For now I'm just returning a list of the two outputs. In the future maybe want to find a way to specify output count.
		state = Input('state')
		state.value = self.tff.run()
		return [Or(And(state, Or(Not(self.left), Not(self.right))), And(Not(self.left), Not(self.right))).run() , Or(And(Not(state), Or(Not(self.left), Not(self.right))), And(Not(self.left), Not(self.right))).run()]

class CN3(Circuit):
	def __init__(self, one, two, three):
		pass

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

		return And(top, bot).run()

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
	old_tests = False
	if sys.argv[1:] == []:
		if old_tests:
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

			_input_probs = {'top': 0.3, 'bottom': 0.5}
			bal_output = random_bitstream_sim(bal, _input_probs, 10000)
			transposed_output = list(map(list, zip(*bal_output)))

			print("Single Balancer top: %s" % su.eval_prob(transposed_output[0]))
			print("Single Balancer bot: %s" % su.eval_prob(transposed_output[1]))

			andbal = AndBalancer(Input('top'), Input('bottom'))
			andbal_output = random_bitstream_sim(andbal, _input_probs, 10000)
			print("andbal output %s" % su.eval_prob(andbal_output))
		else:
			rsnor_test = Rsnor(Input('a'), Input('b'))
			print(rsnor_test.run())
			rsnor_test.set_input('a', True)
			print(rsnor_test.run())

	else:
		main(sys.argv[1:]) #TODO: Implement parsing of equations later

#Results:
#It is known that the MUX does scaled addition as follows: sx + (1 - s)y
#The 1 balancer is experimentally shown to compute the function: P_out = 0.5(x + y) (the same probability exists on both outputs. These probabilities are correlated but out of phase such that operations on them work fine)
#TODO: Can out-of-phase probabilities be useful in some way?
#The theoretical n-input counting network therefore produces the function: (1 / n)(sum(x)), where x is the input vector. This is exactly an average function.
#Can a mux
#And(Balance1(x, y)) = And(x, y). Or(Balance1(x, y)) = Or(x, y). Operations among the balancer's outputs do NOT fall victim to reconvergence issues.
