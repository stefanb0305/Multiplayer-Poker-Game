#    15-112: Principles of Programming and Computer Science
#    Final Project: Poker game, play.py
#    Name      : Stefan Baumann
#    AndrewID  : sbaumann
#    Created   : 03 DEC 2018
#    Updated   : 07 DEC 2018


import socket
from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk

class ChatProgram:
	def __init__(self):
		self.thename = ''
		self.location = 'Login'

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

	# returns name of user
	def getName(self):
		return self.thename

	# shows messages received as a list
	def getMail(self, s):
		s.send('@rxmsg')
		reply = s.recv(2048)

		thelist = reply.split('@')
		thelist = [x for x in thelist if x != 'msg']
		if len(thelist) < 3:
			return []
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
			while thelist != ['end'] and len(thelist) > 2:
				sin = (thelist[0], thelist[1])
				newlist.append(sin)
				thelist = thelist[2:]

		return newlist

player = ChatProgram()


class LoginGUI:
	''' creates window for players to log in to server '''
	def __init__(self, parent, player):
		self.parent = parent
		self.parent.title('Poker -- Log In')
		self.parent.resizable(False, False)

		self.theframe = Frame()
		self.theframe.pack()
		self.maketheFrame()

		self.errorlbl = None

		self.player = player
		self.s = self.player.startConnection('86.36.46.10', 15112)

	def maketheFrame(self):
		''' creates the window '''
		userlbl = Label(self.theframe, text='Username')
		userlbl.pack()
		self.textboxuser = Entry(self.theframe)
		self.textboxuser.pack() 
		passlbl = Label(self.theframe, text='Password')
		passlbl.pack() 
		self.textboxpass = Entry(self.theframe, show="*")
		self.textboxpass.pack()
		okbutton = Button(self.theframe, text='OK', command=self.okClicked)
		okbutton.pack()

	def okClicked(self):
		''' tries logging use in '''
		if self.errorlbl != None:
			self.errorlbl.destroy()

		inputs = self.getInputs()
		if inputs[0] != '' and inputs[0] != '':
			returned = self.player.login(self.s, inputs[0], inputs[1])
			if returned:
				''' add server as friend, destroy log in page and create new window for open room '''
				self.parent.destroy()
				self.successLogin()
				page2 = OpenRoomGUI(self.s, self.player)
			else:
				self.errorLogin()
		else:
			self.errorLogin()

	def getInputs(self):
		''' returns inputs of text boxes as tuple '''
		userinput = self.textboxuser.get()
		passinput = self.textboxpass.get()
		return (userinput, passinput)
	
	def errorLogin(self):
		self.errorlbl = Label(self.theframe, text="Couldn't find your account.", foreground='red')
		self.errorlbl.pack()
		self.textboxuser.delete(0, END)
		self.textboxpass.delete(0, END)

	def successLogin(self):
		self.player.taskThree(self.s, 'sbaumann11', '@request')
		logon = self.player.sendMessage(self.s, 'sbaumann11', 'Logon-Player')
		while not logon:
			logon = self.player.sendMessage(self.s, 'sbaumann11', 'Logon-Player')


