
#    15-112: Principles of Programming and Computer Science
#    Final Project: Poker game, server.py
#    Name      : Stefan Baumann
#    AndrewID  : sbaumann
#    Created   : 23 NOV 2018
#    Updated   : 10 DEC 2018


from random import *
import socket
import itertools
from Tkinter import *


class Card:
	def __init__(self, value, suit):
		self.value = value     # 2-10, J, Q, K, A
		self.suit = suit        # C(lubs), D(iamonds), H(earts), S(pades)

	def getCard(self):
		''' returns value and suit of card object '''
		return self.value + self.suit

class Deck:
	def __init__(self):
		self.thedeck = []
		self.shuffled = False
		self.makeDeck()
		
	def makeDeck(self):
		""" creates 52 card objects and adds to thedeck list """
		values = []
		for i in range(2, 11):
			values.append(str(i))
		values += ['J', 'Q', 'K', 'A']
		suits = ['C', 'D', 'H', 'S']
		for j in values:
			for s in suits:
				cardobj = Card(j, s)
				card = cardobj.getCard()
				self.thedeck.append(card)

	def shuffleDeck(self):
		''' shuffles thedeck list '''
		shuffle(self.thedeck)
		self.shuffled = True

	def removeCard(self, card):
		''' removes given card from deck '''
		self.thedeck.remove(card)

	def takeTopCard(self):
		thecard = self.thedeck[0]
		self.removeCard(thecard)
		return thecard


class Player:
	''' creates a player on the table '''
	def __init__(self, username):
		self.playername = username
		self.location = 'Login'

		self.dealer = False
		self.smallblind = False
		self.bigblind = False

		self.stack = 2500
		self.holecards = []
		self.active = False
		self.yourturn = False
		self.bet = 0
		self.roundturns = 0

		self.result = 11
		self.besthand = ()


