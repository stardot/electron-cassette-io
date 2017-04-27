#!/usr/bin/env python

"""
Copyright (C) 2015 David Boddie <david@boddie.org.uk>

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
"""

import os, sys

import Image, ImageOps
from palette import get_entries

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

def find_colour(r, g, b):

    r = r / 85
    g = g / 85
    b = b / 85
    
    if r == g == b:
        if r <= 1:
            colour = 0
        else:
            colour = 7

    elif r == g:
        if r > b:
            colour = 3
        elif r > 1:
            colour = 6
        else:
            colour = 4

    elif g == b:
        if g > r:
            colour = 6
        elif g > 1:
            colour = 5
        else:
            colour = 1

    elif b == r:
        if b > g:
            colour = 5
        elif b > 1:
            colour = 3
        else:
            colour = 2

    else:
        if b > r and b > g:
            colour = 4
        elif r > g and r > b:
            colour = 1
        elif g > b and g > r:
            colour = 2
        else:
            colour = 0
    
    return colour


alternatives = {
    Black:   (Blue, Red, Magenta, Green),
    Red:     (Magenta, Yellow),
    Green:   (Cyan, Yellow),
    Yellow:  (Green, Cyan, White),
    Blue:    (Cyan, Green),
    Magenta: (Red, Yellow),
    Cyan:    (Blue, Green, Yellow),
    White:   (Cyan, Yellow)
    }

def find_alternative(palette, physical_colour):

    for alt_colour in alternatives[physical_colour]:
        try:
            return palette.index(alt_colour)
        except ValueError:
            pass
    
    return 0

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
        
        #im.save(os.path.join("Pictures", "c_" + os.path.split(file_name)[1]))
        
        data = im.tostring()
        rows = []
        
        print "Converting image..."
        
        y = start_row
        while y < min(start_row + max_rows, im.size[1]):
        
            row = []
            x = 0
            while x < im.size[0]:
            
                i = ((y * im.size[0]) + x) * 3
                r, g, b = map(ord, data[i:i+3])
                colour = find_colour(r, g, b)
                
                row.append(colour)
                
                x += 1
            
            rows.append(row)
            y += 1
        
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
                            i = 0 # find_alternative(palette[y - start_row], v)
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
