#!/bin/bash

#####################################################################
# Collect all command line arguments.
#####################################################################

XYZ_PATTERN="$1"
PNG_DIR="$2"
MODEL="$3"

if [ -z "`ls $XYZ_PATTERN????????.xyz`" ]; then
  echo "Didn't find any XYZ files matching pattern: $XYZ_PATTERN????????.xyz"
  echo "Aborting PNG model generation."
  exit 1
else
  echo "XYZ files are: $XYZ_PATTERN????????.xyz"
fi

mkdir -p $PNG_DIR
if [ -d "$PNG_DIR" ]; then
  echo "Output directory for model PNGs: $PNG_DIR"
else
  echo "Invalid output directory for model PNGs: $PNG_DIR"
  echo "Aborting PNG model generation."
  exit 1
fi

if [ -z "`which aviz`" ]; then
  echo "AVIZ not detected."
  echo "Aborting PNG model generation."
  exit 0
fi

#####################################################################
# Process command line arguments and set basic parameters.
#####################################################################

XYZ_BASE_NAME=`basename $XYZ_PATTERN`
XYZ_DIR_NAME=`dirname $XYZ_PATTERN`

WIDTH=400
HEIGHT=300

OUT_DIR="$PNG_DIR"
mkdir -p $OUT_DIR

FONT="8x13bold"
COLOR="yellow" 
GEOMETRY1="${WIDTH}x${HEIGHT}+0+0"
GEOMETRY2="${WIDTH}x${HEIGHT}!"

#####################################################################
# Gather all XYZ files and sort them in a list.
#####################################################################

ORDERED_LIST=/tmp/ordered_list

XYZ_FILES="$XYZ_PATTERN????????.xyz"
ls $XYZ_FILES | sort > $ORDERED_LIST

#####################################################################
# Create PNG files with AVIZ.
#####################################################################

FILE_LIST=(`cat $ORDERED_LIST`)
NUM_FILES=${#FILE_LIST[*]}

for XYZ_FILE in ${FILE_LIST[*]}
do
  # Set the name of the generated PNG file, and if it exists overwrite.
  PNG_FILE="$XYZ_DIR_NAME/`basename $XYZ_FILE .xyz`.0001.png"
  if [ -e $PNG_FILE ]; then
    echo "Overwriting already existing PNG file: $PNG_FILE"
    rm -f $PNG_FILE
  fi

  # Create a PNG with AVIZ.
  aviz -vpm 3d.vpm -geometry $GEOMETRY1 -snapq $XYZ_FILE >& /dev/null
  if [ ! -e $PNG_FILE ]; then
    echo "PNG file could not be created by AVIZ: $PNG_FILE"
    continue
  fi

  # Set the dimensions correctly (width and height).
  convert -geometry $GEOMETRY2 $PNG_FILE $PNG_FILE

  # Add the text overlay.
  convert -mattecolor blue -frame 6x6 $PNG_FILE $PNG_FILE
  convert -font $FONT -fill $COLOR -draw "text 25,49 '$MODEL'" $PNG_FILE $PNG_FILE

  # Move the PNG to the right place.
  PNG_OUT_FILE="`basename $PNG_FILE .0001.png`.png"
  mv -f $PNG_FILE $OUT_DIR/$PNG_OUT_FILE
done

# Cleanup.
rm -f $ORDERED_LIST
