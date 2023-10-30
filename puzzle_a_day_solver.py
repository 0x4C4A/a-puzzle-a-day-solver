import copy # For easy deepcopying of 2D shape arrays
import sys
import time

# If you want to prohibit flipping shapes over, set this to False.
# This was added simply because I was curious whether it was possible to solve all dates without flipping. Turned out it is not.
ALLOW_FLIPPING_SHAPES = True

# A single piece that goes into the puzzle frame
class Shape:
    def __init__(self, name, color, shapedata):
        self._name = name
        self._color = color
        self._shapedata = copy.deepcopy(shapedata)
        self.findUniqueConfigs()

    def name(self):
        return self._name

    def color(self):
        return self._color

    def printShapeData(self, shapeData):
        for row in shapeData:
            string = ''
            for cell in row:
                if cell:
                    string += 'X'
                else:
                    string += ' '
            print(string)

    def print(self, rotation=0, flip=False):
        self.printShapeData(self.getShapedata(rotation, flip))

    def printUniqueShapes(self):
        for config in self._uniqueShapes:
            self.print(rotation=config['rotation'], flip=config['flip'])

    def getShapedata(self, rotation=0, flip=False):
        temp = copy.deepcopy(self._shapedata)

        if flip:
            temp = [row[::-1] for row in temp]

        while rotation:
            temp = list(zip(*temp[::-1]))
            rotation -= 1

        return temp

    def isShapeDataEqual(self, shapeA, shapeB):
        if len(shapeA) != len(shapeB) or len(shapeA[0]) != len(shapeB[0]):
            return False

        for y in range(0, len(shapeA)):
            for x in range(0, len(shapeA[0])):
                if shapeA[y][x] != shapeB[y][x]:
                    return False

        return True

    def findUniqueConfigs(self):
        configs = []

        if ALLOW_FLIPPING_SHAPES:
            configs = [{'unique': True, 'rotation': i, 'flip': j}
                    for i in range(0, 4) for j in [False, True]]
        else:
            configs = [{'unique': True, 'rotation': i, 'flip': j}
                    for i in range(0, 4) for j in [False]]

        shapes = []
        for id, config1 in enumerate(configs):
            shapes.append(self.getShapedata(
                rotation=config1['rotation'],
                flip=config1['flip']))

            for j in range(id, len(configs)):
                config2 = configs[j]
                if not config2['unique']:
                    continue

                if config1['rotation'] == config2['rotation'] and config1['flip'] == config2['flip']:
                    continue

                shape2 = self.getShapedata(
                    rotation=config2['rotation'], flip=config2['flip'])

                if self.isShapeDataEqual(shapes[id], shape2):
                    config2['unique'] = False

        self._uniqueShapes = [
            shapes[id] for id, config in enumerate(configs) if config['unique'] == True]
        self._uniqueConfigs = [
            config for config in configs if config['unique'] == True]


    def getUniqueShapes(self):
        return self._uniqueShapes

# The frame/field the pieces are set into.
class Field:
    def __init__(self, fieldArr):
        self._fieldArr = copy.deepcopy(fieldArr)
        self.clear()

    def emptyFieldArrShapeArray(self):
        shapeArray = []

        for idy, row in enumerate(self._fieldArr):
            shapeArray.append([])
            for idx, cell in enumerate(row):
                if cell:
                    shapeArray[idy].append(0)
                else:
                    shapeArray[idy].append(None)

        return shapeArray

    def clear(self):
        self._placedShapesAggregate = self.emptyFieldArrShapeArray()
        self._placedShapes = []

    def print_field(self):
        print()
        for idy, row in enumerate(self._fieldArr):
            string = ''
            stringOccupied = ''
            for idx, cell in enumerate(row):
                string = f'{string} {cell:>5}'
                value = self._placedShapesAggregate[idy][idx]
                if type(value) == dict:
                    stringOccupied = f'{stringOccupied} \x1b[0;30;{value["color"]}m[-{value["name"][0]}-]\x1b[0m'
                elif value:
                    stringOccupied = f'{stringOccupied} [-{value}-]'
                else:
                    stringOccupied = f'{stringOccupied}      '

            print(string)
            print(stringOccupied)
        print()

    def blockDate(self, month, date):
        foundMonth = False
        foundDate = False

        for idy, row in enumerate(self._fieldArr):
            for idx, cell in enumerate(row):
                if cell == month:
                    self._placedShapesAggregate[idy][idx] = 'M'
                    foundMonth = True

                if cell == date:
                    self._placedShapesAggregate[idy][idx] = 'D'
                    foundDate = True

                if foundDate and foundMonth:
                    return None
                elif foundDate or foundMonth:
                    continue



        raise Exception(f"Failed to find month ({not foundMonth}; {month}) or date ({not foundDate}; {date})!")

    def coordsWithinBounds(self, x, y):
        if y >= len(self._placedShapesAggregate):
            return False

        if x >= len(self._placedShapesAggregate[y]):
            return False

        return True

    def spaceIsEmpty(self, x, y):
        if self.coordsWithinBounds(x, y):
            return self._placedShapesAggregate[y][x] == 0

        return False

    def spaceIsUnavailable(self, x, y):
        if self.coordsWithinBounds(x, y):
            return self._placedShapesAggregate[y][x] != 0

        return True

    def isFilled(self):
        for row in self._placedShapesAggregate:
            for cell in row:
                if cell == 0:
                    return False
        return True

    def testIfShapeFits(self, shapeData, x, y):
        for idy, row in enumerate(shapeData):
            for idx, cell in enumerate(row):
                if cell and self.spaceIsUnavailable(idx+x, idy+y):
                    return False

        return True

    def placeShape(self, shapeData, name, color, x, y):
        if not self.testIfShapeFits(shapeData, x, y):
            return False

        for idy, row in enumerate(shapeData):
            for idx, cell in enumerate(row):
                if shapeData[idy][idx]:
                    self._placedShapesAggregate[idy+y][idx+x] = {"name": name, "color": color}


        self._placedShapes.append({'shape': shapeData, 'x': x, 'y': y})

        return True

    def removeLastShape(self):
        shape = self._placedShapes[-1]

        for idy, row in enumerate(shape["shape"]):
            for idx, coell in enumerate(row):
                if shape["shape"][idy][idx]:
                    self._placedShapesAggregate[idy + shape["y"]][idx + shape["x"]] = 0

        del self._placedShapes[-1]

    def checkContiguousSpaceSize(self, x, y, testedPlaces):
        if y < 0 or len(testedPlaces) <= y or \
           x < 0 or len(testedPlaces[y]) <= x or \
           testedPlaces[y][x] != 0:
           return 0

        testedPlaces[y][x] = 1

        if not self.spaceIsEmpty(x, y):
            return 0

        emptySpaces = 1
        emptySpaces = emptySpaces + self.checkContiguousSpaceSize(x + 1, y, testedPlaces)
        emptySpaces = emptySpaces + self.checkContiguousSpaceSize(x, y + 1, testedPlaces)
        emptySpaces = emptySpaces + self.checkContiguousSpaceSize(x - 1, y, testedPlaces)
        emptySpaces = emptySpaces + self.checkContiguousSpaceSize(x, y - 1, testedPlaces)

        return emptySpaces

    def checkContiguousSpacesAllOver5(self):
        testedPlaces = self.emptyFieldArrShapeArray()

        for idy, row in enumerate(testedPlaces):
            for idx, cell in enumerate(row):
                emptySpaceSize = self.checkContiguousSpaceSize(idx, idy, testedPlaces)
                if emptySpaceSize > 0 and emptySpaceSize < 5:
                    return False

        return True

