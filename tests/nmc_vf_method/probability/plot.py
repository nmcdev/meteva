import numpy as np
import nmc_verification.nmc_vf_method.probability.plot as plot

ob = np.array([1, 3, 5, 7, 9, 11, 8, 9, 6, 4, 2, 0])
fo = np.array([1, 3, 4, 6, 9, 11, 8, 9, 6, 5, 3, 0])
plot.reliability_diagrams(ob, fo, grade_list=[0, 3, 6])
