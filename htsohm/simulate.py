# standard library imports
import os
import shlex
import shutil
import subprocess

# related third party imports
import numpy as np

# local application/library specific imports
from htsohm import config
from htsohm import simulation
from htsohm.db import Material, session

def get_bins(material):
    """Returns methane_loading_bin, surface_area_bin, and void_fraction_bin.
    Each material is sorted into a bin corresponding to its combination of structure-properties.
    First, the structure property space is subdivided into arbitrary quadrants, or bins, then
    the simulated properties for a particular material are used to assigned it to a particular
    bin."""

    methane_loading = material.ml_absolute_volumetric_loading
    surface_area = material.sa_volumetric_surface_area
    void_fraction = material.vf_helium_void_fraction
    ############################################################################
    # assign arbitrary maxima and subdivide the parameter space.
    bins = config['number-of-convergence-bins']
    ml_min = 0.
    ml_max = 350.
    sa_min = 0.
    sa_max = 4500.
    vf_min = 0.
    vf_max = 1.
    ml_step = ml_max / float(bins)
    sa_step = sa_max / float(bins)
    vf_step = vf_max / float(bins)
    ml_edges = np.arange(ml_min, ml_max + ml_step, ml_step)
    sa_edges = np.arange(sa_min, sa_max + sa_step, sa_step)
    vf_edges = np.arange(vf_min, vf_max + vf_step, vf_step)

    ############################################################################
    # assign material to its respective bin
    for i in range( bins ):
        if surface_area >= sa_edges[i] and surface_area <= sa_edges[i + 1]:
            sa_bin = i
        if methane_loading >= ml_edges[i] and methane_loading <= ml_edges[i + 1]:
            ml_bin = i
        if void_fraction >= vf_edges[i] and void_fraction <= vf_edges[i + 1]:
            vf_bin = i
    print("\nBINS\t%s\t%s\t%s\n" % (ml_bin, sa_bin, vf_bin))

    results = {}
    results['ml_bin'] = ml_bin
    results['sa_bin'] = sa_bin
    results['vf_bin'] = vf_bin
    return results

def run_all_simulations(material):
    """Simulate helium void fraction, methane loading, and surface area.

    For a given material (id) three simulations are run using RASPA. First a helium void fraction
    is calculated, and then it is used to run a methane loading simulation (void fraction needed to
    calculate excess v. absolute loading). Finally, a surface area is calculated and the material is
    assigned to its appropriate bin."""

    ############################################################################
    # run helium void fraction simulation
    results = simulation.helium_void_fraction.run(material.run_id, material.uuid)
    material.update_from_dict(results)

    ############################################################################
    # run methane loading simulation
    results = simulation.methane_loading.run(material.run_id,
                                             material.uuid,
                                             material.vf_helium_void_fraction)
    material.update_from_dict(results)

    ############################################################################
    # run surface area simulation
    results = simulation.surface_area.run(material.run_id, material.uuid)
    material.update_from_dict(results)

    ############################################################################
    # assign material to bin
    results = get_bins(material)
    material.methane_loading_bin    = float(results['ml_bin'])
    material.surface_area_bin       = float(results['sa_bin'])
    material.void_fraction_bin      = float(results['vf_bin'])
