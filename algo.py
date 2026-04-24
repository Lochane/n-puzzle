import numpy as np
import heapq

class A_star:
	def __init__(self):
		content = "3 2 6\n1 4 0\n8 7 5"
		rows = [line.strip() for line in content.strip().splitlines() if line.strip()]
		self.input = np.array([list(map(int, row.split())) for row in rows], dtype=int)
	

	def snake_solution(self, input_len:int):
		grid = [[-1] * input_len for _ in range(input_len)]
		dir =[(0,1), (1,0), (0,-1), (-1,0)]
		dir_index = 0
		row, col = 0, 0

		for value in range(1, input_len*input_len):
			grid[row][col] = value

			next_row = row + dir[dir_index][0]
			next_col = col + dir[dir_index][1]
			
			if (next_row == input_len or next_col == input_len or grid[next_row][next_col] != -1):
				dir_index = (dir_index + 1) % 4

				next_row = row + dir[dir_index][0]
				next_col = col + dir[dir_index][1]

			row, col = next_row, next_col

		grid[row][col] = 0
		return np.asarray(grid)

	def manhattan_distance(self, state: np.ndarray, goal: np.ndarray):
		h = 0
		for row in state:
			for value in row:
				if value != 0:
					pos1 = np.argwhere(state == value)[0] 
					pos2 = np.argwhere(goal == value)[0] 
					h += abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
		return h

	def create_node(self, state: tuple, g: float = float('inf'), h:float = 0.0, parent: dict = None ) -> dict:
		return {
			'state': state,
			'g': g,
			'h': h,
			'f': g + h,
			'parent': parent
		}
	
	def get_valid_neighbors(self, state: np.ndarray):
		pos = np.argwhere(state == 0)[0]
		x, y = pos
		rows, cols = state.shape

		moves = [
			(x+1, y), (x-1, y),
			(x, y+1), (x, y-1)]
		
		neighbors = []
		for nx, ny in moves:
			if 0 <= nx < rows and 0 <= ny < cols:
				new_state = state.copy()
				new_state[x, y], new_state[nx, ny] = new_state[nx, ny], new_state[x, y]
				neighbors.append(new_state)
		return neighbors


	def run(self):
		goal = self.snake_solution(len(self.input))
		state = tuple(self.input.flatten())
		# self.manhattan_distance(self.input, goal)
		start_node = self.create_node(state=self.input, g=0, h=self.manhattan_distance(self.input, goal))
		open_list = [(start_node['f'], state)]
		open_dict = {state: start_node}
		closed_set = set()
		# closed_set.add(tuple(self.input.flatten()))
		while open_list :

			_, current_state = heapq.heappop(open_list)
			current_node = open_dict[current_state]
			if np.array_equal(current_node['state'], goal) is True:
				print("succes")
				return
			
			closed_set.add(current_state)

			for neighbor in self.get_valid_neighbors(current_node['state']):
				if tuple(neighbor.flatten()) in closed_set:
					continue