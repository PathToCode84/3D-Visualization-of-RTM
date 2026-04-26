# reproducing Figure 1 from Stigler 1997


library(ggplot2)
library(plot3D)
library(mvtnorm)

# 1. Generate Bivariate Normal Data
set.seed(420)
n=50
mu <- c(0, 0)
Sigma <- matrix(c(1, 0.5, 0.5, 1), nrow = 2)  # correlation = 0.5

# Create grid for smooth surface visualization
x <- seq(-3, 3, length.out = n)
y <- seq(-3, 3, length.out = n)
grid <- expand.grid(x = x, y = y) ## look at this more closely

# Calculate bivariate normal density (Z values)
grid$z <- dmvnorm(grid, mean = mu, sigma = Sigma)

# z-dim is the joint distribution

# 3D Surface Plot
persp3D(
  x = x, y = y, z = matrix(grid$z, nrow = n),
  theta = 30, phi = 20,
  col = "lightblue", shade = 0.3,
  xlab = "X",
  ylab = "Y",
  zlab = "f(x,y)",
  main = "Bivariate Normal Distribution"
)

# Scatterplot for visualizing the real Data
library(MASS)
library(plot3D)
library(rgl) # For interactive 3D viewing

# 1. Generate Data
set.seed(123)
n <- 2000
mu <- c(0, 0)
Sigma <- matrix(c(1, 0.5, 0.5, 1), nrow = 2) # Correlation 0.5
data <- mvrnorm(n, mu, Sigma)

# Convert to dataframe for easier handling
df <- as.data.frame(data)
colnames(df) <- c("X", "Y")

# 2. Calculate Density (Z) for each point
# We estimate the density at each point's location
# This creates a "Z" value representing how "dense" the area around that point is
library(kde2d) # From MASS package
dens <- kde2d(df$X, df$Y, n = 50)

# Interpolate density for each data point
df$Z <- approx2(dens$x, dens$y, dens$z, df$X, df$Y)

# 3. Plot using plot3D (Static)
# Color points by density (Z) to mimic the "hill" shape
scatter3D(df$X, df$Y, df$Z,
          pch = 16, cex = 0.5,
          colvar = df$Z, col = topo.colors(100),
          xlab = "X (Standardized)", ylab = "Y (Standardized)", zlab = "Density Estimate",
          main = "3D Scatter of Bivariate Normal Data\n(Color = Local Density)",
          theta = 30, phi = 20, ticktype = "detailed")

# Add the regression line (Y = 0.5 * X)
abline3d(a = 0, b = 0.5, c = 0, col = "red", lwd = 2) # Slope = rho = 0.5



library(rgl)

# Open 3D window
open3d()

# Plot points
plot3d(grid$x, grid$y, grid$z, 
       size = 3, 
       xlab = "X", ylab = "Y", zlab = "Density")

# Add the regression line (The "ridge" of the hill)
# E[Y|X] = rho * X
lines3d(x = c(-3, 3), y = c(-1.5, 1.5), z = rep(max(grid$z), 2), 
        col = "red", lwd = 3)

# Add the line Y=X for comparison (Perfect correlation line)
lines3d(x = c(-3, 3), y = c(-3, 3), z = rep(max(grid$z), 2), 
        col = "gray", lwd = 1, lty = 2)

# Add a title
title3d("Interactive 3D View: Bivariate Normal Data")
