import Config
import WorldModel
import TimePredictor

# === 任务队列 ===
task_queue = []
game_time = 0

def init():
	global task_queue
	global game_time
	task_queue = []
	game_time = 0

def tick():
	global game_time
	game_time = game_time + 1

def get_time():
	return game_time

def clear_queue():
	global task_queue
	task_queue = []

def add_task(task_type, x, y, entity):
	task_queue.append({
		"type": task_type,
		"x": x,
		"y": y,
		"entity": entity,
	})

def has_tasks():
	return len(task_queue) > 0

def next_task():
	if len(task_queue) > 0:
		return task_queue.pop(0)
	return None

# === 移动 ===
def move_to(target_x, target_y):
	# 利用边界穿越优化
	current_x = get_pos_x()
	current_y = get_pos_y()
	
	dx = target_x - current_x
	dy = target_y - current_y
	
	# X 方向：选择更短的路径（直接或穿越）
	if dx > 0:
		# 向东：比较直接走 vs 向西穿越
		if dx <= Config.WIDTH - dx:
			for _ in range(dx):
				move(East)
		else:
			for _ in range(Config.WIDTH - dx):
				move(West)
	elif dx < 0:
		# 向西：比较直接走 vs 向东穿越
		dx = -dx
		if dx <= Config.WIDTH - dx:
			for _ in range(dx):
				move(West)
		else:
			for _ in range(Config.WIDTH - dx):
				move(East)
	
	# Y 方向：同理
	if dy > 0:
		if dy <= Config.HEIGHT - dy:
			for _ in range(dy):
				move(North)
		else:
			for _ in range(Config.HEIGHT - dy):
				move(South)
	elif dy < 0:
		dy = -dy
		if dy <= Config.HEIGHT - dy:
			for _ in range(dy):
				move(South)
		else:
			for _ in range(Config.HEIGHT - dy):
				move(North)

def snake_traverse(callback):
	# 优化版：利用边界穿越
	# 单向遍历，每行向东，到边界自动穿越
	for y in range(Config.HEIGHT):
		for x in range(Config.WIDTH):
			# 移动到目标位置
			move_to(x, y)
			callback(x, y)

def linear_traverse(callback):
	# 最简单的线性遍历
	# 利用穿越特性，每行都向东走
	for y in range(Config.HEIGHT):
		# 移动到行首（利用穿越）
		move_to(0, y)
		
		for x in range(Config.WIDTH):
			callback(x, y)
			if x < Config.WIDTH - 1:
				move(East)

def spiral_traverse(callback):
	# 螺旋遍历（从外向内）
	visited = {}
	x = 0
	y = 0
	direction = 0  # 0:East, 1:North, 2:West, 3:South
	
	dirs = {
		0: (1, 0, East),
		1: (0, 1, North),
		2: (-1, 0, West),
		3: (0, -1, South),
	}
	
	for _ in range(Config.WIDTH * Config.HEIGHT):
		move_to(x, y)
		callback(x, y)
		visited[(x, y)] = True
		
		# 尝试继续当前方向
		dx, dy, dir_move = dirs[direction]
		next_x = (x + dx) % Config.WIDTH
		next_y = (y + dy) % Config.HEIGHT
		
		if (next_x, next_y) in visited:
			# 转向
			direction = (direction + 1) % 4
			dx, dy, dir_move = dirs[direction]
			next_x = (x + dx) % Config.WIDTH
			next_y = (y + dy) % Config.HEIGHT
		
		x = next_x
		y = next_y

# === 基础操作 ===
def do_harvest():
	if can_harvest():
		harvest()
		x = get_pos_x()
		y = get_pos_y()
		WorldModel.invalidate_resources()
		TimePredictor.clear_tile(x, y)
		return True
	return False

def do_till():
	if get_ground_type() == Grounds.Grassland:
		till()
		WorldModel.invalidate_tile(get_pos_x(), get_pos_y())
		return True
	return False

def do_plant(entity):
	if entity == Entities.Carrot or entity == Entities.Pumpkin or entity == Entities.Sunflower:
		do_till()
	
	plant(entity)
	
	x = get_pos_x()
	y = get_pos_y()
	WorldModel.invalidate_tile(x, y)
	WorldModel.invalidate_resources()
	TimePredictor.record_plant(x, y, entity, get_time())
	do_fertilize()

def do_water():
	water = num_items(Items.Water)
	current = get_water()
	margin = Config.SAFE_MARGIN["water"]
	
	if current >= Config.MIN_WATER_LEVEL:
		return
	
	if water > margin and current < Config.WATER_THRESHOLD:
		while get_water() < Config.WATER_TARGET:
			if num_items(Items.Water) <= margin:
				break
			use_item(Items.Water)
		
		x = get_pos_x()
		y = get_pos_y()
		WorldModel.invalidate_tile(x, y)
		WorldModel.invalidate_resources()
		TimePredictor.update_ready_time(x, y, get_water(), get_time())

# === 任务执行 ===
def execute_task(task):
	move_to(task["x"], task["y"])
	tick()
	
	if task["type"] == "harvest":
		return do_harvest()
	elif task["type"] == "plant":
		if task["entity"] != None:
			do_plant(task["entity"])
			return True
	elif task["type"] == "water":
		do_water()
		return True
	elif task["type"] == "scan":
		WorldModel.scan_tile(task["x"], task["y"])
		return True
	
	return False

def execute_all():
	while has_tasks():
		task = next_task()
		if task != None:
			execute_task(task)
			
# Executor.py 新增
def should_fertilize():
	# 未达标时积极用肥料
	current = num_items(Items.Weird_Substance)
	if current < Config.WEIRD_SUBSTANCE_TARGET:
		return True
	# 达标后看配置
	return Config.FERTILIZER_AFTER_TARGET

def do_fertilize():
	if not Config.FERTILIZER_ENABLED:
		return
	if not should_fertilize():
		return
	if num_items(Items.Fertilizer) <= Config.FERTILIZER_SAFE_MARGIN:
		return
	
	# 持续施肥直到即将成熟
	while num_items(Items.Fertilizer) > Config.FERTILIZER_SAFE_MARGIN:
		if can_harvest():
			break
		use_item(Items.Fertilizer)