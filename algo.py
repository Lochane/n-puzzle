import numpy as np
import heapq

class A_star:
	def __init__(self, input=None, N=0):

		if input is None:
			content = "3 2 6\n1 4 0\n8 7 5\n"
			rows = [line.strip() for line in content.strip().splitlines() if line.strip()]
			self.input = np.array([list(map(int, row.split())) for row in rows], dtype=int)
		else:
			self.input = input
		self.N = len(self.input)

	def snake_solution(self, input_len:int):
		grid = [[-1] * self.N for _ in range(self.N)]
		dir =[(0,1), (1,0), (0,-1), (-1,0)]
		dir_index = 0
		row, col = 0, 0

		for value in range(1, self.N * self.N):
			grid[row][col] = value

			next_row = row + dir[dir_index][0]
			next_col = col + dir[dir_index][1]
			
			if (next_row == self.N or next_col == self.N or grid[next_row][next_col] != -1):
				dir_index = (dir_index + 1) % 4

				next_row = row + dir[dir_index][0]
				next_col = col + dir[dir_index][1]

			row, col = next_row, next_col

		grid[row][col] = 0
		return np.asarray(grid)

	def manhattan_distance(self, state: np.ndarray, goal_pos: dict):
		h = 0
		for i, row in enumerate(state):
			for j, value in enumerate(row):
				if value != 0:
					goal_i, goal_j = goal_pos[value]
					h += abs(i - goal_i) + abs(j - goal_j)
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
				if (arr[i] > arr[j]):
					count += 1
		return count


	def is_solvable(self, init_state, goal):
		goal_index = {}
		init_index = init_state.flatten().copy()
		N = len(init_index)
		for i in range(0, N):
			goal_index[goal.flatten()[i]] = i
		for i in range(0, N):
			init_index[i] = goal_index.get(init_index[i])

		inv_count = self.get_inv_count(init_index, N)
		blank_init_x, blank_init_y  = np.argwhere(init_state == 0)[0]
		blank_goal_x, blank_goal_y  = np.argwhere(goal == 0)[0]
		manhattan_blank = abs(blank_init_x - blank_goal_x) + abs(blank_init_y - blank_goal_y)
		return (inv_count + manhattan_blank) % 2 == 0


	def reconstruct_path(self, goal_node):
		path = []
		current = goal_node

		while current is not None:
			path.append(current['state'])
			current = current['parent']
		
		return path[::-1]

	def pos_dict(self, arr:np.ndarray):
		pos = {}
		for i, row in enumerate(arr):
			for j, value in enumerate(row):
				pos[value] = i , j
		return pos

	def run(self):
		goal = self.snake_solution(self.N)
		state = tuple(self.input.flatten())
		if self.is_solvable(self.input, goal) != True:
			print("Puzzle not solvable.")
			return
		goal_pos = self.pos_dict(goal)
		start_node = self.create_node(state=self.input, g=0, h=self.manhattan_distance(self.input, goal_pos))
		open_list = [(start_node['f'], state)]
		open_dict = {state: start_node}
		closed_set = set()
		
		count_node = 1
		max_node = 1
		current_size = 0
		
		while open_list:
			_, current_state = heapq.heappop(open_list)
			if current_state in closed_set:
				continue
			current_node = open_dict[current_state]
			if np.array_equal(current_node['state'], goal) is True:
				print("succes")
				path = self.reconstruct_path(current_node)
				return {'count_node': count_node,'max_node': max_node,'nb_moves': len(path) - 1 ,'path': path, }
			
			closed_set.add(current_state)

			for neighbor_node in self.get_valid_neighbors(current_node['state']):
				neighbor_tuple = tuple(neighbor_node.flatten())
				if neighbor_tuple in closed_set:
					continue
				heuristic = self.manhattan_distance(neighbor_node, goal_pos)
				cost = current_node['g'] + 1

				if neighbor_tuple not in open_dict:
					neighbor = self.create_node(state=neighbor_node, g=cost, h=heuristic, parent=current_node)
					heapq.heappush(open_list, (neighbor['f'], neighbor_tuple))
					open_dict[neighbor_tuple] = neighbor
					
					count_node += 1
					current_size = len(closed_set) + len(open_dict)
					if current_size > max_node:
						max_node = current_size
				
				elif cost < open_dict[neighbor_tuple]['g']:
					neighbor = open_dict[neighbor_tuple]
					neighbor['g'] = cost
					neighbor['f'] = cost + neighbor['h']
					neighbor['parent'] = current_node
					heapq.heappush(open_list,((neighbor['f'], neighbor_tuple)))
		return