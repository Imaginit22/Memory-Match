import pygame
from pygameRogers import Room, Game, GameObject, TextRectangle
import random
import math
from math import factorial as fac
#reused stuff

#placeholder to trick game into moving forward without real room initialized
class EmptyRoom(Room):
    def __init__(self, background):
        Room.__init__(self, "", background)
#TextRectangle that changes room when clicked
class TextPortal(TextRectangle):
    def __init__(self, destination, text, xPos, yPos, font, textColor, xCentered=False, yCentered=False, buttonWidth=None, buttonHeight=None, buttonColor=None):
        TextRectangle.__init__(self, text, xPos, yPos, font, textColor, xCentered, yCentered, buttonWidth, buttonHeight, buttonColor)
        self.destination = destination
    def click(self):
        if self.destination != "exit":
            self.getRoom().getGame().goToRoom(self.destination)
        else:
            0/0
#text portal with a setter method for difficulty
class DifficultyTextPortal(TextPortal):
    def __init__(self, difficulty, destination, text, xPos, yPos, font, textColor, xCentered=False, yCentered=False, buttonWidth=None, buttonHeight=None, buttonColor=None):
        TextPortal.__init__(self, destination, text, xPos, yPos, font, textColor, xCentered, yCentered, buttonWidth, buttonHeight, buttonColor)
        self.difficulty = difficulty
    def click(self):
        TextPortal.click(self)
        self.getRoom().getGame().difficulty = self.difficulty
#portal that either goes to a game having set a seed or goes to the instructions page given a bad seed
class Importal(TextPortal):
    def __init__(self, fileLoc, goodest, badest, text, xPos, yPos, font, textColor, xCentered=False, yCentered=False, buttonWidth=None, buttonHeight=None, buttonColor=None):
        TextPortal.__init__(self, badest, text, xPos, yPos, font, textColor, xCentered, yCentered, buttonWidth, buttonHeight, buttonColor)
        self.fileLoc = fileLoc
        self.goodest = goodest
    def click(self):
        line = None
        try:
            #read import.txt for seed
            file = open(self.fileLoc, "r")
            line = int(file.readline().rstrip('\n'))
            file.close()
            #if seed within bounds continue on
            if line < fac(12)+fac(24)+fac(36)+fac(48) and line >= 0:
                self.getRoom().getGame().seed = line
                #point to game instead of instructions manual
                self.destination = self.goodest
            else:
                0/0

        except Exception as e:
            pass
        #replace with seed logic
        TextPortal.click(self)
#exports seed, as import
class Exportal(TextPortal):
    def __init__(self, fileLoc, destination, text, xPos, yPos, font, textColor, xCentered=False, yCentered=False, buttonWidth=None, buttonHeight=None, buttonColor=None):
        TextPortal.__init__(self, destination, text, xPos, yPos, font, textColor, xCentered, yCentered, buttonWidth, buttonHeight, buttonColor)
        self.fileLoc = fileLoc
    def click(self):
        TextPortal.click(self)
        file = open(self.fileLoc, 'w')
        #writes seed to file for dissemination
        file.write(str(self.getRoom().getGame().seed))
#Card object with some extra addons for centering etc
class Card(GameObject):
    def __init__(self, picture = None, xPos = 0, yPos = 0, centeredHoriz = False, centeredVert = False):
        if picture == None:
            pic = [None, None, None]
        else:
            pic = card(picture)
        GameObject.__init__(self, pic[0])
        if centeredHoriz:
            self.rect.centerx = xPos
        else:
            self.rect.x = xPos
        if centeredVert:
            self.rect.centery = yPos
        else:
            self.rect.y = yPos
    def click(self):
        pass
#this allows gameobjects to be changed using reinitialization without angering arrays
class Holder(GameObject):
    def __init__(self, object = None, xPos = None, yPos = None):
        GameObject.__init__(self)
        #this is a bit cleaner in my opinion since and not looks weird
        if not object and xPos and yPos:
            self.setObject(Card(None, xPos, yPos))
        else:
            self.setObject(object)
    #update child
    def update(self):
        self.object.update()
    #click child
    def click(self):
        self.object.click()
    #setter method that extracts image data for display
    def setObject(self, object = None):
        if object == None:
            self.object = Card()
            object = self.object
        else:
            self.object = object
        self.image = object.image
        self.rect = object.rect
        self.mask = pygame.mask.from_surface(object.image)


