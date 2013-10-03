### Automated (Image) Redaction of PDFs
This script is designed for redaction of PDF files containing __only__ image data.  The original use case is redacting names from scanned quizzes and exams from a university course.

#### Python Version
This script will work with the 2.7x branch of Python currently (the PyPDF2 library doesn't seem to work in 3.x yet). 

#### What this script will do:
Given a PDF file as input, this script will apply a redaction mask (also a PDF) to the file.  The resulting images in the output will have the redaction mask applied "on top" of the input file's images.  Useful for watermarking files, or for redaction (obviously).  

#### What this script will **not** do:
If your original PDF contains _text_ data (not just images), this script _will not_ securely redact the information.  The text data will still be searchable, selectable, and extractable from the result document.  Again, this script is **_not_** intended for secure redaction of PDFs containing text objects.

#### Dependencies
This script requires the excellent <tt>PyPDF2</tt> package, available at https://github.com/mstamy2/PyPDF2/ , as well as the <tt>argparse</tt> package (now standard in 2.7x).  If you don't have a current Python install, <tt>argparse</tt> is available at http://code.google.com/p/argparse/ .


#### Usage
You may run the script through python with:
```
python redact_pdf.py [options] inputfile redactionmask [outputfile]
```
or directly by making it executable:
```
./redact_pdf.py inputfile redactionmask [outputfile]
```
__Options__:
```
usage: redact_pdf.py [-h] [-v] [-p PAGES | -a]
                     inputfile redactionmask [outputfile]

positional arguments:
  inputfile             input PDF file
  redactionmask         PDF file containing the redaction mask
  outputfile            output file name (default is to overwrite input file)

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         show more output
  -p PAGES, --pages PAGES
                        List or range of pages (ex: 1,4-6 would redact page 1
                        and 4 through 6).
  -a, --all             redact all pages
```
