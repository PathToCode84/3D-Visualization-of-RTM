####################################################################
# This code builds an interactive 3d representation of regression 
# toward the mean with the help of plotly

# To view plot locally, run this code and open up the index.html 
# file that it creates

# The interactive graphic is deployed at 
# https://threed-visualization-of-rtm.onrender.com

# The code for this project (incl. requirements and deployment spec-
# ific files (render)) can also be found on github (not anonymous)
####################################################################

from pathlib import Path
import json
import math

import numpy as np
import plotly.graph_objects as go

# default values
rho = 0.2
x_plane = 1 # = cut-off points
# range of x_plane and rho
x_plane_values = np.linspace(0, 3, 25)
rho_values = np.linspace(-0.9, 0.9, 19)

# Grid
resolution = 200
x = np.linspace(-3, 3, resolution)
y = np.linspace(-3, 3, resolution)
X, Y = np.meshgrid(x, y)

# set of angles around circle
theta = np.linspace(0, 2 * np.pi, 240)

x_line = np.linspace(-3, 3, 240)

# Coords for Vertical plane/ Wall at x = x_plane
y_plane = np.linspace(-3, 3, 60)
z_plane_base = np.linspace(0, 1, 60)
Y_plane, Z_plane_base = np.meshgrid(y_plane, z_plane_base)

fig = go.Figure()

# wall outline
wall_color = "black"
wall_width = 5


def density(rho_value, x_values, y_values):
    # just standard normal density
    normalizing_constant = 1 / (2 * np.pi * np.sqrt(1 - rho_value**2))
    return normalizing_constant * np.exp(
        -(x_values**2 - 2 * rho_value * x_values * y_values + y_values**2)
        / (2 * (1 - rho_value**2))
    )


def normal_pdf(value):
    return math.exp(-0.5 * value**2) / math.sqrt(2 * math.pi)


def normal_cdf(value):
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))
# expressed through erf (error fct) since cdf has no closed form solution (just tabulated)


def rtm_effect(rho_value, x_plane_value):
    a1 = x_plane_value
    return (1 - rho_value) * (normal_pdf(a1) / (1 - normal_cdf(a1)))


def rtm_label(rho_value, x_plane_value):
    return f"RTM-effect = {rtm_effect(rho_value, x_plane_value):.3f}"


def rho_geometry(rho_value):
    sigma = np.array([[1, rho_value], [rho_value, 1]])
    sigma_inv = np.linalg.inv(sigma)
    quadratic_form = (
        sigma_inv[0, 0] * X**2
        + 2 * sigma_inv[0, 1] * X * Y
        + sigma_inv[1, 1] * Y**2
    )
    eigenvalues, eigenvectors = np.linalg.eigh(sigma)
    return {
        "normalizing_constant": 1 / (2 * np.pi * np.sqrt(1 - rho_value**2)),
        "sigma_inv": sigma_inv,
        "quadratic_form": quadratic_form,
        "eigenvalues": eigenvalues,
        "eigenvectors": eigenvectors,
        "z": density(rho_value, X, Y),
        "y_regression": rho_value * x_line,
    }

# makes sure that regression 2d and indentity 2d are contained in ellipse
def line_segment(direction, level, z_value, sigma_inv):
    direction = np.asarray(direction, dtype=float)
    quad_scalar = direction @ sigma_inv @ direction
    extent = np.sqrt(level / quad_scalar)
    segment = np.column_stack((-extent * direction, extent * direction))
    return segment[0], segment[1], np.full(2, z_value)


