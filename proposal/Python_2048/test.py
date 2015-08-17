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

def score_evaluation_snake(grid):
	height = len(grid)
	width = len(grid[0])
	score = 0.0
	scoreList = []
	n = 0
	r0 = 0.25
	r1 = 0.25
	r2 = 0.25
	r3 = 0.25

	figureGrid = copy.deepcopy(grid)

	for i in range(height):
		for j in range(width):
			if grid[i][j] == '':
				figureGrid[i][j] = 0

	# 1
	for j in range(width):
		if j % 2 == 0:
			for i in range(height):
				if n/4 == 0:
					score += figureGrid[i][j] * (r0 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r2 ** n)
					n = n + 1
		if j % 2 == 1:
			for i in range(height - 1, -1, -1):
				if n/4 == 1:
					score += figureGrid[i][j] * (r1 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r3 ** n)
					n = n + 1

	scoreList.append(score)
	n = 0
	score = 0.0

	# 2
	for j in range(width):
		if j % 2 == 0:
			for i in range(height - 1, -1, -1):
				if n/4 == 0:
					score += figureGrid[i][j] * (r0 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r2 ** n)
					n = n + 1
		if j % 2 == 1:
			for i in range(height):
				if n/4 == 1:
					score += figureGrid[i][j] * (r1 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r3 ** n)
					n = n + 1

	scoreList.append(score)
	n = 0
	score = 0.0

	# 3
	for j in range(width - 1, -1, -1):
		if j % 2 == 0:
			for i in range(height):
				if n/4 == 0:
					score += figureGrid[i][j] * (r0 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r2 ** n)
					n = n + 1
		
		if j % 2 == 1:
			for i in range(height - 1, -1, -1):
				if n/4 == 1:
					score += figureGrid[i][j] * (r1 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r3 ** n)
					n = n + 1
	scoreList.append(score)	
	n = 0
	score = 0.0

	# 4
	for j in range(width - 1, -1, -1):
		if j % 2 == 0:
			for i in range(height - 1, -1, -1):
				if n/4 == 0:
					score += figureGrid[i][j] * (r0 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r2 ** n)
					n = n + 1
		
		if j % 2 == 1:
			for i in range(height):
				if n/4 == 1:
					score += figureGrid[i][j] * (r1 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r3 ** n)
					n = n + 1

	scoreList.append(score)	
	n = 0
	score = 0.0

	# 5
	for i in range(height):
		if i % 2 == 0:
			for j in range(width):
				if n/4 == 0:
					score += figureGrid[i][j] * (r0 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r2 ** n)
					n = n + 1
		
		if i % 2 == 1:
			for j in range(width - 1, -1, -1):
				if n/4 == 1:
					score += figureGrid[i][j] * (r1 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r3 ** n)
					n = n + 1

	scoreList.append(score)
	n = 0
	score = 0.0

	# 6
	for i in range(height):
		if i % 2 == 0:
			for j in range(width - 1, -1, -1):
				if n/4 == 0:
					score += figureGrid[i][j] * (r0 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r2 ** n)
					n = n + 1
		
		if i % 2 == 1:
			for j in range(width):
				if n/4 == 1:
					score += figureGrid[i][j] * (r1 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r3 ** n)
					n = n + 1

	scoreList.append(score)
	n = 0
	score = 0.0

	# 7
	for i in range(height - 1, -1, -1):
		if i % 2 == 0:
			for j in range(width - 1, -1, -1):
				if n/4 == 0:
					score += figureGrid[i][j] * (r0 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r2 ** n)
					n = n + 1
		
		if i % 2 == 1:
			for j in range(width):
				if n/4 == 1:
					score += figureGrid[i][j] * (r1 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r3 ** n)
					n = n + 1

	scoreList.append(score)	
	n = 0
	score = 0.0

	# 8
	for i in range(height - 1, -1, -1):
		if i % 2 == 0:
			for j in range(width):
				if n/4 == 0:
					score += figureGrid[i][j] * (r0 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r2 ** n)
					n = n + 1
		
		if i % 2 == 1:
			for j in range(width - 1, -1, -1):
				if n/4 == 1:
					score += figureGrid[i][j] * (r1 ** n)
					n = n + 1
				else:
					score += figureGrid[i][j] * (r3 ** n)
					n = n + 1

	scoreList.append(score)	
	n = 0
	score = 0.0

	return max(scoreList)

