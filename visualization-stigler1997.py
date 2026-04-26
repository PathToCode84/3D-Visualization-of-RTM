from pathlib import Path

import numpy as np
import plotly.graph_objects as go

rho = 0.5
x_plane = 1.5 # where does plane cut
x_plane_values = np.concatenate((np.linspace(-3, -0.25, 12), np.linspace(0.25, 3, 12)))
# where 0.18377 is maximum

# Grid
resolution = 100
x = np.linspace(-3, 3, resolution)
y = np.linspace(-3, 3, resolution)
X, Y = np.meshgrid(x, y)

# normal density
normalizing_constant = 1 / (2 * np.pi * np.sqrt(1 - rho**2))
Z = normalizing_constant * np.exp(
    -(X**2 - 2 * rho * X * Y + Y**2) / (2 * (1 - rho**2))
)

# Contour geometry for the correlated normal
sigma = np.array([[1, rho], [rho, 1]])
sigma_inv = np.linalg.inv(sigma)
quadratic_form = (
    sigma_inv[0, 0] * X**2
    + 2 * sigma_inv[0, 1] * X * Y
    + sigma_inv[1, 1] * Y**2
)

theta = np.linspace(0, 2 * np.pi, 240)
eigenvalues, eigenvectors = np.linalg.eigh(sigma)
x_line = np.linspace(-3, 3, 240)
y_regression = rho * x_line
y_identity = x_line

# Vertical plane at x = x_plane
y_plane = np.linspace(-3, 3, 60)
z_plane_base = np.linspace(0, 1, 60)
Y_plane, Z_plane_base = np.meshgrid(y_plane, z_plane_base)

fig = go.Figure()

# wall outline
wall_color = "black"
wall_width = 5


def line_segment(direction, level, z_value):
    direction = np.asarray(direction, dtype=float)
    quad_scalar = direction @ sigma_inv @ direction
    extent = np.sqrt(level / quad_scalar)
    segment = np.column_stack((-extent * direction, extent * direction))
    return segment[0], segment[1], np.full(2, z_value)


def slice_data(x_plane_value):
    # The wall touches the highest density at y = rho * x_plane.
    z_touch = normalizing_constant * np.exp(-(x_plane_value**2) / 2)
    level = x_plane_value**2
    # Cap the surface at the slice height to avoid triangulation spikes.
    z_cap = np.minimum(Z, z_touch)

    z_wall = z_touch * Z_plane_base
    x_wall = np.full_like(Y_plane, x_plane_value)
    z_horizontal_ellipse = np.where(quadratic_form <= level, z_touch, np.nan)

    ellipse_xy = eigenvectors @ np.diag(np.sqrt(level * eigenvalues)) @ np.vstack(
        (np.cos(theta), np.sin(theta))
    )
    ellipse_x = ellipse_xy[0]
    ellipse_y = ellipse_xy[1]
    ellipse_z = np.full_like(ellipse_x, z_touch)

    z_regression = normalizing_constant * np.exp(
        -(x_line**2 - 2 * rho * x_line * y_regression + y_regression**2)
        / (2 * (1 - rho**2))
    )
    z_regression_3d = np.minimum(z_regression, z_touch)

    regression_x_2d, regression_y_2d, z_regression_2d = line_segment(
        [1, rho], level, z_touch
    )
    identity_x_2d, identity_y_2d, z_identity_2d = line_segment(
        [1, 1], level, z_touch
    )

    return {
        "z_touch": z_touch,
        "z_cap": z_cap,
        "x_wall": x_wall,
        "z_wall": z_wall,
        "z_horizontal_ellipse": z_horizontal_ellipse,
        "ellipse_x": ellipse_x,
        "ellipse_y": ellipse_y,
        "ellipse_z": ellipse_z,
        "z_regression_3d": z_regression_3d,
        "regression_x_2d": regression_x_2d,
        "regression_y_2d": regression_y_2d,
        "z_regression_2d": z_regression_2d,
        "identity_x_2d": identity_x_2d,
        "identity_y_2d": identity_y_2d,
        "z_identity_2d": z_identity_2d,
    }


