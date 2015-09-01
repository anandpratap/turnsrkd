import numpy as np

def phi_quad(d, r): return np.sqrt(d*d + r*r)
def phi_quad_inv(d, r): return 1./np.sqrt(d*d + r*r)
def thin_plate(d, r): return d*d*np.log(d + 1E-20)
def phi_gauss(d, r): return np.exp(-d*d/(r*r))

def calc_rbf(x, y, x_nodes, y_nodes, r_nodes, w_nodes, func=phi_gauss):
    beta_rbf = np.ones_like(x)
    n_nodes = np.size(x_nodes)
    for i in range(n_nodes):
        d = np.sqrt((x - x_nodes[i])**2 + (y - y_nodes[i])**2)
        beta_rbf = beta_rbf + func(d, r_nodes[i])*w_nodes[i]
    return beta_rbf


def calc_kernel(x, y, x_node, y_node, r_node,func=phi_gauss):
    d = np.sqrt((x - x_node)**2 + (y - y_node)**2)
    return func(d, r_node)
