import math


def update_data_plots(geom1, geom2, length, legend_category, surface1, surface2, a_val, h_perc, k_val):
    df_filtered = df.copy()
    
    filter_conditions = {
        "Geom1": geom1,
        "Geom2": geom2,
        "length": length
    }
    
    for column, value in filter_conditions.items():
        if value != "All":
            df_filtered = df_filtered[df_filtered[column] == value]
    
    highlight_mask = highlighted_mask(df_filtered, surface1, surface2, a_val, h_perc, k_val)
    df_filtered['highlight'] = highlight_mask
    
    colorMin = math.floor(min(df_filtered[legend_category]))
    colorMax = math.ceil(max(df_filtered[legend_category]))
    
    figure_configs = [
        ("Norm_Density", "Max_Stress", "Density[mg/cm<sup>3</sup>]", "Yield Strength [GPa]", True, True),
        ("Norm_Density", "Young_Modulus", "Density[mg/cm<sup>3</sup>]", "Young Modulus [GPa]", True, True),
        ("Norm_Density", "norm_dens_stress_geom1", "Density[mg/cm<sup>3</sup>]", "Normalized Yield Strength via Type-1", False, False),
        ("Norm_Density", "norm_dens_stress_geom2", "Density[mg/cm<sup>3</sup>]", "Normalized Yield Strength via Type-2", False, False),
        ("Norm_Density", "norm_dens_young_geom1", "Density[mg/cm<sup>3</sup>]", "Normalized Young Modulus via Type-1", False, False),
        ("Norm_Density", "norm_dens_young_geom2", "Density[mg/cm<sup>3</sup>]", "Normalized Young Modulus via Type-2", False, False),
        ("Norm_Density", "norm_dens_Ener_geom1", "Density[mg/cm<sup>3</sup>]", "Normalized Strain Energy via Type-1", False, False),
        ("Norm_Density", "norm_dens_Ener_geom2", "Density[mg/cm<sup>3</sup>]", "Normalized Strain Energy via Type-2", False, False)
    ]
    
    figures = []
    for x, y, x_title, y_title, use_trendline, use_log_scale in figure_configs:
        fig = create_figure(df_filtered, x, y, legend_category, use_trendline, use_log_scale)
        
        x_min, x_max = min(df[x]) * 0.9, max(df[x]) * 1.1
        y_min, y_max = min(df[y]) * 0.9, max(df[y]) * 1.1
        
        if y in ["Max_Stress", "Young_Modulus"]:
            x_min, x_max = my_floor_2(min(df[x]) * 0.9), my_ceil_2(max(df[x]) * 1.1)
            y_min, y_max = my_floor_2(min(df[y]) * 0.9), my_ceil_2(max(df[y]) * 1.1)
        
        update_figure_layout(fig, [x_min, x_max], [y_min, y_max], [colorMin, colorMax], x_title, y_title, use_log_scale)
        
        # Add highlighted points
        fig.add_trace(go.Scatter(
            x=df_filtered[highlight_mask][x],
            y=df_filtered[highlight_mask][y],
            mode='markers',
            marker=dict(size=15, color='red', symbol='star'),
            name='Selected Model'
        ))
        
        if y.startswith("norm_dens"):
            fig.add_shape(
                type='rect',
                y0=1, x0=0, y1=2, x1=1500,
                opacity=0.2, fillcolor='lightgreen', line=dict(width=0)
            )
        
        figures.append(fig)
    
    return tuple(figures)