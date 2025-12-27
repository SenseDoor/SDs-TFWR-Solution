import Config
import WorldModel

# Items 到资源名映射
ITEM_TO_NAME = {
	Items.Wood: "wood",
	Items.Hay: "hay",
	Items.Carrot: "carrot",
	Items.Pumpkin: "pumpkin",
	Items.Power: "power",
	Items.Gold: "gold",
	Items.Weird_Substance: "weird",
}

# 解锁优先级
UNLOCK_PRIORITY = [
	Unlocks.Speed,
	Unlocks.Watering,
	Unlocks.Expand,
	Unlocks.Plant,
	Unlocks.Sunflowers,
	Unlocks.Trees,
	Unlocks.Carrots,
	Unlocks.Pumpkins,
	Unlocks.Grass,
	Unlocks.Fertilizer,
	Unlocks.Mazes,
]

def get_item_count(item):
	if item == Items.Wood:
		return num_items(Items.Wood)
	elif item == Items.Hay:
		return num_items(Items.Hay)
	elif item == Items.Carrot:
		return num_items(Items.Carrot)
	elif item == Items.Pumpkin:
		return num_items(Items.Pumpkin)
	elif item == Items.Power:
		return num_items(Items.Power)
	elif item == Items.Gold:
		return num_items(Items.Gold)
	elif item == Items.Weird_Substance:
		return num_items(Items.Weird_Substance)
	return 0

def can_afford(cost):
	if cost == None:
		return False
	
	for item in cost:
		needed = cost[item]
		current = get_item_count(item)
		if current < needed:
			return False
	
	return True

def get_missing(cost):
	if cost == None:
		return None
	
	missing = {}
	for item in cost:
		needed = cost[item]
		current = get_item_count(item)
		if current < needed:
			missing[item] = needed - current
	
	if len(missing) == 0:
		return None
	return missing

def try_unlock_one():
	# 尝试解锁优先级最高的可负担项目
	for u in UNLOCK_PRIORITY:
		cost = get_cost(u)
		
		# 跳过已满级
		if cost == None:
			continue
		
		# 跳过无法负担
		if not can_afford(cost):
			continue
		
		# 解锁
		unlock(u)
		WorldModel.invalidate_resources()
		return u
	
	return None

def get_next_target():
	# 获取下一个目标解锁项
	for u in UNLOCK_PRIORITY:
		cost = get_cost(u)
		if cost != None:
			return {
				"unlock": u,
				"cost": cost,
				"missing": get_missing(cost),
				"affordable": can_afford(cost),
			}
	return None

def adjust_priority_for_unlock():
	# 根据下一个解锁目标返回需要优先生产的资源
	target = get_next_target()
	
	if target == None:
		return None
	
	missing = target["missing"]
	if missing == None:
		return None
	
	# 找缺口最大的资源
	max_missing = 0
	priority_item = None
	
	for item in missing:
		if missing[item] > max_missing:
			max_missing = missing[item]
			priority_item = item
	
	if priority_item in ITEM_TO_NAME:
		return ITEM_TO_NAME[priority_item]
	
	return None

def needs_gold():
	# 检查下一个解锁是否需要 Gold
	target = get_next_target()
	if target == None:
		return False
	
	missing = target["missing"]
	if missing == None:
		return False
	
	return Items.Gold in missing

def needs_weird_substance():
	# 检查下一个解锁是否需要 Weird_Substance
	target = get_next_target()
	if target == None:
		return False
	
	missing = target["missing"]
	if missing == None:
		return False
	
	return Items.Weird_Substance in missing