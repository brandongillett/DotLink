import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Dot Link")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)


class Node:  # keeps track of color and location or all the nodes on the grid

	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		# finds the location of the node by finding the row or column
		# Then multiplies the width example: width = 800/50 = 16
		self.x = row * width
		self.y = col * width
		# makes all nodes white
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		# calls row first(x) then calls column(y)
		return self.row, self.col

	# Looks to see if the node is closed
	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	# looks to see if the node is blocked
	def is_blocked(self):
		return self.color == BLACK

	# looks for starting node
	def is_start(self):
		return self.color == ORANGE

	# looks for goal node
	def is_goal(self):
		return self.color == ORANGE

	# clears all nodes
	def restart(self):
		self.color = WHITE

	# makes the start node ORANGE
	def make_start(self):
		self.color = ORANGE

	# makes the closed nodes RED
	def make_closed(self):
		self.color = RED

	# makes the open nodes GREEN
	def make_open(self):
		self.color = GREEN

	# makes blocked nodes black
	def make_blocked(self):
		self.color = BLACK

	# makes the goal node ORANGE
	def make_goal(self):
		self.color = ORANGE

	# makes the path to the start node and the goal node PURPLE
	def make_path(self):
		self.color = PURPLE

	def draw(self, window):
		pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		# creates neighbors list
		self.neighbors = []
		# checks to if the neighbor is a barrier if not then will move down a row down
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_blocked():  # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])
		# checks to if the neighbor is a barrier if not then will move down a row up
		if self.row > 0 and not grid[self.row - 1][self.col].is_blocked():  # UP
			self.neighbors.append(grid[self.row - 1][self.col])
		# checks to if the neighbor is a barrier if not then will move one column to the right
		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_blocked():  # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])
		# checks to if the neighbor is a barrier if not then will move one column to the left
		if self.col > 0 and not grid[self.row][self.col - 1].is_blocked():  # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False


# Heuristic : Manhattan Distance USED
def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	# while the current node is in the came_from list draw the path until it reaches the start node then stop.
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def aStar(draw, grid, start, goal):
	count = 0  # keeps track of the order of the queue in order to tiebreak nodes with the same F score
	open_set = PriorityQueue()
	open_set.put((0, count, start))  # adds start node to the priority queue with F score = 0
	came_from = {}  # keeps track from which node a came from
	g_score = {node: float("inf") for row in grid for node in row}  # g_score is first set to infinity
	g_score[start] = 0  # g score = 0
	f_score = {node: float("inf") for row in grid for node in row}  # f_score is first set to infinity
	f_score[start] = h(start.get_pos(), goal.get_pos())  # f score is the heuristic of the start and goal position

	open_set_hash = {start}  # allows us to keep track of the items in and out of the priority queue

	while not open_set.empty():  # allows to exit the algorithm loop if somthing goes wrong or is taking too long.
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]  # Gets the current node we are looking at.
		open_set_hash.remove(current)  # removes current node from the hash that was removed from the PQ

		if current == goal:  # if a path is found then it constructs the path.
			reconstruct_path(came_from, goal, draw)
			goal.make_goal()
			return True

		for neighbor in current.neighbors: # gets the g score from the neighbor node
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]: # if g score is less than neighbor then update the path.
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score # neighbor g score is equal to temp g score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), goal.get_pos())  # fscore = new gscore + heuristic
				if neighbor not in open_set_hash: # if the neighbor is not in the hash then add it into the hash
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()  # makes the neighbor open

		draw()

		if current != start: # if the node that was considered is not the start not then make it closed.
			current.make_closed()

	return False


# To make grid ask how many rows there will be and what is the desired width
def make_grid(rows, width):
	grid = []
	# gap gives width of each cube on the grid.
	gap = width // rows
	# creates a list to store all the nodes.
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			node = Node(i, j, gap, rows)
			grid[i].append(node)

	return grid


def draw_grid(window, rows, width):
	gap = width // rows
	# Draws the horizontal lines for the grid
	for i in range(rows):
		pygame.draw.line(window, GREY, (0, i * gap), (width, i * gap))
		# draws the vertical lines for the grid
		for j in range(rows):
			# coordinates are always on the top and bottom when drawing the vert lines
			pygame.draw.line(window, GREY, (j * gap, 0), (j * gap, width))


def draw(window, grid, rows, width):
	window.fill(WHITE)
	# draws all nodes in the grid list
	for row in grid:
		for node in row:
			node.draw(window)

	draw_grid(window, rows, width)
	# updates the display
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos
	# Gets the position of the x and y and then divides it by the width of the node
	row = y // gap
	col = x // gap
	# gets the row and column that was clicked on
	return row, col


def main(window, width):
	ROWS = 50
	grid = make_grid(ROWS, width)

	start = None
	goal = None

	run = True
	while run:
		draw(window, grid, ROWS, width)
		for event in pygame.event.get():
			# if the close button is hit on the program then close the program
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: # Left mouse button
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				node = grid[row][col]

				# if start node hasn't been selected makes the user select a start
				if not start and node != goal:
					start = node
					start.make_start()

				# if goal node hasn't been selected makes the user select a goal
				elif not goal and node != start:
					goal = node
					goal.make_goal()
				# if node isn't start or goal then be able to block nodes.
				elif node != goal and node != start:
					node.make_blocked()

			elif pygame.mouse.get_pressed()[2]: # Right mouse button
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				node = grid[row][col]
				node.restart()
				# clicking right mouse button on the start and goal node will remove them
				if node == start:
					start = None
				elif node == goal:
					goal = None

			# if space bar key is hit and start and goal nodes are selected then update all neighbors in the row
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and goal:
					for row in grid:
						for node in row:
							node.update_neighbors(grid)
					# A star algo begins
					aStar(lambda: draw(window, grid, ROWS, width), grid, start, goal)

				if event.key == pygame.K_c: # if the button C is pressed then clear the entire grid.
					start = None
					goal = None
					grid = make_grid(ROWS, width)

	pygame.quit()


main(WINDOW, WIDTH)
