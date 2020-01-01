import numpy as np
import nmc_verification.nmc_vf_method.probability as probability

fo = np.random.rand(10000)
er = np.random.rand(10000)-0.5
ob0 = fo + er
ob = np.zeros_like(ob0)
ob[ob0>0.5] = 1
ob[ob0<=0.5] = 0
#Discrimination_diagram(ob,fo)
#reliability_diagrams(ob,fo)
#roc(ob,fo)
probability.plot.comprehensive(ob,fo)
pass