class Start:
	def __init__(self, parent):
		self.wnd = parent
		self.gamewnd = None			# window for Game instance

		self.server = None
		self.s = None

		self.allfriendnames = []	# list of names of all friends
		self.totalplayers = {}		# dictionary of names and player objs of friends
		self.onlineplayers = {}		# dictionary of names and player objs of online friends

		self.openplayers = []		# list of player objs that are in Open
		self.tableplayers = []		# list of player objs that are in Table
		self.gameplayers = []		# list of player objs that are in Game

		self.anythingNew = False	# Boolean for new messages received

		self.game = None			# Game instance when game is started
		self.gameon = False 		# Boolean for game running

		if self.getOnline():
			self.timer1()
		else:
			self.wnd.destroy()

	def getOnline(self):
		''' creates connection to server and logs into sbaumann11/poker server '''
		self.server = ChatProgram()
		self.s = self.server.startConnection('86.36.46.10', 15112)
		if self.server.login(self.s, 'sbaumann11', 'sbaumann'):
			Label(self.wnd, text='Server is online.').pack()
			print 'Server is online.'
			return True
		else:
			print 'Cannot get online.'
			return False

	def timer1(self):
		''' reocurring function checks for new players and new messages '''
		self.acceptNewFriends()
		self.getAllFriends()
		self.addNewPlayers()

		self.checkMessages()
		oldopen, oldtable, oldgame = self.openplayers, self.tableplayers, self.gameplayers
		self.locatePlayers()

		if self.anythingNew:
			for plyrobj in self.openplayers:
				self.giveHomeData(plyrobj)
			for plyrobj in self.tableplayers:
				self.giveTableData(plyrobj)

		self.wnd.after(500, self.timer1)


	def acceptNewFriends(self):
		''' goes through active users and checks for friend requests '''
		allusers = self.server.taskTwo(self.s, '@users')
		for i in allusers:
			self.server.taskThree(self.s, i, '@accept')

	def getAllFriends(self):
		''' turns allfriends into a list of all friends '''
		self.allfriendnames = self.server.taskTwo(self.s, '@friends')

	def addNewPlayers(self):
		''' checks which friends arent players and adds them to totalplayers '''
		oldplayers = self.totalplayers
		for name in self.allfriendnames:
			if name not in oldplayers:
				plyrobj = Player(name)
				self.totalplayers[name] = plyrobj

	def checkMessages(self):
		''' checks for new messages from players and changes location of players'''
		messagelist = self.server.getMail(self.s)

		if messagelist == []:
			self.anythingNew = False
		else:
			self.anythingNew = True

		for t in messagelist:
			username = t[0]
			msg = t[1]
			if msg == 'Logon-Player':
				self.onlineplayers[username] = self.totalplayers[username]
				self.onlineplayers[username].location = 'Open'
				self.server.sendMessage(self.s, username, "Welcome to Stefan's online poker room.")
				self.server.sendMessage(self.s, username, "Join the table, invite some friends, and have some fun!")
			elif msg == 'Logoff-Player':
				if username in self.onlineplayers:
					self.onlineplayers[username].location = 'Login'
					del self.onlineplayers[username]
			elif msg == 'Try-Logon':
				if username not in self.onlineplayers:
					self.server.sendMessage(self.s, username, "Can-Login")
				else:
					self.server.sendMessage(self.s, username, "Cannot-Login")

			''' ignore messages from users who aren't poker players '''
			if username in self.onlineplayers:
				if msg == 'Sit-Table':
					self.onlineplayers[username].location = 'Table'
					self.server.sendMessage(self.s, username, "The game will start when a player")
					self.server.sendMessage(self.s, username, "clicks the 'Start game' button.")
				elif msg == 'Leave-Table':
					self.onlineplayers[username].location = 'Open'

				elif msg == 'Start-Game':
					for plyrobj in self.tableplayers:
						plyrobj.location = 'Game'
					self.gameon = True
					for plyrobj in self.openplayers:
						self.giveHomeData(plyrobj)
					self.initiateGame()
				elif msg == 'Game-Done':
					for plyrobj in self.gameplayers:
						plyrobj.location = 'Table'
					self.gameon = False

	def locatePlayers(self):
		''' assorts each online player to a list depending on their location '''
		self.openplayers = []
		self.tableplayers = []
		self.gameplayers = []

		for name in self.onlineplayers:
			plyrobj = self.onlineplayers[name]
			location = plyrobj.location
			if location == 'Open':
				self.openplayers.append(plyrobj)
			elif location == 'Table':
				self.tableplayers.append(plyrobj)
			elif location == 'Game':
				self.gameplayers.append(plyrobj)
			else:
				if name in self.onlineplayers:
					del self.onlineplayers[name]

	def initiateGame(self):
		''' starts game for players on table and creates Toplevel as Game instance '''
		self.gamewnd = Toplevel(self.wnd)
		self.gamewnd.geometry('150x150')
		self.game = Game(self.gamewnd, self.s, self.server, self.tableplayers)

	def giveHomeData(self, plyrobj):
		''' sends message with new data to all friends whenever there are updates on gui side '''
		plyrname = plyrobj.playername

		data = ['homexx']

		data += ['location']
		data += [plyrobj.location]

		data += ['onlineusers']
		''' sends names of online users '''
		for name in self.onlineplayers:
			data.append(name)

		data += ['canplay']
		''' sends true/false if user can play '''
		data += [str(self.canPlay(plyrobj))]

		data += ['myinfo']
		''' sends name of player and stack size '''
		for j in [plyrobj.playername, plyrobj.stack]:
			data += [str(j)]

		data += ['tablespace']
		space = 9 - len(self.tableplayers)
		data += [str(space)]

		data += ['tableplyrs']
		for obj in self.tableplayers:
			data.append(obj.playername)

		data += ['gameon']
		data += [str(self.gameon)]

		data += ['END']
		dstring = '-'.join(data)

		self.server.sendMessage(self.s, plyrname, dstring)

	def giveTableData(self, plyrobj):
		''' sends message with new data to all friends whenever there are updates on gui side of table'''
		plyrname = plyrobj.playername

		data = ['tablexx']

		data += ['location']
		data += [plyrobj.location]

		data += ['tableplyrs']
		for v in self.tableplayers:
			data.append(v.playername)

		data += ['gameon']
		data += [str(self.gameon)]

		data += ['canplay']
		data += [str(self.canPlay(plyrobj))]

		data += ['END']
		dstring = '-'.join(data)

		self.server.sendMessage(self.s, plyrname, dstring)

	def canPlay(self, plyrobj):
		if plyrobj.stack > 100:
			return True
		return False


