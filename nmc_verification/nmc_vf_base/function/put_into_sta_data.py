import pandas as pd
import numpy as np
import copy

def join(sta,sta1):
    if(sta is None):
        return sta1
    else:
        sta = pd.concat([sta,sta1])
    return sta


def merge(sta,sta1):
    df = pd.merge(sta, sta1, on='id', how='left')
    return df
