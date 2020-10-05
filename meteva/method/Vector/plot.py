import matplotlib as mpl
import matplotlib.pyplot as plt
import os

import numpy as np

def scatter_uv(ob,fo,labels = None,save_path=None,show = False,title = "风矢量频率分布图",
               sup_fontsize = 10,width = None,height = None):

    u1 = ob[:,0]
    v1 = ob[:,1]
    u2 = fo[:,0]
    v2 = fo[:,1]

    if width is None:
        width = 5
    if height is None:
        height = width
    fig = plt.figure(figsize = (width,height))
    plt.plot(u1,v1,'.',color= 'b',  markersize=5,label ="839005")
    plt.plot(u2,v2,'.',color= 'r',  markersize=5,label ="838967")
    plt.xlabel("u分量",fontsize = sup_fontsize *0.9)
    plt.ylabel("v分量",fontsize = sup_fontsize *0.9)
    plt.title(title,fontsize = sup_fontsize)
    s1 = np.sqrt(u1 * u1 + v1 * v1)
    s2 = np.sqrt(u2 * u2 + v2 * v2)
    maxs = np.maximum(np.max(s1),np.max(s2))
    #print(maxs)
    plt.xlim(-8,8)
    plt.ylim(-8,8)
    plt.legend()
    angles = np.arange(0,360,45)
    for i in range(len(angles)):
        angle = angles[i] * 3.1415926 /180
        r = np.arange(0,maxs,maxs * 0.1)
        x = r * np.sin(angle)
        y = r * np.cos(angle)
        plt.plot(x,y,"--",color = "k",linewidth = 0.5)

    rs = np.arange(0,maxs,1)
    for i in range(len(rs)):
        r = rs[i]
        angle = np.arange(0,360) * 3.1415926 /180
        x = r * np.sin(angle)
        y = r * np.cos(angle)
        plt.plot(x,y,"--",color = "k",linewidth = 0.5)


    if(save_path is not None):
        file1,extension = os.path.splitext(save_path)
        extension = extension[1:]
        plt.savefig(save_path,format = extension)
    else:
        show = True
    if show:
        plt.show()
    plt.close()