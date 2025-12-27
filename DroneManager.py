import Config
import ZoneManager

# === 全局无人机句柄列表 ===
active_drones = []

def spawn_worker(task_func):
	"""生成工作无人机，返回句柄"""
	drone = spawn_drone(task_func)
	if drone != None:
		active_drones.append(drone)
	return drone

def wait_all():
	"""等待所有无人机完成"""
	global active_drones
	for drone in active_drones:
		wait_for(drone)
	active_drones = []

def get_available_count():
	"""获取可用无人机数量"""
	return max_drones() - num_drones()

def is_excluded_zone(x, y):
	"""检查是否为排除区域（迷宫、南瓜）"""
	if ZoneManager.is_maze_zone(x, y):
		return True
	# 南瓜区由专用无人机处理
	if Config.PUMPKIN_DRONE_ENABLED:
		if x < Config.PUMPKIN_SIZE and y < Config.PUMPKIN_SIZE:
			return True
	return False

def parallel_patrol(process_func):
	"""按行并行巡逻"""
	total_drones = max_drones()

	# 留一个给主无人机
	worker_count = total_drones - 1

	# 如果还有南瓜无人机，再减一个
	if Config.PUMPKIN_DRONE_ENABLED:
		worker_count = worker_count - 1

	if worker_count <= 0:
		return 0

	# 计算每个无人机负责的行数
	rows_per_drone = Config.HEIGHT // worker_count
	remainder = Config.HEIGHT % worker_count

	current_y = 0
	spawned = 0

	for i in range(worker_count):
		start_y = current_y
		# 分配行数，前 remainder 个无人机多分一行
		row_count = rows_per_drone
		if i < remainder:
			row_count = row_count + 1
		end_y = start_y + row_count
		current_y = end_y

		# 创建闭包捕获变量
		def make_worker(sy, ey):
			def worker():
				patrol_rows(sy, ey, process_func)
			return worker

		drone = spawn_worker(make_worker(start_y, end_y))
		if drone != None:
			spawned = spawned + 1

	return spawned

def patrol_rows(start_y, end_y, process_func):
	"""巡逻指定行范围"""
	for y in range(start_y, end_y):
		for x in range(Config.WIDTH):
			# 跳过排除区域
			if is_excluded_zone(x, y):
				continue
			process_func(x, y)

def for_all_parallel(process_func):
	"""通用并行遍历（利用所有可用无人机）"""
	# 参考游戏文档中的 for_all 模式
	def row_worker(y):
		def worker():
			for x in range(Config.WIDTH):
				if not is_excluded_zone(x, y):
					process_func(x, y)
		return worker

	for y in range(Config.HEIGHT):
		worker = row_worker(y)
		if not spawn_drone(worker):
			# 无可用无人机，主无人机自己执行
			worker()
