from DrawDriver import DrawDriver
from parsley import makeGrammar
import time
import math

drawGrammarDef= """

start = cmdseq

cmdseq = cmd+

cmd = "M" integer:left "," integer:right -> {'action':'M', 'a':left,'b':right}
	| "Pd" -> {'action':'Pd'}
	| "Pu" -> {'action':'Pu'}
	| "Pr" -> {'action':'Pr'}
	| "A" advanceseq:path -> {'action':'A', 'path':path}
	| "Sa" sign:sign integer:len -> {'action':'S', 'axis':'a', 'sign':sign, 'length':len}
	| "Sb" sign:sign integer:len -> {'action':'S', 'axis':'b', 'sign':sign, 'length':len}
	| "R" -> {'action':'R'}

sign = '+' ->  1
	 | '0' ->  0
	 | '-' -> -1

advanceseq = advance+

advance = sign:a sign:b -> {'da':a, 'db':b}

integer = <digit+>:ds -> int(ds)

"""
drawGrammar = makeGrammar(drawGrammarDef,{})


class DrawInterpreter(object):
	AXIS_A = 'a'
	AXIS_B = 'b'

	PEN_UP = 0
	PEN_DOWN = 1

	def __init__(self,radiusA=13, radiusB=10.5, stepsPerRev=512,initialA=0,initialB=131,maxB=250,stepdelay=0.05,pendelay=0.2,dotmode=False):
		self.rA = radiusA
		self.rB = radiusB
		self.steps = stepsPerRev
		self.initialA = initialA
		self.initialB = initialB
		self.maxB = 250
		self.a = initialA
		self.b = initialB
		self.delay = stepdelay
		self.pendelay = pendelay
		self.penPos = self.PEN_UP

		self.bDelay = 0
		self.bDelayQueue = [0]*self.bDelay

		self.dotmode = dotmode

		self.driver = DrawDriver(self._getBaseAngle())
		self.driver.penUp()

	def do(self, commands):
		cmdseq = drawGrammar(commands).cmdseq()
		for cmd in cmdseq:
			act = cmd['action']
			if act=='M':
				self._move(cmd['a'],cmd['b'])
			elif act == 'Pd':
				self._penDown()
			elif act == 'Pu':
				self._penUp()
			elif act == 'Pr':
				self._penUp()
			elif act == 'A':
				self._advance(cmd['path'])
			elif act == 'S':
				self._sweep(cmd['axis'],cmd['sign'],cmd['length'])
			elif act == 'R':
				self.reset()


	def _getBaseAngle(self):
		return int(round(165-5*math.sin(2*math.pi*(self.a+self.b)/self.steps)))
	def _penUp(self):
		if self.penPos is self.PEN_UP: return
		self.driver.penUp()
		self.penPos=self.PEN_UP
		time.sleep(self.pendelay)
	def _penDown(self):
		if self.penPos is self.PEN_DOWN: return
		self.driver.penDown()
		self.penPos=self.PEN_DOWN
		time.sleep(self.pendelay)

	def _move(self,targetA,targetB):
		if self.a-targetA>self.steps/2:  self.a-=self.steps
		if self.a-targetA<-self.steps/2: self.a+=self.steps
		if self.b-targetB>self.steps/2:  self.b-=self.steps
		if self.b-targetB<-self.steps/2: self.b+=self.steps
		while (self.a!=targetA or self.b!=targetB):
			da=0
			db=0
			if self.a<targetA:
				da=1
			elif self.a>targetA:
				da=-1
			if self.b<targetB:
				db=1
			elif self.b>targetB:
				db=-1
			self._delta(da,db)

	def _sweep(self,axis,sign,length):
		for x in xrange(0,length):
			if axis==self.AXIS_A:
				self._delta(sign,0)
			else:
				self._delta(0,sign)

	def _advance(self,sequence):
		for action in sequence:
			self._delta(action['da'], action['db'])

	def _delta(self, da, db):
		self.a += da
		self.b += db
		if self.b > self.maxB:
			db = 0
		if self.dotmode and self.penPos is self.PEN_DOWN:
			self.driver.penUp()
			time.sleep(self.pendelay)
			self._delayAdv(-da,db)
			time.sleep(self.delay)
			self.driver.penDown()
			time.sleep(self.pendelay)
		else:
			self._delayAdv(-da,db)
			time.sleep(self.delay)
		self.driver.setServoBaseAngle(self._getBaseAngle())

	def _delayAdv(self,da,db):
		self.bDelayQueue += [db]
		ndb = self.bDelayQueue.pop( 0 )
		self.driver.advance(da,ndb)



	def reset(self):
		self._penUp()
		self._move(self.initialA,self.initialB)
		pass

	def activate(self):
		if self.driver is None:
			self.driver = DrawDriver(self._getBaseAngle())
			if self.penPos is self.PEN_DOWN:
				self.driver.penDown()
			else:
				self.driver.penUp()
			time.sleep(self.pendelay)

	def deactivate(self):
		if self.driver is not None:
			self.driver.cleanup()
			self.driver=None

	def cleanup(self):
		self.deactivate()

	def __del__(self):
		self.deactivate()
