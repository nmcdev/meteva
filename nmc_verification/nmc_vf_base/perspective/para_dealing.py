
class plot_group:
    picture = "picture"
    subplot = "subplot"
    legend = "legend"
    axis_x = "axis_x"


class data_para:
    def __init__(self):
        self.level = "fold"
        self.time = "fold"
        self.year = "fold"
        self.month = "fold"
        self.xun = "fold"
        self.hou = "fold"
        self.day = "fold"
        self.hour = "fold"
        self.dtime = "fold"
        self.dhour = "fold"
        self.dday = "fold"
        self.id = "fold"
        self.lon = "fold"
        self.lat = "fold"
        self.alt = "fold"

    def set_level_unfold(self):
        self.level = "unfold"

    def set_time_unfold(self):
        self.time = "unfold"

    def set_year_unfold(self):
        self.time = "fold"
        self.year = "unfold"

    def set_month_unfold(self):
        self.time = "fold"
        self.month = "unfold"

    def set_xun_unfold(self):
        self.time = "fold"
        self.xun = "unfold"

    def set_hou_unfold(self):
        self.time = "fold"
        self.hou = "unfold"

    def set_day_unfold(self):
        self.time = "fold"
        self.day = "unfold"

    def set_hour_unfold(self):
        self.time = "fold"
        self.hour = "unfold"

    def set_dtime_unfold(self):
        self.dtime = "unfold"

    def set_dhour_unfold(self):
        self.dtime = "fold"
        self.dhour = "unfold"

    def set_dday_unfold(self):
        self.dtime = "fold"
        self.dday = "unfold"

    def set_id_unfold(self):
        self.id = "unfold"

    def set_lon_unfold(self,dlon,slon = 0):
        self.lon = "unfold"

    def set_lat_unfold(self,dlat,slat = 0):
        self.lat = "unfold"

    def set_alt_unfold(self,dalt,alt = 0):
        self.alt = "unfold"
