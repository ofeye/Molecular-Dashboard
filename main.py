import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.getcwd())
from src.save_mean_curvature import save_mean_curvature_xy_plot, save_multiple_mean_curvature_xy_plots

from app import get_app

if __name__ == '__main__':
    get_app().run_server(debug=True)
    # save_multiple_mean_curvature_xy_plots(
    #     ['primitive'], ['gyroid'], 
    #     [50], [50], 
    #     [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 
    #     [100],  # Increased grid size
    #     'mean_curvature_xy_plot.png', 
    #     colorize='Abs',  # Changed from 'Abs' to 'Real'
    #     legend_min= 0,  # Set a fixed range for the color scale
    #     legend_max= 5
    # ) 