class OpenRoomGUI:
	''' creates window with all the main info on it and where you can create a game '''
	def __init__(self, s, player):
		self.parent = Tk()
		self.parent.title('Poker -- Open Room -- %s' % player.thename)
		self.parent.geometry('1080x608')
		self.parent.resizable(False, False)
		theimg = Image.open('bg2.png')
		thebg = ImageTk.PhotoImage(theimg)
		bglabel2 = Label(self.parent, image=thebg)
		bglabel2.pack()

		self.player = player
		self.s = s

		self.theopenmsg = []
		self.anythingnew = False
		self.excntr = 0

		self.onlineusers = []			# list of online player names
		self.tableplayers = []			# list of player names on table
		self.tablefull = False 			# boolean for table capacity
		self.gamestarted = False 		# boolean for game running

		self.myinfo = []				# [name, stack]
		self.canplay = True				# boolean for playable

		self.after_id = None

		self.errlbl = None				# error label if can not play
		self.thebox = None				# the message box
		self.makeBg()

		self.makeFrame1()
		self.makeFrame2()
		self.makeFrame3()

		self.timedEventRoom()

		self.parent.protocol("WM_DELETE_WINDOW", self.exitPro)
		self.parent.mainloop()
		
	def makeBg(self):
		lbl1 = Label(self.parent, text='A Poker Program by sbaumann')
		lbl1.config(font=('Arial',26))
		lbl1.place(relx=0.5, rely=0.05, anchor=CENTER)

		self.thebox = Listbox(self.parent, width=40, height=7)
		self.thebox.place(relx=0.8, rely=0.39, anchor=CENTER)

	def timedEventRoom(self):
		self.getInfo()

		if self.anythingnew:
			self.frame1.destroy()
			self.makeFrame1()
			self.frame2.destroy()
			self.makeFrame2()
			self.frame3.destroy()
			self.makeFrame3()

		self.updateMsgBox()

		self.after_id = self.parent.after(1500, self.timedEventRoom)


	def getInfo(self):
		allmsg = self.player.getMail(self.s)
		self.theopenmsg = allmsg

		if allmsg == []:
			return

		themsgs = []
		for i in allmsg:
			if i[0] == 'sbaumann11' and 'homexx' in i[1] and 'END' in i[1]:
				themsgs.append(i[1])

		if themsgs != []:
			themessage = themsgs[len(themsgs)-1]
			self.anythingnew = True
		else:
			self.anythingnew = False
			return

		themessage = themessage.split('-')

		j = 2
		self.player.location == themessage[j]

		self.onlineusers = []
		j += 2
		while themessage[j] != 'canplay':
			self.onlineusers.append(themessage[j])
			j += 1
		j += 1

		if themessage[j] == 'True':
			self.canplay = True
		else:
			self.canplay = False
		j += 2

		self.myinfo = []
		while themessage[j] != 'tablespace':
			self.myinfo.append(themessage[j])
			j += 1

		j += 1
		if int(themessage[j]) >= 1:
			self.tablefull = False
		else:
			self.tablefull = True

		self.tableplayers = []
		j += 2
		while themessage[j] != 'gameon':
			self.tableplayers.append(themessage[j])
			j += 1

		j += 1
		if themessage[j] == 'True':
			self.gamestarted = True
		else:
			self.gamestarted = False

	def makeFrame1(self):
		self.frame1 = Frame(self.parent, width=150, height=150)
		self.frame1.place(relx=0.15, rely=0.3, anchor=CENTER)

		lbl2 = Label(self.frame1, text='Online players')
		lbl2.pack()

		self.onlinebox = Listbox(self.frame1, height=11, selectmode=SINGLE)
		for i in self.onlineusers:
			self.onlinebox.insert(END, i)
		self.onlinebox.pack()

		# invitebtn = Button(self.frame1, text='Invite to table', command=self.inviteToTable)
		# invitebtn.pack()

	def makeFrame2(self):
		self.frame2 = Frame(self.parent, width=150)
		self.frame2.place(relx=0.5, rely=0.3, anchor=CENTER)

		lbl = Label(self.frame2, text='Players on table')
		lbl.pack()

		self.tablebox = Listbox(self.frame2, height=11)
		for i in self.tableplayers:
			self.tablebox.insert(END, i)
		self.tablebox.pack()

		thestate = self.checkState()
		btn = Button(self.frame2, text='Sit on table', state=thestate, command=self.joinTable)
		btn.pack()

	def makeFrame3(self):
		self.frame3 = Frame(self.parent, width=150, height=150)
		self.frame3.place(relx=0.75, rely=0.1)

		lbl1 = Label(self.frame3, text="Profile")
		lbl1.pack()

		btn = Button(self.frame3, text='Exit', command=self.exitPro)

		if self.myinfo == []:
			btn.pack()
			return

		lbl2 = Label(self.frame3, text="Name: %s" % self.myinfo[0])
		lbl2.pack()

		lbl3 = Label(self.frame3, text="Stack: %s" % self.myinfo[1])
		lbl3.pack()

		btn.pack()

	def updateMsgBox(self):
		# print 'messaaages: ', self.theopenmsg
		for i in self.theopenmsg:
			person = i[0]
			msg = i[1]
			if person == 'sbaumann11':
				if ('Welcome to' in msg) or ('Join the table' in msg):
					self.thebox.insert(END, msg)
			elif (('wants you to' in msg) or ('is already on' in msg)) and (self.excntr < 3):
				self.thebox.insert(END, msg)
				self.excnty += 1


	def joinTable(self):
		if self.errlbl != None:
			self.errlbl.destroy()
		if not self.canplay:
			self.errlbl = Label(self.frame2, fg='red', text="Your stack is too small.")
			self.errlbl.pack()
			return
		self.player.sendMessage(self.s, 'sbaumann11', 'Sit-Table')
		self.player.location = 'Table'
		if self.after_id != None:
			self.parent.after_cancel(self.after_id)
		self.parent.destroy()
		pagen = TableGUI(self.s, self.player)

	def exitPro(self):
		self.player.sendMessage(self.s, 'sbaumann11', 'Logoff-Player')
		self.parent.destroy()

	def checkState(self):
		if not self.tablefull and not self.gamestarted:
			return 'normal'
		return 'disabled'

	def inviteToTable(self):
		cell = self.onlinebox.curselection()
		if cell != '':
			selplayer = self.onlinebox.get(cell)
			if selplayer not in self.tableplayers:
				self.player.sendMessage(self.s, selplayer, ('%s wants you to join the table.' % self.player.thename))
				self.thebox.insert(END, 'Invite sent to %s.' % selplayer)
			else:
				self.thebox.insert(END, '%s is already on the table.' % selplayer)




