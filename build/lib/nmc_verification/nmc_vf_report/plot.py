import xarray as xr
import nmc_verification.nmc_vf_report.perspective.veri_plot_set as veri_plot_set

def vplot(veri_result,para_list,output_dir):
    dims = []
    coords = {}
    shape = []
    subplot = None
    axis = None
    legend = None
    for para in para_list:
        coord = para[-2]
        dims.append(coord)
        coords[coord] = para[0:-2]
        shape.append(len(coords[coord]))
        if para[-1] == "subplot":
            subplot = coord
        elif para[-1] == "axis":
            axis = coord
        elif para[-1] == "legend":
            legend = coord

    vr_xr = xr.DataArray(veri_result, coords=coords, dims=dims)
    print(vr_xr)
    vplot = veri_plot_set(subplot,legend,axis,output_dir)
    vplot.bar(vr_xr)