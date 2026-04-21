# Notes because I'm a student
# activate myvenv with cmd . myvenv/bin/activate

import numpy as np
import plotly.graph_objects as go

rho = 0.5
x_plane = 1.0 # where does plane cut
z_cut = 0.12

# Grid
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)

# normal density
Z = (1/(2*np.pi*np.sqrt(1-rho**2))) * np.exp(
    -(X**2 - 2*rho*X*Y + Y**2)/(2*(1-rho**2)))
Z_cut = np.where(Z <= z_cut, Z, np.nan)

# Horizontal plane at z = z_cut
Z_horizontal = np.full_like(X, z_cut)

fig = go.Figure()

# Surface
fig.add_trace(
    go.Surface(x=X, y=Y, z=Z_cut, opacity=1, #change to z=Z for full bell
    colorscale="Teal",
    lighting=dict(ambient=0.7, diffuse=0.9, specular=0.2, roughness=0.8),
    lightposition=dict(x=100, y=200, z=300),
    contours={ 
        "z": {"show": True, "usecolormap": True, "highlightcolor": "black", "project_z": False},
        "x": {"show": True, "start": -3, "end": 3, "size": 0.25, "color": "black", "width": 1},
        "y": {"show": True, "start": -3, "end": 3, "size": 0.25, "color": "black", "width": 1}
    }
))

# Short colorscale notes:
# agsunset, burg, magenta, purpor ... girly
# bluered, plotly3 ... grell aber pretty
# blues, rdbu, redor, sunset, sunsetdark, 
# blugrn, darkmint, emrld, teal .. green 
# jet .. obnoxious 2000
# pubu, purp ... maybe too light?

# Vertical plane at x = x_plane
y_plane = np.linspace(-3, 3, 100)
z_plane = np.linspace(0, z_cut, 100)
Y_plane, Z_plane = np.meshgrid(y_plane, z_plane)
X_plane = np.full_like(Y_plane, x_plane)

fig.add_trace(go.Surface(
    x=X_plane, y=Y_plane, z=Z_plane,
    opacity=0.75,
    showscale=False,
    colorscale=[[0, "#005ed0"], [1, "#005ed0"]]
))

# beheading
fig.add_trace(go.Surface(
    x=X, y=Y, z=Z_horizontal,
    opacity=0.45,
    showscale=False,
    colorscale=[[0, "#7a0019"], [1, "#7a0019"]]
))

# for Regression line
x_line = np.linspace(-3, 3, 50)
y_line = rho * x_line # because slope of regression line = cov(X,Y)/Var(X) = rho 
# (because X,Y standardized) (normal equations)
z_line = (1/(2*np.pi*np.sqrt(1-rho**2))) * np.exp(
    -(x_line**2 - 2*rho*x_line*y_line + y_line**2)/(2*(1-rho**2)))
z_line_cut = np.where(z_line <= z_cut, z_line, np.nan)
# where do these spikes come from?

# Regression line
fig.add_trace(go.Scatter3d(
    x=x_line, y=y_line, z=z_line_cut,
    mode='lines', line=dict(width=6, color ="black")))

fig.show()
