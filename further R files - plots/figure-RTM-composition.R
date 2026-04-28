## What is regression toward the Mean
# reproducing figure 1 of Yudkin1996

setwd("/Users/mia8425/Documents/Studium/6. Semester SS 2026/SE Seminar")
pdf("figure-RTM.pdf", width = 7, height = 5)

x <- seq(0, 10, length.out = 500)

mu_pop <- 5
sd_pop <- 1.3
y_pop <- dnorm(x, mu_pop, sd_pop)

# Reduce margins: bottom, left, top, right
par(mar = c(2, 0.5, 0.5, 0.5))

# Set up empty plot
plot(x, y_pop, type = "n",
     ylim = c(0, max(y_pop) * 1.3),
     xlab = "", ylab = "",
     main = "",
     xaxt = "n", yaxt = "n", bty = "n")
axis(1, at = seq(0, 10, by = 1), labels = FALSE, lwd = 2, lwd.ticks = 1.5, tck = -0.02)
axis(1, at = mu_pop, labels = "Mean", tick = FALSE)

# Add individual distributions
set.seed(420)

n_ind <- 75

scale <- 0.025  # size of individual dist relative to pop dist

sd_ind <- 0.3  # individual within-person SD 

draw_individual <- function(mu_i, lwd = 1, lty = 2, col = "gray60", offset = NULL) {
  # Random vertical position; mean stays inside the curve, tails may extend outside
  pop_height_at_mu <- dnorm(mu_i, mu_pop, sd_pop)
  peak_height <- scale / (sd_ind * sqrt(2 * pi))
  if (is.null(offset))
    offset <- runif(1, min = 0, max = max(0, pop_height_at_mu - peak_height))
  x_i <- seq(mu_i - 3 * sd_ind, mu_i + 3 * sd_ind, length.out = 200)
  y_top <- dnorm(x_i, mu_i, sd_ind) * scale + offset
  lines(x_i, y_top, lwd = lwd, lty = lty, col = col)
  invisible(list(mu = mu_i, offset = offset, y_top = y_top, x_i = x_i))
}

for(i in 1:n_ind){
  mu_i <- rnorm(1, mu_pop, 0.8)
  draw_individual(mu_i)
}

# individual A (below mean)
mu_A <- 6
res_A <- draw_individual(mu_A, lwd = 2, col = "black", offset = 0.12)

# individual B (above mean)
mu_B <- 7
res_B <- draw_individual(mu_B, lwd = 2, col = "black")

# Draw population curve
lines(x, y_pop, lwd = 3, col = "black")

# cutoff
abline(v = 6.5, lwd = 2)

text(6.5, max(y_pop), "cut off", pos = 4)
text(mu_A, max(res_A$y_top), "A", pos = 3)
text(mu_B, max(res_B$y_top), "B", pos = 3)

legend("topleft",
       legend = c("Population distribution",
                  "Individual distribution",
                  "Individuals A,B"),
       lty    = c(1, 2, 2),
       lwd    = c(3, 1, 2),
       col    = c("black", "gray60", "black"),
       bty    = "n",
       seg.len = 1.5)

dev.off()
