import random
from copy import deepcopy

numColors = 6
colors = ['F', 'G', 'W', 'L', 'D', 'H']

def getRandomBoard(seed=None):
  if seed != None:
    random.seed(seed)
  board = [[0]*6 for i in xrange(5)]
  for i in xrange(5):
    for j in xrange(6):
      board[i][j] = random.randint(0, 5)
  return board

def printBoard(board):
  for i in xrange(5):
    print ' '.join(colors[c] if c < numColors else '*' for c in board[i])


def findLinears(board):
  linears = [([], []) for c in xrange(numColors)]

  # find linear groups in the rows
  for i in xrange(5):
    row = board[i]
    color = None
    num = 0
    for j in xrange(6):
      if row[j] == color:
        num += 1
        continue
      if num >= 3:
        linears[color][0].append(((i, i+1), (j-num, j)))
      color = row[j]
      num = 1
    if num >= 3:
      linears[color][0].append(((i, i+1), (6-num, 6)))

  #find linear groups in the columns
  for j in xrange(6):
    color = None
    num = 0
    for i in xrange(5):
      if board[i][j] == color:
        num += 1
        continue
      if num >= 3:
        linears[color][1].append(((i-num, i), (j, j+1)))
      color = board[i][j]
      num = 1
    if num >= 3:
      linears[color][1].append(((5-num, 5), (j, j+1)))

  return linears

def isIntersecting(horLinear, verLinear):
  return horLinear[0][0] >= verLinear[0][0] and horLinear[0][1] <= verLinear[0][1] and \
      horLinear[1][0] <= verLinear[1][0] and horLinear[1][1] >= verLinear[1][1]

def isHorAdjacent(linear1, linear2):
  return linear1[0][1] == linear2[0][0] and \
      linear1[1][1] > linear2[1][0] and linear1[1][0] < linear2[1][1]

def isVerAdjacent(linear1, linear2):
  return linear1[1][1] == linear2[1][0]

def mergeGroups(groupMap, groups, linear1, linear2):
  newGroup = groups[groupMap[linear1]] | groups[groupMap[linear2]]
  for linear in newGroup:
    groupMap[linear] = len(groups)
  groups.append(newGroup)

def groupLinears(linears):
  # find pairs of linears that intersect or are adjacent
  grouped = [[] for c in xrange(numColors)]
  for index, colorLinears in enumerate(linears):
    horLinears = colorLinears[0]
    verLinears = colorLinears[1]
    groupMap = {}
    groups = []
    for h in horLinears:
      groupMap[h] = len(groups)
      groups.append(set([h]))
    for v in verLinears:
      groupMap[v] = len(groups)
      groups.append(set([v]))
    for h in horLinears:
      for v in verLinears:
        if isIntersecting(h,v):
          mergeGroups(groupMap, groups, h, v)
    for i in xrange(len(horLinears) - 1):
      if isHorAdjacent(horLinears[i], horLinears[i+1]):
        mergeGroups(groupMap, groups, horLinears[i], horLinears[i+1])
    for j in xrange(len(verLinears) - 1):
      if isVerAdjacent(verLinears[j], verLinears[j+1]):
        mergeGroups(groupMap, groups, verLinears[j], verLinears[j+1])
    finalGroupIndices = set(groupMap.values())
    for groupIndex in finalGroupIndices:
      grouped[index].append(groups[groupIndex])
  return grouped


def testGroupedLinears(board):
  linears = findLinears(board)
  grouped = groupLinears(linears)
  for index, colorGroups in enumerate(grouped):
    print '************* linears for color', colors[index]
    printBoard(board)
    print '***********************************'
    for linearGroup in colorGroups:
      boardCopy = deepcopy(board)
      for linear in linearGroup:
        for i in xrange(linear[0][0], linear[0][1]):
          for j in xrange(linear[1][0], linear[1][1]):
            boardCopy[i][j] = numColors
      printBoard(boardCopy)
    print '***********************************\n'


def testLinears(board):
  linears = findLinears(board)
  print linears
  for index, colorLinears in enumerate(linears):
    print '************* linears for color', colors[index]
    printBoard(board)
    print '***********************************'
    for linear in colorLinears[0] + colorLinears[1]:
      boardCopy = deepcopy(board)
      for i in xrange(linear[0][0], linear[0][1]):
        for j in xrange(linear[1][0], linear[1][1]):
          boardCopy[i][j] = numColors
      printBoard(boardCopy)
    print '***********************************\n'





def randomSearch(board, moves=40, iters=100):
  pass
