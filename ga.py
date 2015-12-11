import random
from copy import deepcopy
from board import *
import numpy
from multiprocessing import Process, Array
import operator

deltas = {'U': (-1, 0), 'R': (0, 1), 'D': (1, 0), 'L': (0, -1), 'P': (0, 0)}
moveDist = ['U', 'R', 'D', 'L'] + ['P'] * 2

allowedMoves = {}
for row in xrange(numRows):
  for col in xrange(numCols):
    allowedMoves[(row, col)] = ['U', 'R', 'D', 'L']
    if row == 0: 
      allowedMoves[(row, col)].remove('U')
    if row == numRows - 1: 
      allowedMoves[(row, col)].remove('D')
    if col == 0: 
      allowedMoves[(row, col)].remove('L')
    if col == numCols - 1: 
      allowedMoves[(row, col)].remove('R')

def initPopulation(size, avgLength):
  population = []
  for _ in xrange(size):
    row = random.randint(0, numRows - 1)
    col = random.randint(0, numCols - 1)
    path = []
    for j in xrange(avgLength):
      m = random.choice(allowedMoves[(row, col)])
      path.append(((row, col), m))
      row += deltas[m][0]
      col += deltas[m][1]
    population.append(path)
  return population

def isLegalPath(path, startRow, startCol):
  row = startRow
  col = startCol
  for m in path:
    row += deltas[m][0]
    col += deltas[m][1]
    if row < 0 or col < 0 or row >= numRows or col >= numCols:
      return False
  return True

def legalStats(population):
  legalCounts = [[0] * numCols for i in xrange(numRows)]
  for path in population:
    for r in xrange(numRows):
      for c in xrange(numCols):
        if isLegalPath(path, r, c):
          legalCounts[r][c] += 1
  print legalCounts

def followPath(originalBoard, path, startRow, startCol):
  board = deepcopy(originalBoard)
  prevRow = startRow
  prevCol = startCol
  color = board[startRow][startCol]
  for m in path:
    row = prevRow + deltas[m][0]
    col = prevCol + deltas[m][1]

    # Use this if you want to just truncate scoring instead of giving 0
    # if row < 0 or col < 0 or row >= numRows or col >= numCols:
      # return board

    board[prevRow][prevCol] = board[row][col]
    board[row][col] = color
    prevRow = row
    prevCol = col
  return board

def scorePath(board, pathVerbose):
  path = [move[1] for move in pathVerbose]
  startRow, startCol = pathVerbose[0][0]
  if not isLegalPath(path, startRow, startCol):
    return 0
  finalBoard = followPath(board, path, startRow, startCol)
  return countLinears(finalBoard)

def chooseParents(population, cdf, num):
  total = cdf[-1]
  return [population[numpy.searchsorted(cdf, random.randint(1, total))] for _ in xrange(num)]

def onePointCrossover(parents):
  split = random.randint(0, len(parents[0]) - 1)
  return [parents[0][:split] + parents[1][split:], parents[1][:split] + parents[0][split:]]

def twoPointCrossover(parents):
  length = len(parents[0])
  split1 = random.randint(0, length - 1)
  split2 = random.randint(0, length - 1)
  maxSplit = max(split1, split2)
  minSplit = min(split1, split2)
  return [parents[0][:minSplit] + parents[1][minSplit:maxSplit] + parents[0][maxSplit:]]

def cutAndSplice(parents):
  split1 = random.randint(0, len(parents[0]) - 1)
  split2 = random.randint(0, len(parents[1]) - 1)
  return [parents[0][split1:] + parents[1][:split2], parents[1][split2:] + parents[0][:split1]]

def onePointCrossover2(parents):
  # for variable length
  split = random.randint(0, min(len(parents[0]), len(parents[1])) - 1)
  return [parents[0][:split] + parents[1][split:], parents[1][:split] + parents[0][split:]]

def crossoverLocation(parents):
  locs = [[move[0] for move in parent] for parent in parents]
  intersect = set(locs[0]).intersection(set(locs[1]))
  if len(intersect) == 0:
    return parents
  loc = random.choice(list(intersect))
  indices = [[i for i, x in enumerate(parent) if x == loc] for parent in locs]
  split1 = random.choice(indices[0])
  split2 = random.choice(indices[1])
  return [parents[0][:split1] + parents[1][split2:], parents[1][:split2] + parents[0][split1:]]

def mutate(population):
  pass
  # length = len(population[0])
  # numMoves = len(moveDist)
  # prob = 1.0/length
  # for i, path in enumerate(population):
  #   if random.random() > prob:
  #     continue
  #   index = random.randint(0, length - 1)
  #   population[i] = path[:index] + moveDist[random.randint(0, numMoves - 1)] + path[index+1:]


def advanceGeneration(board, population):
  scores = [scorePath(board, path) for path in population]
  cdf = numpy.cumsum(scores)
  #print 'avgScore:', cdf[-1] * 1.0/len(population)
  newPop = []
  while len(newPop) < len(population):
    parents = chooseParents(population, cdf, 2)
    children = crossoverLocation(parents)
    for child in children:
      child = simplifyPath(child)
      if len(child) <= 40 and len(child) > 0:
        newPop.append(child)
  mutate(newPop)
  return newPop

def geneticAlg(size, length, gen):
  initBoard = getRandomBoard()
  bestScore = 0
  bestPath = None
  bestLoc = None
  iterScore = 0
  multIter = 0.0
  for x in xrange(1):
    pop = initPopulation(size, length)
    for i in xrange(gen):
      print x, 'generation', i
      pop = advanceGeneration(initBoard, pop)
    for path in pop:
      startRow, startCol = path[0][0]
      path_pretty = prettyPath(path)
      score = scoreBoard(followPath(initBoard, path_pretty, startRow, startCol))
      if score > bestScore:
        bestPath = path
        bestScore = score
        bestLoc = (startRow, startCol)
    if bestScore > iterScore:
      multIter = 1.0
    print x, bestScore
  pretty_path = prettyPath(bestPath)
  print initBoard
  print "best path", pretty_path, "starts at", bestLoc, "and scores", bestScore
  return bestScore, bestPath, bestLoc, multIter

def prettyPath(path):
  return ''.join([move[1] for move in path])

def simplifyPrettyPath(path):
  repl = ['RL', 'LR', 'UD', 'DU']
  length = len(path)
  while True:
    for r in repl:
      path = path.replace(r, '')
    if len(path) == length:
      return path
    length = len(path)

def simplifyPath(path):
  pretty_path = simplifyPrettyPath(prettyPath(path))
  row, col = path[0][0]
  path = []
  for m in pretty_path:
    path.append(((row, col), m))
    row += deltas[m][0]
    col += deltas[m][1]
  return path

def pathLength(path):
  return len(simplifyPath(path))

def simulate(numBoards = 30, size = 10000, avgLength = 30, gen = 50):
  bestScores = Array('f', numBoards)
  bestPathLengths = Array('f', numBoards)
  multIters = Array('f', numBoards)
  threads = []

  def store(i, bestScores, bestPathLengths):
    score, path, start, multIter = geneticAlg(size, avgLength, gen)
    bestScores[i] = score
    bestPathLengths[i] = pathLength(path)
    multIters[i] = multIter

  for i in range(numBoards):
    t = Process(target = store, args = (i, bestScores, bestPathLengths))
    t.start()
    threads.append(t)
  for t in threads:
    t.join()

  multIters = [x for x in multIters if x == 1.0]
  print "of %d boards, %d needed more than one iteration", (numBoards, len(multIters))
  print "avg score:", sum(bestScores) / numBoards, "avg len:", sum(bestPathLengths) / numBoards