grid_step = 0.3
grid_values = np.arange(-3, 3 + 1e-9, grid_step)


def bell_grid_lines(z_touch):
    x_lines = []
    y_lines = []
    z_lines = []

    for x_value in grid_values:
        x_curve = np.full_like(y, x_value)
        y_curve = y
        z_curve = normalizing_constant * np.exp(
            -(x_value**2 - 2 * rho * x_value * y_curve + y_curve**2)
            / (2 * (1 - rho**2))
        )
        z_curve = np.where(z_curve < z_touch, z_curve, np.nan)
        x_lines.append(x_curve)
        y_lines.append(y_curve)
        z_lines.append(z_curve)

    for y_value in grid_values:
        x_curve = x
        y_curve = np.full_like(x, y_value)
        z_curve = normalizing_constant * np.exp(
            -(x_curve**2 - 2 * rho * x_curve * y_value + y_value**2)
            / (2 * (1 - rho**2))
        )
        z_curve = np.where(z_curve < z_touch, z_curve, np.nan)
        x_lines.append(x_curve)
        y_lines.append(y_curve)
        z_lines.append(z_curve)

    return x_lines, y_lines, z_lines


def wall_traces(x_plane_value, z_touch, z_wall):
    return [
        go.Surface(
            x=np.full_like(Y_plane, x_plane_value), y=Y_plane, z=z_wall,
            opacity=0.75,
            showscale=False,
            colorscale=[[0, "#45718E"], [1, "#45718E"]],
            name="wall"
        ),
        go.Scatter3d(
            x=[x_plane_value, x_plane_value], y=[-3, 3], z=[0, 0],
            mode="lines",
            line=dict(color=wall_color, width=wall_width),
            showlegend=False
        ),
        go.Scatter3d(
            x=[x_plane_value, x_plane_value], y=[-3, 3], z=[z_touch, z_touch],
            mode="lines",
            line=dict(color=wall_color, width=wall_width),
            showlegend=False
        ),
        go.Scatter3d(
            x=[x_plane_value, x_plane_value], y=[-3, -3], z=[0, z_touch],
            mode="lines",
            line=dict(color=wall_color, width=wall_width),
            showlegend=False
        ),
        go.Scatter3d(
            x=[x_plane_value, x_plane_value], y=[3, 3], z=[0, z_touch],
            mode="lines",
            line=dict(color=wall_color, width=wall_width),
            showlegend=False
        ),
    ]

initial_slice = slice_data(x_plane)

# Surface
fig.add_trace(
    go.Surface(x=X, y=Y, z=initial_slice["z_cap"], opacity=1, #change to z=Z for full bell
    colorscale="Teal", showscale=False,
    lighting=dict(ambient=0.7, diffuse=0.9, specular=0.2, roughness=0.8),
    lightposition=dict(x=100, y=200, z=300),
    contours={ 
        "z": {"show": True, "usecolormap": True, "highlightcolor": "black", "project_z": False},
        "x": {"show": False},
        "y": {"show": False}
    },
    name="density"
))

# Short colorscale notes:
# agsunset, burg, magenta, purpor ... girly
# bluered, plotly3 ... grell aber pretty
# blues, rdbu, redor, sunset, sunsetdark, 
# blugrn, darkmint, emrld, teal .. green 
# jet .. obnoxious 2000
# pubu, purp ... maybe too light?

for trace in wall_traces(x_plane, initial_slice["z_touch"], initial_slice["z_wall"]):
    fig.add_trace(trace)

initial_grid_x, initial_grid_y, initial_grid_z = bell_grid_lines(initial_slice["z_touch"])
for x_curve, y_curve, z_curve in zip(initial_grid_x, initial_grid_y, initial_grid_z):
    fig.add_trace(go.Scatter3d(
        x=x_curve, y=y_curve, z=z_curve,
        mode="lines",
        line=dict(width=2, color="black"),
        hoverinfo="skip",
        showlegend=False
    ))


