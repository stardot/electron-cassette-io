Electron Cassette I/O Programs
==============================

These programs aim to illustrate ways of using the Acorn Electron's cassette
interface other than to read and write data to cassette tape.

Building the Programs
---------------------

Both Python and the Ophis 6502 assembler need to be installed in order to build
the programs. At the command line run the `build.py` tool to create a UEF file:

  ./build.py programs.uef

This can either be converted to a WAV file using a tool like `uef2wave.py`
(http://www.stairwaytohell.com/essentials/index.html?page=homepage) and played
using a media player, or using an application that can play UEF files directly
as audio.

Running the Programs
--------------------

Currently, it is better to load the programs and run them separately than to
try to run them directly from audio files. This allows time to pass between the
loading of each program from its interaction with the cassette hardware. The
following example shows how this is done for the `RB` program:

  *LOAD RB
  CALL &1900

The RB program expects encoded text to be sent via the audio cable. This is
prepared using the `tools/make_data.py` tool. Instructions for each of the
programs and their corresponding tools is given below.

`read_bytes.oph` is the source file for the `RB` program. Text is prepared for
the program to use by running the `tools/make_data.py` tool, as in the
following example:

  ./tools/make_data.py text/card.txt card.wav

Once the `RB` program has been loaded and run on the Electron, the `card.wav`
file can then be played using a suitable media player application.

`read_screen.oph` is the source file for the `RS` program. Screen data is
prepared for the program to use by running the `tools/make_picture.py` tool, as
in the following example:

  cd tools
  ./make_picture.py mypicture.jpg
  cd ..
  ./tools/make_data tools/data/mypicture.dat mypicture.wav

Once the `RS` program has been loaded and run on the Electron, the
`mypicture.wav` file can then be played using a suitable media player
application.

`read_touch.oph` is the source file for the `RT` program. This program requires
the Electron Touch application to be running on a connected Android phone.

`keys2bytes.oph` is the source file for the `KB` program. This program sends
keypress information to a connected desktop machine. To interpret the output
from the Electron, run the following command in a console:

  ./tools/record_to_stdout.sh | ./tools/read_keys.py

This should show the text `Synchronised` when keyboard input can be processed.
If you have problems receiving input, try the following command instead:

  ./tools/record_to_stdout.sh -r | ./tools/read_keys.py

`write_bytes.oph` is a test program that was used in the development of the
`keys2bytes.oph` program.


Copyright and License Information
---------------------------------

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
