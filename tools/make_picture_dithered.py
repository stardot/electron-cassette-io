#!/usr/bin/env python

"""
Copyright (C) 2023 Luke Johnson <luke.g.johnson@outlook.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Original by David Boddie - modified by Luke Johnson 2023 to include
Floyd-Steinberg dithering at 75% strength.
"""

import os, sys
import numpy as np
import time

from PIL import Image, ImageOps

bitmap = {0: 0x00, 1: 0x01, 2: 0x04, 3: 0x05, 4: 0x10, 5: 0x11, 6: 0x14, 7: 0x15}
rgb_values = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0),
              (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1)]
max_rows = 256
start_row = 0

# Physical colour values
Black = 0
Red = 1
Green = 2
Yellow = 3
Blue = 4
Magenta = 5
Cyan = 6
White = 7

# Simple palette - array indices used to select colour
palette = np.array([[[Black, Blue], [Green, Cyan]],
    [[Red, Magenta], [Yellow, White]]])

def find_colour(palette, this_row, next_row, i):

    rgb = this_row[:,i]
                
    # Clip to between 0 and 255
    rgb = np.clip(rgb, 0, 255)

    # Divisor calculation
    levels = len(palette)
    div = 256 / levels; # = 128 when binary for each channel

    # Using floor division
    r = rgb[0] // div
    g = rgb[1] // div
    b = rgb[2] // div

    colour = palette[r, g, b]

    """ Finding the closest 8-bit rgb value represented by
    each palette colour - distributing between 0 and 255"""
    
    mul = 255 / (levels - 1)
    rgb_closest = np.array([r*mul, g*mul, b*mul])

    this_row, next_row = diffuse_error(rgb_closest,
                                       this_row, next_row, i)
    
    return colour, this_row, next_row

def diffuse_error(c, sr, nr, i):
    """ Perform Floyd-Steinberg dithering at 75% strength 
    c = colour (closest rgb represented in palette),
    sr = scan row,
    nr = next row,
    i = index in row """
    
    rgb_target = sr[:,i]
    rgb_actual = c # np.multiply(c, 255)

    # Quantization error
    rgb_error = rgb_target-rgb_actual

    sr[:,i] = rgb_actual
    
    sr = add_pixel_error(sr, i+1, rgb_error, 0.75*7/16)
    nr = add_pixel_error(nr, i-1, rgb_error, 0.75*3/16)
    nr = add_pixel_error(nr, i, rgb_error, 0.75*5/16)
    nr = add_pixel_error(nr, i+1, rgb_error, 0.75/16)

    return sr, nr

def add_pixel_error(row, idx, error, weight):
    try:
        rgb = row[:,idx]
        rgb = rgb + np.multiply(error, weight)

        row[:,idx] = rgb

        return row
    except IndexError:
        # Off edge of image - do nothing

        return row

#############################

if __name__ == "__main__":

    if len(sys.argv) >= 2 and sys.argv[1] == "-r":
        argv = sys.argv[:1] + sys.argv[2:]
        rotate = True
    else:
        argv = sys.argv[:]
        rotate = False
    
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: %s [-r] <image file> ...\n" % sys.argv[0])
        sys.exit(1)
    
    if not os.path.exists("data"):
        os.mkdir("data")
    
    #if not os.path.exists("Pictures"):
    #    os.mkdir("Pictures")
    
    for file_name in argv[1:]:
    
        im = Image.open(file_name)
        if rotate:
            im = im.rotate(270)
        if im.mode == "P":
            im = im.convert("RGB")
        
        if im.size[0] > 160:
            im = im.resize((160, 256), Image.NEAREST)
                
        data = im.tobytes()
        rows = []
        
        print "Converting image..."
        
        y = start_row

        # Pre-load r, g, b rows for dithering error diffusion
        a = y * im.size[0] * 3          # index of start of 1st row
        b = (y+1) * im.size[0] * 3      # index of start of 2nd row
        c = (y+2) * im.size[0] * 3     # guess
        
        scan_row = np.array([map(ord, data[a:b:3]), # r
                    map(ord, data[a+1:b+1:3]),      # g
                    map(ord, data[a+2:b+2:3])])     # b
        
        while y < min(start_row + max_rows, im.size[1]):
        
            out_row = []

            # r, g, b array for next row 

            try: 
                next_row = np.array([map(ord, data[b:c:3]), # r
                            map(ord, data[b+1:c+1:3]),      # g
                            map(ord, data[b+2:c+2:3])])     # b
                
            except IndexError:  # reached last row
                next_row = np.array([])
            
            x = 0
            while x < im.size[0]:

                
                
                #r, g, b = map(ord, data[i:i+3])
                (colour, scan_row, next_row) = \
                         find_colour(palette,
                                     scan_row, next_row, x)
                
                out_row.append(colour)
                
                x += 1
            
            rows.append(out_row)
            y += 1

            # Prepare for next loop
            scan_row = next_row

            b = c
            c = (y+2) * im.size[0] * 3
            
        
        while len(rows) % 8 != 0:
            rows.append([0] * im.size[0])
        
        name = os.path.split(file_name)[1]
        output_file = os.path.join("data", os.path.splitext(name)[0] + ".dat")
        print "Writing", output_file
        
        f = open(output_file, "w")
        
        by = start_row
        while by < min(start_row + max_rows, len(rows)):
        
            if im.size[0] < 160:
                bx = 0
                padding = ""
                while bx < 160 - im.size[0]/2:
                    values = []
                    y = by
                    while y < by + 8:
                        try:
                            # Use the logical colour for black.
                            i = 0
                        except ValueError:
                            i = 0
                        value = bitmap[i] | (bitmap[i] << 1)
                        padding += chr(value)
                        y += 1
                    
                    bx += 2
                
                f.write(padding)
                
            bx = 0
            while bx < im.size[0]:
            
                values = []
                y = by
                while y < by + 8:
                
                    value = 0
                    data = rows[y - start_row][bx:bx + 2]
                    shift = 0
                    
                    while data:
                        v = data.pop()
                        try:
                            # Find the logical colour for this physical colour.
                            i = v
                        except ValueError:
                            # Find the next best alternative from the palette.
                            i = 0
                        value |= (bitmap[i] << shift)
                        shift += 1
                    
                    f.write(chr(value))
                    y += 1
                
                bx += 2
            
            if im.size[0] < 160:
                f.write(padding)
            
            by += 8
        
        f.close()
    
    sys.exit()
