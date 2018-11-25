
#    15-112: Principles of Programming and Computer Science
#    Final Project: Poker game
#    Name      : Stefan Baumann
#    AndrewID  : sbaumann
#    Date      : 23 NOV 2018


from random import *
import socket


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

class Start:
    __init__(self, xxxloggedin, players=[]):
        self.allusers = self.getAllusers(loggedin)
        self.newusers = self.getNewusers(self.allusers) # gotta define
        self.newplayers = self.makeUsersPlayers(self.newusers)
        self.oldplayers = players
        self.allplayers = self.oldplayers + self.newplayers

    def getAllusers(self, loggedin):
        ''' check for logged in users '''
        allusers = []
        for i in loggedin:
            allplayers.append(i)
        return allusers

    def makeUsersPlayers(self, allusers):
        ''' turns users into players and adds them to list '''
        newplayers = []
        for i in allusers:
            player = Player(i)
            allplayers.append(player)
        return newplayers

    def canwantPlay(self, player):
        if player.stack > 100:
            re = "Do you want to play? [yes, no] "
            response = player.getResponse(re)
            if response == 'yes' or response == 'Yes':
                return True
            return False
        return False

    def gameStart(allplayers):
        for i in allplayers:
            if not self.canwantPlay(i):
                allplayers.remove(i)
        if len(allplayers) > 3:
            game = Game(allplayers)
        else:
            for i in allplayers:
                string = 'There are not enough players.'
                i.print(string)

class Player:
    ''' creates a player on the table '''
    def __init__(self, username):
        self.playername = username
        self.stack = 2500
        self.holecards = []

        self.dealer = False
        self.smallblind = False
        self.bigblind = False
        self.enoughMoney = self.checkMoney()

        self.active = False
        self.possibleacts = []

        self.bet = 0
        self.roundturns = 0

    def checkMoney(self):
        if self.stack > mincash:
            return True
        return False

    def getResponse(self, re):
        return raw_input(re)

    def print(self, smt):
        print smt

