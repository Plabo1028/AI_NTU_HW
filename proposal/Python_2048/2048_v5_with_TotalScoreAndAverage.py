# v5. checkmate + adaptive depth + smooth + snack + monotonicity + GetTotalScore and average 

from __future__ import print_function

import os
import sys
import copy
import random
import functools
import math

import colorama
from colorama import Back, Fore, Style

# define probabilities
prob_2 = 0.9
prob_4 = 0.1

#Python 2/3 compatibility.
if sys.version_info[0] == 2:
	range = xrange
	input = raw_input


def _getch_windows(prompt):
	"""
	Windows specific version of getch.  Special keys like arrows actually post
	two key events.  If you want to use these keys you can create a dictionary
	and return the result of looking up the appropriate second key within the
	if block.
	"""
	print(prompt, end="")
	key = msvcrt.getch()
	if ord(key) == 224:
		key = msvcrt.getch()
		return key
	print(key.decode())
	return key.decode()


def _getch_linux(prompt):
	"""Linux specific version of getch."""
	print(prompt, end="")
	sys.stdout.flush()
	fd = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	new = termios.tcgetattr(fd)
	new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
	new[6][termios.VMIN] = 1
	new[6][termios.VTIME] = 0
	termios.tcsetattr(fd, termios.TCSANOW, new)
	char = None
	try:
		char = os.read(fd, 1)
	finally:
		termios.tcsetattr(fd, termios.TCSAFLUSH, old)
	print(char.decode())
	return char.decode()


#Set version of getch to use based on operating system.
if sys.platform[:3] == 'win':
	import msvcrt
	getch = _getch_windows
else:
	import termios
	getch = _getch_linux


RESET = Style.RESET_ALL
WHITE = Fore.BLACK+Back.WHITE+Style.BRIGHT

BRIGHTS = {"GREEN" : Back.GREEN+Fore.RED+Style.BRIGHT,
		   "RED" : Back.RED+Fore.GREEN+Style.BRIGHT,
		   "YELLOW" : Back.YELLOW+Fore.CYAN+Style.BRIGHT,
		   "BLUE" : Back.BLUE+Fore.YELLOW+Style.BRIGHT,
		   "MAGENTA" : Back.MAGENTA+Fore.CYAN+Style.BRIGHT,
		   "CYAN" : Back.CYAN+Fore.YELLOW+Style.BRIGHT,
		   "WHITE" : Back.WHITE+Fore.RED+Style.BRIGHT}

IMPOSSIBLE = {"CYAN" : Back.CYAN+Fore.GREEN+Style.BRIGHT,
			  "RED" : Back.RED+Fore.WHITE+Style.BRIGHT,
			  "YELLOW" : Back.YELLOW+Fore.WHITE+Style.BRIGHT}

COLORS = {2      : "{}   2  {}".format(Back.GREEN, RESET),
		  4      : "{}   4  {}".format(Back.RED, RESET),
		  8      : "{}   8  {}".format(Back.YELLOW, RESET),
		  16     : "{}  16  {}".format(Back.BLUE, RESET),
		  32     : "{}  32  {}".format(Back.MAGENTA, RESET),
		  64     : "{}  64  {}".format(Back.CYAN, RESET),
		  128    : "{}  128 {}".format(WHITE, RESET),
		  256    : "{}  256 {}".format(BRIGHTS["GREEN"], RESET),
		  512    : "{}  512 {}".format(BRIGHTS["RED"], RESET),
		  1024   : "{} 1024 {}".format(BRIGHTS["YELLOW"], RESET),
		  2048   : "{} 2048 {}".format(BRIGHTS["BLUE"], RESET),
		  4096   : "{} 4096 {}".format(BRIGHTS["MAGENTA"], RESET),
		  8192   : "{} 8192 {}".format(BRIGHTS["CYAN"], RESET),
		  16384  : "{}16384 {}".format(BRIGHTS["WHITE"], RESET),
		  32768  : "{}32768 {}".format(IMPOSSIBLE["CYAN"], RESET),
		  65536  : "{}65536 {}".format(IMPOSSIBLE["RED"], RESET),
		  131972 : "{}131972{}".format(IMPOSSIBLE["YELLOW"], RESET)}

