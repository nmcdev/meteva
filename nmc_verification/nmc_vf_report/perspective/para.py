
para_whole = {
    "fo_time_range": ["2019060108", "2019060309", "3h"],
    "dtime":[3,6,9,12,18,21,24,"h"],
    "station":{
        "path": r"G:\ppt\sta_alt_1w.txt"
    },
    "dim_type":[
        {
            "name":"dim_type_region",
            "type": "grid_data",
            "path": r"G:\ppt\sr.nc"
        }
    ],
    "observation":{
        "path":r"G:\ppt\ob\sta\rain03\BTYYMMDDHH.000",
        "valid" :[0,1000],
    },
    "sample_must_be_same":True,
    "forecasts":[
        {
            "name": "Grapes_meso",
            "type": "grid_data",
            "path": r"G:\ppt\grapes_meso\grid\rain03\BTYYMMDDHH.TTT.nc",
            "fo_time_move_back":[12,12.5,1],
            "ob_time_need_be_same":True,
        },
    ],
    "group_set":{
        "level":"fold",
        "time":"fold",
        "year":"fold",
        "month":"fold",
        "xun":"fold",
        "hou":"fold",
        "day":"fold",
        "hour":{
            "group":[[8],[11],[14],[17],[20],[23],[2],[5]]
        },
        "dtime":{
            "group":[[3],[6],[9],[12],[15],[18],[21],[24]],
            "group_name" : ["03h","06h","09h","12h","15h","18h","21h","24h"],
        },
        "id":"fold",
         "dim_type_region":{
            "group": [[1], [2], [3], [4], [5], [6], [7]],
            "group_name": ["新疆", "西北中东部", "华北", "东北", "黄淮江淮江南", "华南", "西南"],
         },
    },
    "veri_set":[
        {
            "name":"pc",
            "method":["ts","bias"],
            "para1":[0.1],
            "para1Name":["暴雨"],
            "plot_type":"line"
        }
    ],
    "plot_set":{
        "subplot": "vmethod",
        "legend":"member",
        "axis":"dtime"
    },
    "save_dir":r"G:\veri_result\p10"
}

para_group_set ={
    "dtime": {
        "group": [[3], [6], [9], [12], [15], [18], [21], [24]],
        "group_name": ["03h", "06h", "09h", "12h", "15h", "18h", "21h", "24h"],
    },
    "id": "fold",
    "dim_type_region": {
        "group": [[1], [2], [3], [4], [5], [6], [7]],
        "group_name": ["新疆", "西北中东部", "华北", "东北", "黄淮江淮江南", "华南", "西南"],
    },
}

para_dict_list_list ={
    "dtime": [[3], [6]],
    "dim_type_region": [[1], [2]],
}

para_list_dict_list ={
    {"dtime":[3],"dim_type_region":[1]},
    {"dtime":[3],"dim_type_region":[2]},
    {"dtime":[6],"dim_type_region":[1]},
    {"dtime":[6],"dim_type_region":[2]},
}

