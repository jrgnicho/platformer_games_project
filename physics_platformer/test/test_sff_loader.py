#!/usr/bin/env python

"""
SSF Extract for python

This utility will read a Elecbyte SFF file (version 1.01) and write the
portrait to the current folder.


leif theden, 2012 - 2015
public domain
"""

from StringIO import StringIO
from PIL import Image
from physics_platformer.resource_management.sff_support import *
from panda3d.core import PNMImage, StringStream
from panda3d.core import Texture
from panda3d.core import LColor
import logging
import sys
import os

def main():

  sff_file =''
  output_dir=''

  if len(sys.argv) >= 2:
    sff_file = sys.argv[1]
  
  else:
    logging.error('Usage: sff-test ssf_file [output_dir]')
    return 
  
  if len(sys.argv) >= 3:
    output_dir = sys.argv[2]
  

  #checking output dir
  if (output_dir != '') and (not os.path.exists(output_dir)):
      os.makedirs(output_dir)
  else:
    logging.info("Output directory not set from command line, skipping image save")

  fh = open(sff_file, 'rb')

  header = sff1_file.parse(fh.read(512))
  print(header)

  next_subfile = header.next_subfile
  count = 0
  while next_subfile and count < header.image_total:
      fh.seek(next_subfile)
      subfile = sff1_subfile_header.parse(fh.read(32))
      next_subfile = subfile.next_subfile

      try:
          buff = StringIO(fh.read(subfile.length))
          image = Image.open(buff)
          
          buff = StringIO()
          image.save(buff,'PNG')
          output = PNMImage()
          if not output.read(StringStream(buff.getvalue()), "i.png"):
            logging.error("Failed to read image from buffer")
            raise ValueError("Invalid image!")
          

          print "Image Group: %i, no: %i, size: %i x %i ,offset: (%i , %i), palette %i"%(subfile.groupno,subfile.imageno, 
            image.size[0],image.size[1],subfile.axisx,subfile.axisy,subfile.palette)
      except IOError:
          print("ioerror", subfile.groupno, subfile.imageno)
          pass
      else:
#           image.save(output_dir + "/g{0}-i{1}.png".format(subfile.groupno, subfile.imageno))
        if len(output_dir) > 0:
          output.write(output_dir + "/g{0}-i{1}.png".format(subfile.groupno, subfile.imageno))
            
      count+=1

if __name__ == '__main__':

  main()

