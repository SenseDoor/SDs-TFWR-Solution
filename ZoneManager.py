import Config

def get_zone_at(x, y):
	if (x, y) in Config.ZONES:
		return Config.ZONES[(x, y)]
	return Config.ZONE_FLEX

def is_maze_zone(x, y):
	return get_zone_at(x, y) == Config.ZONE_MAZE

def is_cactus_zone(x, y):
	return get_zone_at(x, y) == Config.ZONE_CACTUS

def is_tree_zone(x, y):
	return get_zone_at(x, y) == Config.ZONE_TREE

def is_carrot_zone(x, y):
	return get_zone_at(x, y) == Config.ZONE_CARROT

def is_hay_zone(x, y):
	return get_zone_at(x, y) == Config.ZONE_HAY

def is_flex_zone(x, y):
	return get_zone_at(x, y) == Config.ZONE_FLEX

def is_tree_tile(x, y):
	zone = get_zone_at(x, y)
	if zone == Config.ZONE_TREE or zone == Config.ZONE_FLEX:
		return (x + y) % 2 == 0
	return False

def set_zone(x, y, zone_type):
	Config.ZONES[(x, y)] = zone_type

def set_zone_rect(start_x, start_y, width, height, zone_type):
	for dy in range(height):
		for dx in range(width):
			Config.ZONES[(start_x + dx, start_y + dy)] = zone_type

def init_zones():
	# 初始化迷宫区域
	if Config.MAZE_ENABLED:
		set_zone_rect(Config.MAZE_X, Config.MAZE_Y, Config.MAZE_SIZE, Config.MAZE_SIZE, Config.ZONE_MAZE)

init_zones()