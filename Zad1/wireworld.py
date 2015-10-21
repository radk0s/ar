from mpi4py import MPI
import random
import copy
import json

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
neighbours = [0, 0, 0, 0]

N = 4       #size of aglomeration
iters = 4  #number of iterations
Matrix = []

STATES = ['EPTY', 'HEAD', 'TAIL', 'COND']

def printMatrix(matrix):
    for x in range(len(matrix)):
        print matrix[x]

def getTop():
    return copy.deepcopy(Matrix[len(Matrix)-1])

def getBottom():
    return copy.deepcopy(Matrix[0])

def getLeft():
    return comm.sendrecv([row[len(Matrix)-1] for row in Matrix],
                         dest=neighbours[LEFT],
                         source=neighbours[RIGHT])

def getRight():
    return comm.sendrecv([row[0] for row in Matrix],
                         dest=neighbours[RIGHT],
                         source=neighbours[LEFT])

def doStep():
    top = getTop()
    bottom = getBottom()
    left = getLeft()
    right = getRight()

    tmp = copy.deepcopy(Matrix)
    for row in range(len(tmp)):
        tmp[row].insert(0, left[row])
        tmp[row].append(right[row])

    bottom.insert(0, 'NONE')
    bottom.append('NONE')

    top.insert(0, 'NONE')
    top.append('NONE')

    tmp.insert(0, top)
    tmp.append(bottom)

    for x in xrange(1, len(tmp) -1):
        for y in xrange(1,len(tmp[x])-1):
            newState = changeState(tmp[x][y], [tmp[x][y-1], tmp[x][y+1], tmp[x+1][y], tmp[x-1][y]])
            Matrix[x-1][y-1] = newState


def changeState(cell, neightbours):
    if cell == 'EPTY':
        return 'EPTY'

    if cell == 'HEAD':
        return 'TAIL'

    if cell == 'TAIL':
        return 'COND'

    if cell == 'COND':
        heads = filter(lambda neightbour: neightbour == 'HEAD', neightbours)
        if len(heads) in [1,2]:
            return 'HEAD'
        return 'COND'

for x in range(0, N):
    Matrix.append([])
    for y in range(0, N):
        Matrix[x].append(random.choice(STATES))


comm = MPI.COMM_WORLD
rank = comm.rank
size = comm.size

grid_rows = 1
grid_column = size

if rank == 0:
    print "Building a %d x %d grid topology:" % (grid_rows, grid_column)

communicator = comm.Create_cart((grid_rows, grid_column), periods=(True, True), reorder=True)
current_row, current_col = communicator.Get_coords(communicator.rank)

neighbours[UP], neighbours[DOWN] = communicator.Shift(0, 1)
neighbours[LEFT], neighbours[RIGHT] = communicator.Shift(1, 1)

print "Process %d - UP: %d, DOWN: %d, LEFT: %d, RIGHT: %d" % \
      (rank, neighbours[UP], neighbours[DOWN], neighbours[LEFT], neighbours[RIGHT])

result = {
    'id': rank,
    'row': current_row,
    'col': current_col,
    'neighbours': {
        'up': neighbours[UP],
        'down': neighbours[DOWN],
        'left': neighbours[LEFT],
        'right': neighbours[RIGHT]
    },
    'steps': [copy.deepcopy(Matrix)]
}

for i in xrange(iters):
    doStep()
    result['steps'].append(copy.deepcopy(Matrix));

with open('result_'+str(rank)+'.json', 'w') as file:
    file.write(json.dumps(result))
