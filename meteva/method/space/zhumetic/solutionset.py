def solutionset(envir, **args):

    W = {
        'type': 'mask',
        'xrange': envir['xrange'],
        'yrange': envir['yrange'],
        'dim': envir['dim'],
        'xstep': envir['xstep'],
        'ystep': envir['ystep'],
        'warnings': ["Row index corresponds to increasing y coordinate; column to increasing x",
                    "Transpose matrices to get the standard presentation in R",
                    "Example: image(result$xcol,result$yrow,t(result$d))"],
        'xcol': envir['xcol'],
        'yrow': envir['yrow'],
        'm': envir['v'],
        'units': envir['units'],
    }
    return W