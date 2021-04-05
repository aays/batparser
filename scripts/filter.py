"""
filter.py - filter pdf-to-txt conversions for desired sections

outfile is set to append mode, so the same file could have
sections from multiple files written

usage for single file:
python3.6 filter.py [infile.txt] [outfile.txt]

usage for multiple files:
for fname in dir/*; do
    python3.6 ${fname} [outfile.txt]
done
"""

import re
import sys
from tqdm import tqdm

# python3.6 scripts/filter.py data/pdf-txt/Genus_species.txt data/pdf-txt/all.txt
# for fname in data/pdf-txt/*; do python

fname = sys.argv[-2]
outname = sys.argv[-1]
species = fname.replace('_', ' ').replace('.txt', '').replace('data/pdf-txt/', '')

headers = ['DIAGNOSIS', 'CONTEXT AND CONTENT', 
    'GENERAL CHARACTERS', 'DISTRIBUTION', 'FORM AND FUNCTION',
    'GENETICS', 'ONTOGENY AND REPRODUCTION', 'ECOLOGY',
    'CONSERVATION', 'BEHAVIOR', 'ANIMAL HUSBANDRY', 'LITERATURE CITED']

headers_keep = ['GENERAL CHARACTERS', 'DISTRIBUTION', 'FORM AND FUNCTION',
    'ONTOGENY AND REPRODUCTION', 'ECOLOGY', 'CONSERVATION', 
    'BEHAVIOR']

headers_exclude = ['DIAGNOSIS', 'CONTEXT AND CONTENT', 'GENETICS',
    'ANIMAL HUSBANDRY', 'LITERATURE CITED']

text_dict = {}
position_dict = {}

# get raw text
print('[batparser] parsing {}'.format(fname))
with open(fname, 'r') as f:
    raw_text = f.read()

# populate dict
print('[batparser] finding section locations...')
raw_text_upper = raw_text.upper()
for header in tqdm(headers):
    # try regex
    pattern = r'\n{}\n'.format(header)
    match = re.search(pattern, raw_text_upper)
    if match:
        header_idx = match.span()[0]
    else: # header not at start of line - fall back on find
        header_idx = raw_text_upper.find(header)

    if header_idx == -1: # used .find and nothing came up
        continue
    elif header_idx > 0:
        text_dict[header] = ''
        position_dict[header] = header_idx
    
# account for ecology and behaviour being close together
if 'ECOLOGY' in position_dict and 'BEHAVIOR' in position_dict:
    diff = abs(position_dict['ECOLOGY'] - position_dict['BEHAVIOR'])
    if diff < 40: # hardcoded, should catch this I guess?
        lower_val = min(position_dict['ECOLOGY'], position_dict['BEHAVIOR'])
        position_dict['ECOLOGY AND BEHAVIOR'] = lower_val
        _ = position_dict.pop('ECOLOGY')
        _ = position_dict.pop('BEHAVIOR')
    else:
        pass

# sort by position
keys_sorted = sorted(position_dict.items(), key=lambda item: item[1])

# write
print('[batparser] writing to file...')
with open(outname, 'a') as f:
    f.write('\n')
    f.write('-' * 15 + '\n')
    f.write(species.capitalize() + '\n')
    f.write('-' * 15 + '\n')
    f.write('found headers:\n')
    f.write(', '.join([i[0] for i in keys_sorted]) + '\n')

    for i, items in tqdm(enumerate(keys_sorted)):
        header, pos = items
        if header in headers_exclude:
            continue
        try:
            next_pos = keys_sorted[i + 1][1]
        except IndexError: # reached end
            break
        f.write('\n' + raw_text[pos:next_pos])
        f.write('\n')

print('[batparser] {} written to {}'.format(species.capitalize(), outname))

