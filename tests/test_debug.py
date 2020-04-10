import meteva
import pandas as pd

anal =  pd.read_hdf(r"H:\anal.h5",'df')
sele =  pd.read_hdf(r"H:\select.h5",'df')

meteva.base.by_stadata(anal,sele)