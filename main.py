import Config
import WorldModel
import Executor
import MazeZone
import UnlockManager
import ZoneManager
import DroneManager
import DroneWorker
import PumpkinDrone

# === 主无人机巡逻区域 ===
main_drone_start_y = 0
main_drone_end_y = 0

def init():
	"""初始化"""
	WorldModel.init()
	Executor.init()
	ZoneManager.init_zones()

def process_tile_main(x, y):
	"""主无人机处理格子（使用 DroneWorker 逻辑）"""
	DroneWorker.process_tile(x, y)

def patrol_main_region():
	"""主无人机巡逻自己负责的区域"""
	for y in range(main_drone_start_y, main_drone_end_y):
		for x in range(Config.WIDTH):
			if DroneManager.is_excluded_zone(x, y):
				continue
			process_tile_main(x, y)

def calculate_main_region(total_workers):
	"""计算主无人机负责的区域"""
	global main_drone_start_y, main_drone_end_y

	if total_workers <= 0:
		# 主无人机负责全部
		main_drone_start_y = 0
		main_drone_end_y = Config.HEIGHT
		return

	rows_per_drone = Config.HEIGHT // (total_workers + 1)
	remainder = Config.HEIGHT % (total_workers + 1)

	# 主无人机负责最后一部分
	main_drone_start_y = total_workers * rows_per_drone + min(total_workers, remainder)
	main_drone_end_y = Config.HEIGHT

def main_loop():
	"""并行主循环"""
	init()

	# 南瓜无人机句柄
	pumpkin_drone = None

	while True:
		# === 主无人机职责 ===
		WorldModel.scan_resources()

		# 自动解锁
		if Config.AUTO_UNLOCK:
			UnlockManager.try_unlock_one()

		# 迷宫（主无人机处理）
		MazeZone.farm()

		# === 并行处理 ===

		# 生成南瓜专用无人机（如果启用且未在运行）
		if Config.PUMPKIN_DRONE_ENABLED:
			if pumpkin_drone == None or has_finished(pumpkin_drone):
				pumpkin_drone = DroneManager.spawn_worker(PumpkinDrone.run)

		# 计算工作无人机数量
		available = DroneManager.get_available_count()
		worker_count = available

		# 计算主无人机负责的区域
		calculate_main_region(worker_count)

		# 生成巡逻无人机
		DroneManager.parallel_patrol(DroneWorker.process_tile)

		# 主无人机巡逻自己的区域
		patrol_main_region()

		# 等待所有巡逻无人机完成（不等待南瓜无人机）
		DroneManager.wait_all()

clear()
main_loop()