# Original a-puzzle-a-day shapes
shapes = [
    Shape('7', 41, [
        [1, 1],
        [0, 1],
        [0, 1],
        [0, 1]
    ]),
    Shape('L', 42, [
        [1, 0, 0],
        [1, 0, 0],
        [1, 1, 1]
    ]),
    Shape('Rectangle', 43, [
        [1, 1, 1],
        [1, 1, 1]
    ]),
    Shape('Z', 44, [
        [1, 1, 0],
        [0, 1, 0],
        [0, 1, 1]
    ]),
    Shape('1', 45, [
        [1, 0],
        [1, 1],
        [1, 0],
        [1, 0]
    ]),
    Shape('U', 46, [
        [1, 0, 1],
        [1, 1, 1]
    ]),
    Shape('Snake', 47, [
        [0, 0, 1, 1],
        [1, 1, 1, 0]
    ]),
    Shape('Pip', "43;1", [
        [1, 1, 1],
        [0, 1, 1]
    ])
]

# Original a-puzzle-a-day frame
field = Field([
    ['jan', 'feb', 'mar', 'apr', 'may', 'jun'],
    ['jul', 'aug', 'sep', 'oct', 'nov', 'dec'],
    [1, 2, 3, 4, 5, 6, 7],
    [8, 9, 10, 11, 12, 13, 14],
    [15, 16, 17, 18, 19, 20, 21],
    [22, 23, 24, 25, 26, 27, 28],
    [29, 30, 31]
])

def print_shapes():
    for shape in shapes:
        print(f'### {shape.name()} ###')
        shape.printUniqueShapes()


def recursiveAlgo(shape_index = 0, ):
    global solutions
    global mode
    if(shape_index == len(shapes)):
        solutions += 1
        print(f'Solution #{solutions}')
        field.print_field()

        if mode == 'findOne':
            return True

        return False

    shape = shapes[shape_index]
    shapePlaced = False
    uniqueShapes = shape.getUniqueShapes()

    for x in range(0, 7):
        for y in range(0, 7):
            # print(shape_index, x, y)
            for unqiueShape in uniqueShapes:
                if field.placeShape(unqiueShape, shape.name(), shape.color(), x, y):
                    if field.checkContiguousSpacesAllOver5() and recursiveAlgo(shape_index + 1):
                        return True
                    else:
                        field.removeLastShape()

    return False

solutions = 0 # Used as a global
error = False
months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
month = 'jan'
date = 1
mode = 'findOne' # Used as a global

# Parse arguments
if len(sys.argv) >= 2:
    month = sys.argv[1]

if len(sys.argv) >= 3:
    try:
        date = int(sys.argv[2]) or 1
    except:
        print("Issue parsing date, is it a valid integer?")
        error = True

if len(sys.argv) >= 4:
    mode = sys.argv[3]

# Check argument validity
if date < 1 or date > 31:
    print(f"Date must be between 1 and 31!")
    error = True
if month not in months:
    print(f"Month must be one of {months}")
    error = True
if mode not in ['findOne', 'findAll']:
    print(f"Mode shall be either findOne or findAll!")
    error = True

if error:
    sys.exit(1)

# Block off the provided date in the frame
field.blockDate(month, date)

# Run the main task
print(f"Trying to solve puzzle-a-day for {month} {date}!")
start = time.time()
if recursiveAlgo() or solutions > 0:
    print(f"Finished, success! Found {solutions} solutions!")
else:
    print("Failed!")

print(f"Time elapsed: {time.time() - start:.1f} seconds.")





