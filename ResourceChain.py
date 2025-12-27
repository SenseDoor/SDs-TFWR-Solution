import Config
import WorldModel
import ZoneManager
import UnlockManager

# 资源到作物映射
RESOURCE_TO_ENTITY = {
	"wood": Entities.Tree,
	"hay": Entities.Grass,
	"carrot": Entities.Carrot,
	"pumpkin": Entities.Pumpkin,
}

ENTITY_TO_RESOURCE = {
	Entities.Tree: "wood",
	Entities.Grass: "hay",
	Entities.Carrot: "carrot",
	Entities.Pumpkin: "pumpkin",
}

# 依赖关系
DEPENDENCIES = {
	"wood": (None, 0),
	"hay": (None, 0),
	"carrot": ("wood", 1),
	"pumpkin": ("carrot", 1),
}

def get_dependency(resource):
	if resource in DEPENDENCIES:
		return DEPENDENCIES[resource]
	return (None, 0)

def can_produce(resource):
	dep = get_dependency(resource)
	if dep[0] == None:
		return True
	
	required = dep[0]
	amount = dep[1]
	current = WorldModel.get_resource(required)
	
	return current >= amount

def get_deficit():
	res = WorldModel.get_resources()
	
	total = res["wood"] + res["hay"] + res["carrot"] + res["pumpkin"]
	if total == 0:
		total = 1
	
	ratio_total = 0
	for r in Config.TARGET_RATIO:
		ratio_total = ratio_total + Config.TARGET_RATIO[r]
	
	if ratio_total == 0:
		ratio_total = 1
	
	deficits = {}
	for r in Config.TARGET_RATIO:
		target = Config.TARGET_RATIO[r] / ratio_total
		current = res[r] / total
		deficits[r] = target - current
	
	return deficits

def get_priority():
	deficits = get_deficit()
	priorities = {}
	
	for r in deficits:
		priorities[r] = deficits[r]
	
	# 依赖链传播
	if "pumpkin" in priorities and priorities["pumpkin"] > 0:
		carrot_needed = priorities["pumpkin"] * 0.5
		priorities["carrot"] = max(priorities["carrot"], carrot_needed)
	
	if "carrot" in priorities and priorities["carrot"] > 0:
		wood_needed = priorities["carrot"] * 0.5
		priorities["wood"] = max(priorities["wood"], wood_needed)
	
	# 紧急模式
	emergencies = WorldModel.get_emergency_list()
	for e in emergencies:
		if e in priorities:
			priorities[e] = priorities[e] + 10
	
	# 解锁目标加成
	if Config.AUTO_UNLOCK:
		unlock_priority = UnlockManager.adjust_priority_for_unlock()
		if unlock_priority != None and unlock_priority in priorities:
			priorities[unlock_priority] = priorities[unlock_priority] + 5
	
	return priorities

def get_highest_priority():
	priorities = get_priority()
	
	highest = "hay"
	highest_val = -999
	
	for r in priorities:
		if priorities[r] > highest_val:
			highest_val = priorities[r]
			highest = r
	
	return highest

def get_best_plant_for_zone(x, y):
	zone = ZoneManager.get_zone_at(x, y)
	res = WorldModel.get_resources()
	priorities = get_priority()
	
	# 仙人掌区由 CactusZone 管理
	if zone == Config.ZONE_CACTUS:
		return None
	
	# 树专区
	if zone == Config.ZONE_TREE:
		if ZoneManager.is_tree_tile(x, y):
			return Entities.Tree
		else:
			if priorities["carrot"] >= priorities["hay"] and res["wood"] >= 1:
				return Entities.Carrot
			else:
				return Entities.Grass
	
	# 胡萝卜专区
	if zone == Config.ZONE_CARROT:
		if res["wood"] >= 1:
			return Entities.Carrot
		else:
			return Entities.Grass
	
	# 草专区
	if zone == Config.ZONE_HAY:
		return Entities.Grass
	
	# 灵活区
	return get_best_plant_flex(x, y)

def get_best_plant_flex(x, y):
	priorities = get_priority()
	res = WorldModel.get_resources()
	is_tree_pos = ZoneManager.is_tree_tile(x, y)
	
	# 候选作物
	candidates = {}
	candidates["wood"] = is_tree_pos
	candidates["hay"] = True
	candidates["carrot"] = (not is_tree_pos) and (res["wood"] >= 1)
	
	# 找优先级最高且可种植的
	best = None
	best_priority = -999
	
	for r in candidates:
		if candidates[r] and priorities[r] > best_priority:
			best_priority = priorities[r]
			best = r
	
	# 兜底
	if best == None:
		if is_tree_pos:
			best = "wood"
		else:
			best = "hay"
	
	return RESOURCE_TO_ENTITY[best]