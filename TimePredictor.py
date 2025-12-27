import Config
import WorldModel

# === 生长时间缓存 ===
# {(x, y): {"entity": ..., "plant_time": ..., "ready_time": ...}}
growth_cache = {}

def init():
	global growth_cache
	growth_cache = {}

def get_base_grow_time(entity):
	if entity in Config.GROW_TIME:
		return Config.GROW_TIME[entity]
	return 60

def estimate_grow_time(entity, water_level):
	base_time = get_base_grow_time(entity)
	speed = 1 + 4 * water_level
	return base_time / speed

def record_plant(x, y, entity, current_time):
	water_level = get_water()
	estimated = estimate_grow_time(entity, water_level)
	ready_time = current_time + estimated
	
	growth_cache[(x, y)] = {
		"entity": entity,
		"plant_time": current_time,
		"ready_time": ready_time,
	}

def update_ready_time(x, y, water_level, current_time):
	if (x, y) not in growth_cache:
		return
	
	record = growth_cache[(x, y)]
	remaining = record["ready_time"] - current_time
	
	if remaining <= 0:
		return
	
	new_speed = 1 + 4 * water_level
	new_remaining = remaining / new_speed
	
	growth_cache[(x, y)]["ready_time"] = current_time + new_remaining

def get_ready_time(x, y):
	if (x, y) in growth_cache:
		return growth_cache[(x, y)]["ready_time"]
	return -1

def clear_tile(x, y):
	if (x, y) in growth_cache:
		growth_cache.pop((x, y))

def get_nearly_ready_tiles(current_time, threshold):
	ready = []
	for pos in growth_cache:
		record = growth_cache[pos]
		remaining = record["ready_time"] - current_time
		if remaining <= threshold and remaining > 0:
			ready.append([pos[0], pos[1], remaining])
	return ready

def get_ready_tiles(current_time):
	ready = []
	for pos in growth_cache:
		if growth_cache[pos]["ready_time"] <= current_time:
			ready.append([pos[0], pos[1]])
	return ready