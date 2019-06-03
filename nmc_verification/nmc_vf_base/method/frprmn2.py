import math
import numpy as np
import time
def frprmn2(x,targe,grads,tol = 0.001,caculate_time = 60):

    x0 = x
    n = len(x0)
    x_min = math.sqrt(1.0/n)
    df = grads(x0)
    g_0 = -df
    h_0 = g_0
    f_min_line0 = 0
    f_min_line1 = targe(x0)
    start_time = time.time()
    for i in range(10000):
        d0 = np.dot(df,h_0)
        x1 = x0 + h_0 * x_min
        df = grads(x1)
        d1 = np.dot(df,h_0)
        if d0 == d1:
            f_min_line1 = targe(x0)
            return x0
        else:
            x_min = x_min * d0/(d0 - d1)
            x0 += h_0 * x_min
        df = grads(x0)
        g_1 = -df
        v1 = np.dot(g_1 - g_0, g_1)
        v2 = np.dot(g_0,g_0)
        h_0 = g_1 + (v1/v2) * h_0
        g_0 = g_1
        if i%10 == 0:
            f_min_line0 = f_min_line1
            f_min_line1 = targe(x0)
            print(str(i) + "  " + str(f_min_line1))
            delta = 2 * abs(f_min_line1 - f_min_line0) / (abs(f_min_line1) + abs(f_min_line0)) - tol
            if delta < 0:
                return x0
        if(time.time() - start_time > caculate_time):
            return x0
    print('迭代分析超过10000次而退出')
    return x0

