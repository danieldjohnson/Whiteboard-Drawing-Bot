from Adafruit_MCP230xx import Adafruit_MCP230XX
import RPi.GPIO as GPIO
import time
class ServoDriver(object):
	def __init__(self, maxval, baseval, initial):
		self.baseval = baseval
		self.relangle = initial

		self.setProp("delayed", "0")
		self.setProp("mode", "servo")
		self.setProp("servo_max", str(maxval))
		self.setServoRelative(initial)
		self.setProp("active", "1")
	def setProp(self,property, value):
		try:
			f = open("/sys/class/rpi-pwm/pwm0/" + property, 'w')
			f.write(value)
			f.close()	
		except:
			print("Error writing to: " + property + " value: " + value)
	def setServoAbsolute(self,aangle):
		self.relangle = aangle - baseval
		self.setProp("servo", str(aangle))
	def setServoRelative(self,rangle):
		self.relangle = rangle
		absang = rangle+self.baseval
		self.setProp("servo", str(absang))
	def setBase(self,base):
		self.baseval = base;
		absang = self.relangle+self.baseval
		self.setProp("servo", str(absang))
	def cleanup(self):
		self.setProp("active", "0")
	def __del__(self):
		self.cleanup()
		

class DrawDriver(object):
	STEPS = [
		0b0101, # 1 0 1 0
		0b0110, # 0 1 1 0
		0b1010, # 0 1 0 1
		0b1001  # 1 0 0 1
	]
	IDLE = 0b00000000
	def __init__(self,baseang):
		#Setup stepper access pins
		self.mcp = Adafruit_MCP230XX(address = 0x20, num_gpios = 16)
		for x in xrange(0,8):
			self.mcp.config(x, self.mcp.OUTPUT)

		#Activate steppers
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(23,GPIO.OUT)
		GPIO.output(23,1)

		#Setup servo
		self.servo = ServoDriver(180,baseang,-7)

		self._set(0,0)

	def _combinedSteps(self, stepa, stepb):
		return self.STEPS[stepa] | (self.STEPS[stepb] << 4)
	def _set(self,a,b):
		self.a = a
		self.b = b
		self.mcp.write16(self._combinedSteps(a,b))
	def setServoBaseAngle(self,base):
		self.servo.setBase(base)

	def release(self):
		self.mcp.write16(self.IDLE)
	def penDown(self):
		self.servo.setServoRelative(0)
	def penUp(self):
		self.servo.setServoRelative(-13)
	def advance(self, da, db):
		a = (self.a + da) % 4
		b = (self.b + db) % 4
		self._set(a,b)

	def cleanup(self):
		self.release()
		GPIO.output(23,0)
		self.servo.cleanup()
		for x in xrange(0,8):
			self.mcp.config(x, self.mcp.INPUT)

def Test(driver,da, db, amt, delay):
	for x in xrange(0,amt):
		driver.advance(da,db)
		time.sleep(delay)




