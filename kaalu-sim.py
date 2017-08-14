#!/usr/bin/env python
#@+leo-ver=5-thin
#@+node:peckj.20170814140357.3: * @file kaalu-sim.py
#@@first
#@@language python

#@+<<imports>>
#@+node:peckj.20170814140714.1: ** <<imports>>
import sys
import re
import copy
#@-<<imports>>
#@+<<declarations>>
#@+node:peckj.20170814140720.1: ** <<declarations>>
PILES_TO_WIN = 4
CHAR_WHITE = '*'
CHAR_BLACK = '+'
CHAR_NEUTRAL = '^'

move_syntax = re.compile("^[a-g]([0-9]+\/[0-9]+[a-g])?$")
#@-<<declarations>>

#@+others
#@+node:peckj.20170814140810.1: ** class Player
class Player:
  #@+others
  #@+node:peckj.20170814141623.1: *3* __init__
  def __init__(self, name):
    self.name = name
  #@-others
#@+node:peckj.20170814140821.1: ** class Game
class Game:
  #@+others
  #@+node:peckj.20170814141718.1: *3* __init__
  def __init__(self, player_black, player_white):
    self.player_black = player_black
    self.player_white = player_white
    self.active_player = self.player_black
    
    self.previous_gamestate = None
    
    # board represented by tuples (black, neutral, white)
    self.board = { 'a': (2,3,2),
                   'b': (2,3,2),
                   'c': (2,3,2),
                   'd': (2,3,2),
                   'e': (2,3,2),
                   'f': (2,3,2),
                   'g': (2,3,2) }
    
    self.stock_black = 7
    self.stock_white = 7
    
    self.primacy_black = 0
    self.primacy_white = 0
    self.primacy_neutral = 0
    self.check_primicies()
  #@+node:peckj.20170814142235.1: *3* check_primicies
  def check_primicies(self):
    d = {'black': 0,
         'white': 0,
         'neutral': 0 }
    black = 0
    white = 0
    neutral = 0
    
    for key,pile in self.board.items():
      p = self.check_primicy(pile)
      d[p] = d[p] + 1

    self.primicy_black = d['black']
    self.primicy_white = d['white']
    self.primicy_neutral = d['neutral']
  #@+node:peckj.20170814142723.1: *3* check_primicy
  def check_primicy(self, pile):
    # pile is a tuple of form (b,n,w)
    # primicy is either the one with the most stones, or in case of a tie for most, the one with the least
    
    m = max(pile)
    c = pile.count(m)
    if c == 1:
      pos = pile.index(m)
    else:
      pos = pile.index(min(pile))

    return ['black','neutral','white'][pos]
  #@+node:peckj.20170814154755.1: *3* construct_gamestate
  def construct_gamestate(self):
    stock_black = self.stock_black
    stock_white = self.stock_white
    board = copy.deepcopy(self.board)
    gs = { 'stock_black': stock_black,
           'stock_white': stock_white,
           'board': board }
    return gs
  #@+node:peckj.20170814143859.1: *3* over
  def over(self):
    return self.primicy_black >= PILES_TO_WIN or self.primicy_white >= PILES_TO_WIN
      
  #@+node:peckj.20170814144023.1: *3* display_board
  def display_board(self):
    maxpad = max(sorted(self.board.values(), key=lambda x: sorted(x, reverse=True), reverse=True)[0])+1
    for key,pile in sorted(self.board.items()):
      b = pile[0] * CHAR_BLACK
      n = pile[1] * CHAR_NEUTRAL
      w = pile[2] * CHAR_WHITE
      print '%s  %s%s%s' % (key, b.center(maxpad), n.center(maxpad), w.center(maxpad))
  #@+node:peckj.20170814150015.1: *3* valid_move
  def valid_move(self, move):
    # first pass -- ensure the move is syntactically valid
    m = move.strip().lower()
    if move_syntax.search(m) is None:
      print 'does not match syntax'
      return False
    # if it passes, parse it niavely, returning a new hypothetical gamestate
    new_gamestate = self.parse_move(m)
    if new_gamestate is False:
      return False
    # ensure the new gamestate doesn't overallocate stock pieces
    if new_gamestate['stock_black'] < 0 or new_gamestate['stock_white'] < 0:
      return False
    # ensure the new gamestate consists of only valid piles
    if not self.check_board_validity(new_gamestate):
      return False
    # ensure the new gamestate doesn't 'undo' the previous player's turn
    # (compare to the gamestate prior to the opponent's last turn)
    if self.check_for_undo(new_gamestate):
      return False
    return new_gamestate
  #@+node:peckj.20170814150018.1: *4* parse_move
  def parse_move(self, move):  
    stock_black = self.stock_black
    stock_white = self.stock_white
    board = copy.deepcopy(self.board)
    if len(move) == 1:
      if move in 'abcdefg':
        new = board[move]
        if self.active_player == self.player_black:
          stock_black -= 1
          new = (new[0]+1, new[1], new[2])
        else:
          stock_white -= 1
          new = (new[0], new[1], new[2]+1)
        board[move] = new
        gs = { 'stock_black': stock_black,
               'stock_white': stock_white,
               'board': board }
        return gs
      else:
        return False
    else:
      from_pile = move[0]
      to_pile = move[-1]
      if from_pile == to_pile:
        return False
      m = move[1:-1]
      player,neutral = (int(x) for x in move[1:-1].split('/'))
      if player == 0 and neutral == 0:
        return False
      gs = self.construct_gamestate()
      source = gs['board'][from_pile]
      dest = gs['board'][to_pile]
      if self.active_player == self.player_black:
        source = (source[0]-player, source[1]-neutral, source[2])
        dest = (dest[0]+player, dest[1]+neutral, dest[2])
      else:
        source = (source[0], source[1]-neutral, source[2]-player)
        dest = (dest[0], dest[1]+neutral, dest[2]+player)
      gs['board'][from_pile] = source
      gs['board'][to_pile] = dest
      return gs
      
  #@+node:peckj.20170814154316.1: *4* check_board_validity
  def check_board_validity(self, gamestate):
    # check gamestate for 21 stones total of each color
    # check each pile for:
    # at least 7 stones
    # at least one of each color
    # no three-way ties
    print "game.check_board_validity stubbed."
    return True
  #@+node:peckj.20170814155217.1: *4* check_for_undo
  def check_for_undo(self, new_gamestate):
    # return True if the new move is an 'undo' state
    old_gamestate = self.previous_gamestate
    if old_gamestate is None:
      return False # first move of the game, so it's valid by default
    return old_gamestate == new_gamestate
  #@+node:peckj.20170814155618.1: *3* execute_move
  def execute_move(self, new_gamestate):
    self.previous_gamestate = self.construct_gamestate()
    self.stock_black = new_gamestate['stock_black']
    self.stock_white = new_gamestate['stock_white']
    self.board = new_gamestate['board']
    
    self.check_primicies()
    if self.active_player == self.player_black:
      self.active_player = self.player_white
    else:
      self.active_player = self.player_black
  #@-others
#@+node:peckj.20170814140850.1: ** main
def main():
  black = Player('black')
  white = Player('white')
  game = Game(black, white)
  
  #test_strings = ['a', 'b', 'a2/1b', 'h3/89a']
  #for s in test_strings:
  #  print s
  #  print move_syntax.search(s)
  #sys.exit(0)


  while not game.over():
    game.display_board()
    active_player = game.active_player
    move = raw_input("%s enter move:" % active_player.name)
    m = game.valid_move(move)
    if m:
      print m  
      game.execute_move(m)
    else:
      print "Invalid move."
  
  game.print_log()
  
#@-others

if __name__=='__main__':
  main()
  
#@-leo
