Electron Touch Application
==========================

This application sends information about touch events to an Acorn Electron via
its cassette port. To use it, you will need an audio cable with a 7-pin DIN
connector on one end that plugs into the Electron's cassette port and a
suitable connector for your Android phone on the other.

WARNING: The application generates noise when it is used. It is strongly
recommended that you only ever run it when it is connected to an Electron and
ensure that it is shut down before removing the audio cable from the phone.

Building the Application
------------------------

The application is written in the Python-like Serpentine language. You will
need to obtain the Dalvik Unpythonic Compiler Kit (DUCK) to build it:

https://bitbucket.org/dboddie/duck

This application can be built in the same way as any of the Serpentine examples
in the DUCK distribution. Follow the instructions for creating a signing key
and building the DUCK examples to see how this is done.

Running the Application
-----------------------

Currently it is necessary to load the corresponding `RT` program on the
Electron before this application can be used. The source code for this program
can be found in the `read_touch.oph` file in the top level of the Electron
Cassette I/O Programs repository.


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
