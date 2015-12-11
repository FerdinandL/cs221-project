import random
from copy import deepcopy
from board import *
import numpy
from multiprocessing import Process, Array

deltas = {'U': (-1, 0), 'R': (0, 1), 'D': (1, 0), 'L': (0, -1), 'P': (0, 0)}
moveDist = ['U', 'R', 'D', 'L']

def initPopulation(size, avgLength, stdev, startRow, startCol):
  population = []
  lengths = numpy.random.normal(avgLength, stdev, size)
  for length in lengths:
    # while True:
    rand = [random.randint(0, len(moveDist) - 1) for j in xrange(int(round(length)))]
    path = ''.join(moveDist[ind] for ind in rand)
      # if isLegalPath(path, startRow, startCol):
      #   break
    #print path
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
    board[prevRow][prevCol] = board[row][col]
    board[row][col] = color
    prevRow = row
    prevCol = col
  return board

def scorePath(board, path, startRow, startCol):
  if not isLegalPath(path, startRow, startCol):
    return 0
  finalBoard = followPath(board, path, startRow, startCol)
  return countLinears(finalBoard)

def chooseParents(population, cdf, num):
  total = cdf[-1]
  return [population[numpy.searchsorted(cdf, random.randint(1, total))] for _ in xrange(num)]

def onePointCrossover(parents):
  split = random.randint(0, len(parents[0]) - 1)
  return [parents[0][:split] + parents[1][split:]]

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


def advanceGeneration(board, population, startRow, startCol):
  scores = [scorePath(board, path, startRow, startCol) for path in population]
  cdf = numpy.cumsum(scores)
  #print 'avgScore:', cdf[-1] * 1.0/len(population)
  newPop = []
  while len(newPop) < len(population):
    parents = chooseParents(population, cdf, 2)
    children = onePointCrossover2(parents)
    newPop += children
  mutate(newPop)
  return newPop

def geneticAlg(size, length, stdev, gen):
  initBoard = getRandomBoard()
  bestScore = 0
  bestPath = None
  bestLoc = None
  for startRow in xrange(numRows):
    for startCol in xrange(numCols):
      pop = initPopulation(size, length, stdev, startRow, startCol)
      for i in xrange(gen):
        pop = advanceGeneration(initBoard, pop, startRow, startCol)
      for path in pop:
        if not isLegalPath(path, startRow, startCol):
          continue
        score = scoreBoard(followPath(initBoard, path, startRow, startCol))
        if score > bestScore:
          bestPath = path
          bestScore = score
          bestLoc = (startRow, startCol)
  print "best score:", bestScore
  return bestScore, bestPath, bestLoc

def pathLength(path):
  pauseCount = 0
  for i in xrange(len(path)):
    if path[i] == 'P':
      pauseCount += 1
  return len(path) - pauseCount

def simulate(numBoards = 30, size = 10000, avgLength = 30, stdev = 5, gen = 50):
  bestScores = Array('f', numBoards)
  bestPathLengths = Array('f', numBoards)
  threads = []

  def store(i, bestScores, bestPathLengths):
    score, path, start = geneticAlg(size, avgLength, stdev, gen)
    bestScores[i] = score
    bestPathLengths[i] =  pathLength(path)

  for i in range(numBoards):
    t = Process(target = store, args = (i, bestScores, bestPathLengths))
    t.start()
    threads.append(t)
  for t in threads:
    t.join()

  print "avg score:", sum(bestScores) / numBoards, "avg len:", sum(bestPathLengths) / numBoards



