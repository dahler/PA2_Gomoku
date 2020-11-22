# 
# Programming Assignment 2, CS640
#
# A Gomoku (Gobang) Game
#
# Adapted from CS111
# By Yiwen Gu
#
# You need to implement an AI Player for Gomoku
# A Random Player is provided for you
# 
#

import math
from pa2_gomoku import Player
import time


class AIPlayer(Player):
    """ a subclass of Player that looks ahead some number of moves and 
    strategically determines its best next move.
    """
    MAX_DEPTH = 2

    def next_move(self, board):
        """ returns the called AIPlayer's next move for a game on
            the specified Board object. 
            input: board is a Board object for the game that the called
                     Player is playing.
            return: row, col are the coordinated of a vacant location on the board 
        """
        

        bestScore = - math.inf
        matrix = self.toMatrix(board)
        squares = self.getSquaresToCheck(matrix)
        move = []

        if len(squares) == 0:
            return[4,4]


        start = time.time()        
        for [y, x] in squares:     
            matrix[y][x] = -1
            score = self.alphaBeta(matrix, 0, -math.inf, math.inf, False)
            matrix[y][x] = 0

            if score > bestScore:
                bestScore = score
                move = [y, x]

        self.num_moves += 1
        print(move)
        print("number of squares, ",len(squares))
        print(squares)
        t = time.time() - start
        if t >= 5 :
           
            
            print("time needed: ", t)

        return move




        ################### TODO: ######################################
        # Implement your strategy here. 
        # Feel free to call as many as helper functions as you want.
        # We only cares the return of this function
        ################################################################


    def alphaBeta(self, matrix, depth, alpha, beta, isAiTurn):

        

        if depth >= self.MAX_DEPTH:
            staticEval = self.staticEval(matrix)
            return staticEval

        best = - math.inf if isAiTurn else math.inf
        squares = self.getSquaresToCheck(matrix)

        # Check every possible cell
        for i in range(len(squares)):
            [y, x] = squares[i]
            matrix[y][x] = -1 if isAiTurn else 1

            # Get the score if put chess in this cell. Update best with the score
            score = self.alphaBeta(matrix, depth + 1, alpha, beta, not isAiTurn)
            best = max(score, best) if isAiTurn else min(score, best)

            # Update alpha and beta
            if isAiTurn:
                alpha = max(alpha, best)
            else:
                beta = min(beta, best)

            matrix[y][x] = 0

            # Prune if alpha is larger than beta. Because this path will definitely not selected by opponent.
            if alpha >= beta:
                break

      

        return best




    def getSquaresToCheck(self, matrix):
        adjacent = []
        forcedWins = []

        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j] == 0 and self.isTouchingOccupied(matrix, i, j):
                    adjacent.append([i, j])

                    # Check winner for opponent
                    matrix[i][j] = 1
                    if self.checkWinner(matrix, 1, i, j):
                        forcedWins.append([i, j])

                    # Check winner for ai
                    matrix[i][j] = -1
                    if self.checkWinner(matrix, -1, i, j):
                        forcedWins.append([i, j])

                    matrix[i][j] = 0

        return forcedWins if forcedWins else adjacent



    def isTouchingOccupied(self, matrix, i, j):
        return self.occupied(matrix, i + 1, j) or self.occupied(matrix, i - 1, j) or self.occupied(matrix, i, j + 1)\
               or self.occupied(matrix, i, j - 1) or self.occupied(matrix, i + 1, j + 1) \
               or self.occupied(matrix, i - 1, j + 1) \
               or self.occupied(matrix, i - 1, j - 1) or self.occupied(matrix, i + 1, j - 1)


    def occupied(self, matrix, i, j):
        if 0 <= i < len(matrix) and 0 <= j < len(matrix[0]):
            return matrix[i][j]
        else:
            return False




    def staticEval(self, matrix):
        return self.horizontalScore(matrix) \
               + self.verticalScore(matrix) \
               + self.diagonalScore(matrix)


    def horizontalScore(self, matrix):
        score = 0
       
        for i in range(len(matrix)):
            current = 0
            streak = 0

            for j in range(len(matrix[i])):
                current, streak, score = self.scoreConsecutive(matrix[i][j], current, streak, score)

            # If the counting hasn't ended before the row come to an end, add the missing score to it
            if current != 0:
                score += current * self.adjacentBlockScore(streak)

        return -1 * score


    def verticalScore(self, matrix):
        score = 0
        for i in range(len(matrix[0])):
            current = 0
            streak = 0
             
            for j in range(len(matrix)):
                current, streak, score = self.scoreConsecutive(matrix[j][i], current, streak, score)

            if current != 0:
                score += current * self.adjacentBlockScore(streak)

        return -1 * score


    def diagonalScore(self, matrix):
        score = 0
        length = len(matrix)
        res = []

        for i in range(4, length):

            # Initialization
            for k in range(4):
                res.append({"streak": 0, "current": 0, "score": 0})


            for j in range(i + 1):

                # Start at (i, 0) and move upper right
                res[0]["current"], res[0]["streak"], res[0]["score"] = \
                    self.scoreConsecutive(matrix[i - j][j], res[0]["current"],
                                          res[0]["streak"], res[0]["score"])

                # Start at (len - 1, i) and move upper left
                res[1]["current"], res[1]["streak"], res[1]["score"] = \
                    self.scoreConsecutive(matrix[length - 1 - j][i - j], res[1]["current"],
                                          res[1]["streak"], res[1]["score"])

                # Start at (0, len - 1 - i) and move lower right
                res[2]["current"], res[2]["streak"], res[2]["score"] = \
                    self.scoreConsecutive(matrix[j][length - 1 - i + j], res[2]["current"],
                                          res[2]["streak"], res[2]["score"])

                # Start at (len - 1 - i, len - 1) and move lower left
                res[3]["current"], res[3]["streak"], res[3]["score"] = \
                    self.scoreConsecutive(matrix[length - 1 - i + j][length - 1 - j], res[3]["current"],
                                          res[3]["streak"], res[3]["score"])

                for d in res:
                    score += d["score"]

            return -1 * score


    # Check if this cell has the same symbol as current streak
    # cell: currently checking block
    # current: current in a row symbol
    # streak: current number of symbol current in a row
    def scoreConsecutive(self, cell, current, streak, score):
        if cell != current:
            # If current is 0, set current to be the same as cell, initialize streak to 1
            if current == 0:
                current = cell
                streak = 1
            # If the sequence is broken, count the score and add it
            else:
                score += current * self.adjacentBlockScore(streak)
                current = cell
                streak = 1
        # If cell has the same symbol as current, add streak by 1
        else:
            if cell != 0:
                streak += 1

        return current, streak, score


    # Return the score of a consecutive sequence of blocks
    # count: number in a row
    def adjacentBlockScore(self, count):
        scoreMatrix = [0, 2, 4, 8, 16, 32]
        if count > 4:
            print("count", count)
        return scoreMatrix[count]

    def checkWinner(self, matrix, checker, i, j):
        return self.is_horizontal_win(matrix, checker, i, j) \
               or self.is_vertical_win(matrix, checker, i, j) \
               or self.is_diagonal1_win(matrix, checker, i, j) \
               or self.is_diagonal2_win(matrix, checker, i, j)


    def is_horizontal_win(self, matrix, checker, r, c):
        cnt = 0

        for i in range(5):

            if c + i < len(matrix[0]) and matrix[r][c + i] == checker:
                cnt += 1
            else:
                break

        if cnt == 5:
            return True
        else:
            for i in range(1, 6 - cnt):
                if c - i >= 0 and matrix[r][c - i] == checker:
                    cnt += 1
                else:
                    break

            if cnt == 5:
                return True

        return False


    def is_vertical_win(self, matrix, checker, r, c):
        cnt = 0

        for i in range(5):
            if r + i < len(matrix[0]) and matrix[r + i][c] == checker:
                cnt += 1
            else:
                break

        if cnt == 5:
            return True
        else:
            for i in range(1, 6 - cnt):
                if r - i >= 0 and matrix[r - i][c] == checker:
                    cnt += 1
                else:
                    break

            if cnt == 5:
                return True
        return False


    def is_diagonal1_win(self, matrix, checker, r, c):
        cnt = 0
        for i in range(5):
            if r + i < len(matrix) and c + i < len(matrix[0]) and \
                    matrix[r + i][c + i] == checker:
                cnt += 1
                # print('D1: L ' + str(cnt))
            else:
                break
        if cnt == 5:
            return True
        else:
            for i in range(1, 6 - cnt):
                if r - i >= 0 and c - i >= 0 and \
                        matrix[r - i][c - i] == checker:
                    cnt += 1
                    # print('D1: R ' + str(cnt))
                else:
                    break

            if cnt == 5:
                return True

        return False


    def is_diagonal2_win(self, matrix, checker, r, c):
        cnt = 0
        for i in range(5):
            if r - i >= 0 and c + i < len(matrix[0]) and \
                    matrix[r - i][c + i] == checker:
                cnt += 1
                # print('D2: L ' + str(cnt))
            else:
                break

        if cnt == 5:
            return True
        else:
            for i in range(1, 6 - cnt):
                if r + i < len(matrix) and c - i >= 0 and \
                        matrix[r + i][c - i] == checker:
                    cnt += 1
                    # print('D2: R ' + str(cnt))
                else:
                    break

            if cnt == 5:
                return True

        return False

    def toMatrix(self, board):
        height = board.height #board.getHeight()
        width = board.width #board.getWidth()
        matrix = [[0 for x in range(height)] for y in range(width)]

        for i in range(height):
            for j in range(width):
                if board.getChecker(i, j) == self.checker:
                    matrix[i][j] = -1
                if board.getChecker(i, j) == self.opponent_checker():
                    matrix[i][j] = 1

        return matrix






