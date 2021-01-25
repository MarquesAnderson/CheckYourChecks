import re
import time
import cv2
import pytesseract as tess
import os

# Globals
tess.pytesseract.tesseract_cmd = r'...Tesseract-OCR\tesseract.exe'
toAssume = []
toDateAssume = []
toDolAssume = []
path = r'...\images\check_52.png'

date = [(590, 95), (840, 55)]
dollar = [(755, 110), (920, 155)]
text = [(45, 150), (720, 190)]
underexam = "date"

words = []
guesses = []
maker = ""
iterate = 0
examine = "ninety"
placetolook = []
error = ""
previousWordTries = 0
output = []
reevaluator = [False, 0]

# determine index potential classifications

index1 = [["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"], ["twenty", "thirty",
                                                                                            "forty", "fifty", "sixty",
                                                                                            "seventy", "eighty",
                                                                                            "ninety"]]
index2 = [["cents", "dollars", "hundred", "thousand", "million", "billion", "trillion"],
          ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]]
index3 = ["and", "only", "", "dc"]
index4 = [""]

# 2D array to assign letters to their potential numbers
assignment = [
                  [0, ["o", "e", "D", "O", "a", "c"]],
                  [1, ["I", "l", "H", "L", "i", "t"]],
                  [2, ["s", "z", "Q", ")"]],
                  [3, ["B", "E", "J", "W", "w"]],
                  [4, ["U", "A", "N", "k", "u", "v"]],
                  [5, ["S", "Y", "K", "h", "j"]],
                  [6, ["G", "R", "X", "b", "d", "r", "x"]],
                  [7, ["F", "T", "Z", "M", "V", "y"]],
                  [8, ["C", "(", "f", "m", "n"]],
                  [9, ["P", "g", "p", "q"]],
                  ["default", ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-", "/", ".", ","]]
                  ]

inputWord = ""
numRelease = ""

def crop(img, ref_point):
    # order the x and ys in ascending order and put them into a new tuple

    if ref_point[0][1] > ref_point[1][1]:
        tempX1 = ref_point[1][1]
        tempX2 = ref_point[0][1]
    else:
        tempX1 = ref_point[0][1]
        tempX2 = ref_point[1][1]
    if ref_point[0][0] > ref_point[1][0]:
        tempY1 = ref_point[1][0]
        tempY2 = ref_point[0][0]
    else:
        tempY1 = ref_point[0][0]
        tempY2 = ref_point[1][0]

    newTuple = [(tempY1, tempX1), (tempY2, tempX2)]
    cropped = img[newTuple[0][1]:newTuple[1][1], newTuple[0][0]:newTuple[1][0]]
    return cropped


# Recognize the words of the cropped image

def recognition(cropped):
    (H, W) = cropped.shape[:2]
    # define the two output layer names for the EAST detector model that
    # we are interested -- the first is the output probabilities and the
    # second can be used to derive the bounding box coordinates of text
    layerNames = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"]

    # load the pre-trained EAST text detector
    net = cv2.dnn.readNet('frozen_east_text_detection.pb')

    # construct a blob from the image and then perform a forward pass of
    # the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(cropped, 1.0, (W, H),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    start = time.time()
    net.setInput(blob)
    # (scores, geometry) = net.forward(layerNames)
    end = time.time()

    # print more info
    hopeful = tess.image_to_string(cropped)

    # hopeful is for text
    if underexam == "text":
        res = []
        for sub in hopeful:
            x = re.sub('\n', '', sub)
            x.casefold()
            res.append(x)
        toAssume.clear()
        toAssume.append(res)
    elif underexam == "date":
        toDateAssume.clear()
        toDateAssume.append(hopeful)
    elif underexam == "dollar":
        toDolAssume.clear()
        toDolAssume.append(hopeful)


# This code portion is for making a rough draft of the corrections for the Check HTR

# algorithm for seeing how many characters two words share
def compare(see, guess):
    # turn string into a set
    singles = {""}
    for char in see:
        singles.add(char)

    lettersShared = 0
    for letter in guess:
        if letter in singles:
            lettersShared += 1
    percent = lettersShared/max(len(guess), 1)
    # if guess == examine:
    # print(guess + ": compare = " + str(percent))
    return percent


# algorithm for comparing the length of the two words
def checklength(see, guess):
    diff = abs((len(see)) - len(guess))/len(see)
    # if guess == examine:
    # print(guess + ": checklength = " + str(diff))
    return diff


# algorithm for checking if out guess contains segments of what we see
def segmentcheck(see, guess):
    segmentsize = max(round(len(see)/2), 2)
    segmentscontained = 0
    segmentstart = 0
    segmentend = segmentsize - 1

    while segmentend < len(see):
        #print(see[segmentstart:segmentend + 1])
        if see[segmentstart:segmentend+1] in guess:
            segmentscontained += 1
        segmentstart += 1
        segmentend += 1
    # if guess == examine:
    #print(guess + ": segmentscontained = " + str(segmentscontained))
    return segmentscontained


# algorithm for choosing which set of words to assume from
#            guesses,  guesses[len(guesses)-1]
def picklist(fulllist, spot, tries, errorRelist):
    # global var
    global placetolook, error

    # first word?
    if len(fulllist) == 0 and tries < 2:
        # print("Guesses leg = " + str(len(fulllist)))
        placetolook = index1[tries]

    # PW was "cents" or dc error
    elif fulllist[spot] == "cents" or fulllist[spot] == "dc":
        placetolook = index4
        error = "Force it down"

    # PW was one-ten?
    elif fulllist[spot] in index1[0] and tries < 2:
        placetolook = index2[0]

    # PW was twenty-ninety?
    elif fulllist[spot] in index1[1] and tries == 0:
        # check one-nine
        placetolook = index2[1]

    elif fulllist[spot] in index1[1] and tries == 1:
        # check hun - trill
        placetolook = index2[0]

    # PW was hundred?
    elif fulllist[spot] == "hundred" and tries == 0:
        # check "and"
        placetolook = index3

    elif fulllist[spot] == "hundred" and tries == 1:
        # check one - nine
        placetolook = index2[1]

    elif fulllist[spot] == "hundred" and tries == 2:
        placetolook = index1[1]

    # PW was thou, mill, bill, etc.?
    elif fulllist[spot] in index2[0] and tries == 0:
        placetolook = index1[0]

    elif fulllist[spot] in index2[0] and tries == 1:
        placetolook = index1[1]

    elif fulllist[spot] in index2[0] and tries == 2:
        placetolook = index3

    # PW was "and"?
    elif fulllist[spot] in index3 and tries < 10:
        placetolook = index1[tries]

    elif tries >= 5:
        placetolook = index4
        error = "Force it down"

    # We were not able to find a word to match, reevaluate previous word
    elif error == "No new list was selected" and tries < 10 and not reevaluator[0]:
        error = ""
        guesses.pop(len(guesses) - 1)
       # print("I am reevaluating the previous word given this word has no match")
        reevaluator[0] = True
        assume(errorRelist, previousWordTries)

    else:
        error = "No new list was selected"
       # print("Error: No new list was selected")
   # print("placetolook = ")
   # print(placetolook)


# give a score to determine which answer it might be
def assume(listofwords, retries):
    global previousWordTries, error, placetolook

    for eachword in listofwords:
        # Only check the word if its index is higher than len(guesses)
       # print("Guesses: " + str(len(guesses)) + ", List: " + str(len(listofwords)))
        if listofwords.index(eachword) >= len(guesses) and len(eachword) > 0 and retries + previousWordTries < 5:
           # print(eachword + ", retries = " + str(retries) + ", previousTries = " + str(previousWordTries))
            scores = []
            test = eachword
            indexPickerScore = 0
            indexPicker = 0

            # is it in broken index3?
            if eachword in index3 and eachword != "and" and eachword != "only":
                continue

            picklist(guesses, len(guesses) - 1, retries, listofwords)

            if len(guesses) == len(listofwords) or error == "Force it down":
                break

            # if the exact word is in the array we are checking, recognize that
            if test in placetolook:
                if placetolook == index4:
                    continue
                guesses.append(test)
                retries = 0
                placetolook = index1
                reevaluator[0] = False
               # print("(Auto) Guesses so far: ")
               # print(guesses)
                continue

            # force the addition of a blank string if too many tries to avoid errors or recursion
            elif error == "Force it down" or placetolook == index4:
                guesses.append("")
                retries = 0
                placetolook = index1
                continue

            # Produce scores for each potential guess
            for pot in placetolook:
                score = (-checklength(test, pot)) + compare(test, pot) + segmentcheck(test, pot)
                scores.append(score)

           # print(scores)

            # find the word whose index matches that of the highest score; that is my guess
            for val in scores:
                if val > indexPickerScore:
                    indexPicker = scores.index(val)
                    indexPickerScore = val

            # if our score is not high enough, check the next set of words
            if indexPickerScore < 0.33 and retries < 5:
                retries += 1
                assume(listofwords, retries)
                break

            # Confirm our high scoring guess
            corre = placetolook[indexPicker]
            if corre != "and" and corre in index4:
                continue
            guesses.append(corre)
            previousWordTries = retries + 1
            retries = 0
            placetolook = index1
            reevaluator[0] = False
           # print("Guesses so far: ")
           # print(guesses)


# algorithm for turning alphanumeric sequences into most likely numbers
def assumeNum(innie):
    global numRelease
    numRelease = ""
    for let in innie:
        for brax in assignment:
            if let in brax[1] and brax[0] != "default":
                numRelease = numRelease + str(brax[0])
            elif let in brax[1] and brax[0] == "default":
                for subbrax in brax[1]:
                    numRelease = numRelease + let
                    break


# the super function
def superfunciton():

    global underexam, inputWord, iterate, maker

    # load the image
    checkName = path[72:]
    reg = cv2.imread(path)
    reg = cv2.resize(reg, (960, 320))
    image = cv2.cvtColor(reg, cv2.COLOR_BGR2GRAY)
    # testing to see if improves reading
    image = cv2.fastNlMeansDenoising(image, None, 20, 20, 15)
    # cv2.namedWindow("image")

    underexam = "date"
    part = crop(image, date)
    recognition(part)
    underexam = "dollar"
    part = crop(image, dollar)
    recognition(part)
    underexam = "text"
    part = crop(image, text)
    recognition(part)

    inputWord = toAssume[0]
    sentence = inputWord

    # separate long string into single words
    for letter in sentence:
        if letter == '' or letter == ' ' or letter == '-':
            maker = maker.casefold()
            words.append(maker)
            maker = ""
        elif iterate == len(sentence) - 1:
            maker = maker + sentence[iterate]
            maker.rstrip()
            maker = maker.casefold()
            words.append(maker)
            maker = ""
        else:
            maker = maker.casefold()
            maker = maker + sentence[iterate]
        iterate = iterate + 1
    for eachword in sentence:
        eachword.casefold()
    print("Starting words: ")
    print(words)

    assumeNum(toDateAssume[0])
    tempDol = numRelease
   # numRelease = ""
    print("TempDol is:")
    print(tempDol)

    assumeNum(toDolAssume[0])
    print("numRelease is:")
    print(numRelease)

    for w in words:
        w.casefold()

    assume(words, 0)
    print("final guesses are:")
    print(guesses)

    tofill = open("recognition.csv", "a")
    tofill.write("\n")

    # check name
    tofill.write(checkName)
    tofill.write(",")

    # check date
    tofill.write(tempDol)
    tofill.write(",")

    # check amount in text
    for to in guesses:
        tofill.write(to + " ")
    tofill.write(",")

    # check dollar amount
    tofill.write("\"" + numRelease + "\"")
    # tofill.write(",")

    tofill.close()
    tempDol = ''


# run the super function for every picture
for f in os.listdir("images"):
    if f.endswith('.jpg') or f.endswith('.png'):
        path = "C:\\" + "...images\\" + f
        print(path)
        superfunciton()

        # reset the variables
        words.clear()
        guesses.clear()
        toDateAssume.clear()
        toDolAssume.clear()
        toAssume.clear()
        underexam = ""
        maker = ""
        iterate = 0
        placetolook.clear()
        error = ""
        previousWordTries = 0
        numRelease = ""
        index1 = [["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"], ["twenty", "thirty",
                                                                                                    "forty", "fifty",
                                                                                                    "sixty",
                                                                                                    "seventy", "eighty",
                                                                                                    "ninety"]]
