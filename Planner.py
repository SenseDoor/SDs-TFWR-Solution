import Config
import WorldModel
import Executor
import ResourceChain
import ZoneManager

def decide_plant_for_tile(x, y):
	if ZoneManager.is_cactus_zone(x, y):
		return None
	
	if ZoneManager.is_maze_zone(x, y):
		return None
	
	if Config.OVERRIDE_PLANT != None:
		return Config.OVERRIDE_PLANT
	
	return ResourceChain.get_best_plant_for_zone(x, y)

def should_replace(current, new_entity):
	if current == None or current == new_entity:
		return current == None
	
	priorities = ResourceChain.get_priority()
	
	current_res = None
	new_res = None
	
	if current in ResourceChain.ENTITY_TO_RESOURCE:
		current_res = ResourceChain.ENTITY_TO_RESOURCE[current]
	if new_entity in ResourceChain.ENTITY_TO_RESOURCE:
		new_res = ResourceChain.ENTITY_TO_RESOURCE[new_entity]
	
	if current_res == None or new_res == None:
		return True
	
	return priorities[new_res] > priorities[current_res]

def generate_tasks_for_tile(x, y):
	if ZoneManager.is_cactus_zone(x, y):
		return
	
	if ZoneManager.is_maze_zone(x, y):
		return
	
	tile = WorldModel.scan_tile(x, y)
	entity = tile["entity"]
	harvestable = tile["harvestable"]
	water = tile["water"]
	
	if water < Config.MIN_WATER_LEVEL:
		Executor.add_task("water", x, y, None)
	
	if harvestable:
		Executor.add_task("harvest", x, y, None)
		plant_entity = decide_plant_for_tile(x, y)
		if plant_entity != None:
			Executor.add_task("plant", x, y, plant_entity)
	
	elif entity == None:
		plant_entity = decide_plant_for_tile(x, y)
		if plant_entity != None:
			Executor.add_task("plant", x, y, plant_entity)
	
	elif entity == Entities.Grass:
		plant_entity = decide_plant_for_tile(x, y)
		if plant_entity != None and should_replace(entity, plant_entity):
			Executor.add_task("harvest", x, y, None)
			Executor.add_task("plant", x, y, plant_entity)