def push_row(row, left=True):
	"""Push all tiles in one row; like tiles will be merged together."""
	row = row[:] if left else row[::-1]
	new_row = [item for item in row if item]
	for i in range(len(new_row)-1):
		if new_row[i] and new_row[i] == new_row[i+1]:
			new_row[i], new_row[i+1:] = new_row[i]*2, new_row[i+2:]+[""]
	new_row += [""]*(len(row)-len(new_row))
	return new_row if left else new_row[::-1]


def get_column(grid, column_index):
	"""Return the column from the grid at column_index  as a list."""
	return [row[column_index] for row in grid]


def set_column(grid, column_index, new):
	"""
	Replace the values in the grid at column_index with the values in new.
	The grid is changed inplace.
	"""
	for i,row in enumerate(grid):
		row[column_index] = new[i]


def push_all_rows(grid, left=True):
	"""
	Perform a horizontal shift on all rows.
	Pass left=True for left and left=False for right.
	The grid will be changed inplace.
	"""
	for i,row in enumerate(grid):
		grid[i] = push_row(row, left)


def push_all_columns(grid, up=True):
	"""
	Perform a vertical shift on all columns.
	Pass up=True for up and up=False for down.
	The grid will be changed inplace.
	"""
	for i,val in enumerate(grid[0]):
		column = get_column(grid, i)
		new = push_row(column, up)
		set_column(grid, i, new)


def get_empty_cells(grid):
	"""Return a list of coordinate pairs corresponding to empty cells."""
	empty = []
	for j,row in enumerate(grid):
		for i,val in enumerate(row):
			if not val:
				empty.append((j,i))
	return empty


def any_possible_moves(grid):
	"""Return True if there are any legal moves, and False otherwise."""
	if get_empty_cells(grid):
		return True
	for row in grid:
		if any(row[i]==row[i+1] for i in range(len(row)-1)):
			return True
	for i,val in enumerate(grid[0]):
		column = get_column(grid, i)
		if any(column[i]==column[i+1] for i in range(len(column)-1)):
			return True
	return False


def get_start_grid(cols=4, rows=4):
	"""Create the start grid and seed it with two numbers."""
	grid = [[""]*cols for i in range(rows)]
	for i in range(2):
		empties = get_empty_cells(grid)
		y,x = random.choice(empties)
		grid[y][x] = 2 if random.random() < prob_2 else 4
	return grid


def prepare_next_turn(grid):
	"""
	Spawn a new number on the grid; then return the result of
	any_possible_moves after this change has been made.
	"""
	empties = get_empty_cells(grid)
	y,x = random.choice(empties)
	grid[y][x] = 2 if random.random() < prob_2 else 4
	return any_possible_moves(grid)


def print_grid(grid):
	"""Print a pretty grid to the screen."""
	print("")
	wall = "+------"*len(grid[0])+"+"
	print(wall)
	for row in grid:
		meat = "|".join(COLORS[val] if val else " "*6 for val in row)
		print("|{}|".format(meat))
		print(wall)

