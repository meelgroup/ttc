import sys
import math
import random
import pandas as pd

from .utils import *
from .global_storage import gbl
from .latte_runner import run_volesti_on_matrix, run_volesti_sampling_on_matrix, run_tool_on_matrix
from .polytope_bv import Polytope


def volume_of_polytope(polytopefile, epsilon_prime, delta_prime):
    log(f"Calculating volume of polytope {polytopefile}", 3)
    result = 0
    if gbl.exactvolume:
        result = run_tool_on_matrix(
            polytopefile, toolname="latteintegrate")
    else:
        result = run_volesti_on_matrix(polytopefile)
    return result


def create_all_polytope_filenames(num):
    filenames = []
    random_prefix = ''.join(random.choice(string.ascii_letters)
                            for _ in range(8))
    for i in range(num):
        filename = f"{random_prefix}_cube{i+1}.ine"
        filenames.append(filename)
    log(f"Created {len(filenames)} polytope files", 2)
    return filenames

def generate_samples(polytopefile, n, epsilon_prime, delta_prime):
    log(f"Generating samples for polytope {polytopefile}", 3)
    result = run_volesti_sampling_on_matrix(polytopefile, n)
    return result

def process_cubes_nondisjoint(cubes, mapping, eps = 0.8, delta = 0.2):
  np.random.seed(gbl.seed)
  random.seed(gbl.seed)
  mvc_eps = eps
  numcubes = len(cubes)
  filenames = create_all_polytope_filenames(numcubes)
  dimensions = len(mapping.constraint_matrix.columns)
  if gbl.exactvolume:
    mvc_eps = eps/2
  else:
    mvc_eps = eps
  thresh = max(12*math.log(24.0/delta)/(mvc_eps**2), 6.0 *
               (math.log(6.0/delta) + math.log(numcubes)))
  log(f"Threshold: {thresh}", 2)
  p = 1
  # X = [[float(format(0, ".3f")) for _ in range(dimensions)] for _ in range(int(thresh))]
  X = []
  polytopes = []
  volumes = []
  S = []
  max_volume = 0
  num_zero_volume = 0

  log(f"{gbl.time()} Getting volumes for {numcubes} cubes", 1)

  for i in range(numcubes):
    polytope = Polytope.create_polytope_from_cube(
        cubes[i], mapping, filenames[i])
    volume = volume_of_polytope(filenames[i], eps, delta)
    if volume <= 0:
      log(f"Volume of polytope is zero, skipping", 2)
      num_zero_volume += 1
      continue
    polytopes.append(polytope)
    volumes.append(volume)
    if volume > max_volume:
      max_volume = volume

  log(f"{gbl.time()} Got volumes for {numcubes} cubes", 1)

  log(f"Skipping {num_zero_volume} polytopes out of {numcubes} where volume is zero", 2)

  numeffectivecubes = len(volumes)
  i = 0
  current_len = len(volumes)
  while i < current_len:
    if volumes[i] <= max_volume * 0.001:
      volumes.pop(i)
      polytopes.pop(i)
    else:
      i += 1
    current_len = len(volumes)

  log(f"Skipping {numeffectivecubes - len(volumes)} polytopes out of {numeffectivecubes} where volume is negligible", 2)

  # num_remove_inside = 0
  # num_remove_poiss_1 = 0
  # num_remove_poiss_2 = 0

  for i in range(len(polytopes)):
    polytope = polytopes[i]
    volume = volumes[i]
    log(f"--- {gbl.time()} Processing cube {i+1}/{len(polytopes)}", 2)
    if volume <= 0:
      log(f"Volume of polytope is zero, skipping", 2)
      continue
    prevXlen = len(X)
    X = [s for s in X if not polytope.is_in_polytope(s)]
    log(f"Volume of polytope: {volume}", 2)
    log(
        f"Number of points in X: {len(X)}, removed {prevXlen - len(X)}  [inside this polytope]", 2)
    prevXlen = len(X)
    while (p*volume) > thresh:
      X = [s for s in X if random.random() >= 0.5]
      p = p/2
    log(f"Number of points in X: {len(X)}, removed {prevXlen - len(X)} [make p < thresh/vol]", 2)
    prevXlen = len(X)
    N = np.random.poisson(p*volume)
    while (N + len(X)) > thresh:
      X = [s for s in X if random.random() >= 0.5]
      p = p/2
      N = np.random.poisson(p*volume)
    log(f"Number of points in X: {len(X)}, removed {prevXlen - len(X)} [make N + |X| < thresh]", 2)
    if N == 0:
      log(f"Number of samples asked for is zero, skipping", 2)
      continue
    S = generate_samples(filenames[i], N, eps, delta)
    if S is None:
      log(f"Sampling failed for polytope {i+1}, skipping!!!", 2)
      continue
    X.extend(S)
    log(f"Number of point in X: {len(X)} samples added: {N}", 2)

  return len(X)/p
