from concurrent.futures import ThreadPoolExecutor
import plotly.graph_objs as go
from src.bond_cracks import get_atom_data_or_cache
from src.cache_manager import load_results, save_results
from scripts.utils.file_utils import get_file_path, find_with_extension
import threading

# Thread-safe executor
executor = ThreadPoolExecutor(max_workers=3)

def create_and_cache_figure(surface1, surface2, a_val, h_perc, k_val, time_step, cutoff):
    key = f"figure_{surface1}_{surface2}_{a_val}_{h_perc}_{k_val}_{time_step}_{cutoff}"
    
    # Check if figure is already in cache
    cached_figure = load_results(key, 'bond_crack_figures')
    if cached_figure is not None:
        return go.Figure(cached_figure)
    
    # If not in cache, create the figure
    positions, cracked_bond_coords = get_atom_data_or_cache(surface1, surface2, a_val, h_perc, k_val, time_step, cutoff)
    
    colors = ['red' if tuple(pos) not in [tuple(c) for c in cracked_bond_coords] else 'blue' for pos in positions]
    sizes = [3 if tuple(pos) not in [tuple(c) for c in cracked_bond_coords] else 7 for pos in positions]

    fig = go.Figure(data=[go.Scatter3d(
        x=positions[:, 0],
        y=positions[:, 1],
        z=positions[:, 2],
        mode='markers',
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.5
        ),
        text=[f"Atom at {tuple(pos)}: {'Cracked' if tuple(pos) in [tuple(c) for c in cracked_bond_coords] else 'Normal'}" for pos in positions],
        hoverinfo='text'
    )])
    
    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='cube'
        ),
        yaxis=dict(range=[0, 1]),
        xaxis=dict(range=[0, 1]),
        title=f'Atom Visualization (Time Step: {time_step})'
    )
    
    # Cache the figure in a separate thread
    threading.Thread(target=save_results, args=(key, fig.to_dict(), 'bond_crack_figures')).start()
    
    return fig

def preload_model_cache(surface1, surface2, a_val, h_perc, k_val, cutoff, time_step):
    folder_dir = get_file_path(surface1, surface2, a_val, h_perc, k_val)
    file_path = find_with_extension(folder_dir, 'lammpstrj')
    
    with open(file_path, 'r') as f:
        time_steps = sum(1 for line in f if 'ITEM: TIMESTEP' in line)
    
    for ts in [x for x in (time_step-1, time_step, time_step+1) if 0 <= x <= time_steps]:
        executor.submit(create_and_cache_figure, surface1, surface2, a_val, h_perc, k_val, ts, cutoff)

def update_3d_graph_bond_crack(surface1, surface2, a_val, h_perc, k_val, time_step, cutoff):
    # Start preloading in the background
    threading.Thread(target=preload_model_cache, args=(surface1, surface2, a_val, h_perc, k_val, cutoff, time_step)).start()
    
    # Get or create the figure for the current time step
    return create_and_cache_figure(surface1, surface2, a_val, h_perc, k_val, time_step, cutoff)