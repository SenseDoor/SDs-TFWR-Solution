import Config
import WorldModel
import Executor

def is_enabled():
	return Config.MAZE_ENABLED

def get_substance_needed():
	# 根据升级等级计算所需 Weird_Substance
	level = num_unlocked(Unlocks.Mazes)
	if level == 0:
		return 0  # 未解锁
	multiplier = 2 ** (level - 1)
	return Config.MAZE_SIZE * multiplier

def can_generate():
	if not is_enabled():
		return False
	
	needed = get_substance_needed()
	if needed == 0:
		return False
	
	current = num_items(Items.Weird_Substance)
	return current >= needed + Config.MAZE_SUBSTANCE_MARGIN

def generate():
	# 移动到迷宫起点
	Executor.move_to(Config.MAZE_X, Config.MAZE_Y)
	
	# 种植灌木
	if get_entity_type() != None:
		if can_harvest():
			harvest()
	plant(Entities.Bush)
	
	# 使用 Weird_Substance 生成迷宫
	amount = get_substance_needed()
	use_item(Items.Weird_Substance, amount)

def solve():
	# 简单寻路：目标导向 + 回溯
	# measure() 返回宝藏坐标
	
	visited = {}
	path = []
	
	while get_entity_type() != Entities.Treasure:
		x = get_pos_x()
		y = get_pos_y()
		visited[(x, y)] = True
		
		# 获取宝藏位置
		target = measure()
		tx = target[0]
		ty = target[1]
		
		# 计算优先方向
		dirs = []
		if tx > x:
			dirs.append(East)
		if tx < x:
			dirs.append(West)
		if ty > y:
			dirs.append(North)
		if ty < y:
			dirs.append(South)
		
		# 补充其他方向
		for d in [North, East, South, West]:
			if d not in dirs:
				dirs.append(d)
		
		# 尝试移动
		moved = False
		for d in dirs:
			# 计算目标位置
			nx = x
			ny = y
			if d == North:
				ny = y + 1
			elif d == South:
				ny = y - 1
			elif d == East:
				nx = x + 1
			elif d == West:
				nx = x - 1
			
			# 跳过已访问
			if (nx, ny) in visited:
				continue
			
			# 尝试移动
			if move(d):
				path.append(d)
				moved = True
				break
		
		# 无路可走，回溯
		if not moved:
			if len(path) == 0:
				break  # 无解
			
			# 回退一步
			last = path.pop()
			if last == North:
				move(South)
			elif last == South:
				move(North)
			elif last == East:
				move(West)
			elif last == West:
				move(East)

def harvest_treasure():
	harvest()
	WorldModel.invalidate_resources()

def farm():
	if not is_enabled():
		return
	
	if not can_generate():
		return
	
	# 生成迷宫
	generate()
	
	# 寻路
	solve()
	
	# 收获
	harvest_treasure()