class TableGUI:
	''' creates window when a game is created with players on it, keeps the OpenRoom open tho '''
	def __init__(self, s, player):
		self.parent = Tk()
		self.parent.title('Poker -- Table -- %s' % player.thename)
		self.parent.geometry('800x650')
		self.parent.resizable(False, False)
		theimg = Image.open('bg3.png')
		self.thebg = ImageTk.PhotoImage(theimg)
		bglabel3 = Label(self.parent, image=self.thebg)
		bglabel3.pack()

		self.s = s
		self.player = player

		self.anythingnew = False
		self.gamestarted = False
		self.themessages = []
		self.tableplayers = []
		self.eycntr = 0

		self.street = ''
		self.activeplayers = ['']
		self.gameinfo = ['', '', '', '']
		self.holecards = ['', '']
		self.yourturn = False
		self.communitycards = []
		self.possibleacts = []

		self.after_id = None
		self.gamewidgets = []


		self.frameclose = Frame(self.parent)
		thisstate = self.returnOtherState()
		self.btnexit = Button(self.frameclose, text='Leave table', state=thisstate, command=self.leaveTable)
		self.framestart = Frame(self.parent)
		self.tableplyrframe = Frame(self.parent)
		self.makeTableBg()

		self.chatframe = Frame(self.parent, width=160, height=220)
		self.convobox = Listbox(self.chatframe)
		self.msgbox = Entry(self.chatframe, width=20)
		datstate = self.returnState()
		self.enterbtn = Button(self.chatframe, text='Enter', state=datstate, command=self.sendInfo)
		self.makeChatBox()

		self.parent.protocol("WM_DELETE_WINDOW", self.leaveTable)
		self.timedEventTable()

		self.parent.mainloop()

	def makeTableBg(self):
		self.frameclose.place(x=2, y=2)
		self.btnexit.pack()

		self.framestart.place(relx=0.5, rely=0.35, anchor=CENTER)
		thestate = self.gameCanStart()
		btnstart = Button(self.framestart, text='Start game', state=thestate, command=self.startGame)
		btnstart.pack()

		self.tableplyrframe.place(relx=0.5, rely=0.8, anchor=CENTER)
		plyrlbl = Label(self.tableplyrframe, text='Players on table')
		plyrlbl.pack()

	def makeChatBox(self):
		''' creates message box for further commands '''
		self.chatframe.place(x=560, y=435)
		self.convobox.pack(fill=BOTH, expand=2)
		self.msgbox.pack(side=LEFT)
		self.enterbtn.pack(side=RIGHT)


	def leaveTable(self):
		self.player.sendMessage(self.s, 'sbaumann11', 'Leave-Table')
		if self.after_id != None:
			self.parent.after_cancel(self.after_id)
		self.parent.destroy()
		self.player.location = 'Open'
		pagen = OpenRoomGUI(self.s, self.player)

	def startGame(self):
		self.player.sendMessage(self.s, 'sbaumann11', 'Start-Game')

	def gameCanStart(self):
		if len(self.tableplayers) >= 2:
			return 'normal'
		return 'disabled'

	def timedEventTable(self):
		self.getOther()
		if self.anythingnew:
			if self.player.location == 'Table':
				self.framestart.destroy()
				self.tableplyrframe.destroy()
				self.getTableData()
				self.makeTableWidgets()
				if self.gameCanStart() == 'disabled':
					notlbl = Label(self.framestart, text='Not enough players on table.', fg='red')
					notlbl.pack()
			elif self.player.location == 'Game':
				self.getGameData()
				for i in self.gamewidgets:
					i.destroy()
				self.gamewidgets = []
				self.makeGameWidgets()
			self.updateBtns()

		self.after_id = self.parent.after(1500, self.timedEventTable)


	def getOther(self):
		allmsg = self.player.getMail(self.s)
		self.themessages = allmsg

		if allmsg == []:
			self.anythingnew = False
		else:
			self.anythingnew = True

		for i in allmsg:
			person = i[0]
			msg = i[1]
			if person == 'sbaumann11':
				if ('Game done.' in msg):
					self.player.sendMessage(self.s, 'sbaumann11', 'Game-Done')
					self.player.location= 'Table'
					for i in self.gamewidgets:
						i.destroy()
					self.getTableData()
					self.makeTableWidgets()
					self.gamestarted = False
				elif ('Game started.' in msg):
					self.player.location = 'Game'
					self.framestart.destroy()
					self.tableplyrframe.destroy()
					self.gamestarted = True
				elif (('The game will' in msg) or ('clicks the' in msg)) and (self.eycntr < 3):
					self.convobox.insert(END, msg)
				elif ('>>' in msg):
					self.convobox.insert(END, msg)

	def getTableData(self):
		allmsg = self.themessages
		themsgs = []
		for i in allmsg:
			if i[0] == 'sbaumann11' and 'tablexx' in i[1] and 'END' in i[1]:
				themsgs.append(i[1])
				
		if themsgs != []:
			themessage = themsgs[len(themsgs)-1]
		else:
			return

		themessage = themessage.split('-')

		c = 2
		# self.player.location = themessage[c]

		self.tableplayers = []
		c += 2
		while themessage[c] != 'gameon':
			self.tableplayers.append(themessage[c])
			c += 1

		c += 1
		if themessage[c] == 'True':
			self.gamestarted = True
		else:
			self.gamestarted = False

	def makeTableWidgets(self):
		self.framestart = Frame(self.parent)
		self.framestart.place(relx=0.5, rely=0.35, anchor=CENTER)
		thestate = self.gameCanStart()
		btnstart = Button(self.framestart, text='Start game', state=thestate, command=self.startGame)
		btnstart.pack()

		self.tableplyrframe = Frame(self.parent)
		self.tableplyrframe.place(relx=0.5, y=536, anchor=CENTER)
		plyrlbl = Label(self.tableplyrframe, text='Players on table')
		plyrlbl.pack()
		plyrbox = Listbox(self.tableplyrframe)
		for i in self.tableplayers:
			plyrbox.insert(END, i)
		plyrbox.pack()

	def getGameData(self):
		allmsg = self.themessages
		themsgs = []
		for i in allmsg:
			if i[0] == 'sbaumann11' and 'gamexx' in i[1] and 'END' in i[1]:
				themsgs.append(i[1])
				
		if themsgs != []:
			themessage = themsgs[len(themsgs)-1]
		else:
			return

		themessage = themessage.split('-')

		z = 2
		# self.player.location = themessage[z]

		z += 2
		self.street = themessage[z]

		z += 2
		self.activeplayers = []
		while themessage[z] != 'gameinfo':
			self.activeplayers.append(themessage[z])
			z += 1

		z += 1
		self.gameinfo = []
		while themessage[z] != 'holecards':
			self.gameinfo.append(themessage[z])
			z += 1

		z += 1
		self.holecards = []
		while themessage[z] != 'yourturn':
			self.holecards.append(themessage[z])
			z += 1

		z += 1
		if themessage[z] == 'True':
			self.yourturn = True
		else:
			self.yourturn = False

		z += 2
		self.possibleacts = []
		while themessage[z] != 'communitycards':
			self.possibleacts.append(themessage[z])
			z += 1

		z += 1
		self.communitycards = []
		while themessage[z] != 'END':
			self.communitycards.append(themessage[z])
			z += 1
		# print 'Community cards: ', self.communitycards

	def makeGameWidgets(self):
		streetlbl = Label(self.parent, text="Street: %s" % self.street)
		streetlbl.place(relx=0.5, y=30, anchor=CENTER)
		self.gamewidgets.append(streetlbl)

		infoframe = Frame(self.parent, width=150, height=230)
		infoframe.place(x=680, y=0)
		info1 = Label(infoframe, text="Highest bet: %s" % self.gameinfo[0])
		info1.pack()
		info2 = Label(infoframe, text="Your bet: %s" % self.gameinfo[1])
		info2.pack()
		info3 = Label(infoframe, text="Pot: %s" % self.gameinfo[2])
		info3.pack()
		info4 = Label(infoframe, text="Your stack: %s" % self.gameinfo[3])
		info4.pack()
		self.gamewidgets.append(infoframe)

		many = len(self.communitycards)
		for nr in range(many):
			x = self.calcPosCard(nr)
			cardfr = Frame(self.parent, width=45, height=63, bg='black')
			cardfr.place(x=x, y=190)

			value = self.communitycards[nr]
			vallbl = Label(cardfr, text=value)
			vallbl.place(relx=0.5, rely=0.5, anchor=CENTER)

			self.gamewidgets.append(cardfr)

		holecardframe = Frame(self.parent, width=130, height=190, bg='grey', bd=2)
		title = Label(holecardframe, text='Your holecards:')
		title.pack()
		if len(self.holecards) == 2:
			hcard1 = Label(holecardframe, text=self.holecards[0])
			hcard1.pack(side=LEFT)
			hcard2 = Label(holecardframe, text=self.holecards[1])
			hcard2.pack(side=RIGHT)
		else:
			l = len(self.holecards)
			hcard1 = Label(holecardframe, text=self.holecards[l-2])
			hcard1.pack(side=LEFT)
			hcard2 = Label(holecardframe, text=self.holecards[l-1])
			hcard2.pack(side=RIGHT)
		holecardframe.place(x=5, y=545)
		self.gamewidgets.append(holecardframe)

		if self.yourturn:
			actframe = Frame(self.parent, width=130, height=190)
			for act in self.possibleacts:
				actbtn = Button(actframe, text=act, command=lambda x = act: self.doAct(x))
				actbtn.pack()
			actframe.place(x=190, y=525)
			self.gamewidgets.append(actframe)

		gameplyrframe = Frame(self.parent)
		gameplyrframe.place(relx=0.5, y=548, anchor=CENTER)
		plyrlbl = Label(gameplyrframe, text='Active players')
		plyrlbl.pack()
		plyrbox = Listbox(gameplyrframe)
		for kl in self.activeplayers:
			plyrbox.insert(END, kl)
		plyrbox.pack()
		self.gamewidgets.append(gameplyrframe)

	def calcPosCard(self, nr):
		''' calculates position of community card in window '''
		cardamount = len(self.communitycards)
		totw = cardamount * 45
		half = totw / 2
		x = (400 - half) + (nr * 45)
		return x

	def updateBtns(self):
		thisstate = self.returnOtherState()
		self.btnexit.configure(state=thisstate)
		self.btnexit.pack()

		datstate = self.returnState()
		self.enterbtn.configure(state=datstate)
		self.enterbtn.pack(side=RIGHT)

	def doAct(self, action):
		self.player.sendMessage(self.s, 'sbaumann11', action)

	def sendInfo(self):
		msg = self.msgbox.get()
		self.player.sendMessage(self.s, 'sbaumann11', msg)
		self.msgbox.delete(0, END)

	def returnState(self):
		if self.yourturn:
			return 'normal'
		return 'disabled'

	def returnOtherState(self):
		if self.gamestarted:
			return 'disabled'
		return 'normal'



wnd = Tk()
wnd.geometry('320x480')

theimg = Image.open('bg1.jpg')
thebg = ImageTk.PhotoImage(theimg)
global bglabel1
bglabel1 = Label(wnd, image=thebg)
bglabel1.place(x=0, y=0, relwidth=1, relheight=1)

page1 = LoginGUI(wnd, player)

wnd.mainloop()



# Image sources
# bg1: https://i.pinimg.com/originals/ed/2f/18/ed2f18d3055df42e8c1d9cd82990b04f.jpg
# bg2: https://d2v9y0dukr6mq2.cloudfront.net/video/thumbnail/ ...
# ... 4wOdBhjueijqd8s52/poker-chips-looping-on-dark-background_vdlqkka_l__F0000.png
