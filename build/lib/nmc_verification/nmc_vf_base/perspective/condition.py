
class plot_group:
    picture = "picture"
    subplot = "subplot"
    legend = "legend"
    axis_x = "axis_x"

def get_default_condition():
    condition ={
        "level":"fold",
        "time": "fold",
        "year": "unfold",
        "month":"fold",
        "xun": "fold",
        "hou": "fold",
        "day":"fold",
        "hour":"fold",
        "dt":"fold",
        "dh_hour":"fold",
        "dh_day":"fold",
        "id":"fold",
        "lon":"fold",
        "lat":"fold",
        "alt":"fold",
    }
    return condition