class Game:
	def __init__(self, window, socket, server, players):
		self.wnd = window
		self.createWindow()

		self.s = socket 				# socket connection
		self.server = server 			# ChatProgram object acting as server
		self.themail = []				# newest mail received

		self.tableplayers = players 	# list of all player objs on table during game
		self.activeplayers = []			# list of all active player objs in game
		self.playercntr = 0				# counts players for rounds
		self.iswinner = False 			# Boolean for having winner

		self.currentplyrobj = None		# Player obj of current player
		self.possibleacts = []			# list of possible acts for current player

		self.deck = Deck()				# creates Deck object
		self.deck.shuffleDeck()			# shuffles Deck obj

		self.pot = 0
		self.communitycards = []
		self.street = ''				# street Game is in
		self.maxbet = 0					# current maxbet of street
		
		self.dealerCounter = 0
		self.dealer = None
		self.whoDealer(self.dealerCounter, self.tableplayers)
		self.smallblind = 10
		self.bigblind = 20
		self.smallblinder = None
		self.whoSmallblind(self.dealerCounter, self.tableplayers)
		self.bigblinder = None
		self.whoBigblind(self.dealerCounter, self.tableplayers)

		self.pushMsg('Game started.')

		self.game_Blinds()

	''' specific functions '''
	def createWindow(self):
		self.wnd.geometry('150x150')
		self.wnd.title('Poker -- Server -- Game')
		lbl = Label(self.wnd, text='Game in progress.')
		lbl.pack()

	def whoDealer(self, counter, players):
		''' checks which player is dealer '''
		dealer = players[counter]
		dealer.dealer = True
		counter += 1
		counter %= len(players)
		self.dealer = dealer

	def whoSmallblind(self, counter, players):
		smallblinder = players[counter+1]
		smallblinder.smallblind = True
		self.smallblinder = smallblinder

	def whoBigblind(self, counter, players):
		bigblinder = players[counter+2]
		bigblinder.bigblind = True
		self.bigblinder = bigblinder

	''' action functions '''
	def checked(self, player):
		self.pushMsg('[all]>> %s checked.' % player.playername)

	def called(self, player):
		thebet = self.maxbet - player.bet
		player.bet += thebet 
		player.stack -= thebet
		self.pot += thebet
		self.pushMsg('[all]>> %s called.' % player.playername)

	def betted(self, player, betamt):
		thebet = betamt
		player.bet = thebet
		self.maxbet = thebet
		self.pot += thebet
		player.stack -= thebet
		self.pushMsg('[all]>> %s bet %s.' % (player.playername, betamt))

	def raised(self, player, raiseamt):
		thebet = raiseamt
		player.bet += thebet
		self.maxbet = player.bet
		player.stack -= thebet
		self.pot += thebet
		self.pushMsg('[all]>> %s raised by %s.' % (player.playername, raiseamt))

	def folded(self, player):
		self.activeplayers.remove(player)
		self.pushMsg('[all]>> %s folded.' % player.playername)

	''' game functions '''
	def game_Blinds(self):
		self.street = 'blinds'

		print 'We reached the blinds phase.'

		for player in self.tableplayers:
			player.holecards.append(self.deck.takeTopCard())
			player.holecards.append(self.deck.takeTopCard())
			string = '[%s]>> Your holecards are: %s.' % (player.playername, player.holecards)
			self.sendMsg(player.playername, string)

			if player == self.smallblinder:
				player.bet = self.smallblind
				player.stack -= self.smallblind
				self.pot += self.smallblind
				self.pushMsg('[all]>> %s paid the small blind of %s.' % (player.playername, self.smallblind))

			elif player == self.bigblinder:
				player.bet = self.bigblind
				player.stack -= self.bigblind
				self.pot += self.bigblind
				self.maxbet = self.bigblind
				self.pushMsg('[all]>> %s paid the big blind of %s.' % (player.playername, self.bigblind))

		''' turns all players into active players '''
		for i in self.tableplayers[3:]:
			self.activeplayers.append(i)

		for i in self.tableplayers[:3]:
			self.activeplayers.append(i)

		self.game_Preflop()

	def game_Preflop(self):
		self.street = 'preflop'
		print 'We reached the preflop phase.'
		self.playercntr = 0

		while self.roundOn():
			self.processSt()

		self.reInitialize()

		self.game_Flop()

	def game_Flop(self):
		if self.iswinner == True:
			return
		self.beginSt('flop')

		while self.roundOn():
			self.processSt()

		self.reInitialize()

		self.game_Turn()

	def game_Turn(self):
		if self.iswinner == True:
			return
		self.beginSt('turn')

		while self.roundOn():
			self.processSt()

		self.reInitialize()

		self.game_River()

	def game_River(self):
		if self.iswinner == True:
			return
		self.beginSt('river')

		while self.roundOn():
			self.processSt()

		if self.iswinner == False:
			winners = self.calcWinners()
			self.win(winners)

	''' game helper functions '''
	def possibleActs(self):
		if self.maxbet == 0:
			return ['bet', 'check', 'fold']
		elif self.maxbet == self.bigblind and self.currentplyrobj.bigblind and self.street == 'preflop':
			return ['check', 'raise', 'fold']
		else:
			return ['call', 'raise', 'fold']

	def beginSt(self, st):
		print 'We reached the %s.' % st
		if self.iswinner == False:
			self.street = st
			self.maxbet = 0
			self.playercntr = 0

			self.communitycards.append(self.deck.takeTopCard())
			if st == 'flop':
				for i in range(2):
					self.communitycards.append(self.deck.takeTopCard())     
			msg = '[all]>> The community cards after the %s are %s.' % (self.street, self.communitycards)
			self.pushMsg(msg)

	def roundOn(self):
		if len(self.activeplayers) == 1:
			self.win([self.activeplayers[0]])
			return False
		for i in self.activeplayers:
			if i.bet != self.maxbet or i.roundturns == 0:
				print 'The round is on.'
				return True
		return False

	def processSt(self):
		player = self.activeplayers[self.playercntr]	# get player object
		self.currentplyrobj = player
		self.possibleacts = self.possibleActs()

		player.yourturn = True
		for obj in self.tableplayers:
			self.giveGameData(obj)
		lets.timer1()

		print "It is %s's turn." % player.playername

		str1 = '[%s]>> Your holecards are %s.' % (player.playername, player.holecards)
		self.sendMsg(player.playername, str1)
		str2 = '[%s]>> You can do the following %s.' % (player.playername, self.possibleacts)
		self.sendMsg(player.playername, str2)

		act = self.getResponse()
		while (act == None):
			act = self.getResponse()

		if act == 'check':
			self.checked(player)
			
		elif act == 'call':
			self.called(player)

		elif act =='bet':
			betstr = '[%s]>> You want to bet: ' % player.playername
			self.sendMsg(player.playername, betstr)
			betamt = self.getIntResponse()
			while (betamt == None):
				betamt = self.getIntResponse()
			self.betted(player, betamt)

		elif act == 'raise':
			raisestr = '[%s]>> You want to raise by: ' % player.playername
			self.sendMsg(player.playername, raisestr)
			raiseamt = self.getIntResponse()
			while (raiseamt == None):
				raiseamt = self.getIntResponse()
			self.raised(player, raiseamt)

		elif act == 'fold':
			self.folded(player)

		player.roundturns += 1
		player.yourturn = False

		if act != 'fold':
			self.playercntr += 1
			self.playercntr %= len(self.activeplayers)

	def reInitialize(self):
		''' reinitializing variables for active players '''
		for i in self.activeplayers:
			i.bet = 0
			i.roundturns = 0

	''' winning functions '''
	def win(self, winners):
		self.iswinner = True
		for i in winners:
			winnings = float(self.pot)/len(winners)
			i.stack += winnings
			for k in self.tableplayers:
				str1 = '[all]>> ' + i.playername + ' won: ' + str(winnings)
				self.sendMsg(k.playername, str1)
				if self.street == 'river':
					str2 = '[all]>> ' + i.playername + "'s hand was: " + ', '.join(i.besthand)
					self.sendMsg(k.playername, str2)
		for j in self.tableplayers:
			j.dealer = False
			j.smallblind = False
			j.bigblind = False
			j.bet = 0
			j.roundturns = 0
			j.result = 11
			j.besthand = ()
		self.pushMsg('Game done.')
		print 'The game is done.'
		lets.timer1()
		self.wnd.destroy()

	def getAllHands(self, player):
		''' returns list of all possible hands with community and hole cards '''
		allcards = player.holecards + self.communitycards
		return list(itertools.combinations(allcards, 5))

	def getBestHand(self, player):
		''' returns strength of player's hand '''
		allhands = self.getAllHands(player)
		counter = 11
		saved = ()
		for hand in allhands:
			eve = HandEvaluator(list(hand))
			pos = eve.evaluate()
			if pos < counter:
				counter = pos
				saved = hand
		return counter, saved

	def calcWinners(self):
		''' calculates who are the winners, returns as list '''
		winners = []
		best = 11
		for plyr in self.activeplayers:
			plyr.result, plyr.besthand = self.getBestHand(plyr)
			if plyr.result <= best:
				best = plyr.result
				winners.append(plyr)
		for plyr in winners:
			if plyr.result != best:
				winners.remove(plyr)
		return winners

	''' general functions '''
	def pushMsg(self, message):
		for plyrobj in self.tableplayers:
			plyrname = plyrobj.playername
			self.server.sendMessage(self.s, plyrname, message)

	def sendMsg(self, plyrname, message):
		self.server.sendMessage(self.s, plyrname, message)

	def getResponse(self):
		plyrname = self.currentplyrobj.playername
		gotit = False
		recvsmt = False
		response = ''

		self.themail = self.server.getMail(self.s)
		for t in self.themail:
			user, msg = t[0], t[1]
			if user == plyrname:
				if msg in self.possibleacts:
					response = msg
					gotit = True
				else:
					recvsmt = True

		if gotit:
			if (response == 'call' or response == 'raise') and self.maxbet > self.currentplyrobj.stack:
				str1 = '[%s]>> That is not a possibility.' % plyrname
				self.sendMsg(plyrname, str1)
			else:	
				return response
		else:
			if recvsmt:
				str1 = '[%s]>> That is not a possibility.' % plyrname
				self.sendMsg(plyrname, str1)
				str2 = '[%s]>> You can do the following %s.' % (plyrname, self.possibleacts)
				self.sendMsg(plyrname, str2)

	def getIntResponse(self):
		plyrname = self.currentplyrobj.playername
		ints = range(int(self.currentplyrobj.stack)+1)
		for nr in range(len(ints)):
			ints[nr] = str(ints[nr])
		gotit = False
		recvsmt = False
		response = ''

		self.themail = self.server.getMail(self.s)
		for t in self.themail:
			user, msg = t[0], t[1]
			if user == plyrname:
				if msg in ints:
					response = msg
					gotit = True
				else:
					recvsmt = True

		if gotit:
			return int(response)
		else:
			if recvsmt:
				str1 = '[%s]>> That is not a possibility.' % plyrname
				self.sendMsg(plyrname, str1)
				str2 = '[%s]>> Please enter a value: ' % plyrname
				self.sendMsg(plyrname, str2)

	def giveGameData(self, playerobj):
		plyrname = playerobj.playername

		data = ['gamexx']

		data += ['location']
		data += [playerobj.location]

		data += ['street']
		data += [self.street]

		data += ['activeplayers']
		if self.street == '' or self.street == 'blinds':
			for v in self.tableplayers:
				data.append(v.playername)
		else:
			for v in self.activeplayers:
				data.append(v.playername)

		data += ['gameinfo']
		for i in [self.maxbet, playerobj.bet, self.pot, playerobj.stack]:
			data += [str(i)]

		data += ['holecards']
		for j in playerobj.holecards:
			data += [j]

		data += ['yourturn']
		data += [str(playerobj.yourturn)]

		data += ['possibleacts']
		for l in self.possibleacts:
			data += [l]

		data += ['communitycards']
		for k in self.communitycards:
			data += [k]

		data += ['END']
		dstring = '-'.join(data)

		self.sendMsg(plyrname, dstring)



