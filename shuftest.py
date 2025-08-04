import random
import math
from math import factorial as fac
def shuffle (toShuffle, seed = None):
    retArr = []
    if seed != None:
        for i in range(1,5):
            fact = fac(3)
            if seed > fact:
                seed -= fact
            else:
                randArr = []
                for j in reversed(range(1, 3 + 1)):
                    randArr.append(seed%j)
                print("BREAKIN", randArr)
                break
    else:
        for i in range(len(toShuffle)):
            rand = random.randint(0, len(toShuffle)-1)
            retArr.append(toShuffle[rand])
            toShuffle.pop(rand)
    return retArr
for i in range(6):
    shuffle([4], i)
print(chr(0x10FFFF))
print(int(0x10FFFF))
unilimit = 0x110000
num = 8986605357327344374084478819576892590482507081502040129120393
print(bin(num))
depth = math.log(num)/math.log(0x110000)
depth = math.ceil(depth)
print(num)
finalArr = []
for i in reversed(range(depth)):
    finalArr.append(num // (0x110000**i))
    num %= 0x110000**i
print(finalArr)
print(int(0xd800))

recon = 0
for i in range(depth):
    recon += finalArr[depth - i - 1]*0x110000**i
print(recon)
retStr = ""
for i in range(len(finalArr)):
    finalArr[i] = chr(finalArr[i])
print(finalArr)
file = open("./16.bin", "wb")
str = ""
for i in finalArr:
    str += i
print(str)