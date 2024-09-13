import pandas as pd
import json


def highlighted_mask(df_filtered, surface1, surface2, a_val, h_perc, k_val):
    with open('data/json/surf_dict.json', 'r') as json_file:
        surf_dict = json.load(json_file)

    if surface1 == surface2: 
        surface2 = list(surf_dict.keys())[list(surf_dict.keys())!=surface1]
        k_val = 0
    
    # Highlight the selected model
    return (
        (df_filtered['Geom1'] == surf_dict[surface1]) &
        (df_filtered['Geom2'] == surf_dict[surface2]) &
        (df_filtered['length'] == a_val) &
        (df_filtered['Hybrid_Perc'] == h_perc) &
        (df_filtered['k_Value'] == k_val)
    )