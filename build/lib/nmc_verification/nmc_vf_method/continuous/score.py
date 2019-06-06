import numpy as np

def me(Ob,Fo):
    mean_error = np.mean(Ob - Fo)
    return mean_error

def mae(Ob,Fo):
    mean_abs_error = np.mean(np.abs(Ob-Fo))
    return mean_abs_error

def mse(Ob,Fo):
    mean_sqrt_error = np.mean(np.square(Ob - Fo))
    return  mean_sqrt_error

def rmse(Ob,Fo):
    mean_sqrt_error = np.sqrt(np.mean(np.square(Ob - Fo)))
    return mean_sqrt_error

def bias(Ob,Fo):
    bias0 = np.mean(Fo) / (np.mean(Ob) + 1e-6)
    return bias0

def corr(Ob,Fo):
    ob_f = Ob.flatten()
    fo_f = Fo.flatten()
    corr0 = np.corrcoef(ob_f,fo_f)[0,1]
    return corr0