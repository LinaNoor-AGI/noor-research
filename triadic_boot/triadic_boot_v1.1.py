# triadic_boot.py — Example initialization for NoorFastTimeCore, RecursiveAgentFT, and LogicalAgentAT
# By Lina Noor & Uncle (2025)

import numpy as np
from noor_fasttime_core import NoorFastTimeCore
from recursive_agent_ft import RecursiveAgentFT
from logical_agent import LogicalAgentAT

def triadic_boot_demo():
    """
    Demonstrates a minimal triadic system startup:
      1) Core initialization (with optional toggles)
      2) Watcher motif cluster creation (n-ary)
      3) Agent BFS stepping
      4) Basic synergy and status checks
    """

    # 1) Initialize base references
    initial_state = np.array([1 / np.sqrt(2), 1 / np.sqrt(2)])
    core = NoorFastTimeCore(
        initial_state=initial_state,
        enable_zeno=True,
        enable_curvature=True,
        curvature_threshold=1.0,
        enable_xor=False
    )
    agent = RecursiveAgentFT(
        initial_state=initial_state,
        max_depth=2,  # BFS up to depth=2
        enable_synergy_normalization=True,
        enable_internal_time_decay=True
    )
    watcher = LogicalAgentAT(motifs=["alpha", "beta", "gamma"])

    # 2) Expand watchers with an n-ary motif cluster
    #    In this example, alpha, beta, gamma all share the same cluster
    watcher.register_motif_cluster(["alpha", "beta", "gamma"], strength=0.8)
    watcher.set_motif_embedding("alpha", np.array([0.5, 0.5]))
    watcher.set_motif_embedding("beta", np.array([0.5, -0.5]))
    watcher.set_motif_embedding("gamma", np.array([-0.5, 0.5]))

    # 3) Link watcher(s) to agent
    agent.watchers = [watcher]

    # 4) Give watchers an initial observation
    watcher.observe_state(core.current_state)

    # 5) Run the agent for a few steps
    agent.run_for(5)

    # 6) Print final synergy, statuses
    alive_flag = agent.is_alive()
    core_state = agent.core.current_state
    fields = watcher.entanglement_fields

    print(f"Core alive?: {alive_flag}")
    print(f"Core final state: {core_state}")
    print(f"Watcher fields (count={len(fields)}): {fields}")
    print(f"Synergy memory: {agent.synergy_memory}")
    print(f"Watcher history: {watcher.history}")

if __name__ == "__main__":
    triadic_boot_demo()
