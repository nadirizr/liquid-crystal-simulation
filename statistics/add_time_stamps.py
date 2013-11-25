import glob
import os
import sys

run_dir = sys.argv[1]
if not os.path.exists(run_dir):
  print "Invalid run directory: '%s'" % run_dir
  sys.exit(1)

output_files = glob.glob("%s/output/*.xyz" % run_dir)
info_file = glob.glob("%s/output/*.txt" % run_dir)[0]
events = file(info_file, "r").readlines()

assert len(events) == len(output_files)

fixed_file = file("%s.fixed" % info_file, "w")
for (i, output_file) in enumerate(output_files):
  fixed_file.write("[%s]\t%s" % (os.path.getmtime(output_file), events[i]))
fixed_file.close()
