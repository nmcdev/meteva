para = {
    "fo_time_range": ["2019010108", "2019020108", "12h"],
    "dtime": [1, 2, 3, "h"],
    "station": {
        "path": r"F:\ppt\sta_alt_1w.txt"
    },
    "sample_must_be_same": True,
    "dim_type": [
        {
            "name": "dim_type_region",
            "type": "grid_data",
            "path": r"F:\ppt\sr.nc"
        },

    ],
    "observation": {
        "path": r"F:\ppt\ob\sta\rain01\BTYYMMDDHH.000",
        "valid": [0, 300],
    },
    "forecasts": [
        {
            "name": "持续预报",
            "type": "sta_data",
            "path": r"F:\ppt\ob\sta\rain01\BTYYMMDDHH.000",
            "fo_time_move_back": [0, 0.5, 1],
            "ob_time_need_be_same": False,
        },
        {
            "name": "定时预报",
            "type": "grid_data",
            "path": r"F:\ppt\nmczhidao\grid\RAIN01\YYMMDD\YYMMDDHH.TTT.nc",
            "fo_time_move_back": [0, 12.5, 1],
            "ob_time_need_be_same": True,
        },
        {
            "name": "Grapes_3km",
            "type": "grid_data",
            "path": r"F:\ppt\grapes_3km\grid\rain01\BTYYMMDDHH.TTT.nc",
            "fo_time_move_back": [0, 12.5, 1],
            "ob_time_need_be_same": True,
        },
        {
            "name": "华东中尺度",
            "type": "grid_data",
            "path": r"F:\ppt\shanghai\grid\rain01\BTYYMMDDHH.TTT.nc",
            "fo_time_move_back": [0, 12.5, 1],
            "ob_time_need_be_same": True,
        },
        {
            "name": "临近外推",
            "type": "grid_data",
            "path": r"F:\ppt\nowcast\grid\rain01\BTYYMMDDHH.TTT.nc",
            "fo_time_move_back": [0, 0.5, 1],
            "ob_time_need_be_same": True,
        },
        {
            "name": "滚动更新",
            "type": "grid_data",
            "path": r"F:\ppt\nmcgundong\grid\rain01\BTYYMMDDHH.TTT.nc",
            "fo_time_move_back": [0, 0.5, 1],
            "ob_time_need_be_same": True,
        }

    ],
    "group_set": {
        "level": "fold",
        "time": "fold",
        "year": 'unfold',
        "month": {'group': [[1]],
                  'group_name': [['1月']]},
        "xun": 'fold',
        "hou": 'fold',
        "day": {'group': [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12, 13]],
                'group_name': [['1d', '2d', '3d', '4d', '5d', '6d'], ['7d', '8d', '9d', '10d', '11d', '12d', '13d']]},
        "hour": "fold",
        "dtime": {'group': [[1, 2], [3]],
                  'group_name': [['1h', '2h'], ['3h']]
                  },
        "id": "fold",
        "dim_type_region": {
            "group": [[1], [2], [3], [4], [5], [6], [7]],
            "group_name": [["新疆"], ["西北中东部"], ["华北"], ["东北"], ["黄淮江淮江南"], ["华南"], ["西南"]],
        },

    },
    "veri_set": [
        {
            "name": "ts_bias",
            "method": ["ts", "bias"],
            "para1": [0.1, 5, 10, 20],
            "para1Name": ["小雨", ">=5毫米", ">=10毫米", ">=20毫米"],
            "plot_type": "bar"
        },

        {
            "name": "pc_sun_rain",
            "method": ["pc"],
            "plot_type": "bar"
        },
        {
            "name": "me_mae_mse_rmse",
            "method": ["me", 'mae', 'mse', 'rmse'],
            "plot_type": "bar"
        }
    ],
    "plot_set": {
        "subplot": "vmethod",
        "legend": "member",
        "axis": "dim_type_region"
    },
    "save_dir": r"F:\veri_result\p8new"
}
