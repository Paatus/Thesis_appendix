IMAGE EXTRACTION
================

Description:
------------

A tool for extracting images from pdf, docx and pptx files.

Compile instructions:
---------------------

Make sure you have the following libraries installed:

* Poppler glib
* Cairo
* libarchive

then run these commands:

1. `mkdir build`
2. Now change directory into the build folder you just created and run these commands.
2. `cmake ..` and make sure there are no errors, if there are errors, you have probably missed a library.
3. `make`

You should now have a `ImgPopper` executable in the build folder

Run instructions:
-----------------
To see the different options run `ImgPopper --help`

### Example:
If your pdfs, docxs and pptxs are in the folder `pdfs` in the current directory and you want the images to be saved in `images` run this command.

`ImgPopper pdfs/ -d images/`
