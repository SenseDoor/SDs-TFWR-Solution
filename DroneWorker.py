import Config
import ZoneManager

# === 独立工作逻辑（不依赖共享缓存）===

def move_to(target_x, target_y):
	"""移动到目标位置（利用边界穿越优化）"""
	current_x = get_pos_x()
	current_y = get_pos_y()

	dx = target_x - current_x
	dy = target_y - current_y

	# X 方向
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

	# Y 方向
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

def process_tile(x, y):
	"""独立处理单个格子（无缓存依赖）"""
	move_to(x, y)

	# 直接读取状态
	entity = get_entity_type()
	water = get_water()
	harvestable = can_harvest()

	# 浇水
	if water < Config.MIN_WATER_LEVEL:
		do_water()

	# 收获
	if harvestable:
		harvest()
		entity = None

	# 种植
	if entity == None:
		plant_entity = decide_plant(x, y)
		if plant_entity != None:
			do_plant(plant_entity)

def decide_plant(x, y):
	"""独立决策种什么"""
	# 检查区域类型
	zone = ZoneManager.get_zone_at(x, y)

	# 仙人掌区和迷宫区由其他逻辑处理
	if zone == Config.ZONE_CACTUS or zone == Config.ZONE_MAZE:
		return None

	# 树位检查（棋盘格模式）
	is_tree_pos = (x + y) % 2 == 0

	# 树专区
	if zone == Config.ZONE_TREE:
		if is_tree_pos:
			return Entities.Tree
		else:
			if num_items(Items.Wood) >= 1:
				return Entities.Carrot
			else:
				return Entities.Grass

	# 胡萝卜专区
	if zone == Config.ZONE_CARROT:
		if num_items(Items.Wood) >= 1:
			return Entities.Carrot
		else:
			return Entities.Grass

	# 草专区
	if zone == Config.ZONE_HAY:
		return Entities.Grass

	# 灵活区：基于位置和资源决策
	if is_tree_pos:
		return Entities.Tree
	else:
		# 有木头种胡萝卜，否则种草
		if num_items(Items.Wood) >= 1:
			return Entities.Carrot
		else:
			return Entities.Grass

def do_water():
	"""独立浇水"""
	margin = Config.SAFE_MARGIN["water"]
	if num_items(Items.Water) <= margin:
		return

	current = get_water()
	if current >= Config.WATER_THRESHOLD:
		return

	while get_water() < Config.WATER_TARGET:
		if num_items(Items.Water) <= margin:
			break
		use_item(Items.Water)

def do_plant(entity):
	"""独立种植"""
	# 需要耕地的作物
	if entity == Entities.Carrot or entity == Entities.Pumpkin or entity == Entities.Sunflower:
		if get_ground_type() == Grounds.Grassland:
			till()

	# 种植前再次检查资源（防止竞态）
	if entity == Entities.Carrot:
		if num_items(Items.Wood) < 1:
			# 资源不足，改种草
			plant(Entities.Grass)
			do_fertilize()
			return

	plant(entity)
	do_fertilize()

def do_fertilize():
	"""施肥"""
	if not Config.FERTILIZER_ENABLED:
		return

	# 检查是否需要继续积累 Weird_Substance
	current = num_items(Items.Weird_Substance)
	if current >= Config.WEIRD_SUBSTANCE_TARGET:
		if not Config.FERTILIZER_AFTER_TARGET:
			return

	margin = Config.FERTILIZER_SAFE_MARGIN
	if num_items(Items.Fertilizer) <= margin:
		return

	# 持续施肥直到成熟
	while num_items(Items.Fertilizer) > margin:
		if can_harvest():
			break
		use_item(Items.Fertilizer)
