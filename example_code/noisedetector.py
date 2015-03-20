
import numpy
import pyaudio
import analyse
import logging

class NoiseDetector:
    def __init__(self, logger, noiseCallback, sampleCount, threshold):
        self.logger = logger
        self.noiseCallback = noiseCallback
        self.sampleCount = sampleCount
        self.threshold = threshold
	      self.bg = []
	      self.sampleRate = int(pyaud.get_device_info_by_index(0)['defaultSampleRate'])
	      self.pyaud = pyaudio.PyAudio()
	      
	def start(self)
	  # Open input stream, 16-bit mono at 44100 Hz
		  stream = self.pyaud.open(
  			format = pyaudio.paInt16,
  			channels = 1,
  			rate = self.sampleRate,
  			input = True)
		
        while True:
          
          try:
				    # Read raw microphone data
				    rawsamps = stream.read(8192)
				    # Convert raw data to NumPy array
				    samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
				    # Show the volume and pitch
				    volume = analyse.loudness(samps)#, analyse.musical_detect_pitch(samps)
			    except IOError: 
      				self.logger.debug("dropped mic frame")
      				
		      if (len(self.bg) != self.sampleCount):
			      self.bg.append(volume)
			      self.logger.debug("filling noise buffer count=" + str(len(self.bg)))
			      continue;
			    
	        averageLoudness = sum(self.bg) / float(len(self.bg))
	        diff = abs(volume) - abs(averageLoudness)
			    isDiff = diff > self.threshold
			    self.logger.debug("volume diff " + str(diff))
			
			    if (isDiff):
			      noiseCallback(diff, averageLoudness)
	        
	        self.bg.pop(0)
	        self.bg.append(volume)
	        
	def stop(self)
	    # stop stream (4)
      self.stream.stop_stream()
      self.stream.close()

      # close PyAudio (5)
      self.pyaud.terminate()
