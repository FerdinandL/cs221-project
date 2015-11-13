import random
from baseline import randomStart
from board import *
from multiprocessing import Process, Array

def allMoves(board, row, col, color):
  # gets possible moves : ((newRow, newCol), newScore)
  moves = []
  deltas = []
  if row > 0:
    deltas.append((-1, 0))
  if row < numRows-1:
    deltas.append((1, 0))
  if col > 0:
    deltas.append((0, -1))
  if col < numCols-1:
    deltas.append((0, 1))
  currentScore = scoreBoard(board)
  for delta in deltas:
    newRow = row + delta[0]
    newCol = col + delta[1]
    board[row][col] = board[newRow][newCol]
    board[newRow][newCol] = color
    score = scoreBoard(board)
    moves.append(((newRow, newCol), score))
    board[newRow][newCol] = board[row][col]
    board[row][col] = color
  return moves

def nondecreasingMoves(board, row, col, color): 
  # gets nondecreasing moves : ((newRow, newCol), newScore)
  moves = allMoves(board, row, col, color)
  score = scoreBoard(board)
  nondecreasingMoves = [move for move in moves if move[1] >= score]
  return nondecreasingMoves

def decreasingMoves(board, row, col, color):
  # gets moves that decrease score
  moves = allMoves(board, row, col, color)
  score = scoreBoard(board)
  decreasingMoves = [move for move in moves if move[1] < score]
  return decreasingMoves

def bestMove(board, row, col, color):
  # gets best move
  moves = allMoves(board, row, col, color)
  return max(moves, key = lambda x : x[1]) if len(moves) > 0 else (None, 0)

def bestNondecreasingMove(board, row, col, color):
  # gets best nondecreasing move
  moves = nondecreasingMoves(board, row, col, color)
  return max(moves, key = lambda x : x[1]) if len(moves) > 0 else (None, 0)


def steepestAscentHillClimbing(originalBoard, numMoves = 40):
  # pick best nondecreasing move at each state - greedy
  board = deepcopy(originalBoard)
  row, col, color = randomStart(board)
  path = [(row, col)]
  for x in xrange(numMoves):
    move, score = bestNondecreasingMove(board, row, col, color)
    if move is None: # score can only decrease - stop
      break
    if len(path) > 1 and move == path[len(path) - 2]:
      # looping -> stop
      break
    newRow, newCol = move
    board[row][col] = board[newRow][newCol]
    board[newRow][newCol] = color
    path.append(move)
    row = newRow
    col = newCol
  return path, scoreBoard(board)

def simulateSteepestAscentHillClimbing(numTrials = 1000):
  print 'simulating steepest ascent hill climbing - take best move at each state'
  scores = []
  for i in xrange(numTrials):
    b = getRandomBoard()
    scores.append(steepestAscentHillClimbing(b)[1])
  print '    average score', sum(scores) / float(len(scores))
  print '    max score', max(scores)


def randomHillClimbing(originalBoard, numMoves = 40):
  # picks random nondecreasing move at each state - less greedy
  board = deepcopy(originalBoard)
  row, col, color = randomStart(board)
  path = [(row, col)]
  for x in xrange(numMoves):
    moves = nondecreasingMoves(board, row, col, color)
    if len(moves) == 0: # score can only decrease - stop
      break
    move, score = random.choice(moves)
    newRow, newCol = move
    board[row][col] = board[newRow][newCol]
    board[newRow][newCol] = color
    path.append(move)
    row = newRow
    col = newCol
  return path, scoreBoard(board)

def simulateRandomHillClimbing(numTrials = 1000):
  print 'simulating random hill climbing - take random nondecreasing move at each state'
  scores = []
  for i in xrange(numTrials):
    b = getRandomBoard()
    scores.append(randomHillClimbing(b)[1])
  print '    average score', sum(scores) / float(len(scores))
  print '    max score', max(scores)


def simulatedAnnealing(originalBoard, prob, iters = 1000, numMoves = 40):
  # hill climbing, but picks worse move with given probability
  bestScore = 0
  bestPath = None
  for i in xrange(iters):
    board = deepcopy(originalBoard)
    row, col, color = randomStart(board)
    path = [(row, col)]
    for x in xrange(numMoves):
      random_num = random.random()
      noDecreasingMove = False
      if random_num < prob: # pick random move that decreases score
        moves = decreasingMoves(board, row, col, color)
        if len(moves) == 0:
          noDecreasingMove = True
          break
        move = random.choice(moves)[0]
      if random_num >= prob or noDecreasingMove is True: # pick best move
        move, score = bestMove(board, row, col, color)
        if move is None:
          print 'THIS IS NOT SUPPOSED TO HAPPEN'
      newRow, newCol = move
      board[row][col] = board[newRow][newCol]
      board[newRow][newCol] = color
      path.append(move)
      row = newRow
      col = newCol
    score = scoreBoard(board)
    if score > bestScore:
      bestScore = score
      bestPath = path
  return (bestPath, bestScore)

def simulateSimulatedAnnealing(prob = 0.2, numBoards = 100, iters = 1000):
  print 'simulating simulated annealing - with prob', prob, 'over', numBoards, 'boards, each with', iters, 'trials'
  bestScores = Array('f', numBoards)
  threads = []

  def storeResult(b, prob, iters, i, bestScores):
    bestPath, bestScore = simulatedAnnealing(b, prob, iters)
    bestScores[i] = bestScore

  for i in xrange(numBoards):
    t = Process(target = storeResult, args = (getRandomBoard(), prob, iters, i, bestScores))
    t.start()
    threads.append(t)
  for t in threads:
    t.join()
    
  avgScore = sum(bestScores) / float(len(bestScores))
  print '    average score ', avgScore
  return avgScore

def getBestProbability(numBoards = 100, iters = 1000):
  # gets best probability for simulated annealing
  probs = []
  for i in range(10):
    prob = i * 0.02
    avgScore = simulateSimulatedAnnealing(prob, numBoards, iters)
    probs.append((prob, avgScore))
  return max(probs, key = lambda x : x[1])[0]
