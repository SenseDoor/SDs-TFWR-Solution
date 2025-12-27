import Config
import WorldModel
import Executor

# 南瓜固定 6x6
SIZE = 6
NEEDED_CARROTS = SIZE * SIZE

# 当前种植区域起点
current_start_x = 0
current_start_y = 0

# 状态缓存 {(x,y): "ready" / "growing"}
tile_cache = {}

def is_enabled():
	return Config.PUMPKIN_ENABLED

def has_enough_carrots():
	return num_items(Items.Carrot) >= NEEDED_CARROTS

def clear_cache():
	global tile_cache
	tile_cache = {}

def set_start_position(x, y):
	global current_start_x
	global current_start_y
	
	if x + SIZE > Config.WIDTH:
		x = Config.WIDTH - SIZE
	if y + SIZE > Config.HEIGHT:
		y = Config.HEIGHT - SIZE
	if x < 0:
		x = 0
	if y < 0:
		y = 0
	
	current_start_x = x
	current_start_y = y

def plant_6x6():
	# 种植 6x6 南瓜
	global tile_cache
	tile_cache = {}
	
	sx = current_start_x
	sy = current_start_y
	
	Executor.move_to(sx, sy)
	
	for dy in range(SIZE):
		y = sy + dy
		if dy % 2 == 0:
			for dx in range(SIZE):
				x = sx + dx
				entity = get_entity_type()
				if entity != Entities.Pumpkin:
					if can_harvest():
						harvest()
					Executor.do_till()
					if num_items(Items.Carrot) >= 1:
						plant(Entities.Pumpkin)
				Executor.do_water()
				tile_cache[(x, y)] = "growing"
				if dx < SIZE - 1:
					move(East)
		else:
			for dx in range(SIZE - 1, -1, -1):
				x = sx + dx
				entity = get_entity_type()
				if entity != Entities.Pumpkin:
					if can_harvest():
						harvest()
					Executor.do_till()
					if num_items(Items.Carrot) >= 1:
						plant(Entities.Pumpkin)
				Executor.do_water()
				tile_cache[(x, y)] = "growing"
				if dx > 0:
					move(West)
		if dy < SIZE - 1:
			move(North)

def scan_and_fix():
	# 扫描 + 即时修复，返回是否全部成熟
	sx = current_start_x
	sy = current_start_y
	all_ready = True
	
	for dy in range(SIZE):
		y = sy + dy
		
		# 跳过整行已 ready 的
		row_all_ready = True
		for dx in range(SIZE):
			x = sx + dx
			pos = (x, y)
			if pos not in tile_cache or tile_cache[pos] != "ready":
				row_all_ready = False
				break
		
		if row_all_ready:
			continue
		
		# 需要检查这一行
		if dy % 2 == 0:
			Executor.move_to(sx, y)
			for dx in range(SIZE):
				x = sx + dx
				pos = (x, y)
				
				# 已 ready 跳过
				if pos in tile_cache and tile_cache[pos] == "ready":
					if dx < SIZE - 1:
						move(East)
					continue
				
				# 检查并修复
				entity = get_entity_type()
				
				if entity == Entities.Pumpkin and can_harvest():
					tile_cache[pos] = "ready"
				else:
					all_ready = False
					# 即时修复
					if entity == None:
						Executor.do_till()
						if num_items(Items.Carrot) >= 1:
							plant(Entities.Pumpkin)
						Executor.do_water()
						tile_cache[pos] = "growing"
					elif entity != Entities.Pumpkin:
						if can_harvest():
							harvest()
						Executor.do_till()
						if num_items(Items.Carrot) >= 1:
							plant(Entities.Pumpkin)
						Executor.do_water()
						tile_cache[pos] = "growing"
					else:
						# 南瓜未熟，可能枯萎
						if num_items(Items.Carrot) >= 1:
							plant(Entities.Pumpkin)
						Executor.do_water()
						tile_cache[pos] = "growing"
				
				if dx < SIZE - 1:
					move(East)
		else:
			Executor.move_to(sx + SIZE - 1, y)
			for dx in range(SIZE - 1, -1, -1):
				x = sx + dx
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
					if entity == None:
						Executor.do_till()
						if num_items(Items.Carrot) >= 1:
							plant(Entities.Pumpkin)
						Executor.do_water()
						tile_cache[pos] = "growing"
					elif entity != Entities.Pumpkin:
						if can_harvest():
							harvest()
						Executor.do_till()
						if num_items(Items.Carrot) >= 1:
							plant(Entities.Pumpkin)
						Executor.do_water()
						tile_cache[pos] = "growing"
					else:
						if num_items(Items.Carrot) >= 1:
							plant(Entities.Pumpkin)
						Executor.do_water()
						tile_cache[pos] = "growing"
				
				if dx > 0:
					move(West)
	
	return all_ready

def harvest_giant():
	Executor.move_to(current_start_x, current_start_y)
	harvest()
	WorldModel.invalidate_resources()
	clear_cache()

def farm():
	if not is_enabled():
		return
	
	if not has_enough_carrots():
		return
	
	# 固定起点
	set_start_position(0, 0)
	
	# 种植
	plant_6x6()
	
	# 扫描即修复，直到全部成熟
	while not scan_and_fix():
		pass
	
	# 收获
	harvest_giant()