class Game:
    ''' creates a game with players on table '''
    def __init__(self, players):
        self.allplayers = players
        self.activeplayers = []
        self.playercntr = 0
        self.iswinner = False

        self.pot = 0
        self.communitycards = []
        self.smallblind = 10
        self.bigblind = 20

        self.deck = Deck()
        self.deck.shuffleDeck

        self.dealerCounter = 0
        self.dealer = self.whoDealer(self.dealerCounter, self.allplayers)
        self.smallblinder = self.whoSmallblind(self.dealerCounter, self.allplayers)
        self.bigblinder = self.whoBigblind(self.dealerCounter, self.allplayers)

        self.street = ''
        self.maxbet = 0

   def pushMsg(self, msg):
    for i in self.activeplayers:
        i.print(msg)

    def whoDealer(self, counter, players):
        ''' checks which player is dealer '''
        dealer = players[counter]
        dealer.dealer = True
        counter += 1
        counter %= len(players)
        return dealer

    def whoSmallblind(self, counter, players):
        smallblinder = players[counter+1]
        smallblinder.smallblind = True
        return smallblinder

    def whoBigblind(self, counter, players):
        bigblinder = players[counter+2]
        bigblinder.bigblind = True
        return bigblinder

    def roundOn(self):
        if length(activeplayers) == 1:
            self.win([activeplayers[0]])
            return False
        for i in self.activeplayers:
            if i.bet != self.maxbet or i.roundturns == 0:
                return True
        return False

    def possibleActs(self):
        if self.maxbet == 0:
            return ['bet', 'check', 'fold']
        elif self.maxbet == self.biglind and self.street == 'preflop':
            return ['bet', 'check', 'fold']
        else:
            return ['call', 'raise', 'fold']

    def win(self, winners):
        self.iswinner = True
        for i in winners:
            winnings = float(self.pot)/len(winners)
            i.stack += winnings
            print i, ' won: ', winnings
        for j in self.allplayers:
            j.active = False
            j.bet = 0
            j.roundturns = 0
        lets = Start(xxxloggedin, self.allplayers)  # find out how to only create player object for new log ins

    def getAllHands(self, player):
        ''' returns list of all possible hands with community and hole cards '''
        allcards = player.holecards + self.communitycards
        return list(itertools.combinations(allcards, 5))

    def getBestHand(self, player):
        allhands = getAllHands(player)
        besthand = []
        i = 0 
        counter = 11
        for i in allhands:
            eve = HandEvaluator(list(i))
            pos = eve.evaluate
            if pos < counter:
                counter = pos

    def calcWinner(self):
        fjdkf



    def beginSt(self, st):
        self.street = st
        self.maxbet = 0
        self.playercntr = 0

        self.communitycards.append(self.deck.takeTopCard())
        if st == 'flop':
            for i in range(2):
                self.communitycards.append(self.deck.takeTopCard())     
        msg = 'The community cards after the %s are %s.' % (self.street, self.communitycards)
        self.pushMsg(msg)

    def processSt(self):
        player = self.activeplayers[self.playercntr]
        player.roundturns += 1
        possibleacts = self.possibleActs()
        player.print('Your holecards are %s.' % player.holecards)
        string = 'You can do the following %s.', % possibleacts
        player.print(string)
        re = 'You want to: '
        act = player.getResponse(re)

        while act not in possibleacts:
            player.print('That is not a possibility.')
            string = 'You can do the following %s.', % possibleacts
            player.print(string)
            re = 'You want to: '
            act = player.getResponse(re)

        if act == 'check':
            self.checked(player)
        elif act == 'call':
            self.called(player)
        elif act =='bet':
            betamt = int(player.getResponse('You want to bet: '))
            self.betted(player, betamt)
        elif act == 'raise':
            raiseamt = int(player.getResponse('You want to raise by: '))
            self.raised(player, raiseamt)
        elif act == 'fold':
            self.folded(player)

        self.playercntr += 1
        self.playercntr %= len(self.activeplayers)

    def reInitialize(self):
        ''' reinitializing variables for active players '''
        for i in self.activeplayers:
            i.bet = 0
            i.roundturns = 0


    def checked(self, player):
        self.pushMsg('%s checked.' % player.playername)
        return

    def called(self, player):
        thebet = self.maxbet - player.bet
        player.bet += thebet 
        player.stack -= thebet
        self.pot += thebet
        self.pushMsg('%s called.' % player.playername)

    def betted(self, player, betamt):
        thebet = betamt
        player.bet = thebet
        self.maxbet = thebet
        self.pot += thebet
        self.pushMsg('%s bet %s.' % (player.playername, betamt))

    def raised(self, player, raiseamt):
        thebet = raiseamt
        player.bet += thebet
        self.maxbet = player.bet
        player.stack -= thebet
        self.pot += thebet
        self.pushMsg('%s raised by %s.' % (player.playername, raiseamt))

    def folded(self, player):
        player.active = False
        activeplayers.remove(player)
        self.pushMsg('%s folded.' % player.playername)


    def game_Blinds(self):
        for i in self.allplayers:
            i.holecards.append(self.deck.takeTopCard())
            i.holecards.append(self.deck.takeTopCard())
            string = 'Your holecards are: %s.', % i.holecards
            i.print(string)

            if i == self.smallblinder:
                i.bet = self.smallblind
                i.stack -= self.smallblind
                self.pot += self.smallblind
                self.allplayers.remove(i)
                self.allplayers.append(i)
                self.pushMsg('%s paid the small blind of %s.' % (i.username, self.smallblind))

            elif i == self.bigblinder:
                i.bet = self.bigblind
                i.stack -= self.bigblind
                self.pot += self.bigblind
                self.allplayers.remove(i)
                self.allplayers.append(i)
                self.maxbet = 20
                self.pushMsg('%s paid the big blind of %s.' % (i.username, self.bigblind))

        for i in self.allplayers:
            ''' turns all players into active players '''
            activeplayers.append(i)
            i.active = True

    def game_Preflop(self):
        self.street = 'preflop'
        self.playercntr = 0

        while self.roundOn():
            self.processSt()

        self.reInitialize()

    def game_Flop(self):
        self.beginSt('flop')

        while self.roundOn():
            self.processSt()

        self.reInitialize()

    def game_Turn(self):
        self.beginSt('turn')

        while self.roundOn():
            self.processSt()

        self.reInitialize()

    def game_River(self):
        self.beginSt('river')

        while self.roundOn():
            self.processSt()

        if self.iswinner == False:
            winners = self.calcWinners()
            self.win(winners)