def score_evaluation_smooth(grid):
	height = len(grid)
	width = len(grid[0])
	score = 0.0
	scoreList = []

	smooth = 0
	
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

	return abs(smooth)

# useless evaluation function
def score_evaluation_mono(grid):
	height = len(grid)
	width = len(grid[0])
	scoreList = [0.0, 0.0, 0.0, 0.0]

	for i in range(height):
		tmpList = []
		for j in range(width):
			if grid[i][j] != '':
				tmpList.append(grid[i][j])

		for k in range(len(tmpList) - 1):
			if tmpList[k] < tmpList[k + 1]:
				scoreList[0] = scoreList[0] + math.log(tmpList[k + 1], 2) - math.log(tmpList[k], 2)
			else:	
				scoreList[1] = scoreList[1] + math.log(tmpList[k], 2) - math.log(tmpList[k + 1], 2)

	for j in range(width):
		tmpList = []
		for i in range(height):
			if grid[i][j] != '':
				tmpList.append(grid[i][j])

		for k in range(len(tmpList) - 1):
			if tmpList[k] < tmpList[k + 1]:
				scoreList[2] = scoreList[2] + math.log(tmpList[k + 1], 2) - math.log(tmpList[k], 2)
			else:	
				scoreList[3] = scoreList[3] + math.log(tmpList[k], 2) - math.log(tmpList[k + 1], 2)

	return max(scoreList[0], scoreList[1]) + max(scoreList[2], scoreList[3])
#	return abs(max(-scoreList[0], -scoreList[1]) + max(-scoreList[2], -scoreList[3]))


functions = {"a" : functools.partial(push_all_rows, left=True), 
				"d" : functools.partial(push_all_rows, left=False),
				"w" : functools.partial(push_all_columns, up=True),
				"s" : functools.partial(push_all_columns, up=False)}

def expectiminimax(grid, player, depth , demo ):
	height = len(grid)
	width = len(grid[0])

	if depth == 0:
		if demo == "1":
		# demo 1: emptyTiles() + smooth()
			return 50 * score_evaluation_emptyTiles(grid) + score_evaluation_smooth(grid)
		else:
		# demo 2: snake()
			return score_evaluation_snake(grid)


	# computer's turn (randomly)
	if player == 0:
		alpha = 0

		for x, y in get_empty_cells(grid):
	
			numEmptyCells = len(get_empty_cells(grid))
			grid[x][y] = 2
			alpha = alpha + prob_2 * 1 / numEmptyCells * expectiminimax(grid, 1, depth - 1,demo)
			grid[x][y] = ''

		for x, y in get_empty_cells(grid):
			numEmptyCells = len(get_empty_cells(grid))
			grid[x][y] = 4
			alpha = alpha + prob_4 * 1 / numEmptyCells * expectiminimax(grid, 1, depth - 1,demo)
			grid[x][y] = ''	

	elif player == 1:
		alpha = 0
		
		grid_copy = copy.deepcopy(grid)
		functions['a'](grid_copy)
		if grid_copy != grid:
			alpha = max(alpha, expectiminimax(grid_copy, 0, depth - 1,demo))

		grid_copy = copy.deepcopy(grid)
		functions['d'](grid_copy)
		if grid_copy != grid:
			alpha = max(alpha, expectiminimax(grid_copy, 0, depth - 1,demo))		

		grid_copy = copy.deepcopy(grid)
		functions['w'](grid_copy)
		if grid_copy != grid:
			alpha = max(alpha, expectiminimax(grid_copy, 0, depth - 1,demo))

		grid_copy = copy.deepcopy(grid)
		functions['s'](grid_copy)
		if grid_copy != grid:
			alpha = max(alpha, expectiminimax(grid_copy, 0, depth - 1,demo))

	return alpha

def get_the_max_gird(grid):
	max1 = 0
	for i in range(0,4,1):
		for j in range(0,4,1):
			if grid[i][j] != '':
				temp=grid[i][j]
				if temp > max1:
					max1=temp
	return max1

def score_evaluation_emptyTiles(grid):
	return len(get_empty_cells(grid))

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
				totalScore = totalScore + figureGrid[i][j] 

	return totalScore

