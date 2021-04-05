'''
convert.py - convert all PDFs in dir to txt files 
using optical character recognition

usage:
python3.6 convert.py [input dir] [output dir]
'''

import sys # input/output
import os # get list of files
import subprocess
import re
from PIL import Image
import cv2
import pytesseract
from tqdm import tqdm

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
for f in file_list:
    if not f.endswith('.pdf'):
        file_list.remove(f)

def get_info(fname):
    '''
    get page numbers and other metrics for each PDF
    
    also returns margins although these are no longer
    needed after we switched to using ocr

    Parameters
    ----------
    fname : str
        name of PDF to get info for

    Returns
    -------
    width : int
        width in px of pages
    height : int
        height in px of pages
    half_width : int
        half of width above - returned for convenience
    page_num : int
        number of pages
    '''
    cmd = ['pdfinfo', '-f', '2', '-l', '2', fname]
    proc = subprocess.Popen(cmd,
            stdout=subprocess.PIPE)
    out, err = proc.communicate()
    out = out.decode('utf-8').split('\n')
    size = [line for line in out if re.search('Page +2 size:', line)][0]
    assert size
    page_num = [line for line in out if line.startswith('Pages:')][0]
    assert page_num
    match = re.search('([0-9]{1,4}) x ([0-9]{1,4})', size)
    if match:
        width = int(match.group(1))
        height = int(match.group(2))
        half_width = int(round(width / 2, 0))
    else:
        raise Exception('getting pdf info failed')
    match = re.search('(Pages: +)([0-9]{1,2})', page_num)
    if match:
        page_num = int(match.group(2))
    else:
        raise Exception('getting pdf info failed')
    return width, height, half_width, page_num
    

def parse(image_path, threshold=False):
    '''
    from stack overflow - I don't know how or why this works
    https://stackoverflow.com/questions/55100037/how-to-extract-text-from-two-column-pdf-with-python

    Parameters
    ----------
    image_path : str
        path to image file to parsr
    threshold : bool
        whether to enable cv2.threshold setting (??)

    Returns
    -------
    text : str
        text of PDF as single str
    '''
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if threshold:
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    filename = '{}.png'.format(os.getpid())
    cv2.imwrite(filename, gray)
    text = pytesseract.image_to_string(Image.open(filename))
    os.remove(filename)
    return text

def main():
    counter = 1
    num_files = len([f for f in file_list if f.endswith('.pdf')])

    for fname in file_list:
        print('[batparser] working on', fname, 
              '- file {} of {}'.format(counter, num_files))
        _, height, half_width, page_num = get_info(input_dir + fname)
        species_name = fname.replace('.pdf', '')
        outname = fname.replace('.pdf', '.txt')
        if os.path.exists(output_dir + outname):
            print('[batparser] file {} exists. skipping...'.format(outname))
            counter += 1
            continue
        cmd_str = 'pdftoppm -f {} -l {} -jpeg {} {}'
        rename_cmd = 'mv {} {}'
        for i in range(page_num):
            i = i + 1 # page numbers are '1-indexed'
            cmd = cmd_str.format(i, i, input_dir + fname, 
                output_dir + species_name)
            proc = subprocess.Popen(cmd.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            out, err = proc.communicate()
            if page_num >= 10:
                if i < 10:
                    i = '0' + str(i)
                else:
                    i = str(i)
            r_cmd = rename_cmd.format(
                output_dir + species_name + '-{}.jpg'.format(i),
                output_dir + species_name + '-{}.jpeg'.format(i))
            proc = subprocess.Popen(r_cmd.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            out, err = proc.communicate()

        # convert images for current paper into text
        if page_num < 10:
            fnames = [
                output_dir + species_name + '-{}.jpeg'.format(i + 1) 
                for i in range(page_num)]
        elif page_num >= 10:
            fnames = [
                output_dir + species_name + '-{}.jpeg'.format('0' + str(i + 1))
                for i in range(9)]
            fnames.extend([
                output_dir + species_name + '-{}.jpeg'.format(i)
                for i in range(10, page_num + 1)])
        # fnames = [subfname for page in fnames_nested for subfname in page]
        with open(output_dir + outname, 'a') as f:
            print('[batparser] converting pages to text...')
            for page_img in tqdm(fnames):
                text = parse(page_img)
                # clean newlines
                text = text.replace('\n\n', '\n')
                text = re.sub(r'(\n +)+', '\n', text)
                f.write(text)
        print('[batparser] cleaning temp files...')
        for page_img in fnames:
            os.remove(page_img) 
                
        print('[batparser] written', outname)
        counter += 1

if __name__ == '__main__':
    main()
