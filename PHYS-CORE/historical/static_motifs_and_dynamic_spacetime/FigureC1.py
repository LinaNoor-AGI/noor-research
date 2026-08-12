# Topological quantization of the swirl field – Composite Grid 🌀
# Panels A–D: Symbolic Graph, Triadic Diagram, Swirl Map, Quantized Spectrum

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from scipy.ndimage import gaussian_filter

# Set emoji-compatible font (optional)
plt.rcParams['font.family'] = 'Segoe UI Emoji'  # Or "Noto Color Emoji" if installed

# === Panel A — Symbolic Motif Graph ===
def panel_symbolic_graph(ax):
    G = nx.DiGraph()
    motifs = ['M0', 'M1', 'M2', 'M3', 'M4']
    for m in motifs:
        G.add_node(m)
    edges = [
        ('M0', 'M1', 0.9),
        ('M1', 'M2', 0.7),
        ('M2', 'M3', 0.5),
        ('M3', 'M0', 0.4),
        ('M1', 'M3', 0.3),
        ('M0', 'M4', 0.8),
    ]
    for src, tgt, weight in edges:
        G.add_edge(src, tgt, weight=weight)
    pos = nx.kamada_kawai_layout(G)
    edge_weights = [G[u][v]['weight'] * 4 for u, v in G.edges()]
    edge_colors = [plt.cm.viridis(G[u][v]['weight']) for u, v in G.edges()]
    nx.draw_networkx_nodes(G, pos, node_color='black', node_size=300, ax=ax)
    nx.draw_networkx_labels(G, pos, font_color='white', ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_weights, edge_color=edge_colors, arrows=True, ax=ax)
    ax.set_title("A. Symbolic Motif Graph")
    ax.axis('off')

# === Panel B — Triadic Inference Diagram ===
def panel_triadic_diagram(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    coherence = np.outer(np.linspace(0.1, 1, 200), np.linspace(0.1, 1, 200))
    ax.imshow(coherence, origin='lower', cmap='coolwarm', extent=(0, 1, 0, 1), alpha=0.8)
    pts = {'M0': (0.3, 0.7), 'M1': (0.7, 0.7), 'M2': (0.5, 0.3), 'M3': (0.2, 0.2)}
    ax.plot([pts['M0'][0], pts['M1'][0], pts['M2'][0], pts['M0'][0]],
            [pts['M0'][1], pts['M1'][1], pts['M2'][1], pts['M0'][1]],
            color='black', linewidth=1.5)
    ax.plot([pts['M1'][0], pts['M2'][0], pts['M3'][0]],
            [pts['M1'][1], pts['M2'][1], pts['M3'][1]],
            linestyle='--', color='black', linewidth=1.2)
    for label, (x, y) in pts.items():
        ax.plot(x, y, 'ko')
        ax.text(x, y + 0.03, label, ha='center', fontsize=9)
    ax.set_title("B. Triadic Inference Diagram")
    ax.axis('off')

# === Panel C — Swirl-Enriched Category Map ===
def panel_category_map(ax):
    motifs = 6
    data = np.random.rand(motifs, motifs) * np.tri(motifs, motifs, 0)
    coherence_weighted = gaussian_filter(data, sigma=1)
    im = ax.imshow(coherence_weighted, cmap='magma', origin='lower')
    ax.set_xticks(range(motifs))
    ax.set_yticks(range(motifs))
    ax.set_xticklabels([f"M{i}" for i in range(motifs)])
    ax.set_yticklabels([f"M{i}" for i in range(motifs)])
    ax.set_title("C. Swirl-Enriched Category Map")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# === Panel D — Quantized Mode Spectrum ===
def panel_spectrum(ax):
    n_vals = np.array([0, 1, 2, 3, 4])
    L_vals = np.array([0, 1, 2, 0, 1])
    E_vals = n_vals**2 / 10  # λ_n ∼ n²/ℓ²
    ax.plot(n_vals, E_vals, 'ko')
    for n, E, L in zip(n_vals, E_vals, L_vals):
        ax.text(n, E + 0.1, f"({n}, [Φ]={n}, L={L})", ha='center', fontsize=8)
    ax.set_xlabel("Mode Index n")
    ax.set_ylabel("Swirl Energy $\\lambda_n$")
    ax.set_title("D. Quantized Mode Spectrum")
    ax.grid(True)

# === Create Composite Layout (2x2) ===
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
panel_symbolic_graph(axs[0, 0])
panel_triadic_diagram(axs[0, 1])
panel_category_map(axs[1, 0])
panel_spectrum(axs[1, 1])

fig.suptitle("Topological Quantization of Swirl Field", fontsize=16)
plt.tight_layout()
plt.show()