def score_evaluation_monotonicity(grid):
	scoreList = [0,0,0,0]

	for i in range(0,4,1):
		#print ("i:",i)
		current = 0
		next = current + 1 
		while(next<4):
			while(next < 4 and grid[i][next] == ''):
				next = next +1 
			if next >= 4:
				next = next -1 

			if grid[i][current]=='' :
				currntValue = 0
				#print ("currntValue:",currntValue)
			else:
				currntValue = math.log(grid[i][current],2)
				#print ("currntValue:",currntValue)
			if grid[i][next] == '':
				nextValue = 0
				#print ("nextValue:",nextValue)
			else:
				nextValue = math.log(grid[i][next],2)
				#print ("nextValue:",nextValue)
			if currntValue > nextValue:
				temp0=scoreList[0]
				temp0 = temp0 + nextValue - currntValue
				scoreList[0] = temp0
				#print ("temp0:",temp0)
			elif currntValue < nextValue:
				temp1=scoreList[1]
				temp1 = temp1 + currntValue - nextValue
				scoreList[1] = temp1
				#print ("temp1:",temp1)
			current = next 
			#print ("current",current)
			next = next +1 

	for i in range(0,4,1):
		#print ("i:",i)
		current = 0
		next = current + 1 
		while(next<4):
			while(next < 4 and grid[next][i] == ''):
				next = next +1 
			if next >= 4:
				next = next -1 

			if grid[current][i]=='' :
				currntValue = 0
				#print ("currntValue:",currntValue)
			else:
				currntValue = math.log(grid[current][i],2)
				#print ("currntValue:",currntValue)

			if grid[next][i] == '':
				nextValue = 0
				#print ("nextValue:",nextValue)
			else:
				nextValue = math.log(grid[next][i],2)
				#print ("nextValue:",nextValue)
			if currntValue > nextValue:
				temp2=scoreList[2]
				temp2 = temp2 + nextValue - currntValue
				scoreList[2] = temp2
				#print ("temp2:",temp2)
			elif currntValue < nextValue:
				temp3=scoreList[3]
				temp3 = temp3 + currntValue - nextValue
				scoreList[3] = temp3
				#print ("temp3:",temp3)

			current = next 
			next = next + 1
	print ("scoreList in score_evaluation_monotonicity:",scoreList)
	return ( max(scoreList[0],scoreList[1]) + max(scoreList[2],scoreList[3]) ) 




def score_evaluation_smooth(grid):
	height = len(grid)
	width = len(grid[0])
	score = 0.0
	scoreList = []

	smooth=0
	
	for i in range(height):
		for j in range(width):
			if grid[i][j] != '':
				value = math.log(grid[i][j],2)

				tempi=i
				tempj=j

				#look upward
				if tempi > 0:
					tempi=tempi-1
					while grid[tempi][tempj] == '' and tempi >0:
						tempi=tempi-1

					if grid[tempi][tempj] != '':
						TargetValue =  math.log(grid[tempi][tempj],2)
						smooth = smooth - abs(value-TargetValue)
						#print (tempi,tempj)
						#print (smooth)
				#look left
				tempi=i
				tempj=j
				if tempj > 0:
					tempj=tempj-1
					while grid[tempi][tempj] == '' and tempj >0:
						tempj=tempj-1
					if grid[tempi][tempj] != '':
						TargetValue = math.log(grid[tempi][tempj],2)
						smooth = smooth - abs(value-TargetValue)
						#print (tempi,tempj)
						#print (smooth)
				#look right
				tempi=i
				tempj=j
				if tempj < 3:
					tempj=tempj+1
					while grid[tempi][tempj] == '' and tempj < 3:
						tempj=tempj+1
					if grid[tempi][tempj] != '':
						TargetValue = math.log(grid[tempi][tempj],2)
						smooth = smooth - abs(value-TargetValue)
						#print (tempi,tempj)
						#print (smooth)
				#look down 
				tempi=i
				tempj=j
				if tempi < 3:
					tempi=tempi+1
					while grid[tempi][tempj] == '' and tempi < 3:
						tempi=tempi+1
					if grid[tempi][tempj] != '':
						TargetValue = math.log(grid[tempi][tempj],2)
						smooth = smooth - abs(value-TargetValue)
						#print (tempi,tempj)
						#print (smooth)

	#print  (5000*(1/(abs(smooth)+1)))
	return (1/(abs(smooth)+1))

