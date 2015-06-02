"""
SSF Extract for python

This utility will read a Elecbyte SFF file (version 1.01) and write the
portrait to the current folder.


leif theden, 2012 - 2015
public domain
"""

from StringIO import StringIO
from PIL import Image
from physics_platformer.sprite.sff import *
import logging
import sys
import os


def main():

  sff_file =''
  output_dir=''

  if len(sys.argv) >= 3:
    sff_file = sys.argv[1]
    output_dir = sys.argv[2]
  else:
    logging.error('Usage: sff-test ssf_file output_dir')
    return 

  #checking output dir
  if not os.path.exists(output_dir):
      os.makedirs(output_dir)

  fh = open(sff_file, 'rb')

  header = sff.sff1_file.parse(fh.read(512))
  print(header)

  next_subfile = header.next_subfile
  while next_subfile:
      fh.seek(next_subfile)
      subfile = sff.sff1_subfile_header.parse(fh.read(32))
      next_subfile = subfile.next_subfile
      try:
          s = StringIO(fh.read(subfile.length))
          image = Image.open(s)
      except IOError:
          print("ioerror", subfile.groupno, subfile.imageno)
          pass
      else:
          image.save(output_dir + "/g{0}-i{1}.png".format(subfile.groupno, subfile.imageno))

if __name__ == '__main__':

  main()

