import Config
import WorldModel
import ZoneManager
import TimePredictor
import PathOptimizer
import Executor

# === 游戏时间计数（简单递增）===
game_time = 0

def init():
	global game_time
	game_time = 0
	TimePredictor.init()

def tick():
	global game_time
	game_time = game_time + 1

def get_time():
	return game_time

def get_pending_tiles():
	# 获取需要处理的格子列表
	pending = []
	
	for y in range(Config.HEIGHT):
		for x in range(Config.WIDTH):
			# 跳过南瓜区
			if ZoneManager.is_pumpkin_zone(x, y):
				continue
			
			# 检查是否需要处理
			tile = WorldModel.get_tile(x, y)
			if tile == None:
				# 未扫描过，需要处理
				pending.append([x, y, 100])  # 高优先级
				continue
			
			entity = tile[2]
			harvestable = tile[5]
			water = tile[4]
			
			# 可收获
			if harvestable:
				pending.append([x, y, 200])  # 最高优先级
				continue
			
			# 空地
			if entity == None:
				pending.append([x, y, 150])
				continue
			
			# 需要浇水
			if water < Config.MIN_WATER_LEVEL:
				pending.append([x, y, 50])
				continue
			
			# 跳过正在生长的
			if Config.SKIP_GROWING_TILES:
				continue
			
			pending.append([x, y, 10])
	
	return pending

def schedule_sequential():
	# 顺序巡逻（原有逻辑）
	return None  # 返回 None 表示使用默认蛇形遍历

def schedule_priority():
	# 优先级调度
	pending = get_pending_tiles()
	
	if len(pending) == 0:
		return []
	
	# 按优先级排序
	sorted_tiles = PathOptimizer.sort_by_priority(pending, None)
	
	# 取前 N 个高优先级任务
	result = []
	count = min(20, len(sorted_tiles))
	for i in range(count):
		result.append([sorted_tiles[i][0], sorted_tiles[i][1]])
	
	# 路径优化
	return PathOptimizer.plan_route(result)

def schedule_nearest():
	# 最近优先
	pending = get_pending_tiles()
	
	if len(pending) == 0:
		return []
	
	# 提取坐标
	tiles = []
	for p in pending:
		tiles.append([p[0], p[1]])
	
	return PathOptimizer.plan_route(tiles)

def get_schedule():
	if Config.CURRENT_STRATEGY == Config.STRATEGY_SEQUENTIAL:
		return schedule_sequential()
	elif Config.CURRENT_STRATEGY == Config.STRATEGY_PRIORITY:
		return schedule_priority()
	elif Config.CURRENT_STRATEGY == Config.STRATEGY_NEAREST:
		return schedule_nearest()
	
	return None