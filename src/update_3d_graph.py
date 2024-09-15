

def update_3d_graph(n_clicks, view_mode, surface1, surface2, a_val, h_perc, k_val, grid_size, view, colorize, legend_min, legend_max, time_step, cutoff):
    if view_mode == 'curvature':
        surface, curvatures = get_or_calculate_tpms(surface1, surface2, a_val, h_perc, k_val, grid_size)
        
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
        
    elif view_mode == 'bond_crack':
        positions, cracked_bond_coords = get_atom_data_or_cache(surface1, surface2, a_val, h_perc, k_val, time_step, cutoff/(2*a_val))
                    
        # Create color array
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
    
    if view == 'XY':
        fig.update_layout(
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='data'
            ),
            title=f'TPMS Visualization: {surface1.capitalize()} + {surface2.capitalize()}',
            scene_camera=dict(
                up=dict(x=0, y=1e-5, z=0),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0, y=0, z=0.1)
            )
        )
    elif view == 'XZ':
        fig.update_layout(
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='data'
            ),
            title=f'TPMS Visualization: {surface1.capitalize()} + {surface2.capitalize()}',
            scene_camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0, y=0.1, z=0)
            )
        )
        
    elif view == 'YZ':
        fig.update_layout(
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='data'
            ),
            title=f'TPMS Visualization: {surface1.capitalize()} + {surface2.capitalize()}',
            scene_camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0.1, y=0, z=0)
            )
        )
    fig.layout.scene.camera.projection.type = "orthographic"
    return fig