def slice_data(rho_value, x_plane_value):
    geometry = rho_geometry(rho_value)
    normalizing_constant = geometry["normalizing_constant"]
    # The wall touches the highest density at y = rho * x_plane.
    z_touch = normalizing_constant * np.exp(-(x_plane_value**2) / 2)
    level = x_plane_value**2
    # Cap the surface at the slice height = ellipse slice
    z_cap = np.minimum(geometry["z"], z_touch)

    z_wall = z_touch * Z_plane_base
    x_wall = np.full_like(Y_plane, x_plane_value)
    x_wall_density = np.full_like(y_plane, x_plane_value)
    z_wall_density = density(rho_value, x_plane_value, y_plane)
    # <= for "filled" ellipse
    z_horizontal_ellipse = np.where(geometry["quadratic_form"] <= level, z_touch, np.nan)

    ellipse_xy = (
        geometry["eigenvectors"]
        @ np.diag(np.sqrt(level * geometry["eigenvalues"]))
        @ np.vstack((np.cos(theta), np.sin(theta)))
        # stacks arrays vertically (@ matrix mult) to make unit circle
        # the mult with the upper matrix stretches circle to ellipse
    )
    ellipse_x = ellipse_xy[0]
    ellipse_y = ellipse_xy[1]
    ellipse_z = np.full_like(ellipse_x, z_touch)

    y_regression = geometry["y_regression"]
    z_regression = density(rho_value, x_line, y_regression)
    z_regression_3d = np.minimum(z_regression, z_touch)

    regression_x_2d, regression_y_2d, z_regression_2d = line_segment(
        [1, rho_value], level, z_touch, geometry["sigma_inv"]
    )
    identity_x_2d, identity_y_2d, z_identity_2d = line_segment(
        [1, 1], level, z_touch, geometry["sigma_inv"]
    )

    return {
        "z_touch": z_touch,
        "z_cap": z_cap,
        "x_wall": x_wall,
        "z_wall": z_wall,
        "x_wall_density": x_wall_density,
        "z_wall_density": z_wall_density,
        "z_horizontal_ellipse": z_horizontal_ellipse,
        "ellipse_x": ellipse_x,
        "ellipse_y": ellipse_y,
        "ellipse_z": ellipse_z,
        "y_regression": y_regression,
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


def bell_grid_lines(rho_value, z_touch):
    x_lines = []
    y_lines = []
    z_lines = []

    for x_value in grid_values:
        x_curve = np.full_like(y, x_value)
        y_curve = y
        z_curve = density(rho_value, x_value, y_curve)
        z_curve = np.where(z_curve < z_touch, z_curve, np.nan)
        x_lines.append(x_curve)
        y_lines.append(y_curve)
        z_lines.append(z_curve)

    for y_value in grid_values:
        x_curve = x
        y_curve = np.full_like(x, y_value)
        z_curve = density(rho_value, x_curve, y_value)
        z_curve = np.where(z_curve < z_touch, z_curve, np.nan)
        x_lines.append(x_curve)
        y_lines.append(y_curve)
        z_lines.append(z_curve)

    return x_lines, y_lines, z_lines

# converts np data structure to py obj
def json_ready(value):
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return json_ready(value.tolist())
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def wall_traces(x_plane_value, z_touch, z_wall):
    return [
        go.Surface(
            # wall surface
            x=np.full_like(Y_plane, x_plane_value), y=Y_plane, z=z_wall,
            opacity=0.75,
            showscale=False,
            colorscale=[[0, "#45718E"], [1, "#45718E"]],
            name="wall"
        ),
        go.Scatter3d(
            # line on bottom edge of wall
            x=[x_plane_value, x_plane_value], y=[-3, 3], z=[0, 0],
            mode="lines",
            line=dict(color=wall_color, width=wall_width),
            showlegend=False
        ),
        go.Scatter3d(
            # line on top edge of wall
            x=[x_plane_value, x_plane_value], y=[-3, 3], z=[z_touch, z_touch],
            mode="lines",
            line=dict(color=wall_color, width=wall_width),
            showlegend=False
        ),
        go.Scatter3d(
            # line on left edge of wall
            x=[x_plane_value, x_plane_value], y=[-3, -3], z=[0, z_touch],
            mode="lines",
            line=dict(color=wall_color, width=wall_width),
            showlegend=False
        ),
        go.Scatter3d(
            # line on right edge of wall
            x=[x_plane_value, x_plane_value], y=[3, 3], z=[0, z_touch],
            mode="lines",
            line=dict(color=wall_color, width=wall_width),
            showlegend=False
        ),
    ]

initial_slice = slice_data(rho, x_plane)

# Surface of density (THE bell curve)
fig.add_trace(
    go.Surface(x=X, y=Y, z=initial_slice["z_cap"], opacity=1, 
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

# draw entire wall
for trace in wall_traces(x_plane, initial_slice["z_touch"], initial_slice["z_wall"]):
    fig.add_trace(trace)

# draw 2d density on the wall f(y|X = x_plane)
fig.add_trace(go.Scatter3d(
    x=initial_slice["x_wall_density"],
    y=y_plane,
    z=initial_slice["z_wall_density"],
    mode="lines",
    line=dict(width=7, color="black"),
    name="wall density outline",
    showlegend=False
))

# draw grid
initial_grid_x, initial_grid_y, initial_grid_z = bell_grid_lines(rho, initial_slice["z_touch"])
for x_curve, y_curve, z_curve in zip(initial_grid_x, initial_grid_y, initial_grid_z):
    fig.add_trace(go.Scatter3d(
        x=x_curve, y=y_curve, z=z_curve,
        mode="lines",
        line=dict(width=2, color="black"),
        hoverinfo="skip",
        showlegend=False
    ))


# draw ellipse slice
fig.add_trace(go.Surface(
    x=X, y=Y, z=initial_slice["z_horizontal_ellipse"],
    opacity=0.75,
    showscale=False,
    colorscale=[[0, "#555555"], [1, "#555555"]],
    name="ellipse"
))

# draw contour line (of ellipse) at the slice height
fig.add_trace(go.Scatter3d(
    x=initial_slice["ellipse_x"], y=initial_slice["ellipse_y"], z=initial_slice["ellipse_z"],
    mode="lines",
    line=dict(width=4, color="black"),
    name="ellipse outline",
    showlegend=False
))

# 3D regression line on the density surface up to the cut height
fig.add_trace(go.Scatter3d(
    x=x_line, y=initial_slice["y_regression"], z=initial_slice["z_regression_3d"],
    mode='lines', line=dict(width=6, color ="#111111"),
    name="regression 3d",
    showlegend=False
))

# 2D regression line inside the ellipse
fig.add_trace(go.Scatter3d(
    x=initial_slice["regression_x_2d"],
    y=initial_slice["regression_y_2d"],
    z=initial_slice["z_regression_2d"],
    mode='lines', line=dict(width=6, color ="black"),
    name="regression 2d",
    showlegend=False
))

# indentity line inside the ellipse
fig.add_trace(go.Scatter3d(
    x=initial_slice["identity_x_2d"],
    y=initial_slice["identity_y_2d"],
    z=initial_slice["z_identity_2d"],
    mode='lines', line=dict(width=6, color ="black"),
    name="identity 2d",
    showlegend=False
))

# make each trace "callable"
trace_indices = list(range(0, 7 + len(initial_grid_x))) + [
    7 + len(initial_grid_x),
    8 + len(initial_grid_x),
    9 + len(initial_grid_x),
    10 + len(initial_grid_x),
    11 + len(initial_grid_x),
]

x_plane_steps = []
for x_plane_index, x_plane_value in enumerate(x_plane_values):
    x_plane_steps.append(
        dict(
            method="skip", # = don't auto update (js does)
            args=[x_plane_index],
            label=f"{x_plane_value:.2f}",
        )
    )
# produced elements like {"method": "skip", "args": [0], "label": "0.00"} for js

rho_steps = []
for rho_index, rho_value in enumerate(rho_values):
    rho_steps.append(
        dict(
            method="skip",
            args=[rho_index],
            label=f"{rho_value:.1f}",
        )
    )

slider_script = f"""
// here starts java script code - use js comments not hastag

// inside curly prackets you can put py things 
// json.ready converts np data strucute to py obj
// json.dumps converts py obj to json string
// this way py vars get to js scrips


const traceIndices = {json.dumps(trace_indices)};
const xValues = {json.dumps(json_ready(x))};
const yValues = {json.dumps(json_ready(y))};
const yPlaneValues = {json.dumps(json_ready(y_plane))};
const zPlaneBaseValues = {json.dumps(json_ready(z_plane_base))};
const thetaValues = {json.dumps(json_ready(theta))};
const xLineValues = {json.dumps(json_ready(x_line))};
const gridValues = {json.dumps(json_ready(grid_values))};
const rhoValues = {json.dumps(json_ready(rho_values))};
const xPlaneValues = {json.dumps(json_ready(x_plane_values))};
let rhoIndex = {int(np.argmin(np.abs(rho_values - rho)))};
let xPlaneIndex = {int(np.argmin(np.abs(x_plane_values - x_plane)))};
let showSlices = true;


// all necessary to contiously compute RTM

function density(rho, x, y) {{
    const normalizingConstant = 1 / (2 * Math.PI * Math.sqrt(1 - rho * rho));
    return normalizingConstant * Math.exp(
        -(x * x - 2 * rho * x * y + y * y) / (2 * (1 - rho * rho))
    );
}}

function normalPdf(value) {{
    return Math.exp(-0.5 * value * value) / Math.sqrt(2 * Math.PI);
}}

function normalCdf(value) {{
    const sign = value < 0 ? -1 : 1;
    const x = Math.abs(value) / Math.sqrt(2);
    const t = 1 / (1 + 0.3275911 * x);
    const erfApprox = 1 - (((((1.061405429 * t - 1.453152027) * t + 1.421413741) *
        t - 0.284496736) * t + 0.254829592) * t) * Math.exp(-x * x);
    return 0.5 * (1 + sign * erfApprox);
}}

function rtmValue(rho, xPlane) {{
    return (1 - rho) * normalPdf(xPlane) / (1 - normalCdf(xPlane));
}}

function rtmText() {{
    if (!showSlices) {{
        return 'RTM-effect = 0.000';
    }}
    return `RTM-effect = ${{rtmValue(rhoValues[rhoIndex], xPlaneValues[xPlaneIndex]).toFixed(3)}}`;
}}

function matrixFromAxes(xAxis, yAxis, fn) {{
    // => is short way to write a fct
    return yAxis.map((y) => xAxis.map((x) => fn(x, y)));
    // .map takes an array applies fct and returns res array
}}

function lineSegment(rho, direction, level, zValue) {{
    const dx = direction[0];
    const dy = direction[1];
    const quadScalar = (dx * dx - 2 * rho * dx * dy + dy * dy) / (1 - rho * rho);
    // is the "end" of ellipse
    const extent = Math.sqrt(level / quadScalar);
    return [
        [-extent * dx, extent * dx],
        [-extent * dy, extent * dy],
        [zValue, zValue],
    ];
    // makes sure that regression 2d and indentity 2d are contained in ellipse
}}

function buildTraceUpdate(rho, xPlane) {{
    const normalizingConstant = 1 / (2 * Math.PI * Math.sqrt(1 - rho * rho));
    //density value of (x, rho x)
    const zTouch = normalizingConstant * Math.exp(-(xPlane * xPlane) / 2);
    const level = xPlane * xPlane;
    const sqrtOneMinusRhoSquared = Math.sqrt(1 - rho * rho);

    const xGrid = matrixFromAxes(xValues, yValues, (x) => x);
    const yGrid = matrixFromAxes(xValues, yValues, (_, y) => y);
    const zCap = matrixFromAxes(xValues, yValues, (x, y) => {{
        const z = density(rho, x, y);
        return showSlices ? Math.min(z, zTouch) : z;
    }});

    const xWall = zPlaneBaseValues.map(() => yPlaneValues.map(() => xPlane));
    const yWall = zPlaneBaseValues.map(() => yPlaneValues.slice());
    const zWall = zPlaneBaseValues.map((zBase) => yPlaneValues.map(() => zTouch * zBase));
    const xWallDensity = yPlaneValues.map(() => xPlane);
    const zWallDensity = yPlaneValues.map((y) => density(rho, xPlane, y));

    const gridX = [];
    const gridY = [];
    const gridZ = [];
    for (const xValue of gridValues) {{
        const xCurve = yValues.map(() => xValue);
        const yCurve = yValues.slice();
        const zCurve = yValues.map((y) => {{
            const z = density(rho, xValue, y);
            return showSlices && z >= zTouch ? null : z;
        }});
        gridX.push(xCurve);
        gridY.push(yCurve);
        gridZ.push(zCurve);
    }}
    for (const yValue of gridValues) {{
        const xCurve = xValues.slice();
        const yCurve = xValues.map(() => yValue);
        const zCurve = xValues.map((x) => {{
            const z = density(rho, x, yValue);
            return showSlices && z >= zTouch ? null : z;
        }});
        gridX.push(xCurve);
        gridY.push(yCurve);
        gridZ.push(zCurve);
    }}
    // that was for the black grid on density curve

    const zHorizontalEllipse = matrixFromAxes(xValues, yValues, (x, y) => {{
        const quadraticForm = (x * x - 2 * rho * x * y + y * y) / (1 - rho * rho);
        return quadraticForm <= level ? zTouch : null;
    }});

    const ellipseX = [];
    const ellipseY = [];
    const ellipseZ = [];
    for (const theta of thetaValues) {{
        const a = Math.sqrt(level) * Math.cos(theta);
        const b = Math.sqrt(level) * Math.sin(theta);
        ellipseX.push(a);
        ellipseY.push(rho * a + sqrtOneMinusRhoSquared * b);
        ellipseZ.push(zTouch);
    }}

    const yRegression = xLineValues.map((x) => rho * x);
    const zRegression3d = xLineValues.map((x, index) => (
        showSlices
            ? Math.min(density(rho, x, yRegression[index]), zTouch)
            : density(rho, x, yRegression[index])
    ));
    const regression2d = lineSegment(rho, [1, rho], level, zTouch);
    const identity2d = lineSegment(rho, [1, 1], level, zTouch);

    // give to plotly
    return {{
        x: [
            xGrid,
            xWall,
            [xPlane, xPlane],
            [xPlane, xPlane],
            [xPlane, xPlane],
            [xPlane, xPlane],
            xWallDensity,
            ...gridX,
            xGrid,
            ellipseX,
            xLineValues,
            regression2d[0],
            identity2d[0],
        ],
        y: [
            yGrid,
            yWall,
            [-3, 3],
            [-3, 3],
            [-3, -3],
            [3, 3],
            yPlaneValues,
            ...gridY,
            yGrid,
            ellipseY,
            yRegression,
            regression2d[1],
            identity2d[1],
        ],
        z: [
            zCap,
            zWall,
            [0, 0],
            [zTouch, zTouch],
            [0, zTouch],
            [0, zTouch],
            zWallDensity,
            ...gridZ,
            zHorizontalEllipse,
            ellipseZ,
            zRegression3d,
            regression2d[2],
            identity2d[2],
        ],
        visible: [
            true,
            showSlices,
            showSlices,
            showSlices,
            showSlices,
            showSlices,
            showSlices,
            ...gridValues.map(() => true),
            ...gridValues.map(() => true),
            showSlices,
            showSlices,
            true,
            showSlices,
            showSlices,
        ],
    }};
}}

// redraw
function applyCurrentSlice() {{
    const plotElement = document.getElementById('{{plot_id}}');
    Plotly.restyle(
        plotElement,
        buildTraceUpdate(rhoValues[rhoIndex], xPlaneValues[xPlaneIndex]),
        traceIndices
    );

    // add rtm annotation
    Plotly.relayout(plotElement, {{
        'annotations[0].text': rtmText(),
    }});
}}

// listen for slider change
document.getElementById('{{plot_id}}').on('plotly_sliderchange', function(event) {{
    const prefix = event.slider.currentvalue.prefix;
    if (prefix === 'rho = ' || prefix === 'ρ = ') {{
        rhoIndex = event.step.args[0];
    }} else if (prefix === 'x_plane = ' || prefix === 'cut-off point = ') {{
        xPlaneIndex = event.step.args[0];
    }}
    // redraw
    applyCurrentSlice();
}});

//button to turn of slices
document.getElementById('{{plot_id}}').on('plotly_buttonclicked', function(event) {{
    if (event.button && event.button.args && event.button.args.length > 0) {{
        showSlices = event.button.args[0];
        applyCurrentSlice();
    }}
}});
"""

fig.update_layout(
    scene=dict(
        xaxis=dict(showbackground=False),
        yaxis=dict(showbackground=False),
        zaxis=dict(showbackground=True, range=[0, 0.4]), # fix "height" of plot (no auto rescaling)
    ),
    sliders=[
        dict(
            active=int(np.argmin(np.abs(rho_values - rho))),
            currentvalue={"prefix": "ρ = "},
            pad={"b": 10},
            x=0.12,
            y=1.25,
            len=0.76,
            steps=rho_steps,
        ),
        dict(
            active=int(np.argmin(np.abs(x_plane_values - x_plane))),
            currentvalue={"prefix": "cut-off point = "},
            pad={"t": 30},
            x=0.12,
            y=0,
            len=0.76,
            steps=x_plane_steps,
        ),
    ],
    updatemenus=[
        dict(
            type="buttons",
            direction="right",
            active=0,
            x=0.88,
            y=1.25,
            buttons=[
                dict(
                    label="include slices",
                    method="skip",
                    args=[True],
                ),
                dict(
                    label="exlucde slices",
                    method="skip",
                    args=[False],
                ),
            ],
        )
    ],
    # just text field
    annotations=[
        dict(
            text=rtm_label(rho, x_plane),
            x=0.95,
            y=0.7,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="left",
            font=dict(size=16, color="#111111"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#111111",
            borderwidth=1,
            borderpad=6,
        )
    ],
    margin=dict(t=110), # in pixels
)
output_path = Path("public/index.html")
output_path.parent.mkdir(parents=True, exist_ok=True)


fig.write_html(
    output_path,
    include_plotlyjs=True,
    full_html=True,
    config={"responsive": True},
    post_script=slider_script, # give java script to plotly
)
print(f"Wrote static site to {output_path}")
