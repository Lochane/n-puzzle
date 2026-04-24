import numpy as np
import heapq

class A_star:
	def __init__(self, input=None):

		if input is None:
			content = "0 10 5 7\n11 14 4 8\n1 2 6 13\n12 3 15 9"
			rows = [line.strip() for line in content.strip().splitlines() if line.strip()]
			self.input = np.array([list(map(int, row.split())) for row in rows], dtype=int)
		else:
			self.input = input

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
	
	def get_inv_count(self, arr, N):
		count = 0
		for i in range(0, N):
			for j in range(i + 1, N):
				if (arr[j] and arr[i] and arr[i] > arr[j]):
					count += 1
		return count


	def is_solvable(self, init_state, goal):
		goal_index = {}
		init_index = init_state.copy()
		N = len(init_state)
		for i in range(0, N):
			goal_index[goal[i]] = i
		
		for i in range(0, N):
			init_index[i] = goal_index.get(init_state[i])
		
		inv_count = self.get_inv_count(init_index, N)
		if (N & 1):
			return not (inv_count & 1)
		
		else:
			blank_pos = np.argwhere(self.input == 0)[0]
			row, _ = blank_pos
			blank_pos_bot = ((len(self.input)) - row)

			if (blank_pos_bot & 1):
				return not (inv_count & 1)
			else:
				return bool(inv_count & 1)

	def run(self):
		goal = self.snake_solution(len(self.input))
		state = tuple(self.input.flatten())
		if self.is_solvable(self.input.flatten(), goal.flatten()) != True:
			print("Puzzle not solvable.")
			exit(0)
		start_node = self.create_node(state=self.input, g=0, h=self.manhattan_distance(self.input, goal))
		open_list = [(start_node['f'], state)]
		open_dict = {state: start_node}
		closed_set = set()
		while open_list :

			_, current_state = heapq.heappop(open_list)
			current_node = open_dict[current_state]
			if np.array_equal(current_node['state'], goal) is True:
				print("succes")
				return
			
			closed_set.add(current_state)

			for neighbor_node in self.get_valid_neighbors(current_node['state']):
				neighbor_tuple = tuple(neighbor_node.flatten())
				if neighbor_tuple in closed_set:
					continue
				heuristic = self.manhattan_distance(neighbor_node, goal)
				cost = current_node['g'] + 1

				if neighbor_tuple not in open_dict:
					neighbor = self.create_node(state=neighbor_node, g=cost, h=heuristic, parent=current_node)
					heapq.heappush(open_list, (neighbor['f'], neighbor_tuple))
					open_dict[neighbor_tuple] = neighbor
				
				elif cost < open_dict[neighbor_tuple]['g']:
					neighbor = open_dict[neighbor_tuple]
					neighbor['g'] = cost
					neighbor['f'] = cost + neighbor['h']
					neighbor['parent'] = current_node
		print('not succes')
		return