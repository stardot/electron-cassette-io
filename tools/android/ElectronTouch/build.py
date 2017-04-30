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

import os, sys

from Tools import buildhelper

if not os.path.exists("resources/electron_code.dat"):
    sys.stderr.write("Run the build.py script in the main directory to prepare "
                     "the resources/electron_code.dat file.\n")
    sys.exit(1)

app_name = "Electron Touch"
package_name = "uk.org.boddie.android.electrontouch"
res_files = {"drawable": {"ic_launcher": "icon.svg"},
             "raw": {"code": "resources/electron_code.dat"}}
code_file = "touch.py"
include_path = "Include"
layout = None
features = []
permissions = []

if __name__ == "__main__":

    args = sys.argv[:]
    
    result = buildhelper.main(__file__, app_name, package_name, res_files,
        layout, code_file, include_path, features, permissions, args,
        include_sources = True)
    
    sys.exit(result)
