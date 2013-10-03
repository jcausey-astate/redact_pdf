## ###########################################################################################
# Redact a PDF by applying a redaction mask (also a PDF file) to the specified pages.
# Default is to save output back over the input file, and to apply the redaction mask to
# the first page only.  This can be changed in options.  Also, if redaction mask is multi-
# paged, it will be applied page-for-page to the input file.
#
# IMPORTANT SECURITY NOTE:
#     The redaction performed here will be secure only if the underlying data is image 
#     data - NOT if the underlying data is PDF text.  This software is designed to be
#     used to redact images from scanned documents, not for PDF files generated directly
#     from software.  PDF text that is under the redaction mark will STILL BE RECOVERABLE,
#     SEARCHABLE, AND SELECTABLE.
#
# usage: redact.py [opts] inputfile redactionmask [outputfile]
#     opts:
#         -h              show usage
#         -v  --verbose   show more output
#         -p  --page      page(s) to apply mask to (default is page 1 only)
#         -a  --all       apply mask to all pages
#     note:
#         The -a and -p options are meaningless if the redactionmask has multiple pages.
#         If that is the case, pages from the redactionmask will be applied to the input
#         on a page-by-page basis (until one file or the other runs out of pages).
#
# License:    Copyright (c) 2013 Jason L Causey, 
#             Distributed under the MIT License (MIT):
#
#             Permission is hereby granted, free of charge, to any person obtaining a copy
#             of this software and associated documentation files (the "Software"), to deal
#             in the Software without restriction, including without limitation the rights
#             to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#             copies of the Software, and to permit persons to whom the Software is
#             furnished to do so, subject to the following conditions:
#
#             The above copyright notice and this permission notice shall be included in
#             all copies or substantial portions of the Software.
#
#             THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#             IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#             FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#             AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#             LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#             OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#             THE SOFTWARE.
# ############################################################################################

from   PyPDF2 import PdfFileWriter, PdfFileReader
import argparse, os, uuid

verbose = False # Global verbosity indicator

def rangeexpand(txt):
    """
    List range expansion function 
    (found at http://rosettacode.org/wiki/Range_expansion#Python )
    """
    lst = []
    for r in txt.split(','):
        if '-' in r[1:]:
            r0, r1 = r[1:].split('-', 1)
            lst += range(int(r[0] + r0), int(r1) + 1)
        else:
            lst.append(int(r))
    return lst

def vprint(msg):
    """
    Print message to the screen only if verbose mode is activated.
    """
    global verbose
    if(verbose):
        print(msg)

# Set up the argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", default=False,
                    help="show more output")
pagegroup = parser.add_mutually_exclusive_group()
pagegroup.add_argument("-p", "--pages", type=str, default="1",
                    help="List or range of pages (ex: 1,4-6 would redact page 1 and 4 through 6).")
pagegroup.add_argument("-a", "--all", action="store_true",
                    help="redact all pages")
parser.add_argument("inputfile", type=str,
                    help="input PDF file")
parser.add_argument("redactionmask", type=str,
                    help="PDF file containing the redaction mask")
parser.add_argument("outputfile", type=str, nargs="?", default="",
                    help="output file name (default is to overwrite input file)")
# Get incoming options and open files:
args             = parser.parse_args()
inputfile        = args.inputfile
pdfout           = PdfFileWriter()
input_stream     = file(args.inputfile, "rb")
pdfin            = PdfFileReader(input_stream)
redaction_mask   = PdfFileReader(file(args.redactionmask, "rb"))
redact_multipage = True           if redaction_mask.getNumPages() > 1   else False
outputfile       = args.inputfile if args.outputfile == ""              else args.outputfile
verbose          = True           if args.verbose                       else False
# If the input file == the output file, PyPDF2 has an issue where you can't actually overwrite
# on-the-fly, (it seems to do a lazy-read of the files that contribute to the output document)
# so generate a temporary output file name:
overwrite_input_file = False
if(inputfile == outputfile):
    # Generated by appending a UUID to the end of the filename
    outputfile           = outputfile + "." + str(uuid.uuid4())  
    overwrite_input_file = True

# Determine list of pages to redact:
if(not args.all):
    redact_pages     = map(lambda x: x - 1, rangeexpand(args.pages))
else:
    redact_pages     = range(pdfin.getNumPages())
# If the redactionmask file has multiple pages, it will determine which pages
# we redact:
multi_page_mask  = False
if(redaction_mask.getNumPages() > 1):
    vprint("Applying multi-page redaction mask from " + args.redactionmask)
    redact_pages     = range(min(pdfin.getNumPages(), redaction_mask.getNumPages()))
    multi_page_mask  = True
redact_pages.sort()
redact_pages = filter(lambda x: x < pdfin.getNumPages(), redact_pages)

vprint("Input file: " + inputfile + " - " + str(pdfin.getNumPages()) + " pages.")
vprint("Redacting pages: " + str(map(lambda x: x + 1, redact_pages)))

# Process the input file (only if it has more than 0 pages):
if(pdfin.getNumPages() > 0):
    # Copy over every page of the input document:
    for i in range(pdfin.getNumPages()):
        pdfout.addPage(pdfin.getPage(i))
        # If redaction should happen on this page, apply it:
        if(len(redact_pages) > 0 and redact_pages[0] == i):
            redact_pages.pop(0)
            if(not multi_page_mask):
                pdfout.getPage(i).mergePage(redaction_mask.getPage(0))  # Redact from single-page mask
            else:
                pdfout.getPage(i).mergePage(redaction_mask.getPage(i))  # Redact from multi-page mask
    # finally, write "pdfout" to output file name
    output_stream = file(outputfile, "wb")
    pdfout.write(output_stream)
    output_stream.close()
    del pdfout
    del pdfin    
    input_stream.close()
    # If we are overwriting the input file, move the temporary output file now:
    if(overwrite_input_file):
        os.rename(outputfile, inputfile)
# Finished!