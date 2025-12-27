import Config

# === 南瓜专用无人机 ===
# 独立运行，不阻塞主循环

# 固定 6x6 南瓜区
SIZE = 6
NEEDED_CARROTS = SIZE * SIZE

# 南瓜区起点（固定在左下角）
START_X = 0
START_Y = 0

# 状态缓存
tile_cache = {}

def move_to(target_x, target_y):
	"""移动到目标位置"""
	current_x = get_pos_x()
	current_y = get_pos_y()

	dx = target_x - current_x
	dy = target_y - current_y

	if dx > 0:
		if dx <= Config.WIDTH - dx:
			for _ in range(dx):
				move(East)
		else:
			for _ in range(Config.WIDTH - dx):
				move(West)
	elif dx < 0:
		dx = -dx
		if dx <= Config.WIDTH - dx:
			for _ in range(dx):
				move(West)
		else:
			for _ in range(Config.WIDTH - dx):
				move(East)

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

def has_enough_carrots():
	return num_items(Items.Carrot) >= NEEDED_CARROTS

def clear_cache():
	global tile_cache
	tile_cache = {}

def do_water():
	"""浇水"""
	margin = Config.SAFE_MARGIN["water"]
	if num_items(Items.Water) <= margin:
		return
	if get_water() >= Config.WATER_THRESHOLD:
		return
	while get_water() < Config.WATER_TARGET:
		if num_items(Items.Water) <= margin:
			break
		use_item(Items.Water)

def plant_pumpkin_at():
	"""在当前位置种植南瓜"""
	entity = get_entity_type()
	if entity != Entities.Pumpkin:
		if can_harvest():
			harvest()
		if get_ground_type() == Grounds.Grassland:
			till()
		if num_items(Items.Carrot) >= 1:
			plant(Entities.Pumpkin)
	do_water()

def plant_6x6():
	"""种植 6x6 南瓜"""
	global tile_cache
	tile_cache = {}

	move_to(START_X, START_Y)

	for dy in range(SIZE):
		y = START_Y + dy
		if dy % 2 == 0:
			# 向东
			for dx in range(SIZE):
				x = START_X + dx
				plant_pumpkin_at()
				tile_cache[(x, y)] = "growing"
				if dx < SIZE - 1:
					move(East)
		else:
			# 向西
			for dx in range(SIZE - 1, -1, -1):
				x = START_X + dx
				plant_pumpkin_at()
				tile_cache[(x, y)] = "growing"
				if dx > 0:
					move(West)
		if dy < SIZE - 1:
			move(North)

def scan_and_fix():
	"""扫描并修复，返回是否全部成熟"""
	global tile_cache
	all_ready = True

	for dy in range(SIZE):
		y = START_Y + dy

		# 检查这一行是否全部 ready
		row_all_ready = True
		for dx in range(SIZE):
			x = START_X + dx
			pos = (x, y)
			if pos not in tile_cache or tile_cache[pos] != "ready":
				row_all_ready = False
				break

		if row_all_ready:
			continue

		# 需要检查这一行
		if dy % 2 == 0:
			move_to(START_X, y)
			for dx in range(SIZE):
				x = START_X + dx
				pos = (x, y)

				if pos in tile_cache and tile_cache[pos] == "ready":
					if dx < SIZE - 1:
						move(East)
					continue

				entity = get_entity_type()

				if entity == Entities.Pumpkin and can_harvest():
					tile_cache[pos] = "ready"
				else:
					all_ready = False
					# 修复
					if entity == None or entity != Entities.Pumpkin:
						if can_harvest():
							harvest()
						if get_ground_type() == Grounds.Grassland:
							till()
						if num_items(Items.Carrot) >= 1:
							plant(Entities.Pumpkin)
						do_water()
						tile_cache[pos] = "growing"
					else:
						# 南瓜未熟，补种（可能枯萎）
						if num_items(Items.Carrot) >= 1:
							plant(Entities.Pumpkin)
						do_water()
						tile_cache[pos] = "growing"

				if dx < SIZE - 1:
					move(East)
		else:
			move_to(START_X + SIZE - 1, y)
			for dx in range(SIZE - 1, -1, -1):
				x = START_X + dx
				pos = (x, y)

				if pos in tile_cache and tile_cache[pos] == "ready":
					if dx > 0:
						move(West)
					continue

				entity = get_entity_type()

				if entity == Entities.Pumpkin and can_harvest():
					tile_cache[pos] = "ready"
				else:
					all_ready = False
					if entity == None or entity != Entities.Pumpkin:
						if can_harvest():
							harvest()
						if get_ground_type() == Grounds.Grassland:
							till()
						if num_items(Items.Carrot) >= 1:
							plant(Entities.Pumpkin)
						do_water()
						tile_cache[pos] = "growing"
					else:
						if num_items(Items.Carrot) >= 1:
							plant(Entities.Pumpkin)
						do_water()
						tile_cache[pos] = "growing"

				if dx > 0:
					move(West)

	return all_ready

def harvest_giant():
	"""收获巨型南瓜"""
	move_to(START_X, START_Y)
	harvest()
	clear_cache()

def run():
	"""南瓜无人机入口（无限循环）"""
	while True:
		# 等待胡萝卜足够
		if not has_enough_carrots():
			# 等待一会儿再检查
			for _ in range(20):
				pass  # 空循环消耗时间
			continue

		# 种植 6x6
		plant_6x6()

		# 等待成熟
		while not scan_and_fix():
			pass

		# 收获
		harvest_giant()

def run_once():
	"""执行一轮南瓜种植（非循环版本）"""
	if not has_enough_carrots():
		return False

	plant_6x6()

	while not scan_and_fix():
		pass

	harvest_giant()
	return True
