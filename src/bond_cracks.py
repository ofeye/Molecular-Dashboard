import numpy as np
from scipy.spatial import cKDTree
from scripts.utils.file_utils import getDataS
from scripts.utils.key_generator import generate_key
from scripts.utils.file_utils import get_file_path, find_with_extension
from src.cache_manager import load_results, save_results
from multiprocessing import Pool, cpu_count

def process_timestep_data(timeStepData):
    atoms = []
    for line in timeStepData:
        if len(line) >= 5:
            atoms.append([int(line[0]), int(line[1]), float(line[2]), float(line[3]), float(line[4])])
    atoms = sorted(atoms, key=lambda x: x[0])
    return np.array(atoms)

def find_neighbors(positions, cutoff):
    tree = cKDTree(positions)
    return tree.query_ball_point(positions, cutoff)

def cracked_bonds(prev_bonds, now_bonds, now_positions):
    cracked_bond_coords = []
    for i, (prev_i, now_i) in enumerate(zip(prev_bonds, now_bonds)):
        bond_cnt_change = len(prev_i) - len(now_i)
        if (bond_cnt_change > 0) and (max(now_positions[i]) < 0.95) and (min(now_positions[i]) > 0.05):
            for _ in range(bond_cnt_change):
                cracked_bond_coords.append(now_positions[i])
    return cracked_bond_coords

def get_atom_data(surface1, surface2, a_val, h_perc, k_val, time_step, cutoff):
    folder_dir = get_file_path(surface1, surface2, a_val, h_perc, k_val)
    print()
    file_path = find_with_extension(folder_dir, 'lammpstrj')
    
    prev_timestep_data = getDataS(time_step - 1, file_path) if time_step > 1 else None
    now_timestep_data = getDataS(time_step, file_path)
    
    prev_atoms = process_timestep_data(prev_timestep_data) if prev_timestep_data else None
    now_atoms = process_timestep_data(now_timestep_data)
    
    prev_positions = prev_atoms[:, 2:5] if prev_atoms is not None else None
    now_positions = now_atoms[:, 2:5]
    
    prev_bonds = find_neighbors(prev_positions, cutoff) if prev_positions is not None else None
    now_bonds = find_neighbors(now_positions, cutoff)
    
    cracked_bond_coords = cracked_bonds(prev_bonds, now_bonds, now_positions) if prev_bonds is not None else []
    
    return now_positions, cracked_bond_coords

def get_atom_data_or_cache(surface1, surface2, a_val, h_perc, k_val, time_step, cutoff, force_recalculate=False):
    key = generate_key(surface1, surface2, a_val, h_perc, k_val, time_step)+f'_{str(cutoff).replace(".","")}'

    if not force_recalculate:
        results = load_results(key,'bond_crack')
        # print(results)
        if results is not None:
            return results
    # print('but you are here')
    now_positions, cracked_bond_coords = get_atom_data(surface1, surface2, a_val, h_perc, k_val, time_step, cutoff/(2*a_val))
    save_results(key, (now_positions, cracked_bond_coords),'bond_crack')
    return now_positions, cracked_bond_coords

def load_cache_parallel(keys, folder):
    with Pool(cpu_count()) as pool:
        results = pool.starmap(load_results, [(key, folder) for key in keys])
    return {key: result for key, result in zip(keys, results) if result is not None}

def get_atom_data_bulk(surface1, surface2, a_val, h_perc, k_val, time_steps, cutoff):
    results = {}
    for time_step in time_steps:
        key = generate_key(surface1, surface2, a_val, h_perc, k_val, time_step)+f'_{str(cutoff).replace(".","")}'
        now_positions, cracked_bond_coords = get_atom_data(surface1, surface2, a_val, h_perc, k_val, time_step, cutoff/(2*a_val))
        results[key] = (now_positions, cracked_bond_coords)
    return results

def get_atom_data_or_cache_bulk(surface1, surface2, a_val, h_perc, k_val, time_steps, cutoff):
    keys = [generate_key(surface1, surface2, a_val, h_perc, k_val, time_step)+f'_{str(cutoff).replace(".","")}' for time_step in time_steps]
    
    cached_results = load_cache_parallel(keys, 'bond_crack')
    
    missing_time_steps = [time_step for time_step in time_steps if generate_key(surface1, surface2, a_val, h_perc, k_val, time_step)+f'_{str(cutoff).replace(".","")}' not in cached_results]
    
    if missing_time_steps:
        new_results = get_atom_data_bulk(surface1, surface2, a_val, h_perc, k_val, missing_time_steps, cutoff)
        for key, value in new_results.items():
            save_results(key, value, 'bond_crack')
        cached_results.update(new_results)
    
    return cached_results