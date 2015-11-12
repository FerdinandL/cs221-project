import random
from copy import deepcopy
from board import *
import numpy

deltas = {'U': (-1, 0), 'R': (0, 1), 'D': (1, 0), 'L': (0, -1), 'S': (0, 0)}

def initPopulation(size = 10000, length = 20):
  population = []
  distribution = ['U', 'R', 'D', 'L'] * 5 + ['S']
  for i in xrange(size):
    rand = [random.randint(0, len(distribution) - 1) for j in xrange(length)]
    population.append(''.join(distribution[ind] for ind in rand))
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

def advanceGeneration(board, population, startRow, startCol):
  scores = [scorePath(board, path, startRow, startCol)**2 for path in population]
  cdf = numpy.cumsum(scores)
  total = cdf[-1]
  print 'totalScore:', total
  newPop = []
  for i in xrange(len(population)/2):
    path1 = population[numpy.searchsorted(cdf, random.randint(1, total))]
    path2 = population[numpy.searchsorted(cdf, random.randint(1, total))]
    split = random.randint(0, len(path1) - 1)
    newPop.append(path1[:split] + path2[split:])
    newPop.append(path2[:split] + path2[split:])
  return newPop

def geneticAlg(size = 10000, length = 20, gen = 20):
  initBoard = getRandomBoard()
  pop = initPopulation(size, length)
  for i in xrange(gen):
    pop = advanceGeneration(initBoard, pop, 3, 3)
  total = 0
  bestScore = 0
  bestPath = None
  for path in pop:
    if not isLegalPath(path, 3, 3):
      continue
    score = scoreBoard(followPath(initBoard, path, 3, 3))
    total += score
    if score > bestScore:
      bestPath = path
      bestScore = score
  print "best score:", bestScore
  print "avg score:", total * 1.0 / size



