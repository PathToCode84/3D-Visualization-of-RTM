# Notes because I'm a student
# activate myvenv with cmd . myvenv/bin/activate

import numpy as np
import plotly.graph_objects as go

rho = 0.5

# Grid
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)

# normal density
Z = (1/(2*np.pi*np.sqrt(1-rho**2))) * np.exp(
    -(X**2 - 2*rho*X*Y + Y**2)/(2*(1-rho**2)))

fig = go.Figure()

# Surface
fig.add_trace(go.Surface(x=X, y=Y, z=Z, opacity=0.8))

# Regressionslinie
x_line = np.linspace(-3, 3, 50)
y_line = rho * x_line # because slope of regression line = cov(X,Y)/Var(X) = rho 
# (because X,Y standardized) (normal equations)
z_line = (1/(2*np.pi*np.sqrt(1-rho**2))) * np.exp(
    -(x_line**2 - 2*rho*x_line*y_line + y_line**2)/(2*(1-rho**2))
)

fig.add_trace(go.Scatter3d(
    x=x_line, y=y_line, z=z_line,
    mode='lines', line=dict(width=6)
))

fig.show()