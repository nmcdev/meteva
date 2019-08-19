import nmc_verification.nmc_vf_method.multi_category.plot as plot
import numpy as np

ob = np.array([1, 3, 5, 7, 9, 11, 8, 9, 6, 4, 2, 0])
fo = np.array([1, 3, 4, 6, 9, 11, 8, 9, 6, 5, 3, 0])

plot.frequency_histogram(ob, fo, clevs=[0, 3, 6])
