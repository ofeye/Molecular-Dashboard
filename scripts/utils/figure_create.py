import plotly.express as px

def create_figure(df_filtered, x, y, legend_category, use_trendline=False, use_log_scale=False, height=750):
    if use_trendline:
        return px.scatter(
        df_filtered,
        labels={"k_Value": "k Value", "length": "Length<br> ", "Hybrid_Perc": "Hybrid<br>Percentage<br>"},
        x=x, y=y,
        hover_data=["Geom1", "Geom2", "length", "k_Value", "Hybrid_Perc"],
        color=legend_category,
        trendline='ols',
        trendline_options=dict(log_x=use_log_scale, log_y=use_log_scale),
        height=height)
    else:
        return px.scatter(
        df_filtered,
        labels={"k_Value": "k Value", "length": "Length<br> ", "Hybrid_Perc": "Hybrid<br>Percentage<br>"},
        x=x, y=y,
        hover_data=["Geom1", "Geom2", "length", "k_Value", "Hybrid_Perc"],
        color=legend_category,
        height=height)
    
    
def update_figure_layout(fig, x_range, y_range, color_range, x_title, y_title, use_log_scale=False):
    axis_type = 'log' if use_log_scale else 'linear'
    fig.update_layout(
        xaxis=dict(range=x_range, type=axis_type, title=x_title),
        yaxis=dict(range=y_range, type=axis_type, title=y_title),
        coloraxis=dict(cmin=color_range[0], cmax=color_range[1]),
        coloraxis_colorbar=dict(
            x=1,  # Colorbar'ı grafikten daha sağa kaydırmak için x ekseni konumu
            y=0.47,  # Colorbar'ın y ekseni boyunca ortalanması
            len=0.97  # Colorbar'ın boyunu ayarlama (0-1 arasında)
        ),
        font=dict(family="Times New Roman", size=20),
        template='none'
    )
    fig.update_xaxes(showline=True, mirror=True, gridcolor='lightgrey')
    fig.update_yaxes(showline=True, mirror=True, gridcolor='lightgrey')