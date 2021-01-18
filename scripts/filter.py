import re
import sys

# python3.6 scripts/filter.py data/pdf-txt/Genus_species.txt

fname = sys.argv[-1]
species = fname.replace('_', ' ').replace('.txt', '')
species = fname.replace('data/pdf-txt/', '')

# get paragraph endings
with open(fname, 'r') as f:
    full_lines = f.readlines()

line_lengths = []
for line in f.readlines():
    line_lengths.append(len(line)

avg_line_length = sum(line_lengths) / len(line_lengths)

bookend_lines = []
for i, line in enumerate(full_lines)):
    if len(line) < (avg_line_length - 10):
        bookend_lines.append(i)
    

    

# general characters
gc_pattern = 'GENERAL CHARACTERS.*DISTRIBUTION'
gc_match = re.search(gc_pattern, full_text)
if not gc_match:
    raise ValueError('gen chars section fd up' + species)
    




# distribution



# form and function



# reproduction/ontogeny



# ecology



# behavio(u)r
