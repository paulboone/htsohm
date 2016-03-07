import sys

from generate import *
from find_missing import *
from binning import *
from mutate import *

%run ./bin/screen.ipy
%run ./bin/cat_data.ipy
%run ./bin/dummy_screen.ipy
%run ./bin/dummy_test.ipy




# parameters...

HTSOHM_dir = '~/HTSOHM-dev' #specifies HTSOHM directory

sys.path.insert(0, './bin') #adds HTSOHM modules to Python


number_of_atom_types = 4
number_of_materials = 50

bins = 5
mutation_strength = 0.2




####
# seed population

generate(number_of_materials,                         # create seed population
         number_of_atom_types)



screen(HTSOHM_dir, 'gen0', 0, number_of_materials)    # screen seed

# WAIT FOR JOBS

prep_gen0(HTSOHM_dir, number_of_materials)            # collect output
find_missing('gen0')                                  # find missing data points




####
# first generation

n_child = number_of_materials

bin_count_gen0, bin_IDs_gen0 = bin3d('gen0', bins)    # bin library

p_list_gen0 = pick_parents('gen0',                    # select parents
                           bin_count_gen0,
                           bin_IDs_gen0,
                           n_child)

dummy_screen(HTSOHM_dir, 'gen0')                      # dummy test, screen

# WAIT FOR JOBS

dummy_test(HTSOHM_dir, 'gen0')                        # dummy test, check output

firstS('gen0', mutation_strength, bins)               # set mutation strength(s)
mutate('gen0', number_of_atom_types, 'gen1')          # mutate gen0, create gen1

screen(HTSOHM_dir, 'gen1', 1 * number_of_materials,   # screen gen1
       number_of_materials)

# WAIT FOR JOBS

prep4mut(HTSOHM_dir, 'gen1', 1 * number_of_materials, # collect output
         number_of_materials, 'gen0', 'tgen1')

find_missing('tgen1')                                 # find missing data points




####
# second generation
