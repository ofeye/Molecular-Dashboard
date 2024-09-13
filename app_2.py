import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from src.tpms_calculation import get_or_calculate_tpms
from src.bond_cracks import get_atom_data_or_cache
from scripts.utils.mathematical import my_ceil, my_ceil_2, my_floor, my_floor_2
from scripts.data_processing.highlighted_mask import highlighted_mask
from scripts.utils.figure_create import create_figure, update_figure_layout
from scripts.utils.file_utils import read_json_file
from scripts.data_processing.create_dataset import save_dataset
import dash_bootstrap_components as dbc
import math


def get_app(update_dateset = False):
    
    if update_dateset:
        save_dataset()
    
    # Read the data
    df_dir = read_json_file('data/json/variables.json')['database']
    df = pd.read_csv(df_dir)
    df['Norm_Density'] = 2300 * df['Norm_Density']

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Model Parameters"),
                html.Label("Surface 1 Selection:"),
                dcc.Dropdown(id='surface1', options=[{'label': i, 'value': i} for i in ['gyroid', 'diamond', 'primitive']], value='gyroid', clearable=False),
                
                html.Label("Surface 2 Selection:"),
                dcc.Dropdown(id='surface2', options=[{'label': i, 'value': i} for i in ['gyroid', 'diamond', 'primitive']], value='gyroid', clearable=False),
                
                html.Label("a Value:"),
                dcc.Slider(id='a-val', min=1, max=100, step=1, value=50, marks={i: str(i) for i in range(0, 101, 10)}),
                
                html.Label("Hybrid Perc Value:"),
                dcc.Slider(id='h_perc', min=0, max=100, step=5, value=50, marks={i: str(i) for i in [0,25,50,70,100]}),
                
                html.Label("k Value:"),
                dcc.Slider(id='k-val', min=0, max=1.0, step=0.1, value=0.5, marks={i/10: f'{i/10:.1f}' for i in range(11)}),
                
                html.Label("Grid Size:"),
                dcc.Slider(id='grid-size', min=20, max=100, step=5, value=50, marks={i: str(i) for i in range(20, 101, 10)}),
                
                html.Label("View Mode:"),
                dcc.Dropdown(id='view', options=[{'label': i, 'value': i} for i in ['XY', 'XZ', 'YZ', '3D']], value='3D', clearable=False),
                
                html.Label("Coloring:"),
                dcc.Dropdown(id='color-by', options=[{'label': i, 'value': i} for i in ['Real', 'Abs']], value='Real', clearable=False),
                
                html.Label("Legend Minimum Value:"),
                dcc.Input(id='legend-min', type='number', placeholder='Auto', step=0.1),
                
                html.Label("Legend Maximum Value:"),
                dcc.Input(id='legend-max', type='number', placeholder='Auto', step=0.1),
                
                html.Label("Cutoff:"),
                dcc.Input(id='cutoff', type='number', value=1.7, min=0.5, max=3.0, step=0.1),
                
                html.Br(),
                
                html.Label("Time Step:"),
                dcc.Input(id='time-step', type='number', value=2, min=2),
                
                html.Button('Update', id='update-button', n_clicks=0)
            ], width=3),
            
            dbc.Col([
                dcc.Tabs(id='view-mode-tabs', value='curvature', children=[
                    dcc.Tab(label='Curvature', value='curvature'),
                    dcc.Tab(label='Bond Crack', value='bond_crack')
                ]),
                dcc.Graph(id='tpms-plot', style={'height': '80vh'})
            ], width=9)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("2D Graph Filters"),
                dcc.Dropdown(id="geom1-dropdown", options=[{"label": 'Select geom-1 here', "value": "All"}]+[{"label": x, "value": x} for x in df["Geom1"].unique()], value="All", placeholder='Select geom-1 here', clearable=False),
                dcc.Dropdown(id="geom2-dropdown", options=[{"label": 'Select geom-2 here', "value": "All"}]+[{"label": x, "value": x} for x in df["Geom2"].unique()], value="All", placeholder='Select geom-2 here', clearable=False),
                dcc.Dropdown(id="length-dropdown", options=[{"label": 'Select length here', "value": "All"}]+[{"label": x, "value": x} for x in df["length"].unique()], value="All", placeholder='Select length here', clearable=False),
                html.Div('Legend Color Category:', style={"text-align": "right", "width": "100%", "padding-right": "10px"}),
                dcc.RadioItems(
                    options=[{"label": 'k Value', "value": 'k_Value'},
                            {"label": 'Hybrid Percentage', "value": 'Hybrid_Perc'},
                            {"label": 'Length', "value": 'length'}],
                    value='k_Value',
                    id='legend_category',
                    inline=True,
                    style={"display": "flex", "text-align": "left", "width": "100%"}
                ),
            ], width=12),
        ]),
        
        dbc.Row([
            dbc.Col(dcc.Graph(id="norm-stress-norm-density-scatter"), width=6),
            dbc.Col(dcc.Graph(id="norm-young-modulus-norm-density-scatter"), width=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="stress-strain-scatter_1"), width=6),
            dbc.Col(dcc.Graph(id="stress-strain-scatter_2"), width=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="stress-strain-scatter_3"), width=6),
            dbc.Col(dcc.Graph(id="stress-strain-scatter_4"), width=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="energy-scatter_1"), width=6),
            dbc.Col(dcc.Graph(id="energy-scatter_2"), width=6),
        ]),
    ], fluid=True)

    @app.callback(
        Output('tpms-plot', 'figure'),
        [Input('update-button', 'n_clicks'),
        Input('view-mode-tabs', 'value')],
        [State('surface1', 'value'),
        State('surface2', 'value'),
        State('a-val', 'value'),
        State('h_perc', 'value'),
        State('k-val', 'value'),
        State('grid-size', 'value'),
        State('view', 'value'),
        State('color-by', 'value'),
        State('legend-min', 'value'),
        State('legend-max', 'value'),
        State('time-step', 'value'),
        State('cutoff', 'value')]
    )
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
            positions, cracked_bond_coords = get_atom_data_or_cache(surface1, surface2, a_val, h_perc, k_val, time_step, cutoff)
                        
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
        fig.layout.scene.camera.projection.type = "orthographic"
        fig.update_layout(margin={'t':0,'l':0,'b':0,'r':0})
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
        
        return fig

    @app.callback(
        [Output("norm-stress-norm-density-scatter", "figure"),
        Output("norm-young-modulus-norm-density-scatter", "figure"),
        Output("stress-strain-scatter_1", "figure"),
        Output("stress-strain-scatter_2", "figure"),
        Output("stress-strain-scatter_3", "figure"),
        Output("stress-strain-scatter_4", "figure"),
        Output("energy-scatter_1", "figure"),
        Output("energy-scatter_2", "figure")],
        [Input("geom1-dropdown", "value"),
        Input("geom2-dropdown", "value"),
        Input("length-dropdown", "value"),
        Input("legend_category", "value"),
        Input('surface1', 'value'),
        Input('surface2', 'value'),
        Input('a-val', 'value'),
        Input('h_perc', 'value'),
        Input('k-val', 'value')]
    )
    
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
                name='Selected Model',
                # legend={"x": 0.9,"y": 0.9,"xref": "container","yref": "container","bgcolor": "Gold",}
            ))
            
            if y.startswith("norm_dens"):
                fig.add_shape(
                    type='rect',
                    y0=1, x0=0, y1=2, x1=1500,
                    opacity=0.2, fillcolor='lightgreen', line=dict(width=0)
                )
            
            figures.append(fig)
        
        return tuple(figures)
    return app
