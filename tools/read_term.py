#!/usr/bin/env python

"""
Copyright (C) 2017 David Boddie <david@boddie.org.uk>

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

import sys

keys = ("Q345" "\x00" "8" "\x00" "-^" "\x00\x00\x00\x00\x00\x00\x00"
        "\x00" "WET7I90_" "\x00\x00\x00\x00\x00\x00\x00"
        "12DR6UOP[" "\x00\x00\x00\x00\x00\x00\x00"
        "\x00" "AXFYJK@:" "\x00\x00\x00\x00\x00\x00\x00"
        "\x00" "SCGHNL;]" "\x00\x00\x00\x00\x00\x00\x00"
        "\x00" "Z VBM,./" "\x00\x00\x00\x00\x00\x00\x00"
        "\x00\x00\x00\x00\x00\x00\x00\x00" "\\" "\x00\x00\x00\x00\x00\x00\x00")


f = sys.stdin

while True:
    pn = ord(f.read(1)) - 128
    if pn != 0:
        break

m = 0       # maximum signal value in the current half-wave
c = 0       # number of samples since the last crossing
d = 0       # current digit being read
dc = 0      # number of half-waves read for the current digit

synchronised = False
in_byte = False
value = 0
vc = 0

key = ""
last_key = ""
quiet = 0

while True:

    b = ord(f.read(1)) - 128
    
    if b * pn < 0:
    
        pn = b
        
        if 9 <= c <= 11:
            c = 0
            d = 1
            if m > 1:
                dc += 1
                if dc >= 4:
                    if in_byte:
                        if vc < 8:
                            value = (value >> 1) | 0x80
                            vc += 1
                        else:
                            in_byte = False
                    dc = 0
            m = 0
        elif 19 <= c <= 21:
            c = 0
            d = 0
            if m > 1:
                dc += 1
                if dc >= 2:
                    value = (value >> 1)
                    if in_byte:
                        vc += 1
                    else:
                        in_byte = True
                        value = 0
                        vc = 0
                    dc = 0
            m = 0
        elif c > 21:
            c = 0
            m = 0
        
        if vc == 8 and in_byte:
            if 16 <= value <= 128:
                key = keys[value - 16]
                if key != last_key:
                    sys.stdout.write(key)
                    sys.stdout.flush()
                    last_key = key
    
    m = max(abs(b), m)
    c += 1
    
    if m <= 1:
        quiet += 1
    else:
        quiet = 0
    
    if quiet >= 400:
        last_key = ""
        quiet = 0
    
    #print "%3i" % b, (b/8)*" ", "*"