def score_evaluation_snack(grid):
	height = len(grid)
	width = len(grid[0])
	score = 0.0
	scoreList = []
	n = 0
	r = 0.25

	figureGrid = copy.deepcopy(grid)

	for i in range(height):
		for j in range(width):
			if grid[i][j] == '':
				figureGrid[i][j] = 0
	
	# 1
	for j in range(width):
		if j % 2 == 0:
			for i in range(height):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1
		
		if j % 2 == 1:
			for i in range(height - 1, -1, -1):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1

	scoreList.append(score)
	n = 0
	score = 0.0
	
	# 2
	for j in range(width):
		if j % 2 == 0:
			for i in range(height - 1, -1, -1):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1
		
		if j % 2 == 1:
			for i in range(height):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1

	scoreList.append(score)
	n = 0
	score = 0.0

	# 3
	for j in range(width - 1, -1, -1):
		if j % 2 == 0:
			for i in range(height):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1
		
		if j % 2 == 1:
			for i in range(height - 1, -1, -1):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1

	scoreList.append(score)	
	n = 0
	score = 0.0

	# 4
	for j in range(width - 1, -1, -1):
		if j % 2 == 0:
			for i in range(height - 1, -1, -1):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1
		
		if j % 2 == 1:
			for i in range(height):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1

	scoreList.append(score)	
	n = 0
	score = 0.0
	
	# 5
	for i in range(height):
		if i % 2 == 0:
			for j in range(width):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1
		
		if i % 2 == 1:
			for j in range(width - 1, -1, -1):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1

	scoreList.append(score)
	n = 0
	score = 0.0
	
	# 6
	for i in range(height):
		if i % 2 == 0:
			for j in range(width - 1, -1, -1):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1
		
		if i % 2 == 1:
			for j in range(width):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1

	scoreList.append(score)
	n = 0
	score = 0.0

	# 7
	for i in range(height - 1, -1, -1):
		if i % 2 == 0:
			for j in range(width - 1, -1, -1):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1
		
		if i % 2 == 1:
			for j in range(width):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1

	scoreList.append(score)	
	n = 0
	score = 0.0

	# 8
	for i in range(height - 1, -1, -1):
		if i % 2 == 0:
			for j in range(width):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1
		
		if i % 2 == 1:
			for j in range(width - 1, -1, -1):
				score += figureGrid[i][j] * (r ** n)
				n = n + 1

	scoreList.append(score)	
	n = 0
	score = 0.0
	
	#print (max(scoreList))

	return max(scoreList)

functions = {"a" : functools.partial(push_all_rows, left=True), 
				"d" : functools.partial(push_all_rows, left=False),
				"w" : functools.partial(push_all_columns, up=True),
				"s" : functools.partial(push_all_columns, up=False)}

def IM(grid, player, depth):
	if depth == 0:
		return score_evaluation_snack(grid)

	# computer's turn (randomly)
	if player == 0:
		alpha = 0
		for x, y in get_empty_cells(grid):
			numEmptyCells = len(get_empty_cells(grid))
			grid[x][y] = 2
			alpha = alpha + prob_2 * 1 / numEmptyCells * IM(grid, 1, depth - 1)
			grid[x][y] = ''

		for x, y in get_empty_cells(grid):
			numEmptyCells = len(get_empty_cells(grid))
			grid[x][y] = 4
			alpha = alpha + prob_4 * 1 / numEmptyCells * IM(grid, 1, depth - 1)
			grid[x][y] = ''	

	elif player == 1:
		alpha = 0
		
		grid_copy = copy.deepcopy(grid)
		functions['a'](grid_copy)
		if grid_copy != grid:
			alpha = max(alpha, IM(grid_copy, 0, depth - 1))

		grid_copy = copy.deepcopy(grid)
		functions['d'](grid_copy)
		if grid_copy != grid:
			alpha = max(alpha, IM(grid_copy, 0, depth - 1))		

		grid_copy = copy.deepcopy(grid)
		functions['w'](grid_copy)
		if grid_copy != grid:
			alpha = max(alpha, IM(grid_copy, 0, depth - 1))

		grid_copy = copy.deepcopy(grid)
		functions['s'](grid_copy)
		if grid_copy != grid:
			alpha = max(alpha, IM(grid_copy, 0, depth - 1))

	return alpha