class HandEvaluator:
	''' returns value that represents strength of hand '''
	def __init__(self, hand):
		self.allcards = hand

		self.dec = 0.99
		self.vs = {'A':0.01, 'K':0.02, 'Q':0.03, 'J':0.04, '10':0.05, '9':0.06, '8':0.07, '7':0.08, \
		 '6':0.09, '5':0.1, '4':0.11, '3':0.12, '2':0.13}

		self.values = []
		self.onlyvalues = []
		self.valueCount = 6
		self.getValueCount()
		self.suits = []
		self.suitCount = 6
		self.getSuitCount()
		
		self.isStraight = False
		self.checkStraight()
		self.isFlush = False
		self.checkFlush()

	def getValueCount(self):
		''' returns number of different values of hand '''
		for i in self.allcards:
			if len(i) != 3:
				self.onlyvalues.append(i[0])
			else:
				self.onlyvalues.append(i[0:2])
		self.values = list(set(self.onlyvalues))
		self.valueCount = len(self.values)

	def getSuitCount(self):
		''' returns number of different suits of hand '''
		for i in self.allcards:
			if len(i) != 3:
				self.suits.append(i[1])
			else:
				self.suits.append(i[2])
		self.suits = list(set(self.suits))
		self.suitCount = len(self.suits)

	def checkStraight(self):
		''' checks if hand is a straight '''
		if self.valueCount == 5:
			realvalues = []
			for i in self.values:
				''' turn J, Q, K, A into number '''
				if i == 'J':
					i = '11'
				elif i == 'Q':
					i = '12'
				elif i == 'K':
					i = '13'
				elif i == 'A':
					i = '14'
				realvalues.append(int(i))
			realvalues.sort()
			if realvalues == range(realvalues[0], realvalues[0]+5):
				self.isStraight = True
				return
			elif realvalues == (range(realvalues[0], realvalues[0]+4) + [14]):
				self.isStraight = True
				return
			self.isStraight = False
			return
		self.isStraight = False
		return

	def checkFlush(self):
		if self.suitCount == 1:
			self.isFlush = True
			return
		self.isFlush = False
		return


	def checkRoyalFlush(self):
		if self.isFlush and self.isStraight:
			royal = ['A', 'K', 'Q', 'J', '10']
			for i in royal:
				if i not in self.values:
					return False
			return True
		return False

	def checkStraightFlush(self):
		if self.isFlush and self.isStraight:
			self.getDec('hi1')
			return True
		return False

	def checkFourKind(self):
		if len(self.values) == 2:
			if self.onlyvalues.count(self.values[0]) == 4:
				return True
			elif self.onlyvalues.count(self.values[1]) == 4:
				return True
			return False
		return False

	def checkFullHouse(self):
		if len(self.values) == 2:
			if not self.checkFourKind():
				return True
			return False
		return False

	def checkThreeKind(self):
		if len(self.values) == 3:
			if self.onlyvalues.count(self.values[0]) == 3:
				return True
			elif self.onlyvalues.count(self.values[1]) == 3:
				return True
			elif self.onlyvalues.count(self.values[2]) == 3:
				return True
			return False
		return False

	def checkTwoPair(self):
		if len(self.values) == 3:
			if not self.checkThreeKind():
				return True
			return False
		return False

	def checkPair(self):
		if len(self.values) == 4:
			return True
		return False


	def getDec(self, kind):
		if kind == 'hi1':
			for val in self.values:
				if self.vs[val] < self.dec:
					value = val

			if self.isStraight:
				if value == 'A' and '2' in self.values:
					value = '5'
				self.dec = self.vs[value]
		
			else:
				''' for high card or flush cases'''
				dec1 = 0.99
				val1 = None
				restvals1 = self.values
				restvals1.remove(value)
				for val in restvals1:
					if self.vs[val] < dec1:
						dec1 = self.vs[val]
						val1 = val

				dec2 = 0.99
				val2 = None
				restvals2 = restvals1
				restvals2.remove(val1)
				for val in restvals2:
					if self.vs[val] < dec2:
						dec2 = self.vs[val]
						val2 = val

				dec3 = 0.99
				val3 = None
				restvals3 = restvals2
				restvals3.remove(val2)
				for val in restvals3:
					if self.vs[val] < dec3:
						dec3 = self.vs[val]
						val3 = val

				restvals3.remove(val3)
				val4 = restvals3[0]
				dec4 = self.vs[val4]

				self.dec = self.vs[value] + (dec1 * 0.01) + (dec2 * 0.0001) + (dec3 * 0.000001) + (dec4 * 0.00000001)

		elif kind == 'pick4':
			cntr0, cntr1 = 0, 0
			for card in self.allcards:
				if self.values[0] in card:
					cntr0 += 1
				else:
					cntr1 += 1

			if cntr0 > cntr1:
				val = self.values[0]
				otherval = self.values[1]
			else:
				val = self.values[1]
				otherval = self.values[0]

			self.dec = self.vs[val] + (self.vs[otherval] * 0.01)

		elif kind == 'pick3':
			cntr0, cntr1, cntr2 = 0, 0, 0
			for card in self.allcards:
				if self.values[0] in card:
					cntr0 += 1
				elif self.values[1] in card:
					cntr1 += 1
				else:
					cntr2 += 1
			if cntr0 == 3:
				val = self.values[0]
				if self.vs[self.values[1]] < self.vs[self.values[2]]:
					otherval1 = self.values[1]
					otherval2 = self.values[2]
				else:
					otherval1 = self.values[2]
					otherval2 = self.values[1]
			elif cntr1 == 3:
				val = self.values[1]
				if self.vs[self.values[2]] < self.vs[self.values[0]]:
					otherval1 = self.values[2]
					otherval2 = self.values[0]
				else:
					otherval1 = self.values[0]
					otherval2 = self.values[2]
			else:
				val = self.values[2]
				if self.vs[self.values[1]] < self.vs[self.values[0]]:
					otherval1 = self.values[1]
					otherval2 = self.values[0]
				else:
					otherval1 = self.values[0]
					otherval2 = self.values[1]

			self.dec = self.vs[val] + (self.vs[otherval1] * 0.01) + (self.vs[otherval2] * 0.0001)

		elif kind == 'pick2':
			cntr0, cntr1, cntr2 = 0, 0, 0
			for card in self.allcards:
				if self.values[0] in card:
					cntr0 += 1
				elif self.values[1] in card:
					cntr1 += 1
				else:
					cntr2 += 1
			if cntr0 == cntr1:
				comp = (self.values[0], self.values[1])
				otherval = self.values[2]
			elif cntr0 == cntr2:
				comp = (self.values[0], self.values[2])
				otherval = self.values[1]
			else:
				comp = (self.values[1], self.values[2])
				otherval = self.values[0]
			
			if self.vs[comp[0]] < self.vs[comp[1]]:
				val1 = comp[0]
				val2 = comp[1]
			else:
				val1 = comp[1]
				val2 = comp[0]

			self.dec = self.vs[val1] + (self.vs[val2] * 0.01) + (self.vs[otherval] * 0.0001)

		elif kind == 'pickpair':
			cntr0, cntr1, cntr2, cntr3 = 0, 0, 0, 0
			for card in self.allcards:
				if self.values[0] in card:
					cntr0 += 1
				elif self.values[1] in card:
					cntr1 += 1
				elif self.values[2] in card:
					cntr2 += 1
				else:
					cntr3 += 1
			if cntr0 == 2:
				value = self.values[0]
			elif cntr1 == 2:
				value = self.values[1]
			elif cntr2 == 2:
				value = self.values[2]
			else:
				value = self.values[3]

			dec1 = 0.99
			val1 = None
			restvals1 = self.values
			restvals1.remove(value)
			for val in restvals1:
				if self.vs[val] < dec1:
					dec1 = self.vs[val]
					val1 = val

			dec2 = 0.99
			val2 = None
			restvals2 = restvals1
			restvals2.remove(val1)
			for val in restvals2:
				if self.vs[val] < dec2:
					dec2 = self.vs[val]
					val2 = val

			restvals2.remove(val2)
			val3 = restvals2[0]
			dec3 = self.vs[val3]

			self.dec = self.vs[value] + (dec1 * 0.01) + (dec2 * 0.0001) + (dec3 * 0.000001)


	def evaluate(self):
		if self.checkRoyalFlush():
			return 1
		elif self.checkStraightFlush():
			self.getDec('hi1')
			return 2 + self.dec
		elif self.checkFourKind():
			self.getDec('pick4')
			return 3 + self.dec
		elif self.checkFullHouse():
			self.getDec('pick4')
			return 4 + self.dec
		elif self.isFlush:
			self.getDec('hi1')
			return 5 + self.dec
		elif self.isStraight:
			self.getDec('hi1')
			return 6 + self.dec
		elif self.checkThreeKind():
			self.getDec('pick3')
			return 7 + self.dec
		elif self.checkTwoPair():
			self.getDec('pick2')
			return 8 + self.dec
		elif self.checkPair(): 
			self.getDec('pickpair')
			return 9 + self.dec
		else:   #high card
			self.getDec('hi1')
			return 10 + self.dec