#holder updated for this specific game. It has extra logic for going faceup and facedown,
#and drives the room through clicks.
class MemoryHolder(Holder):
    def __init__(self, value, xPos=None, yPos=None,centeredHoriz=False, centeredVert=False):
        super().__init__(Card("1B", xPos, yPos, centeredHoriz, centeredVert))
        self.centeredHoriz = centeredHoriz
        self.centeredVert = centeredVert
        self.value = value
        self.flipped = False
        self.taken = False
    #This turns a card faceup
    def faceUp(self):
        temp = self.object.rect.center
        self.setObject(Card(self.value, temp[0], temp[1], self.centeredHoriz, self.centeredVert))
        self.flipped = True
    #This turns a card facedown
    def faceDown(self):
        temp = self.object.rect.center
        self.setObject(Card("1B", temp[0], temp[1], self.centeredHoriz, self.centeredVert))
        self.flipped = False
    def click(self):
        #pokes room to check if all is well, if it is, goes faceup. room will take care of flipping back
        if(self.getRoom().checkFlipped()):
            self.faceUp()
                
            


        


#room that has game logic
class MemoryRoom(Room):
    def __init__(self, name, background, seed, seeded = None):
        #if no seed, randomly determine seed within allowed range.
        if seeded == None:
            fac1 = -1
            fac2 = 0
            facMagnitude = 0
            for i in range(int(seed/6)):
                fac1 += fac(((i+1)*6-6)*2)
                fac2 += fac((i+1)*6*2)
                facMagnitude += 1
            #I am of the probably misinformed opinion that 0! should not be 1. Regardless,
            #this needs to be done to allow for all boards.
            fac1 -= 1
            seed = random.randint(fac1, fac2)
        self.seed = seed
        Room.__init__(self, name, background)
        pairs = 6
        #determine magnitude
        fact = 0
        if seeded != None:
            for i in range(1,5):
                fact += fac((i)*12)
                if seed < fact:
                    facMagnitude = i
                    break
        pairs *= facMagnitude
        
        cards = None
        pairs *= 2
        #turn pairs into rectangle. Probably not ideal but it works, wrote in 2 mins
        self.side1 = math.sqrt(pairs)
        self.side1 = math.floor(self.side1)
        self.side2 = -1
        for i in range(pairs):
            self.side2 = pairs/self.side1
            if self.side2%1 == 0:
                break
            else:
                self.side1-=1
        self.side1 = int(self.side1)
        self.side2 = int(self.side2)
        self.cards = []
        cards = []
        for u in range(2):
            for i in range(int(pairs/2)):
                cards.append(i)
        cards = shuffle(cards, seed)
        #fill decks
        for i in range(len(cards)):
            pos = cards[i]
            value = pos // 4
            suit = pos % 4
            value += 2
            match (value):
                case 10:
                    value = "T"
                case 11:
                    value = "J"
                case 12:
                    value = "Q"
                case 13:
                    value = "K"
                case 14:
                    value = "A"
            match (suit):
                case 0:
                    suit = "S"
                case 1:
                    suit = "H"
                case 2:
                    suit = "C"
                case 3:
                    suit = "D"
            cards[i] = str(value) + suit
        self.known = [False]*self.side1*self.side2
        self.blunders = 0
        shrinkx = 0
        shrinky = 0
        #better to do this than multiplication every single repetition
        jcounter = 0
        for i in range(self.side2):
            self.cards.append([])
            for j in range(self.side1):
                temp = MemoryHolder(cards[jcounter], (i+.5)*((screenWidth - shrinkx)/self.side2) + shrinkx/2, (j+.5)*((screenHeight - shrinky)/self.side1) + shrinky/2, True, True)
                self.cards[i].append(temp)
                self.addObject(temp)
                jcounter+=1
    def moveOn(self):
        self.getGame().mistakes = self.blunders
        self.getGame().nextRoom()
    def checkFlipped(self):
        flipCount = 0
        ixs = []
        blunder = False
        for i, x in enumerate(self.cards):
            #found out about enumerate, very useful
            for j, y in enumerate(x):
                if y.flipped and not y.taken:
                        flipCount+=1
                        oneDex = j + (i*len(x))
                        ixs.append(oneDex)
        if (flipCount < 2):
            return True
        else:
            newInfo = 0
            for i in ixs:
                if self.known[i]:
                    print("KNOWNBLUNDER")
                    blunder = True
                else:
                    newInfo += 1
                    self.known[i] = True
            #if half known, with perfect memory and strategy you can
            #take an unknown one and match it to the corresponding
            #known one. If not, mistake made.
            cardsLeft = 0
            for i, x in enumerate(self.cards):
                for j, y in enumerate(x):
                    if not y.taken:
                        cardsLeft += 1
            knownTotal = 0
            for i, x in enumerate(self.known):
                if x and not self.cards[ixs[0]//self.side1][ixs[0]%self.side1].taken:
                    knownTotal += 1
            #check if should have done an unknown to known pivot
            if knownTotal - newInfo >= cardsLeft/2:
                print("SHOULDHAVEPIVOTED", self.known, newInfo, cardsLeft)
                blunder = True
            #check if card values are the same.
            if self.cards[ixs[0]//self.side1][ixs[0]%self.side1].value ==  self.cards[ixs[1]//self.side1][ixs[1]%self.side1].value:
                print("MATCHING")
                blunder = False
                self.cards[ixs[0]//self.side1][ixs[0]%self.side1].taken = True
                self.cards[ixs[1]//self.side1][ixs[1]%self.side1].taken = True
                self.cards[ixs[0]//self.side1][ixs[0]%self.side1].setObject(None)
                self.cards[ixs[1]//self.side1][ixs[1]%self.side1].setObject(None)
                remaining = False
                for i in self.cards:
                    for j in i:
                        if not j.taken:
                            remaining = True
                            break
                if not remaining:
                    self.moveOn()
            else:
                #flip cards facedown if not removed.
                self.cards[ixs[0]//self.side1][ixs[0]%self.side1].faceDown()
                self.cards[ixs[1]//self.side1][ixs[1]%self.side1].faceDown()
            if blunder:
                print("Youblundered")
                self.blunders+=1
            return False


#The following is my thinking, in realish time (with edits) for a seed
#system. Each difficulty has a certain number of random possibilities. 
#For example, 4 pairs has 8! permutations. However, duplicates of each exist,
#so it is actually 8!/4(2!). This can be described by 2P!/2P or (2P-1)!, where
#P is pairs. The first difficulty will take space from 0 to this function.
#The next will go from the function for previous +1 to it +1 +its own function.
#Easy: 4, goes from 0 to 5040.
#Medium: 8, goes from 5041 to 15! + 5040
#etc.
def shuffle (toShuffle, seed = None):
    retArr = []
    fact = 0
    #determine what the game size is
    for i in range(1,5):
        fact += fac((i)*12)
        if seed >= fact:
            seed -= fact
        else:
            #once size found, deconstruct into various modulos. Found this through google sheet experiments
            for j in reversed(range(1, (i)*12 + 1)):
                retArr.append(toShuffle[seed%j])
                toShuffle.pop(seed%j)
            break
    return retArr


#colors
BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#other things to initialize
scale = 1.5
screenWidth = 640 * scale
screenHeight = 480 * scale
g = Game(screenWidth,screenHeight)
bg = g.makeBackground(WHITE)
arialHead = g.makeFont("Arial",40)
arialSubhead = g.makeFont("Arial", 30)



#Took card logic from War.
#Names of suits in files in order SHCD
suitnames = [
    "SPADES",
    "HEARTS",
    "CLUBS",
    "DIAMONDS"
]
#Names of cards in files in order 2-10, J Q K A. Didn't include jokers as they weren't in the cards file

cardnames = [
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14"
]
#whether the suit comes first in the files
suitFirst = True
#leading for file navigation plus other leading
leading = "./cards/"#"./Culminating/cards/"
#delimiter if exists for files
delimiter = ""
#trailing if exists for files, plus extension
trailing = ".jpg"
#top/back card name
back = "TOP"
#normalized to a card format that I'm more used to (2S, TH, QC)
#not sure where we are with dictionaries but given previous instructions, not using
def card(name):
    if name == "1B":
        return g.makeSpriteImage(leading + back + trailing), 0, 5
    cIndex = name[0]
    match(cIndex):
        case "T":
            cIndex = 10
        case "J":
            cIndex = 11
        case "Q":
            cIndex = 12
        case "K":
            cIndex = 13
        case "A":
            cIndex = 14
        case _:
            cIndex = int(cIndex)
    sIndex = 0
    match(name[1]):
        case "H":
            sIndex = 1
        case "C": 
            sIndex = 2
        case "D":
            sIndex = 3
    retStr = ""
    sIndex = suitnames[sIndex]
    cIndex = cardnames[cIndex - 2]
    if suitFirst:
        retStr = leading + sIndex + delimiter + cIndex + trailing
    else:
        retStr = leading + cIndex + delimiter + sIndex + trailing
    return (g.makeSpriteImage(retStr), int(cIndex), sIndex)



    

#init different rooms only when logic from previous is completed, so rooms can more easily influence each other's behaviour. 
#also allows for easier replayability
buttonWidth = 150
#menu room with difficulties and import
def initR0():
    g.difficulty = None
    g.seed = None
    r = Room("Menu", bg)
    g.setRoomAtPosUninitOthers(r, 0, EmptyRoom(bg))
    title = TextRectangle("Play Memory", screenWidth/2, 0, arialHead, BLACK, True, False)
    easy = DifficultyTextPortal(6, 1, "Easy", screenWidth/5, screenHeight/2, arialHead, BLACK, True, True, buttonWidth, 100, RED)
    medium = DifficultyTextPortal(12, 1, "Medium", screenWidth*2/5, screenHeight/2, arialHead, BLACK, True, True, buttonWidth, 100, RED)
    hard = DifficultyTextPortal(18, 1, "Hard", screenWidth*3/5, screenHeight/2, arialHead, BLACK, True, True, buttonWidth, 100, RED)
    crazy = DifficultyTextPortal(24, 1, "Crazy", screenWidth*4/5, screenHeight/2, arialHead, BLACK, True, True, buttonWidth, 100, RED)
    impozz = Importal("import.txt", 1, 4, "Import Board", screenWidth/2, screenHeight/2 + 130, arialHead, BLACK, True, True, buttonWidth*2, 100, RED)
    Strategy = TextPortal(3, "Strategy", screenWidth/2, screenHeight - 150, arialHead, BLACK, True, False, buttonWidth, 100, RED)
    r.addObject(title)
    r.addObject(easy)
    r.addObject(medium)
    r.addObject(hard)
    r.addObject(crazy)
    r.addObject(impozz)
    r.addObject(Strategy)

#game room
def initR1(): 
    diff = g.difficulty
    seeded = None
    if g.seed != None:
        diff = g.seed
        seeded = True
    r = MemoryRoom("", bg, diff, seeded)
    g.setRoomAtPosUninitOthers(r, 1, EmptyRoom(bg))
    g.seed = r.seed

#end screen
def initR2():
    r = Room("Winner", bg)
    g.setRoomAtPosUninitOthers(r, 2, EmptyRoom(bg))
    finalScore = TextRectangle(f"You could have completed that in {g.mistakes} fewer moves.", 0, 0, arialHead, BLACK, False, False)
    r.addObject(finalScore)
    playAgain = TextPortal(0, "Play Again", 0, 100, arialHead, WHITE, False, False, screenWidth, 50, BLACK)
    r.addObject(playAgain)
    export = Exportal("export.txt", 2, "Export seed", 0, screenHeight/2, arialHead, WHITE, False, True, screenWidth, 50, BLACK)
    r.addObject(export)
    exit = TextPortal("exit", "Exit", 0, screenHeight - 100, arialHead, WHITE, False, False, screenWidth, 50, BLACK)
    r.addObject(exit)

#strategy explanation
def initR3():
    r = Room("Strategy", bg)
    g.setRoomAtPosUninitOthers(r, 3, EmptyRoom(bg))
    explanation = [
    "This game is played by picking two cards, removing",
    "matching picks, until no cards remain. The optimal",
    "strategy is to either reveal two new cards in a",
    "move, or take a known pair. This is unless half or",
    "more remaining cards are known, in which case ",
    "picking unknown and matching it to a known card",
    "is optimal."]
    for i, s in enumerate(explanation):
        explanatory = TextRectangle(s, 0, i*50, arialHead, BLACK)
        r.addObject(explanatory)
    ret = TextPortal(0, "Return", screenWidth/2, screenHeight - 150, arialHead, BLACK, True, False, buttonWidth, 100, RED)
    r.addObject(ret)

#import explanation
def initR4():
    r = Room("Import", bg)
    g.setRoomAtPosUninitOthers(r, 4, EmptyRoom(bg))
    explanation = [
    "To import a file, please navigate to this game's",
    "directory, and add a file called import.txt. There,",
    "add a seed, and try this button again."]
    for i, s in enumerate(explanation):
        explanatory = TextRectangle(s, 0, i*50, arialHead, BLACK)
        r.addObject(explanatory)
    ret = TextPortal(0, "Return", screenWidth/2, screenHeight - 150, arialHead, BLACK, True, False, buttonWidth, 100, RED)
    r.addObject(ret)
#populated with empty rooms
roomFuncList = [initR0, initR1, initR2, initR3, initR4]
for i in range(len(roomFuncList)):
    g.addRoom(EmptyRoom(bg))
initR0()
g.start()
lastRoom = 0

#game loop
while g.running:
    dt = g.clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            g.stop()
        if event.type == pygame.MOUSEBUTTONDOWN:
            g.currentRoom().handleClicks(True)
    if lastRoom != g.inRoom:
        roomFuncList[g.inRoom]()
    lastRoom = g.inRoom
    
    g.currentRoom().updateObjects()
    g.currentRoom().renderBackground(g)
    g.currentRoom().renderObjects(g)
    pygame.display.flip()
pygame.quit()