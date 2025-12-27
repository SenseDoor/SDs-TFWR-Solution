import Config

# === 缓存 ===
# tile_cache: {(x, y): {"entity": ..., "ground": ..., "water": ..., "harvestable": ...}}
tile_cache = {}

# resource_cache: {"wood": n, "hay": n, ...}
resource_cache = {}

def init():
	global tile_cache
	global resource_cache
	tile_cache = {}
	resource_cache = {}

def scan_tile(x, y):
	tile = {
		"x": x,
		"y": y,
		"entity": get_entity_type(),
		"ground": get_ground_type(),
		"water": get_water(),
		"harvestable": can_harvest(),
	}
	tile_cache[(x, y)] = tile
	return tile

def get_tile(x, y):
	if (x, y) in tile_cache:
		return tile_cache[(x, y)]
	return None

def scan_resources():
	global resource_cache
	resource_cache = {
		"wood": num_items(Items.Wood),
		"hay": num_items(Items.Hay),
		"carrot": num_items(Items.Carrot),
		"pumpkin": num_items(Items.Pumpkin),
		"water": num_items(Items.Water),
	}
	return resource_cache

def get_resources():
	if len(resource_cache) == 0:
		return scan_resources()
	return resource_cache

def get_resource(name):
	res = get_resources()
	if name in res:
		return res[name]
	return 0

def is_emergency(name):
	current = get_resource(name)
	margin = Config.SAFE_MARGIN[name]
	return current < margin

def get_emergency_list():
	emergencies = []
	for name in Config.SAFE_MARGIN:
		if is_emergency(name):
			emergencies.append(name)
	return emergencies

def invalidate_tile(x, y):
	if (x, y) in tile_cache:
		tile_cache.pop((x, y))

def invalidate_resources():
	global resource_cache
	resource_cache = {}