class ChatProgram:
	def __init__(self):
		self.thename = ''

	# creates socket connection
	def startConnection(self, IPAddress, PortNumber):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((IPAddress, PortNumber))
		return s

	# logs user into server
	def login(self, s, username, password):
		s.send('LOGIN ' + username + '\n')
		text = s.recv(2048)
		CH = self.findChallenge(text)
		PD = password
		n, m = len(PD), len(CH)
		block = PD + CH + "1"
		while len(block) < 509:
			block += "0"
		length = n + m
		if length < 10:
			strlength = "00" + str(length)
		elif length < 100:
			strlength = "0" + str(length)
		else:
			strlength = str(length)
		block += strlength

		M = []
		while block != "":
			Asum = 0
			substring = block[:32]
			for letter in substring:
				Asum += ord(letter)
			M.append(Asum)
			block = block[32:]

		S = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, \
			 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, \
			 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, \
			 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]
		K = [0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, \
			 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501, \
			 0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, \
			 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821, \
			 0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, \
			 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8, \
			 0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, \
			 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a, \
			 0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, \
			 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70, \
			 0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, \
			 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665, \
			 0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, \
			 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1, \
			 0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, \
			 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391]

		a0 = 0x67452301   #A
		b0 = 0xefcdab89   #B
		c0 = 0x98badcfe   #C
		d0 = 0x10325476   #D
		A, B, C, D = a0, b0, c0, d0
		
		for i in range(64):
			if 0 <= i and i <= 15:

				F = (B & C) | ((~ B) & D)
				F = F & 0xFFFFFFFF
				g = i
			elif 16 <= i and i <= 31:
				F = (D & B) | ((~ D) & C)
				F = F & 0xFFFFFFFF
				g = (5*i + 1) % 16
			elif 32 <= i and i <= 47:
				F = B ^ C ^ D
				F = F & 0xFFFFFFFF
				g = (3*i + 5) % 16
			elif 48 <= i and i <= 63:
				F = C ^ (B  | (~D))
				F = F & 0xFFFFFFFF
				g = (7*i) % 16
			dTemp = D
			D = C
			C = B
			B = B + self.leftrotate((A + F + K[i] + M[g]), S[i])
			B = B & 0xFFFFFFFF
			A = dTemp
			
		a0 = (a0 + A) & 0xFFFFFFFF
		b0 = (b0 + B) & 0xFFFFFFFF
		c0 = (c0 + C) & 0xFFFFFFFF
		d0 = (d0 + D) & 0xFFFFFFFF

		result = str(a0) + str(b0) + str(c0) + str(d0)
		
		s.send('LOGIN ' + username + ' ' + result + '\n')

		data = s.recv(2048)
		if 'Successful' in data:
			self.thename = username
			return True
		else:
			return False

	# finds hash from received string
	def findChallenge(self, text):
		i = 0
		while text[i] != " ":
			i += 1
		i += 1
		while text[i] != " ":
			i += 1
		i += 1
		return text[i:]

	def leftrotate (self, x, c):
		return (x << c)&0xFFFFFFFF | (x >> (32-c)&0x7FFFFFFF>>(32-c))

	# takes a server command and returns responses in list
	def taskTwo(self, s, msg):
		s.send(msg)
		reply = s.recv(2048)
		thelist = reply.split('@')
		if thelist[2] == '0':
			thelist = []
		else:
			thelist = thelist[4:]
		return thelist

	# creates command for server depending on username and action (msg)
	def taskThree(self, s, username, msg):
		command1 = msg + '@friend' + '@' + username
		sizestr = str(6 + len(command1))
		l = len(sizestr)
		addl = 5 - l
		stradd = ''
		for i in range(addl):
			stradd += '0'
		size = stradd + sizestr
		command2 = '@' + size + command1
		s.send(command2)
		reply = s.recv(2048)
		if '@ok' in reply:
			return True
		return False

	# sends message to username (friend)
	def sendMessage(self, s, friend, message):
		command1 = '@sendmsg' + '@' + friend + '@' + message
		sizestr = str(6 + len(command1))
		l = len(sizestr)
		addl = 5 - l
		stradd = ''
		for i in range(addl):
			stradd += '0'
		size = stradd + sizestr
		command2 = '@' + size + command1
		s.send(command2)
		reply = s.recv(2048)
		if '@ok' in reply:
			return True
		return False

	# shows messages received as a list
	def getMail(self, s):
		s.send('@rxmsg')
		reply = s.recv(2048)

		thelist = reply.split('@')
		if thelist != []:
			thelist = [x for x in thelist if x != 'msg']
		if thelist[2] == '0':
			thelist = []
		else:
			if 'file' in thelist:
				findex = thelist.get('file')
				thelist = thelist[3:findex] + ['end']
			else:
				thelist = thelist[3:] + ['end']

		newlist = []
		if thelist != []:
			while thelist != ['end'] and len(thelist) >= 3:
				sin = (thelist[0], thelist[1])
				newlist.append(sin)
				thelist = thelist[2:]

		return newlist



wnd = Tk()
global lets
lets = Start(wnd)
wnd.geometry('200x200')
wnd.title('Poker -- Server')
wnd.mainloop()

