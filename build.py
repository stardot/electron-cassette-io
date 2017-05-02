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

import os, stat, struct, sys
import UEFfile
from tools import make_data

version = "0.1"

def system(command):

    if os.system(command):
        sys.exit(1)

if __name__ == "__main__":

    if not 2 <= len(sys.argv) <= 2:
    
        sys.stderr.write("Usage: %s <new UEF file>\n" % sys.argv[0])
        sys.exit(1)
    
    out_uef_file = sys.argv[1]
    
    files = []
    
    # Assemble the code.
    assemble = [("terminal.oph", "TERM", 0x1900, 0x1900),
                #("read_touch.oph", "RT", 0x1900, 0x1900),
                #("read_bytes.oph", "RB", 0x1900, 0x1900),
                #("read_screen.oph", "RS", 0x1900, 0x1900),
                #("keys2bytes.oph", "K2B", 0x1900, 0x1900),
                #("write_bytes.oph", "WB", 0x1900, 0x1900)
                ]
    
    code_data = {}
    
    for name, output, load_address, exec_address in assemble:
        system("ophis " + name + " -o " + output)
        code = open(output).read()
        code_data[output] = code
    
    bootloader_start = 0xe00
    bootloader_code = ("\r\x00\x0a\x0d*FX 229,1"
                       "\r\x00\x14\x0d*RUN CODE\r\xff\x0a\x14\x00")
    
    files = [] # [("BOOT", bootloader_start, bootloader_start, bootloader_code)]
    for src, obj, code_start, code_exec in assemble:
        files.append((obj, code_start, code_exec, code_data[obj]))
    
    #code_size = os.stat("CODE")[stat.ST_SIZE]
    #print "%i bytes (%04x) of code" % (code_size, code_size)
    
    #code_finish = code_start + code_size
    #print "CODE    runs from %04x to %04x" % (code_start, code_finish)
    
    u = UEFfile.UEFfile(creator = 'build.py '+version)
    u.minor = 6
    u.target_machine = "Electron"
    
    u.import_files(0, files, gap = True)
    
    # Write the new UEF file.
    try:
        u.write(out_uef_file, write_emulator_info = False)
    except UEFfile.UEFfile_error:
        sys.stderr.write("Couldn't write the new executable to %s.\n" % out_uef_file)
        sys.exit(1)
    
    # Remove the executable files.
    for name, output, load_address, exec_address in assemble:
        os.remove(output)
    
    # Also create a WAV file for use in the Android application.
    u = UEFfile.UEFfile()
    #block = u.write_block(code_data["RT"], "RT", 0x1900, 0x1900, 0, 1)
    #
    #open("tools/android/ElectronTouch/resources/electron_code.dat", "wb").write(block)
    block = u.write_block(code_data["TERM"], "TERM", 0x1900, 0x1900, 0, 1)
    make_data.main(block, "/tmp/term.wav")
    
    # Exit
    sys.exit()
