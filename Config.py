# === 地图 ===
WIDTH = get_world_size()
HEIGHT = get_world_size()

# === 资源配置 ===
TARGET_RATIO = {
	"wood": 3,
	"hay": 1,
	"carrot": 2,
	"pumpkin": 2,
}

SAFE_MARGIN = {
	"wood": 5,
	"hay": 0,
	"carrot": 10,
	"pumpkin": 0,
	"water": 5,
}

# === 覆写 ===
OVERRIDE_PLANT = None

# === 浇水控制 ===
WATER_THRESHOLD = 0.25
WATER_TARGET = 0.75
MIN_WATER_LEVEL = 0.5

# === 区域类型 ===
ZONE_FLEX = 0
ZONE_TREE = 1
ZONE_CARROT = 2
ZONE_HAY = 3
ZONE_CACTUS = 4

# === 区域配置 ===
ZONES = {}

# === 南瓜配置（不再划分区域，动态种植）===
PUMPKIN_ENABLED = True
PUMPKIN_SIZE = 6  # 固定 6x6

# === 仙人掌配置 ===
CACTUS_ENABLED = False
CACTUS_X = 0
CACTUS_Y = 0
CACTUS_SIZE = 6

# === 自动解锁 ===
AUTO_UNLOCK = True

# === 作物生长时间 ===
GROW_TIME = {
	Entities.Tree: 120,
	Entities.Grass: 60,
	Entities.Carrot: 60,
	Entities.Pumpkin: 90,
	Entities.Cactus: 90,
}

# Config.py 新增
FERTILIZER_ENABLED = True
FERTILIZER_SAFE_MARGIN = 5
WEIRD_SUBSTANCE_TARGET = 1000    # 目标数量
FERTILIZER_AFTER_TARGET = False  # 达标后是否继续用肥料

# 迷宫区
MAZE_ENABLED = True
MAZE_X = 0          # 左下角，根据地图大小调整
MAZE_Y = 0
MAZE_SIZE = 10      # 10x10 迷宫

# 迷宫触发条件
MAZE_SUBSTANCE_MARGIN = 50  # 保留多少 Weird_Substance

# 区域类型
ZONE_MAZE = 5

# === 并行无人机配置 ===
PARALLEL_ENABLED = True          # 启用并行模式
PUMPKIN_DRONE_ENABLED = True     # 南瓜专用无人机
PATROL_STRATEGY = "rows"         # 巡逻策略: "rows" | "columns"