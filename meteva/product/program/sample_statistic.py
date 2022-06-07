import meteva


def sample_tdt(sta_all,return_result = False,**kwargs):
    if "title" not in kwargs.keys():
        kwargs["title"] =  ["样本数随时间和时效的分布"]
    if "x_y" not in kwargs.keys():
        kwargs["x_y"] ="time_dtime"
    kwargs["width"] = 10
    sta_all_0 = sta_all.copy()
    sta_all_0.iloc[:,6:] = 0
    result = meteva.product.score_tdt(sta_all_0,meteva.method.sample_count,annot = -1,add_min_xticks = True
                                      ,**kwargs)
    if return_result:
        return result

def sample_id(sta_all,return_result = False,**kwargs):
    if "title" not in kwargs.keys():
        kwargs["title"] =  ["所有时间和时效样本数的空间分布"]
    sta_all_0 = sta_all.copy()
    sta_all_0.iloc[:,6:] = 0
    result = meteva.product.score_id(sta_all_0,meteva.method.sample_count,plot = "scatter",
                                    **kwargs)
    if return_result:
        return result
