import os
from datetime import datetime
import numpy as np

def read_micaps14(fname,time = None,dtime = None,data_name = None):
    """
    Read micaps 14 file (编辑图象的图元数据, 即交互操作结果数据).
    :param fname: micaps 14 filename.
    :return: data dictionary
    :Examples:
    #>>> data = read_micaps_14("Z:/diamond/update/rr082008.024")
    """

    # check file exist
    if not os.path.isfile(fname):
        return None

    # read contents
    encodings = ['utf-8', 'gb18030', 'GBK']
    txt = None
    for encoding in encodings:
        txt = None
        try:
            with open(fname, 'r', encoding=encoding) as f:
                txt = f.read().replace('\n', ' ').split()
        except Exception:
            pass
    if txt is None:
        print("Micaps 14 file error: " + fname)
        return None

    # head information
    _ = txt[2]

    # date and time

    if time is None:
        year = int(txt[3]) if len(txt[3]) == 4 else int(txt[3]) + 2000
        month = int(txt[4])
        day = int(txt[5])
        hour = int(txt[6])
        time = datetime(year, month, day, hour)
    fhour = int(txt[7])

    # ======================================================
    # read lines
    # ======================================================
    lines = None
    if 'LINES:' in txt:
        # get the start position
        idx = txt.index('LINES:')

        # number of lines
        number = int(txt[idx+1])
        idx += 2

        # loop every line
        if number > 0:
            # define data
            line_width = []
            line_xyz_num = []
            line_xyz = []
            line_label_num = []
            line_label = []
            line_label_xyz = []

            for _ in range(number):
                # line width
                width = float(txt[idx])
                line_width.append(width)
                idx += 1

                # line xyz point number
                xyz_num = int(txt[idx])
                line_xyz_num.append(xyz_num)
                idx += 1

                # line xyz
                xyz = np.array(txt[idx:(idx + 3*xyz_num)]).astype(np.float)
                xyz.shape = [xyz_num, 3]
                line_xyz.append(xyz)
                idx += xyz_num * 3

                # line label
                label = txt[idx]
                line_label.append(label)
                idx += 1

                # line label number
                label_num = int(txt[idx])
                line_label_num.append(label_num)
                idx += 1

                # label xyz
                if label_num > 0:
                    label_xyz = np.array(
                        txt[idx:(idx + 3*label_num)]).astype(np.float)
                    label_xyz.shape = [label_num, 3]
                    line_label_xyz.append(label_xyz)
                    idx += label_num * 3
                else:
                    line_label_xyz.append([])

                # construct line data type
                lines = {
                    "line_width": line_width, "line_xyz_num": line_xyz_num,
                    "line_xyz": line_xyz, "line_label_num": line_label_num,
                    "line_label": line_label, "line_label_xyz": line_label_xyz}

    # ======================================================
    # read line symbols
    # ======================================================
    lines_symbol = None
    if 'LINES_SYMBOL:' in txt:
        # get the start position
        idx = txt.index('LINES_SYMBOL:')

        # number of line symbols
        number = int(txt[idx + 1])
        idx += 2

        # loop every line symbol
        if number > 0:
            # define data
            linesym_code = []
            linesym_width = []
            linesym_xyz_num = []
            linesym_xyz = []

            for _ in range(number):
                # line symbol code
                code = int(txt[idx])
                linesym_code.append(code)
                idx += 1

                # line width
                width = float(txt[idx])
                linesym_width.append(width)
                idx += 1

                # line symbol xyz point number
                xyz_num = int(txt[idx])
                linesym_xyz_num.append(xyz_num)
                idx += 1

                # line symbol xyz
                xyz = np.array(txt[idx:(idx + 3*xyz_num)]).astype(np.float)
                xyz.shape = [xyz_num, 3]
                linesym_xyz.append(xyz)
                idx += xyz_num * 3

                # line symbol label
                label = txt[idx]
                idx += 1

                # line symbol label number
                label_num = int(txt[idx])
                idx += label_num * 3 + 1

            lines_symbol = {"linesym_code": linesym_code,
                            "linesym_width": linesym_width,
                            "linesym_xyz_num": linesym_xyz_num,
                            "linesym_xyz": linesym_xyz}

    # ======================================================
    # read symbol
    # ======================================================
    symbols = None
    if "SYMBOLS:" in txt:
        # start position of symbols
        idx = txt.index("SYMBOLS:")

        # number of lines
        number = int(txt[idx + 1])
        idx += 2

        # loop every symbol
        if number > 0:
            # define data
            symbol_code = []
            symbol_xyz = []
            symbol_value = []

            for _ in range(number):
                # symbol code
                code = int(txt[idx])
                symbol_code.append(code)
                idx += 1

                # symbol xyz
                xyz = np.array(txt[idx:(idx + 3)]).astype(np.float)
                symbol_xyz.append(xyz)
                idx += 3

                # symbol value
                value = txt[idx]
                symbol_value.append(value)
                idx += 1

            symbols = {"symbol_code": symbol_code,
                       "symbol_xyz": symbol_xyz,
                       "symbol_value": symbol_value}

    # ======================================================
    # read closed contours
    # ======================================================
    closed_contours = None
    if "CLOSED_CONTOURS:" in txt:
        # get the start position
        idx = txt.index('CLOSED_CONTOURS:')

        # number of lines
        number = int(txt[idx + 1])
        idx += 2

        # loop every closed contour
        if number > 0:
            # define data
            cn_width = []
            cn_xyz_num = []
            cn_xyz = []
            cn_label_num = []
            cn_label = []
            cn_label_xyz = []

            for _ in range(number):
                # line width
                width = float(txt[idx])
                cn_width.append(width)
                idx += 1

                # line xyz point number
                xyz_num = int(txt[idx])
                cn_xyz_num.append(xyz_num)
                idx += 1

                # line xyz
                xyz = np.array(txt[idx:(idx + 3 * xyz_num)]).astype(np.float)
                xyz.shape = [xyz_num, 3]
                cn_xyz.append(xyz)
                idx += 3 * xyz_num

                # line label
                label = txt[idx]
                cn_label.append(label)
                idx += 1

                # line label number
                label_num = int(txt[idx])
                cn_label_num.append(label_num)
                idx += 1

                # label xyz
                if label_num > 0:
                    label_xyz = np.array(
                        txt[idx:(idx + 3 * label_num)]).astype(np.float)
                    label_xyz.shape = [3, label_num]
                    cn_label_xyz.append(label_xyz)
                    idx += label_num * 3
                else:
                    cn_label_xyz.append([])

            closed_contours = {
                "cn_width": cn_width, "cn_xyz_num": cn_xyz_num,
                "cn_xyz": cn_xyz, "cn_label": cn_label,
                "cn_label_num": cn_label_num, "cn_label_xyz": cn_label_xyz}

    # ======================================================
    # read station situation
    # ======================================================
    stations = None
    if "STATION_SITUATION" in txt:
        # get the start position
        idx = txt.index('STATION_SITUATION')

        # find data subscript
        end_idx = idx + 1
        while end_idx < len(txt):
            if txt[end_idx].isdigit():
                end_idx += 1
            else:
                try:
                    f = float(txt[end_idx])
                    end_idx += 1
                except:
                    break

        if end_idx > idx + 1:
            stations = np.array(txt[(idx+1):(end_idx)])
            stations.shape = [len(stations)//2, 2]

    # ======================================================
    # read weather regions
    # ======================================================
    weather_region = None
    if "WEATHER_REGION:" in txt:
        # get the start position
        idx = txt.index('WEATHER_REGION:')

        # number of regions
        number = int(txt[idx + 1])
        idx += 2

        # loop every region
        if number > 0:
            # define data
            weather_region_code = []
            weather_region_xyz_num = []
            weather_region_xyz = []

            for _ in range(number):
                # region code
                code = int(txt[idx])
                weather_region_code.append(code)
                idx += 1

                # region xyz point number
                xyz_num = int(txt[idx])
                weather_region_xyz_num.append(xyz_num)
                idx += 1

                # region xyz point
                xyz = np.array(
                    txt[idx:(idx + 3*xyz_num)]).astype(np.float)
                xyz.shape = [xyz_num, 3]
                weather_region_xyz.append(xyz)
                idx += 3 * xyz_num

            weather_region = {
                "weather_region_code": weather_region_code,
                "weather_region_xyz_num": weather_region_xyz_num,
                "weather_region_xyz": weather_region_xyz}

    # ======================================================
    # read fill area
    # ======================================================
    fill_area = None
    if "FILLAREA:" in txt:
        # get the start position
        idx = txt.index('FILLAREA:')

        # number of regions
        number = int(txt[idx + 1])
        idx += 2

        # loop every fill area
        if number > 0:
            # define data
            fillarea_code = []
            fillarea_num = []
            fillarea_xyz = []
            fillarea_type = []
            fillarea_color = []
            fillarea_frontcolor = []
            fillarea_backcolor = []
            fillarea_gradient_angle = []
            fillarea_graphics_type = []
            fillarea_frame = []

            for _ in range(number):
                # code
                code = int(txt[idx])
                fillarea_code.append(code)
                idx += 1

                # xyz point number
                xyz_num = int(txt[idx])
                fillarea_num.append(xyz_num)
                idx += 1

                # xyz point
                xyz = np.array(
                    txt[idx:(idx + 3 * xyz_num)]).astype(np.float)
                xyz.shape = [xyz_num, 3]
                fillarea_xyz.append(xyz)
                idx += 3 * xyz_num

                # fill type
                ftype = int(txt[idx])
                fillarea_type.append(ftype)
                idx += 1

                # line color
                color = np.array(txt[idx:(idx + 4)]).astype(np.int)
                fillarea_color.append(color)
                idx += 4

                # front color
                front_color = np.array(txt[idx:(idx + 4)]).astype(np.int)
                fillarea_frontcolor.append(front_color)
                idx += 4

                # background color
                back_color = np.array(txt[idx:(idx + 4)]).astype(np.int)
                fillarea_backcolor.append(back_color)
                idx += 4

                # color gradient angle
                gradient_angle = float(txt[idx])
                fillarea_gradient_angle.append(gradient_angle)
                idx += 1

                # graphics type
                graphics_type = int(txt[idx])
                fillarea_graphics_type.append(graphics_type)
                idx += 1

                # draw frame or not
                frame = int(txt[idx])
                fillarea_frame.append(frame)
                idx += 1

            fill_area = {
                "fillarea_code": fillarea_code, "fillarea_num": fillarea_num,
                "fillarea_xyz": fillarea_xyz, "fillarea_type": fillarea_type,
                "fillarea_color": fillarea_color,
                "fillarea_frontcolor": fillarea_frontcolor,
                "fillarea_backcolor": fillarea_backcolor,
                "fillarea_gradient_angle": fillarea_gradient_angle,
                "fillarea_graphics_type": fillarea_graphics_type,
                "fillarea_frame": fillarea_frame}

    # ======================================================
    # read notes symbol
    # ======================================================
    notes_symbol = None
    if "NOTES_SYMBOL:" in txt:
        # get the start position
        idx = txt.index('NOTES_SYMBOL:')

        # number of regions
        number = int(txt[idx + 1])
        idx += 2

        # loop every notes symbol
        if number > 0:
            # define data
            nsymbol_code = []
            nsymbol_xyz = []
            nsymbol_charLen = []
            nsymbol_char = []
            nsymbol_angle = []
            nsymbol_fontLen = []
            nsymbol_fontName = []
            nsymbol_fontSize = []
            nsymbol_fontType = []
            nsymbol_color = []

            for _ in range(number):
                # code
                code = int(txt[idx])
                nsymbol_code.append(code)
                idx += 1

                # xyz
                xyz = np.array(txt[idx:(idx + 3)]).astype(np.float)
                nsymbol_xyz.append([xyz])
                idx += 3

                # character length
                char_len = int(txt[idx])
                nsymbol_charLen.append(char_len)
                idx += 1

                # characters
                char = txt[idx]
                nsymbol_char.append(char)
                idx += 1

                # character angle
                angle = txt[idx]
                nsymbol_angle.append(angle)
                idx += 1

                # font length
                font_len = txt[idx]
                nsymbol_fontLen.append(font_len)
                idx += 1

                # font name
                font_name = txt[idx]
                nsymbol_fontName.append(font_name)
                idx += 1

                # font size
                font_size = txt[idx]
                nsymbol_fontSize.append(font_size)
                idx += 1

                # font type
                font_type = txt[idx]
                nsymbol_fontType.append(font_type)
                idx += 1

                # color
                color = np.array(txt[idx:(idx + 4)]).astype(np.int)
                nsymbol_color.append(color)
                idx += 4

            notes_symbol = {
                "nsymbol_code": nsymbol_code,
                "nsymbol_xyz": nsymbol_xyz,
                "nsymbol_charLen": nsymbol_charLen,
                "nsymbol_char": nsymbol_char,
                "nsymbol_angle": nsymbol_angle,
                "nsymbol_fontLen": nsymbol_fontLen,
                "nsymbol_fontName": nsymbol_fontName,
                "nsymbol_fontSize": nsymbol_fontSize,
                "nsymbol_fontType": nsymbol_fontType,
                "nsymbol_color": nsymbol_color}

    # ======================================================
    # read lines symbols with property
    # ======================================================
    plines_symbol = None
    if "WITHPROP_LINESYMBOLS:" in txt:
        # get the start position
        idx = txt.index('WITHPROP_LINESYMBOLS:')

        # number of regions
        number = int(txt[idx + 1])
        idx += 2

        # loop every line symbol
        if number > 0:
            # define data
            plinesym_code = []
            plinesym_width = []
            plinesym_color = []
            plinesym_type = []
            plinesym_shadow = []
            plinesym_xyz_num = []
            plinesym_xyz = []
            plinesym_label = []
            plinesym_label_num = []
            plinesym_label_xyz = []

            for _ in range(number):
                # line symbol code
                code = int(txt[idx])
                plinesym_code.append(code)
                idx += 1

                # line width
                width = float(txt[idx])
                plinesym_width.append(width)
                idx += 1

                # line color
                color = np.array(txt[idx:(idx + 3)]).astype(np.int)
                plinesym_color.append([color])
                idx += 3

                # line type
                ltype = int(txt[idx])
                plinesym_type.append(ltype)
                idx += 1

                # line shadow
                shadow = int(txt[idx])
                plinesym_shadow.append(shadow)
                idx += 1

                # line symbol xyz point number
                xyz_num = int(txt[idx])
                plinesym_xyz_num.append(xyz_num)
                idx += 1

                # line symbol xyz
                xyz = np.array(txt[idx:(idx + 3 * xyz_num)]).astype(np.float)
                xyz.shape = [xyz_num, 3]
                plinesym_xyz.append(xyz)
                idx += 3 * xyz_num

                # line symbol label
                label = txt[idx]
                plinesym_label.append(label)
                idx += 1

                # line label number
                label_num = int(txt[idx])
                plinesym_label_num.append(label_num)
                idx += 1

                # label xyz
                if label_num > 0:
                    label_xyz = np.array(
                        txt[idx:(idx + 3 * label_num)]).astype(np.float)
                    label_xyz.shape = [label_num, 3]
                    plinesym_label_xyz.append(label_xyz)
                    idx += label_num * 3
                else:
                    plinesym_label_xyz.append([])

            plines_symbol = {
                "plinesym_code": plinesym_code,
                "plinesym_width": plinesym_width,
                "plinesym_color": plinesym_color,
                "plinesym_type": plinesym_type,
                "plinesym_shadow": plinesym_shadow,
                "plinesym_xyz_num": plinesym_xyz_num,
                "plinesym_xyz": plinesym_xyz,
                "plinesym_label": plinesym_label,
                "plinesym_label_num": plinesym_label_num,
                "plinesym_label_xyz": plinesym_label_xyz}

    # return data contents
    return {"file_type": 14,
            "time": time,
            "fhour": fhour,
            "lines": lines,
            "lines_symbol": lines_symbol,
            "symbols": symbols,
            "closed_contours": closed_contours,
            "stations": stations,
            "weather_region": weather_region,
            "fill_area": fill_area,
            "notes_symbol": notes_symbol,
            "plines_symbol": plines_symbol,
            "dtime":dtime,
            "data_name":data_name}
