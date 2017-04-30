"""
touch.py - Application code for the Electron Touch application.

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

from java.io import InputStream
from java.lang import Byte, Math, Object, Runnable
from java.nio import ShortBuffer
from java.util import List
from android.app import Activity
from android.content import Context
from android.graphics import Canvas, Paint
from android.media import AudioFormat, AudioManager, AudioTrack
from android.os import Bundle, Handler
from android.view import MotionEvent, View

from app_resources import R

class ViewActivity(Activity):

    __interfaces__ = [Runnable]
    
    def __init__(self):
    
        Activity.__init__(self)
    
    @args(void, [Bundle])
    def onCreate(self, bundle):
    
        Activity.onCreate(self, bundle)
        
        self.view = DrawView(self)
        self.setContentView(self.view)
    
    def onResume(self):
    
        Activity.onResume(self)
    
    def onPause(self):
    
        Activity.onPause(self)
        self.view.pause()


class DrawView(View):

    __interfaces__ = [Runnable]
    
    @args(void, [Context])
    def __init__(self, context):
    
        View.__init__(self, context)
        
        self.player = Player()
        self.paint = Paint()
        self.x = 0
        self.y = 0
        self.r = 10
        self.action = 0
        
        self.handler = Handler()
        self.first = True
        self.ready = False
        self.data = array(byte, 6)
        self.data[0] = 25
        
        resources = context.getResources()
        self.code = resources.openRawResource(R.raw.code)
    
    @args(void, [int, int, int, int])
    def onSizeChanged(self, width, height, oldWidth, oldHeight):
    
        if oldWidth == 0:
            self.x = width/2
            self.y = height/2
    
    @args(void, [Canvas])
    def onDraw(self, canvas):
    
        View.onDraw(self, canvas)
        
        self.paint.setARGB(255, 0, 255, 160)
        canvas.drawPaint(self.paint)
        
        if not self.first:
            self.paint.setARGB(255, 0, 0, 160)
            canvas.drawCircle(self.x, self.y, self.r, self.paint)
    
    @args(bool, [MotionEvent])
    def onTouchEvent(self, event):
    
        self.x = event.getX()
        self.y = event.getY()
        
        action = event.getAction()
        
        if action == MotionEvent.ACTION_DOWN or action == MotionEvent.ACTION_MOVE:
        
            if action == MotionEvent.ACTION_DOWN:
                self.data[1] = 4
            else:
                self.data[1] = 5
            
            x = int(1280 * self.x/self.getWidth())
            self.data[2] = x % 256
            self.data[3] = x / 256
            y = 1023 - int(1024 * self.y/self.getHeight())
            self.data[4] = y % 256
            self.data[5] = y / 256
            
            if not self.ready:
            
                if self.first:
                    self.player.sendCode(self.code)
                    self.first = False
                else:
                    self.player.playHighTone(60)
                    self.player.playData(self.data)
                    self.ready = True
                    self.handler.postDelayed(self, long(50))
        
        elif action == MotionEvent.ACTION_UP:
        
            self.pause()
        
        self.invalidate()
        return True
    
    def pause(self):
    
        self.ready = False
        self.handler.removeCallbacks(self)
    
    def run(self):
    
        self.player.playData(self.data)
        self.handler.postDelayed(self, long(50))


class Player(Object):

    SAMPLE_RATE = 44100
    SAMPLES_PER_BIT = 36
    
    def __init__(self):
    
        Object.__init__(self)
        
        # Define low and high tone waveforms.
        self.low_tone = []
        self.high_tone = []
        self.gap = []
        
        i = 0
        dx = 2 * Math.PI / self.SAMPLES_PER_BIT
        while i < self.SAMPLES_PER_BIT:
        
            low = Math.sin(i * dx)
            if low >= 0:
                self.low_tone.add(short(16384))
            else:
                self.low_tone.add(short(-16384))
            
            high = Math.sin(2 * i * dx)
            if high >= 0:
                self.high_tone.add(short(16384))
            else:
                self.high_tone.add(short(-16384))
            
            self.gap.add(short(0))
            
            i += 1
        
        # Define a track with a capacity large enough to fit five bytes of
        # encoded data.
        #         data (bits)                  bytes per short
        capacity = 60 * self.SAMPLES_PER_BIT * 2
        
        self.track = AudioTrack(AudioManager.STREAM_MUSIC, self.SAMPLE_RATE,
            AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT,
            capacity, AudioTrack.MODE_STREAM)
        
        self.track.play()
    
    @args(int, [ShortBuffer, int, List(short)])
    def writeTone(self, buf, i, tone):
    
        j = 0
        while j < self.SAMPLES_PER_BIT:
            buf.put(i, tone[j])
            i += 1
            j += 1
        
        return i
    
    @args(ShortBuffer, [[byte]])
    def generateData(self, data):
    
        # Each byte in the block is expanded to ten bits. Each bit is
        # represented as one low frequency cycle or two high frequency cycles.
        bytes = len(data)
        bits = bytes * 10
        
        # Include samples for 1 channel
        samples = bits * self.SAMPLES_PER_BIT
        buf = ShortBuffer.allocate(samples)
        
        j = 0
        
        i = 0
        while i < bytes:
        
            j = self.writeTone(buf, j, self.low_tone)
            
            b = Byte(data[i]).intValue()
            k = 0
            while k < 8:
                if b & 1 == 0:
                    j = self.writeTone(buf, j, self.low_tone)
                else:
                    j = self.writeTone(buf, j, self.high_tone)
                
                b = b >> 1
                k += 1
            
            j = self.writeTone(buf, j, self.high_tone)
            i += 1
        
        return buf
    
    @args(void, [[byte]])
    def playData(self, data):
    
        buf = self.generateData(data)
        shorts = buf.capacity()
        bytes = shorts * 2
        
        self.track.write(buf.array(), 0, shorts)
    
    @args(void, [int])
    def playHighTone(self, bits):
    
        # Include samples for 1 channel
        samples = bits * self.SAMPLES_PER_BIT
        buf = ShortBuffer.allocate(samples)
        
        i = 0
        j = 0
        while i < bits:
        
            j = self.writeTone(buf, j, self.high_tone)
            i += 1
        
        shorts = buf.capacity()
        bytes = shorts * 2
        
        self.track.write(buf.array(), 0, shorts)
    
    @args(void, [InputStream])
    def sendCode(self, stream):
    
        self.playHighTone(60)
        
        a = array(byte, 6)
        
        while True:
        
            code = stream.read(a, 0, 6)
            if code == -1:
                break
            
            self.playData(a)
        
        stream.close()
