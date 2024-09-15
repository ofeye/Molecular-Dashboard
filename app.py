import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from numpy import abs
import dash_bootstrap_components as dbc
import os
from src.tpms_calculation import get_or_calculate_tpms
from src.bond_cracks import get_atom_data_or_cache


def get_app():
    # Initialize Dash app
    app = dash.Dash(__name__)

    # Dash uygulaması
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Label("Surface 1 Seçimi:"),
                dcc.Dropdown(id='surface1', options=[{'label': i, 'value': i} for i in ['gyroid', 'diamond', 'primitive']], value='gyroid', clearable=False),
                
                html.Label("Surface 2 Seçimi:"),
                dcc.Dropdown(id='surface2', options=[{'label': i, 'value': i} for i in ['gyroid', 'diamond', 'primitive']], value='gyroid', clearable=False),
                
                html.Label("a Değeri:"),
                dcc.Slider(id='a-val', min=1, max=100, step=1, value=50, marks={i: str(i) for i in range(0, 101, 10)}),
                
                html.Label("Hybrid Perc Değeri:"),
                dcc.Slider(id='h_perc', min=0, max=100, step=5, value=50, marks={i: str(i) for i in [0,25,50,70,100]}),
                
                html.Label("k Değeri:"),
                dcc.Slider(id='k-val', min=0, max=1.0, step=0.1, value=0.5, marks={int(i) if i==int(i) else i: f'{i:.1f}' for i in [round(x * 0.1, 1) for x in range(11)]}),
                
                html.Label("Grid Boyutu:"),
                dcc.Slider(id='grid-size', min=20, max=100, step=5, value=50, marks={i: str(i) for i in range(20, 101, 10)}),
                
                html.Label("Görüntüleme Modu:"),
                dcc.Dropdown(id='view', options=[{'label': i, 'value': i} for i in ['XY', 'XZ', 'YZ', '3D']], value='3D', clearable=False),
                
                html.Label("Renklendirme:"),
                dcc.Dropdown(id='color-by', options=[{'label': i, 'value': i} for i in ['Real', 'Abs']], value='Real', clearable=False),
                            
                html.Label("Legend Minimum Değeri:"),
                html.Br(),  # Boş satır ekle

                dcc.Input(id='legend-min', type='number', placeholder='Otomatik', step=0.1),            
                html.Br(),  # Boş satır ekle
                
                html.Label("Legend Maksimum Değeri:"),
                dcc.Input(id='legend-max', type='number', placeholder='Otomatik', step=0.1),

                html.Br(),  # Boş satır ekle
                
                html.Label("Cutoff:"),
                dcc.Input(id='cutoff', type='number', value=0.017, min=0.001, max=0.1, step=0.001),
                
                html.Br(),
                html.Label("Time Step:"),
                dcc.Input(id='time-step', type='number', value=2, min=2),
                
                html.Br(),
                html.Br(),
                
                html.Button('Güncelle', id='update-button', n_clicks=0)
            ], width=3),
            
            dbc.Col([
                dcc.Tabs(id='view-mode-tabs', value='curvature', style={'height': '5vh'}, children=[
                    dcc.Tab(label='Curvature', value='curvature'),
                    dcc.Tab(label='Bond Crack', value='bond_crack')
                ]),
                dcc.Graph(id='tpms-plot', style={'height': '95vh'})
            ], width=9)
        ])
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
        State('view-mode-tabs', 'value'),
        State('time-step', 'value'),
        State('cutoff', 'value')]
    )

    def update_graph(n_clicks, view_mode, surface1, surface2, a_val, h_perc, k_val, grid_size, view, colorize, legend_min, legend_max, view_mode_tab, time_step, cutoff):

            
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
                    up=dict(x=0, y=1, z=0),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=0, y=0, z=2)
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
                    eye=dict(x=0, y=2.5, z=0)
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
                    eye=dict(x=2, y=0, z=0)
                )
            )
        fig.layout.scene.camera.projection.type = "orthographic"
        return fig
    return app
