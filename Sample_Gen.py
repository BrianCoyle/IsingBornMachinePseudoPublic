from pyquil.quil import Program
from pyquil.paulis import *
import pyquil.paulis as pl
from pyquil.gates import *
import numpy as np
from numpy import pi,log2
from pyquil.api import QVMConnection
from random import *
from pyquil.quilbase import DefGate
from pyquil.parameters import Parameter, quil_exp, quil_cos, quil_sin
import matplotlib.pyplot as plt

from Param_Init import network_params, state_init
from Train_Generation import data_sampler

import sys
qvm = QVMConnection()
p = Program()

'''This Program generates samples from the output distribution of the IQP/QAOA circuit according to the Born Rule:
	P(z) = |<z|U|s>|^2, where |s> is the uniform superposition'''

def born_sampler(N, N_v, N_h, N_born_samples, J, b, gamma_x, gamma_y):

	#final_layer = ('IQP'for IQP), = ('QAOA' for QAOA), = ('IQPy' for Y-Rot)
	#control = 'BIAS' for updating biases, = 'WEIGHTS' for updating weights, ='NEITHER' for neither
	#sign = 'POSITIVE' to run the positive circuit, = 'NEGATIVE' for the negative circuit, ='NEITHER' for neither
	##(N, N_v, N_h, J, b,  gamma_x, gamma_y, p, q, r, final_layer, control, sign)
	
	prog, wavefunction, probs = state_init(N, N_v, N_h, J, b,  gamma_x, gamma_y, 0, 0, 0, 'QAOA', 'NEITHER', 'NEITHER')

	'''Generate (N_samples) samples from output distribution on (N_v) visible qubits'''

	#Index list for classical registers we want to put measurement outcomes into.
	classical_regs = list(range(0, N_v))

	for qubit_index in range(0, N_v):
		prog.measure(qubit_index, qubit_index)

	born_samples = np.asarray(qvm.run(prog, classical_regs, N_born_samples))

	#print("\nThe samples in array form are: \n", born_samples)

	return born_samples


def plusminus_sample_gen(N, N_v, N_h, J, b, gamma_x, gamma_y, p, q, r, final_layer, control, N_born_samples_plus, N_born_samples_minus):
	''' This function computes the samples required in the estimator, in the +/- terms of the MMD loss function gradient
	 with respect to parameter, J_{p, q} (control = 'WEIGHT')  or b_{r} (control = 'BIAS')
	'''

	prog_plus, wavefunction_plus, probs_plus = state_init(N, N_v, N_h, J, b,  gamma_x, gamma_y,\
	 														p, q, r, final_layer, control, 'POSITIVE')
	prog_minus, wavefunction_minus, probs_minus = state_init(N, N_v, N_h, J, b,  gamma_x, gamma_y,\
	 														p, q, r, final_layer, control, 'NEGATIVE')

	for qubit_index in range(0, N_v):
		prog_plus.measure(qubit_index, qubit_index)
		prog_minus.measure(qubit_index, qubit_index)

	#Index list for classical registers we want to put measurement outcomes into.
	classical_regs_plus = list(range(0, N_v))
	classical_regs_minus = list(range(0, N_v))

	born_samples_plus = np.asarray(qvm.run(prog_plus, classical_regs_plus, N_born_samples_plus))
	born_samples_minus = np.asarray(qvm.run(prog_minus, classical_regs_minus, N_born_samples_minus))

	return  born_samples_plus, born_samples_minus
