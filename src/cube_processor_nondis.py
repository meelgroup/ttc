import sys
import math
import random
import pandas as pd

from .utils import *
from .global_storage import gbl
from .latte_runner import run_volesti_on_matrix, run_volesti_sampling_on_matrix
from .polytope_bv import Polytope


def volume_of_polytope(polytopefile, epsilon_prime, delta_prime):
    log(f"Calculating volume of polytope {polytopefile}", 2)
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
  numcubes = len(cubes)
  filenames = create_all_polytope_filenames(numcubes)
  dimensions = len(mapping.constraint_matrix.columns)
  thresh = max(12*math.log(24.0/delta)/(eps**2), 6.0*(math.log(6.0/delta) + math.log(numcubes)))
  log(f"Threshold: {thresh}", 2)
  p = 1
  # X = [[float(format(0, ".3f")) for _ in range(dimensions)] for _ in range(int(thresh))]
  X = []

  for i in range(numcubes):
    log(f"--- Processing cube {i+1}/{numcubes}", 2)
    polytope = Polytope.create_polytope_from_cube(cubes[i], mapping, filenames[i])
    volume = volume_of_polytope(filenames[i], eps, delta)
    if volume <= 0:
      log(f"Volume of polytope is zero, skipping", 2)
      continue
    prevXlen = len(X)
    X = [s for s in X if not polytope.is_in_polytope(s)]
    log(f"Volume of polytope: {volume}", 2)
    log(f"Number of points in X: {len(X)}, removed {prevXlen - len(X)}", 2)
    prevXlen = len(X)
    while (p*volume) > thresh:
      X = [s for s in X if random.random() >= 0.5]
      p = p/2
    log(f"Number of points in X: {len(X)}, removed {prevXlen - len(X)}", 2)
    prevXlen = len(X)
    N = np.random.poisson(p*volume)
    while (N + len(X)) > thresh:
      X = [s for s in X if random.random() >= 0.5]
      p = p/2
      N = np.random.poisson(p*volume)
    log(f"Number of points in X: {len(X)}, removed {prevXlen - len(X)}", 2)
    S = generate_samples(filenames[i], N, eps, delta)
    X.extend(S)
    log(f"Number of point in X: {len(X)} samples added: {N}", 2)

  return len(X)/p
