### 11.3 Architectural Pseudocode: The Primary Artifact

The architecture consists of four core classes that together implement the ontology-free navigation framework:

1. **Guidepost:** A symbolic structure containing coordinates, relations, a pointer, a coherence weight, and an optional basin hint.
2. **GuidepostStore:** A container that manages guideposts, supports nearest-neighbor queries, and maintains the relation graph.
3. **CoherentNavigator:** The reasoning engine that performs multi-path descent, detects Convergence Boundaries, and manages reconstruction.
4. **BoundaryEvent:** A record of a Convergence Boundary crossing, including the time, paths involved, and detector that triggered the event.

The following interfaces are mandatory for any implementation claiming to realize this architecture:

- `add(payload, pointer, basin_hint=None) → gid`: Adds a new guidepost to the store.
- `nearest(coord, k) → List[Guidepost]`: Returns the k nearest guideposts to a given coordinate.
- `descend(seed_coord, n_paths, max_steps) → (List[Path], List[BoundaryEvent])`: Performs multi-path descent from a seed coordinate and returns all paths and detected boundary events.
- `reconstruct(path) → List[payload]`: Retrieves and reconstructs the raw data associated with a given path.

These interfaces are self-contained: they make no reference to static totality, Library, or any ontological substrate beyond ordinary computational objects. This is now a mandatory contract for any practical claim of the framework.

**Formal Reference.**

$$\mathrm{GuidepostStore}:\ G = \{g_i\}$$

*The guidepost store is a finite set of guideposts.*

$$\mathrm{nearest}(c, k) = \mathrm{argmin}_{g \in G} \|c - g.\mathrm{coords}\|_2\ \mathrm{(top}\ k\mathrm{)}$$

*Nearest-neighbor retrieval returns the k guideposts whose stored coordinates are closest to the query coordinate under the Euclidean metric.*

$$\mathrm{descend}(c_0, n, m) = \{\gamma_j : [0, m] \rightarrow \mathcal{M} \mid j = 1..n,\ \gamma_j(0) = c_0\}$$

*Multi-path descent generates n coherent paths, each beginning at the seed coordinate and evolving over m steps.*

$$\mathrm{BoundaryEvent} = (t, \mathrm{paths}, \mathrm{detector}, \mathrm{metadata})$$

*A boundary event records the time of detection, the paths involved, the detector that fired, and detector-specific metadata.*

**GuidepostStore**

*Manages guideposts, supports nearest-neighbor queries, and maintains the relation graph.*

```python
class GuidepostStore:
    def __init__(self):
        self.guideposts = {}       # id → Guidepost
        self.coords = []           # list of coordinate vectors
        self.ids = []              # list of ids matching coords order
        self.relations = {}        # gid → list of Relation
    
    def add(self, payload, pointer, basin_hint=None) -> str:
        # Create a new guidepost with a unique id
        # Extract coordinates from payload (implementation-dependent)
        # Store in guideposts, coords, ids
        # If basin_hint is provided, store it; otherwise, mark as unlabeled
        # Return the new guidepost id
        pass
    
    def nearest(self, coord, k=10) -> List[Guidepost]:
        # Compute Euclidean distances from coord to all stored coords
        # Return the k closest guideposts
        pass
    
    def get_relations(self, gid) -> List[Relation]:
        return self.relations.get(gid, [])
    
    def add_relation(self, source_id, target_id, rel_type, strength):
        # Add a relation to both source and target (bidirectional)
        pass
```

**CoherentNavigator**

*The reasoning engine that performs multi-path descent, detects Convergence Boundaries, and manages reconstruction.*

```python
class CoherentNavigator:
    def __init__(self, store: GuidepostStore, I_N: float):
        self.store = store
        self.I_N = I_N
        self.boundary_history = []
    
    def descend(self, seed_coord, n_paths=8, max_steps=100):
        # For each of n_paths, generate a coherent descent path:
        #   - Start at seed_coord
        #   - At each step, select the nearest guidepost with coherence >= I_N
        #   - Add some stochastic exploration (guided random walk)
        #   - Stop when max_steps reached or no coherent transitions available
        #   - If a path enters a region where all continuations lead to the same attractor,
        #     record a BoundaryEvent
        # Return: List[Path], List[BoundaryEvent]
        pass
    
    def reconstruct(self, path) -> List[dict]:
        # For each guidepost in the path, retrieve the associated payload
        # using the pointer in each guidepost
        # Return the reconstructed data as a list of payloads
        pass
    
    def detect_boundary(self, state, n_paths=8, patience=4, unsupervised=True):
        # See Section 7.3.1 for detailed detector specifications
        # Returns a list of detected BoundaryEvent objects
        pass
```

**BoundaryEvent**

*A record of a Convergence Boundary crossing, including the time, paths involved, and detector that triggered the event.*

```python
class BoundaryEvent:
    def __init__(self, time, paths, detector, metadata):
        self.time = time
        self.paths = paths
        self.detector = detector     # 'entropy', 'recurrence', or 'lyapunov'
        self.metadata = metadata    # dict of detector-specific values
```

With the four core classes defined, the architecture's primary artifact is complete: a self-contained, ontology-free implementation of symbolic navigation whose interfaces make no reference to any metaphysical substrate. GuidepostStore provides the container, CoherentNavigator provides the reasoning engine, Guidepost provides the unit of representation, and BoundaryEvent provides the record of convergence. The architectural flow that follows will show how these four components compose into a complete reasoning system, and how the Ontology-Free Execution Path operates as the primary path while any metaphysical interpretation remains secondary and optional.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/RFC-AI/rfc-ai-004-reasoning_by_coherent_navigation/markdown/rfc-ai-004-reasoning_by_coherent_navigation-sx.MD) | [INDEX](https://github.com/LinaNoor-AGI/noor-research/blob/main/RFC-AI/rfc-ai-004-reasoning_by_coherent_navigation/markdown/rfc-ai-004-reasoning_by_coherent_navigation-index.MD) | [next_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/RFC-AI/rfc-ai-004-reasoning_by_coherent_navigation/markdown/rfc-ai-004-reasoning_by_coherent_navigation-sx.MD) |
