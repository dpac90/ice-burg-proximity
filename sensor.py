import RPi.GPIO as GPIO

class Sensor: 
    def __init__(self, sensor_config, adcnum):
        self._adcnum = adcnum
        self.name = sensor_config['name']
        self._data_out = sensor_config['data_out']
        self._data_in = sensor_config['data_in']
        self._clk = sensor_config['clk']
        self._cs = sensor_config['cs']

        GPIO.setup(self._data_out, GPIO.IN)
        GPIO.setup(self._data_in, GPIO.OUT)
        GPIO.setup(self._clk, GPIO.OUT)
        GPIO.setup(self._cs, GPIO.OUT)



    def readadc(self):
        """
        read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
        returns the distance
        """
        if ((self._adcnum > 7) or (self._adcnum < 0)):
                return -1
        GPIO.output(self._cs, True)

        GPIO.output(self._clk, False) # start clock low
        GPIO.output(self._cs, False) # bring CS low

        commandout = self._adcnum
        commandout |= 0x18 # start bit + single-ended bit
        commandout <<= 3 # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(self._data_in, True)
                else: GPIO.output(self._data_in, False)
                commandout <<= 1
                GPIO.output(self._clk, True)
                GPIO.output(self._clk, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(self._clk, True)
                GPIO.output(self._clk, False)
                adcout <<= 1
                if (GPIO.input(self._data_out)):
                        adcout |= 0x1

        GPIO.output(self._cs, True)
        
        adcout >>= 1 # first bit is 'null' so drop it
        return adcout
