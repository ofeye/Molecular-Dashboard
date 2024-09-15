import sympy as sp
import numpy as np
from os import chdir, path
from src.cache_manager import load_results, save_results
from scripts.utils.key_generator import generate_key
from pyvista import StructuredGrid


def calculate_tpms_function(surface1, surface2, a_val, h_perc, k_val):
    x, y, z, a,hlen, k = sp.symbols('x y z a hlen k')

    F_gyroid = sp.sin(2 * sp.pi * x / a) * sp.cos(2 * sp.pi * y / a) + \
            sp.sin(2 * sp.pi * y / a) * sp.cos(2 * sp.pi * z / a) + \
            sp.sin(2 * sp.pi * z / a) * sp.cos(2 * sp.pi * x / a)

    F_diamond = sp.sin(2 * sp.pi * x / a) * sp.sin(2 * sp.pi * y / a) * sp.sin(2 * sp.pi * z / a) + \
                sp.sin(2 * sp.pi * x / a) * sp.cos(2 * sp.pi * y / a) * sp.cos(2 * sp.pi * z / a) + \
                sp.cos(2 * sp.pi * x / a) * sp.sin(2 * sp.pi * y / a) * sp.cos(2 * sp.pi * z / a) + \
                sp.cos(2 * sp.pi * x / a) * sp.cos(2 * sp.pi * y / a) * sp.sin(2 * sp.pi * z / a)
    
    F_primitive = sp.cos(2 * sp.pi * x / a) + sp.cos(2 * sp.pi * y / a) + sp.cos(2 * sp.pi * z / a)

    weight1 = (1 / (1 + sp.exp(k * ((hlen/2) + x)))) + (1 / (1 + sp.exp(k * ((hlen/2) - x))))
    weight2 = 1 - weight1

    func_Dict = {
        'gyroid': F_gyroid,
        'diamond': F_diamond,
        'primitive': F_primitive
    }

    GeneralFunc = sp.simplify(weight1 * func_Dict[surface1] + weight2 * func_Dict[surface2])
    F = sp.simplify(GeneralFunc.evalf(subs={a: a_val, hlen: h_perc*a_val//100 , k: k_val}))
    F_func = sp.lambdify((x, y, z), F, 'numpy')
    return F,F_func


def calculate_tpms_curvfunc(F):
    x, y, z, a,hlen, k = sp.symbols('x y z a hlen k')
    
    grad_F = sp.Matrix([sp.diff(F, x), sp.diff(F, y), sp.diff(F, z)])
    grad_F_norm = sp.sqrt(grad_F.dot(grad_F))
    Hessian_F = sp.hessian(F, (x, y, z))
    normal = grad_F / grad_F_norm
    shape_operator = (sp.eye(3) - normal * normal.T) * Hessian_F / grad_F_norm
    Mean_curvature = shape_operator.trace() / 2

    return sp.lambdify((x, y, z), Mean_curvature, 'numpy')

def get_surface_and_curvatures(surface1, surface2, a_val, h_perc, k_val, grid_size):

    F, F_func = calculate_tpms_function(surface1, surface2, a_val, h_perc, k_val)
    mean_curvature_func = calculate_tpms_curvfunc(F)
    
    limit = a_val / 2
    x_ = np.linspace(-limit, limit, grid_size)
    y_ = np.linspace(-limit, limit, grid_size)
    z_ = np.linspace(-limit, limit, grid_size)
    X, Y, Z = np.meshgrid(x_, y_, z_)

    F_values = F_func(X, Y, Z)

    grid = StructuredGrid(X, Y, Z)
    grid.point_data["values"] = F_values.ravel(order="F")
    surface = grid.contour(isosurfaces=[0])
    
    curvatures = mean_curvature_func(surface.points[:, 0], surface.points[:, 1], surface.points[:, 2])
    curvatures = np.nan_to_num(curvatures, nan=0.0)
    
    return surface, curvatures

def get_or_calculate_tpms(surface1, surface2, a_val, h_perc, k_val, grid_size, force_recalculate=False):
    key = generate_key(surface1, surface2, a_val, h_perc, k_val, grid_size)
    
    if not force_recalculate:
        results = load_results(key,'curv_and_surfs')
        if results is not None:
            return results

    surface, curvatures = get_surface_and_curvatures(surface1, surface2, a_val, h_perc, k_val, grid_size)
    save_results(key, (surface, curvatures),'curv_and_surfs')
    return surface, curvatures

