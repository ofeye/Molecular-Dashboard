import sympy as sp
import numpy as np
from src.cache_manager import load_results, save_results
from scripts.utils.key_generator import generate_key
from pyvista import StructuredGrid
import plotly.graph_objs as go
from src.tpms_calculation import get_or_calculate_tpms
import plotly.subplots as sp
import math
import itertools

def save_mean_curvature_xy_plot(surface1, surface2, a_val, h_perc, k_val, grid_size, output_path, colorize='Real', legend_min=None, legend_max=None):
    # Get the surface and curvatures
    surface, curvatures = get_or_calculate_tpms(surface1, surface2, a_val, h_perc, k_val, grid_size)

    if colorize == 'Abs':
        curvatures = abs(curvatures)
        
    vertices = surface.points
    faces = surface.faces.reshape(-1, 4)[:, 1:4]            

    if colorize == 'Abs':
        curvatures = abs(curvatures)
    # Legend aralığını ayarla
    zmin = legend_min if legend_min is not None else min(curvatures)
    zmax = legend_max if legend_max is not None else max(curvatures)

    data_to_plot = curvatures  # Curvature verisini kullan
    colorbar_title = 'Mean Curvature'
    
    fig = go.Figure(data=[go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        intensity=data_to_plot,
        colorscale='Jet',
        opacity=1,
        colorbar=dict(title=colorbar_title),
        lighting=dict(ambient=0.6, diffuse=0.5, specular=0.1, fresnel=0.1),
        cmin=zmin,
        cmax=zmax,
        )])

    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'
        ),
        title=f'TPMS Visualization: {surface1.capitalize()} + {surface2.capitalize()}',
        scene_camera=dict(
            up=dict(x=0, y=1, z=0),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=0, z=2)
        )
    )
    fig.layout.scene.camera.projection.type = "orthographic"
    # Remove margins and maximize plot area
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        autosize=False,
        width=1000,
        height=1000
    )
    
    # Adjust camera view to fill the frame
    fig.update_layout(
        scene=dict(
            camera=dict(
                eye=dict(x=0, y=0, z=1.5)
            ),
            aspectratio=dict(x=1, y=1, z=1)
        )
    )
    # Remove axis, background grid, and color
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)'
    )

    fig.write_image(output_path, format='png')

def save_multiple_mean_curvature_xy_plots(surface1_list, surface2_list, a_val_list, h_perc_list, k_val_list, grid_size_list, output_path, colorize='Real', legend_min=None, legend_max=None):
    # Generate all combinations of parameters
    all_combinations = list(itertools.product(surface1_list, surface2_list, a_val_list, h_perc_list, k_val_list, grid_size_list))
    
    num_plots = len(all_combinations)
    rows = math.ceil(math.sqrt(num_plots))
    cols = math.ceil(num_plots / rows)

    fig = sp.make_subplots(rows=rows, cols=cols, specs=[[{'type': 'scene'}]*cols]*rows,
                           subplot_titles=[f"{s1.capitalize()} + {s2.capitalize()}, a={a}, h={h}, k={k}, grid={g}" 
                                           for s1, s2, a, h, k, g in all_combinations],
                           horizontal_spacing=0.02, vertical_spacing=0.02)

    # Calculate global minimum and maximum curvatures
    global_min_curvature = float('inf')
    global_max_curvature = float('-inf')
    for params in all_combinations:
        surface1, surface2, a_val, h_perc, k_val, grid_size = params
        _, curvatures = get_or_calculate_tpms(surface1, surface2, a_val, h_perc, k_val, grid_size)
        if colorize == 'Abs':
            curvatures = np.abs(curvatures)
        global_min_curvature = min(global_min_curvature, np.min(curvatures))
        global_max_curvature = max(global_max_curvature, np.max(curvatures))
        
    print(f"Global curvature range: {global_min_curvature} to {global_max_curvature}")  
    zmin = legend_min if legend_min is not None else global_min_curvature
    zmax = legend_max if legend_max is not None else global_max_curvature
    print(f"Global curvature range: {zmin} to {zmax}")

    for i, params in enumerate(all_combinations):
        surface1, surface2, a_val, h_perc, k_val, grid_size = params
        surface, curvatures = get_or_calculate_tpms(surface1, surface2, a_val, h_perc, k_val, grid_size)

        if colorize == 'Abs':
            curvatures = np.abs(curvatures)
        
        print(f"Curvature range for plot {i+1}: {np.min(curvatures)} to {np.max(curvatures)}")
        vertices = surface.points
        faces = surface.faces.reshape(-1, 4)[:, 1:4]            

        row = i // cols + 1
        col = i % cols + 1

        mesh = go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            intensity=curvatures,
            colorscale='Jet',
            opacity=1,
            colorbar=dict(title='Mean Curvature', len=0.8, thickness=20, x=1.02, tickfont=dict(size=50), titlefont=dict(size=16)),
            lighting=dict(ambient=0.6, diffuse=0.5, specular=0.1, fresnel=0.1),
            cmin=zmin,
            cmax=zmax,
            # showscale=(i == 0)  # Only show colorbar for the first plot
        )

        fig.add_trace(mesh, row=row, col=col)
        fig.update_scenes(
            camera_projection_type="orthographic",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(
                up=dict(x=0, y=1, z=0),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0, y=0, z=1.5)
            ),
            aspectmode='data',
            aspectratio=dict(x=1, y=1, z=1),
            bgcolor='rgba(0,0,0,0)',
            row=row, col=col
        )

    fig.update_layout(
        height=1200*rows,
        width=1200*cols,
        title_text="Multiple TPMS Visualizations",
        title_font=dict(size=24),
        showlegend=False,
        margin=dict(l=0, r=100, t=50, b=0),
        paper_bgcolor='rgba(255,255,255,1)'
    )

    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=14)
        annotation['y'] = annotation['y'] + 0.03  # Move the title slightly up

    fig.write_image(output_path, format='png', scale=2)