class HandEvaluator:
    ''' returns value that represents strength of hand '''
    def __init__(self, hand):
        #self.allcards = holecards + communitycards
        self.allcards = hand
        #self.besthand = []
        self.values = []
        self.valueCount = self.getValueCount()
        self.suits = []
        self.suitCount = self.getSuitCount()

        self.isStraight = self.checkStraight()
        self.isFlush = self.checkFlush()

    def getValueCount(self):
        ''' returns number of different values of hand '''
        for i in self.allcards:
            if len(i) != 3:
                values.append(i[0])
            else:
                values.append(i[0:2])
        list(set(self.values))
        return len(self.values)

    def getSuitCount(self):
        ''' returns number of different suits of hand '''
        for i in self.allcards:
            if len(i) != 3:
                suits.append(i[1])
            else:
                suits.append(i[2])
        list(set(self.suits))
        return len(self.suits)

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
                return True
            elif realvalues == (range(realvalues[0], realvalues[0]+4) + [14]):
                return True
            return False
        return False

    def checkFlush(self):
        if self.suitCount == 1:
            return True
        return False


    def checkRoyalFlush(self):
        if self.isFlush and self.isStraight:
            royal = ['A', 'K', 'Q', 'J', '10']
            for i in royal:
                if i not in self.allcards:
                    return False
            return True
        return False

    def checkStraightFlush(self):
        if self.isFlush and self.isStraight:
            return True
        return False

    def checkFourKind(self):
        if len(self.values) == 2:
            if self.allcards.count(self.values[0]) == 4:
                return True
            elif self.allcards.count(self.values[1]) == 4:
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
            if self.allcards.count(self.values[0]) == 3:
                return True
            elif self.allcards.count(self.values[1]) == 3:
                return True
            elif self.allcards.count(self.values[2]) == 3:
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


    def evaluate(self):
        if self.checkRoyalFlush():
            return 1
        elif self.checkStraightFlush():
            return 2
        elif self.checkFourKind():
            return 3
        elif self.checkFullHouse():
            return 4
        elif self.isFlush:
            return 5
        elif self.isStraigt:
            return 6
        elif self.checkThreeKind():
            return 7
        elif self.checkTwoPair():
            return 8
        elif self.checkPair():
            return 9
        else:   #high card
            return 10


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
        text = s.recv(512)
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

        data = s.recv(512)
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
        reply = s.recv(512)
        print reply
        size = ''
        i = 1
        while reply[i] != '@':
            size += reply[i]
            i += 1
        intsize = int(size)
        if intsize > 512:
            s.send(msg)
            reply = s.recv(intsize+1)
        nindex = reply.find(msg) + len(msg) + 1
        if reply[7] == '0':
            return []
        while reply[nindex] != '@':
            nindex += 1
        thelist = self.makeList(reply[nindex:])
        return thelist

    # turns string seperated by @ signs and adds to list
    def makeList(self, string):
        if string == '':
            return []
        else:
            string = string[1:]
            theuser = ''
            i = 0
            while i < len(string) and string[i] != '@':
                theuser += string[i]
                i += 1
            return [theuser.strip()] + self.makeList(string[i:])

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
        reply = s.recv(512)
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
        reply = s.recv(512)
        if '@ok' in reply:
            return True
        return False

    # returns name of user
    def getName(self):
        return self.thename

    # shows messages received as a list
    def getMail(self, s):
        s.send('@rxmsg')
        reply = s.recv(512)
        size = ''
        i = 1
        while reply[i] != '@':
            size += reply[i]
            i += 1
        intsize = int(size)

        mindex = reply.find('@msg')
        if '@file' in reply:
            findex = reply.find('@file')
        else:
            findex = len(reply)
        listmsg = self.makeListmsg(reply[mindex:findex])
        return listmsg

    # puts users and their messages into a tuple, into a list
    def makeListmsg(self, string):
        if string == '':
            return []
        else:
            string = string[5:]
            theuser = ''
            i = 0
            while i < len(string) and string[i] != '@':
                theuser += string[i]
                i += 1
            themsg = ''
            i += 1
            while i < len(string) and string[i] != '@':
                themsg += string[i]
                i += 1
            if theuser != '' and themsg != '':
                return [(theuser, themsg)] + self.makeListmsg(string[i:])
            return []


# makes user an object of chat program
user = ChatProgram()



lets = Start(xxxloggedin)

