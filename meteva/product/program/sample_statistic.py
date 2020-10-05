import meteva


def sample_tdt(sta_all,return_result = False,**kwargs):
    result = meteva.product.score_tdt(sta_all,meteva.method.sample_count,x_y="time_dtime",annot = -1,
                                      title = "样本数随时间和时效的分布",**kwargs)
    if return_result:
        return result

def sample_id(sta_all,return_result = False,**kwargs):
    result = meteva.product.score_id(sta_all,meteva.method.sample_count,plot = "scatter",
                                     title = "所有时间和时效样本数的空间分布",
                                    **kwargs)
    if return_result:
        return result