# beheading
fig.add_trace(go.Surface(
    x=X, y=Y, z=initial_slice["z_horizontal_ellipse"],
    opacity=0.75,
    showscale=False,
    colorscale=[[0, "#555555"], [1, "#555555"]],
    name="ellipse"
))

# contour line (of ellipse) at the slice height
fig.add_trace(go.Scatter3d(
    x=initial_slice["ellipse_x"], y=initial_slice["ellipse_y"], z=initial_slice["ellipse_z"],
    mode="lines",
    line=dict(width=4, color="black"),
    name="ellipse outline"
))

# 3D regression line on the density surface up to the cut height
fig.add_trace(go.Scatter3d(
    x=x_line, y=y_regression, z=initial_slice["z_regression_3d"],
    mode='lines', line=dict(width=6, color ="#111111"),
    name="regression 3d"
))

# 2D regression line inside the ellipse
fig.add_trace(go.Scatter3d(
    x=initial_slice["regression_x_2d"],
    y=initial_slice["regression_y_2d"],
    z=initial_slice["z_regression_2d"],
    mode='lines', line=dict(width=6, color ="black"),
    name="regression 2d"
))

# indentity line inside the ellipse
fig.add_trace(go.Scatter3d(
    x=initial_slice["identity_x_2d"],
    y=initial_slice["identity_y_2d"],
    z=initial_slice["z_identity_2d"],
    mode='lines', line=dict(width=6, color ="black"),
    name="identity 2d"
))

slider_steps = []
for x_plane_value in x_plane_values:
    current_slice = slice_data(x_plane_value)
    current_grid_x, current_grid_y, current_grid_z = bell_grid_lines(current_slice["z_touch"])
    slider_steps.append(
        dict(
            method="restyle",
            args=[
                {
                    "x": [
                        X,
                        current_slice["x_wall"],
                        [x_plane_value, x_plane_value],
                        [x_plane_value, x_plane_value],
                        [x_plane_value, x_plane_value],
                        [x_plane_value, x_plane_value],
                        *current_grid_x,
                        X,
                        current_slice["ellipse_x"],
                        x_line,
                        current_slice["regression_x_2d"],
                        current_slice["identity_x_2d"],
                    ],
                    "y": [
                        Y,
                        Y_plane,
                        [-3, 3],
                        [-3, 3],
                        [-3, -3],
                        [3, 3],
                        *current_grid_y,
                        Y,
                        current_slice["ellipse_y"],
                        y_regression,
                        current_slice["regression_y_2d"],
                        current_slice["identity_y_2d"],
                    ],
                    "z": [
                        current_slice["z_cap"],
                        current_slice["z_wall"],
                        [0, 0],
                        [current_slice["z_touch"], current_slice["z_touch"]],
                        [0, current_slice["z_touch"]],
                        [0, current_slice["z_touch"]],
                        *current_grid_z,
                        current_slice["z_horizontal_ellipse"],
                        current_slice["ellipse_z"],
                        current_slice["z_regression_3d"],
                        current_slice["z_regression_2d"],
                        current_slice["z_identity_2d"],
                    ]
                },
                list(range(0, 6 + len(current_grid_x))) + [6 + len(current_grid_x), 7 + len(current_grid_x), 8 + len(current_grid_x), 9 + len(current_grid_x), 10 + len(current_grid_x)],
            ],
            label=f"{x_plane_value:.2f}",
        )
    )

fig.update_layout(
    scene=dict(
        xaxis=dict(showbackground=False),
        yaxis=dict(showbackground=False),
        zaxis=dict(showbackground=True),
    ),
    sliders=[
        dict(
            active=int(np.argmin(np.abs(x_plane_values - x_plane))),
            currentvalue={"prefix": "x_plane = "},
            pad={"t": 30},
            steps=slider_steps,
        )
    ]
)
output_path = Path("public/index.html")
output_path.parent.mkdir(parents=True, exist_ok=True)
fig.write_html(
    output_path,
    include_plotlyjs=True,
    full_html=True,
    config={"responsive": True},
)
print(f"Wrote static site to {output_path}")
