import random
from copy import deepcopy
from board import *

def randomMove(board, row, col, color):
  deltas = []
  if row > 0:
    deltas.append((-1, 0))
  if row < numRows-1:
    deltas.append((1, 0))
  if col > 0:
    deltas.append((0, -1))
  if col < numCols-1:
    deltas.append((0, 1))
  move = deltas[random.randint(0, len(deltas)-1)]
  newRow = row + move[0]
  newCol = col + move[1]
  board[row][col] = board[newRow][newCol]
  board[newRow][newCol] = color
  return (newRow, newCol)

def randomStart(board):
  randomRow = random.randint(0, numRows-1)
  randomCol = random.randint(0, numCols-1)
  return (randomRow, randomCol, board[randomRow][randomCol])

def randomBaseline(originalBoard, moves = 40, iters = 1000):
  bestScore = 0
  bestPath = None
  for iter in xrange(iters):
    board = deepcopy(originalBoard)
    row, col, color = randomStart(board)
    iterScore = scoreBoard(board)
    pathLength = 1
    path = [(row, col)]
    for move in xrange(moves):
      row, col = randomMove(board, row, col, color)
      path.append((row, col))
      score = scoreBoard(board)
      if score > iterScore:
        pathLength = len(path)
        iterScore = score
    if iterScore > bestScore:
      bestPath = path[:pathLength]
      bestScore = iterScore
    elif iterScore == bestScore and (bestPath == None or pathLength < len(bestPath)):
      bestPath = path[:pathLength]
  return (bestScore, bestPath)

def followPath(originalBoard, path):
  board = deepcopy(originalBoard)
  prevLoc = path[0]
  color = board[prevLoc[0]][prevLoc[1]]
  for loc in path[1:]:
    board[prevLoc[0]][prevLoc[1]] = board[loc[0]][loc[1]]
    board[loc[0]][loc[1]] = color
    prevLoc = loc
  return board

def testRandomBaseLine(board):
  score, path = randomBaseline(board)
  print '************* Moves:', len(path) - 1, 'Score:', score
  printBoard(board)
  print '***********************************'
  finalBoard = followPath(board, path)
  printBoard(finalBoard)
  print '***********************************\n'

def simulate():
  total = 0
  lenTotal = 0
  for i in xrange(100):
    if i%10 == 0:
      print i
    board = getRandomBoard()
    score, path = randomBaseline(board)
    total += score
    lenTotal += len(path) - 1
  print "avg score:", total/100.0, "avg len:", lenTotal/100.0