def get_totall_score(grid):
	totalScore = 0
	height = len(grid)
	width = len(grid[0])
	figureGrid = copy.deepcopy(grid)

	for i in range(height):
		for j in range(width):
			if grid[i][j] == '':
				figureGrid[i][j] = 0

	for j in range(width):
			for i in range(height):
				totalScore += figureGrid[i][j] 

	return totalScore
				

def get_next_action(grid):
	maxScore = 0
	action = ''

	height = len(grid)
	width = len(grid[0])

	depth =2 

	'''
	if len(get_empty_cells(grid)) > height * width / 4:
		depth = 2
	else:
		depth = 4'''

	grid_copy = copy.deepcopy(grid)
	functions['a'](grid_copy)
	if grid_copy != grid:
		score = IM(grid_copy, 0, depth)
		if score > maxScore:
			maxScore = score
			action = 'a'

	grid_copy = copy.deepcopy(grid)
	functions['d'](grid_copy)
	if grid_copy != grid:
		score = IM(grid_copy, 0, depth)
		if score > maxScore:
			maxScore = score
			action = 'd'

	grid_copy = copy.deepcopy(grid)
	functions['w'](grid_copy)
	if grid_copy != grid:
		score = IM(grid_copy, 0, depth)
		if score > maxScore:
			maxScore = score
			action = 'w'

	grid_copy = copy.deepcopy(grid)
	functions['s'](grid_copy)
	if grid_copy != grid:
		score = IM(grid_copy, 0, depth)
		if score > maxScore:
			maxScore = score
			action = 's'

	return action

def main():
	"""
	Get user input.
	Update game state.
	Display updates to user.
	"""
	colorama.init()

	grid = get_start_grid(*map(int,sys.argv[1:]))
	print_grid(grid)

	while True:
		grid_copy = copy.deepcopy(grid)
		get_input = getch("Enter direction (w/a/s/d/n/r/q/m): ")
		if get_input in functions:	
			functions[get_input](grid)
		elif get_input == "n":
			if get_next_action(grid) == '':
				print("Checkmate!")
				break
			functions[get_next_action(grid)](grid)
		elif get_input == "r":
			break
		elif get_input == "q":
			break
		elif get_input == "m":
			break
		else:
			print("\nInvalid choice.")
			continue
		if grid != grid_copy:
			if not prepare_next_turn(grid):
				print_grid(grid)
				print("You Lose!")
				break
		print_grid(grid)
	
	if get_input == "r":
		while True:
			grid_copy = copy.deepcopy(grid)

			if get_next_action(grid) == '':
				print("Checkmate!")
				break
			
			functions[get_next_action(grid)](grid)
			if grid != grid_copy:
				if not prepare_next_turn(grid):
					print_grid(grid)
					print("You Lose!")
					break
			print_grid(grid)

	if get_input == "m":
		listTS=[]
		sum = 0.0
		for i in range(0,25,1):

			colorama.init()

			grid = get_start_grid(*map(int,sys.argv[1:]))
			print_grid(grid)

			while True:
				if get_next_action(grid) == '':
					print("Checkmate!")
					print_grid(grid)
					listTS.append(get_totall_score(grid))
					break
				
				functions[get_next_action(grid)](grid)
				if grid != grid_copy:
					if not prepare_next_turn(grid):
						print_grid(grid)
						print("You Lose!")
						listTS.append(get_totall_score(grid))
						break
				#print_grid(grid)
		for i in range(len(listTS)):
			sum = sum + listTS[i]
		print ("average:",(sum/len(listTS)))
		print ("list:",listTS)

				

	print("Thanks for playing.")


if __name__ == "__main__":
	main()

