import pandas as pd
import rpy2.robjects as robj
import rpy2.robjects.vectors as rvec
from rpy2.robjects.packages import importr 
from rpy2.robjects.conversion import localconverter
from rpy2.robjects import pandas2ri
pandas2ri.activate()

'''
A Python wrapper for the dscquery in R
'''
def dscquery(dsc_output, targets,
             conditions = None,
             verbose = True
            ):
    dscrutils    = importr('dscrutils')
    r_targets    = rvec.StrVector(targets)        if targets    is not None else robj.NULL
    r_conditions = rvec.StrVector(conditions)     if conditions is not None else robj.NULL

    dscoutr = dscrutils.dscquery(dsc_output, r_targets,
                                 conditions = r_conditions, 
                                 verbose = verbose)

    with localconverter(robj.default_converter + pandas2ri.converter):
        dscout = robj.conversion.rpy2py(dscoutr)

    return dscout