def get_next_action(grid,demo):
	maxScore = 0
	action = ''

	height = len(grid)
	width = len(grid[0])

	#depth = 2
	
	if len(get_empty_cells(grid)) > 3:
		depth = 2
	else:
		depth = 4

	grid_copy = copy.deepcopy(grid)
	functions['a'](grid_copy)
	if grid_copy != grid:
		score = expectiminimax(grid_copy, 0, depth,demo)
		if score > maxScore:
			maxScore = score
			action = 'a'

	grid_copy = copy.deepcopy(grid)
	functions['d'](grid_copy)
	if grid_copy != grid:
		score = expectiminimax(grid_copy, 0, depth,demo)
		if score > maxScore:
			maxScore = score
			action = 'd'

	grid_copy = copy.deepcopy(grid)
	functions['w'](grid_copy)
	if grid_copy != grid:
		score = expectiminimax(grid_copy, 0, depth,demo)
		if score > maxScore:
			maxScore = score
			action = 'w'

	grid_copy = copy.deepcopy(grid)
	functions['s'](grid_copy)
	if grid_copy != grid:
		score = expectiminimax(grid_copy, 0, depth,demo)
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
			print ("Which evaluation function do u want demo:")
			get_demo = getch("Demo1=snake,Demo2=emptyTiles+smooth (1/2): ")
			next_action=get_next_action(grid,get_demo)
			if next_action == '':
				print("Checkmate!")
				break
			functions[next_action](grid)
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
				print ("Total score and Max grid:",get_totall_score(grid),get_the_max_gird(grid))
				print("Well played!")
				break
		print_grid(grid)
	
	if get_input == "r":
		print ("Which evaluation function do u want demo:")
		get_demo = getch("Demo1=emptyTiles+smooth,Demo2=snake (1/2): ")
		while True:
			grid_copy = copy.deepcopy(grid)
			next_action = get_next_action(grid,get_demo)

			if next_action == '':
				print("Checkmate!")
				print ("Total score :",get_totall_score(grid))
				print ("Max grid:",get_the_max_gird(grid))
				print_grid(grid)
				break
			functions[next_action](grid)
			if grid != grid_copy:
				if not prepare_next_turn(grid):
					print_grid(grid)
					print ("Total score :",get_totall_score(grid))
					print ("Max grid:",get_the_max_gird(grid,))
					print("Well played!")
					break
			print_grid(grid)			

	if get_input == "m":

		print ("Which evaluation function do u want demo:")
		get_demo = getch("Demo1=emptyTiles+smooth,Demo2=snake (1/2): ")
		x = int(input("How many runs do u want to demo: "))
		
		D1={'256':0 ,'512':0 ,'1024':0 ,'2048':0 ,'4096':0 ,'8192':0 ,'16384':0}
		listTS=[]
		sum1 = 0.0

		for i in range(0,x,1):

			colorama.init()

			grid = get_start_grid(*map(int,sys.argv[1:]))
			print_grid(grid)

			while True:
				grid_copy = copy.deepcopy(grid)
				next_action = get_next_action(grid,get_demo)
				if next_action == '':
					print("Checkmate!")
					print_grid(grid)
					listTS.append([get_totall_score(grid)])
					listTS[i].append(get_the_max_gird(grid))
					break
				
				functions[get_next_action(grid,get_demo)](grid)
				if grid != grid_copy:
					if not prepare_next_turn(grid):
						print_grid(grid)
						print("Well played!")
						listTS.append([get_totall_score(grid)])
						listTS[i].append(get_the_max_gird(grid))
						break
				print_grid(grid)

		for i in range(len(listTS)):
			listTemp =listTS[i]
			sum1 = sum1 + listTemp[0]
			#print (listTemp[1])
			if listTemp[1]== 256:
				D1['256'] = D1['256'] + 1
			elif listTemp[1] == 512:
				D1['512'] = D1['512'] + 1
			elif listTemp[1] == 1024:
				D1['1024'] = D1['1024'] + 1
			elif listTemp[1] == 2048:
				D1['2048'] = D1['2048'] + 1
			elif listTemp[1] == 4096:
				D1['4096'] = D1['4096'] + 1
			elif listTemp[1] == 8192:
				D1['8192'] = D1['8192'] + 1
			elif listTemp[1] == 16384:
				D1['16384'] = D1['16384'] + 1
		print (D1)
		print ("Average score :",(sum1/len(listTS)))
		print ("List=[Total Score,Max Grid]:",listTS)


	print("Thanks for playing.")


if __name__ == "__main__":
	main()

