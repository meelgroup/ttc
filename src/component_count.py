from .global_storage import gbl
from .utils import *
from collections import defaultdict
from z3 import sat
from .polytope_bv import Polytope

def create_all_polytope_smt_filenames(num):
    filenames = []
    random_prefix = ''.join(random.choice(string.ascii_letters)
                            for _ in range(8))
    for i in range(num):
        filename = f"{random_prefix}_cube{i+1}.smt2"
        filenames.append(filename)
    log(f"{gbl.time()} Created {len(filenames)} polytope files", 2)
    return filenames

def process_cubes_componentcount(cubes, mapping):
    numcubes = len(cubes)
    sat_polytopes = []
    if gbl.logic != "lra":
        raise ValueError("Component counting only makes sense for LRA logic.")
    for i in range(numcubes):
        polytope = Polytope.create_polytope_from_cube(cubes[i], mapping)
        polytope_smt = polytope.to_smt_lra(solve  = True)
        if polytope_smt == sat:
            sat_polytopes.append(polytope)
    assert len(sat_polytopes) > 0, "No satisfiable polytopes found."
    log(f"{gbl.time()} Found {len(sat_polytopes)} satisfiable polytopes, now running joint satisfiablility", 2)

    # Create a graph where nodes are polytopes and edges represent joint satisfiability
    graph = defaultdict(list)
    for i, polytope in enumerate(sat_polytopes):
      for j, other_polytope in enumerate(sat_polytopes):
        if i != j and polytope.check_joint_satisfiability(other_polytope):
          graph[i].append(j)
          graph[j].append(i)
    log(f"{gbl.time()} Done running joint satisfiability. Running Prim's", 2)

    # Function to find connected components using Prim's algorithm
    def find_connected_components(graph, num_nodes):
      visited = [False] * num_nodes
      components = 0

      def prim(start):
        heap = [start]
        while heap:
          node = heap.pop()
          if not visited[node]:
            visited[node] = True
            for neighbor in graph[node]:
              if not visited[neighbor]:
                heap.append(neighbor)

      for node in range(num_nodes):
        if not visited[node]:
          components += 1
          prim(node)

      return components

    # Count disjoint components
    num_components = find_connected_components(graph, len(sat_polytopes))
    log(f"{gbl.time()} Done running Prim's", 2)
    return num_components

