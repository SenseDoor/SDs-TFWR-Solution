import Config

def get_distance(x1, y1, x2, y2):
	# 曼哈顿距离
	return abs(x2 - x1) + abs(y2 - y1)

def get_current_pos():
	return [get_pos_x(), get_pos_y()]

def sort_by_distance(tiles):
	# 按距离当前位置排序
	pos = get_current_pos()
	cx = pos[0]
	cy = pos[1]
	
	# 简单冒泡排序（游戏可能没有 sorted）
	n = len(tiles)
	for i in range(n):
		for j in range(i + 1, n):
			dist_i = get_distance(cx, cy, tiles[i][0], tiles[i][1])
			dist_j = get_distance(cx, cy, tiles[j][0], tiles[j][1])
			if dist_j < dist_i:
				temp = tiles[i]
				tiles[i] = tiles[j]
				tiles[j] = temp
	
	return tiles

def sort_by_priority(tiles, priorities):
	# 按优先级排序（优先级高的在前）
	# tiles: [[x, y, priority], ...]
	n = len(tiles)
	for i in range(n):
		for j in range(i + 1, n):
			if tiles[j][2] > tiles[i][2]:
				temp = tiles[i]
				tiles[i] = tiles[j]
				tiles[j] = temp
	
	return tiles

def get_nearest_tile(tiles):
	# 返回最近的格子
	if len(tiles) == 0:
		return None
	
	pos = get_current_pos()
	cx = pos[0]
	cy = pos[1]
	
	nearest = tiles[0]
	nearest_dist = get_distance(cx, cy, nearest[0], nearest[1])
	
	for i in range(1, len(tiles)):
		tile = tiles[i]
		dist = get_distance(cx, cy, tile[0], tile[1])
		if dist < nearest_dist:
			nearest = tile
			nearest_dist = dist
	
	return nearest

def plan_route(tiles):
	# 贪心算法规划路径：每次选最近的
	if len(tiles) == 0:
		return []
	
	route = []
	remaining = []
	
	for t in tiles:
		remaining.append([t[0], t[1]])
	
	# 从当前位置开始
	pos = get_current_pos()
	current_x = pos[0]
	current_y = pos[1]
	
	while len(remaining) > 0:
		# 找最近的
		nearest_idx = 0
		nearest_dist = get_distance(current_x, current_y, remaining[0][0], remaining[0][1])
		
		for i in range(1, len(remaining)):
			dist = get_distance(current_x, current_y, remaining[i][0], remaining[i][1])
			if dist < nearest_dist:
				nearest_dist = dist
				nearest_idx = i
		
		nearest = remaining[nearest_idx]
		route.append(nearest)
		current_x = nearest[0]
		current_y = nearest[1]
		remaining.pop(nearest_idx)
	
	return route