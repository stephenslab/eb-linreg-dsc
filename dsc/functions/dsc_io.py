def read_sim_input_params(dims, sfrac=0.5, sfix=None):
    n = dims[0]
    p = dims[1]
    if sfix is not None:
        s = sfix
    else:
        s = max(1, int(sfrac * p)) 
    return n, p, s
