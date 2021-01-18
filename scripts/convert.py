'''
TODO: grab 'halves of pages' sequentially by using margin args

all papers from the journal are formatted the same

ideally - get page dimensions, split width in half, and use
that to determine provide margin arguments - most foolproof
way to do this imo
'''

import sys # input/output
import os # get list of files
# import pdftotext 
import subprocess
# from tqdm import tqdm

# python3.9 scripts/convert.py data/pdf-raw data/pdf-txt
input_dir = sys.argv[-2]
output_dir = sys.argv[-1]

# add leading forward slash if needed
if not input_dir.endswith('/'):
    input_dir += '/'
if not output_dir.endswith('/'):
    output_dir += '/'

# get list of input files
file_list = os.listdir(input_dir)

for fname in file_list:
    print('working on', fname)
    cmd = 'pdftotext -raw {} {}'.format(
        input_dir + fname, output_dir + outname)
    proc = subprocess.Popen(cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    out, err = proc.communicate()
'''
    with open(input_dir + fname, 'rb') as f:
        pdf = pdftotext.PDF(f)

    outname = fname.replace('.pdf', '.txt')

    with open(output_dir + outname, 'w') as f:
        for chunk in pdf:
            chunk = ' '.join(chunk.split())
            f.write(chunk + ' ')
'''
    print('written', outname)
