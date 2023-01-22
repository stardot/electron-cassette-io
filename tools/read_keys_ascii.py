#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

Based on read_keys.py by David Boddie
"""

import sys

f = sys.stdin

while True:
    pn = ord(f.read(1)) - 128
    #print(pn)
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

while True:

    b = ord(f.read(1)) - 128
    #print(b)
    if b * pn < 0:
    
        pn = b
        
        if 9 <= c <= 11:
            c = 0
            d = 1
            if m > 1:
                dc += 1
                if dc >= 4:
                    if not synchronised:
                        value = (value >> 1) | 0x80
                        if value == 255:
                            synchronised = True
                            print "Synchronised"
                    elif in_byte:
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
        
        if vc == 8:
            if 0 <= value <= 127:
                # electron uses almost standard ascii encoding
                # with two exceptions: ` becomes £ and | becomes ¦
                if value == 96:
                    key = "£"
                elif value == 124:
                    key = "¦"
                else: 
                    key = chr(value)

                if key != last_key:
                    sys.stdout.write(key)
                    sys.stdout.flush()

                last_key = key

            elif value == 255:
                last_key = ""

    
    m = max(abs(b), m)
    c += 1
