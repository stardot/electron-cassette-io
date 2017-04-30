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

import struct, sys

zero_bit = ("\xff" * 9) + ("\x00" * 9)
one_bit = ("\xff" * 5) + ("\x00" * 4) + ("\xff" * 5) + ("\x00" * 4)

class WAV:

    def write(self, file_name, samples):
    
        f = open(file_name, "wb")
        
        f.write("RIFF")
        # Write the size of the RIFF file contents.
        f.write(struct.pack("<I", 12 + 16 + 8 + len(samples)))
        
        f.write("WAVE")
        f.write("fmt ")
        # Write the size of the format header.
        f.write(struct.pack("<I", 16))
        
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<I", 22050))
        f.write(struct.pack("<I", 22050))
        f.write(struct.pack("<H", 0))
        f.write(struct.pack("<H", 8))

        f.write("data")
        # Write the size of the data.
        f.write(struct.pack("<I", len(samples)))
        
        # Write the data itself.
        f.write(samples)
        
        f.close()


def encode(text, zero_bit, one_bit):

    data = ""
    
    for c in text:
    
        data += zero_bit
        b = ord(c)
        i = 0
        while i < 8:
        
            if b & 1:
                data += one_bit
            else:
                data += zero_bit
            
            b = b >> 1
            i += 1
        
        data += one_bit
    
    return data


def main(text, wav_file_name):

    samples = ("\x80" * 300) # + (one_bit * 300) + encode("\xdc", zero_bit, one_bit)
    samples += (one_bit * 100)
    samples += encode(text, zero_bit, one_bit)
    samples += (one_bit * 100)
    
    WAV().write(wav_file_name, samples)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s <file> <WAV file>\n" % sys.argv[0])
        sys.exit(1)
    
    input_file = sys.argv[1]
    if input_file == "-":
        text = sys.stdin.read()
    else:
        text = open(input_file, "rb").read()
    
    wav_file_name = sys.argv[2]
    
    main(text, wav_file_name)
