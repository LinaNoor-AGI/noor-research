# Composite of motif lattice, swirl field, and time vector magnitude
# Each subplot corresponds to a symbolic field panel 🪷 🌀 📊

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, sobel
from numpy.random import default_rng

# Initialize grid
nx, ny = 200, 200
Y, X = np.mgrid[0:ny, 0:nx]
rng = default_rng(seed=42)
motif_coords = np.array([[60, 60], [140, 50], [100, 150], [40, 140], [160, 160]])

# Create 3-panel figure
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Composite of Motif Lattice, Swirl Field, and Time Vector Magnitude", fontsize=14)

# === Panel A: Motif Lattice 🪷 ===
anchor_layer = np.zeros((ny, nx))
for x, y in motif_coords:
    axs[0].plot(x, y, 'kx', markersize=6, markeredgewidth=2)
    anchor_layer[y, x] = 1
axs[0].set_title("A. Motif Lattice 🪷")
axs[0].set_xlim(0, nx)
axs[0].set_ylim(0, ny)
axs[0].set_aspect('equal')
axs[0].set_xlabel("x")
axs[0].set_ylabel("y")

# === Panel B: Swirl Field 🌀 with LIC ===
def swirl_field(x, y):
    cx, cy = 100, 100
    dx = x - cx
    dy = y - cy
    r2 = dx**2 + dy**2 + 1e-5
    U = -dy / r2
    V = dx / r2
    return U, V

U, V = swirl_field(X, Y)
magnitude = np.sqrt(U**2 + V**2)
U_norm = U / (magnitude + 1e-8)
V_norm = V / (magnitude + 1e-8)
noise = rng.normal(0.5, 0.2, size=(ny, nx))
lic_texture = gaussian_filter(noise * magnitude, sigma=1)

axs[1].imshow(lic_texture, cmap='Greys', origin='lower', extent=(0, nx, 0, ny))
axs[1].streamplot(X, Y, U, V, color='k', linewidth=0.5, density=1.0)
axs[1].set_title("B. Swirl Field 🌀")
axs[1].set_xlim(0, nx)
axs[1].set_ylim(0, ny)
axs[1].set_aspect('equal')
axs[1].set_xlabel("x")
axs[1].set_ylabel("y")

# === Panel C: Time Vector Magnitude ||T^μ|| ===
coherence = gaussian_filter(anchor_layer, sigma=6)
gx = sobel(coherence, axis=1)
gy = sobel(coherence, axis=0)
T_mag = np.sqrt(gx**2 + gy**2)

im = axs[2].imshow(T_mag, cmap='plasma', origin='lower', extent=(0, nx, 0, ny))
axs[2].set_title("C. Time Vector Magnitude $\\|T^\\mu\\|$")
axs[2].set_xlim(0, nx)
axs[2].set_ylim(0, ny)
axs[2].set_aspect('equal')
axs[2].set_xlabel("x")
axs[2].set_ylabel("y")
fig.colorbar(im, ax=axs[2], fraction=0.046, pad=0.04)

# Display everything
plt.tight_layout()
plt.show()
