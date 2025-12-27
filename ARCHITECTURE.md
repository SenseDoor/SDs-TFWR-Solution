# 系统架构演变记录

## 当前版本 v1.0

### 模块结构

```
main.py          - 主循环入口
Config.py        - 全局配置
WorldModel.py    - 世界状态缓存
Executor.py      - 任务执行器
Planner.py       - 任务规划器
ResourceChain.py - 资源优先级计算
ZoneManager.py   - 区域管理
PumpkinZone.py   - 巨型南瓜种植
MazeZone.py      - 迷宫生成与求解
TimePredictor.py - 作物生长预测
UnlockManager.py - 自动解锁管理
```

### 优点

1. 关注点分离 - WorldModel 管状态，Executor 管执行，Planner 管决策
2. 配置集中 - Config.py 统一管理参数
3. 区域化设计 - ZoneManager 支持不同区域不同策略

---

## 待优化项

### 1. 重复代码较多

**位置**: PumpkinZone.py (plant_6x6 和 scan_and_fix)

**问题**: 两个函数都有大量重复的蛇形遍历逻辑

**建议**: 抽取通用的区域遍历函数

---

### 2. Executor 职责过重

**位置**: Executor.py

**问题**: 同时承担任务队列、移动逻辑、遍历策略、基础操作、时间计数

**建议**: 拆分为子模块
- TaskQueue - 任务队列管理
- Movement - 移动与遍历
- Actions - 基础操作 (harvest/plant/water/fertilize)

---

### 3. 全局状态散落

**问题**: 多个模块各自维护缓存，生命周期不统一
- WorldModel.tile_cache
- WorldModel.resource_cache
- PumpkinZone.tile_cache
- TimePredictor.growth_cache
- Executor.task_queue

**建议**: 统一状态管理，明确初始化/清理时机

---

### 4. 硬编码问题

**位置**: ResourceChain.py:75-81

**问题**: 依赖链传播系数 0.5 是魔法数字

**建议**: 移至 Config.py 或定义为常量

---

### 5. 迷宫求解效率

**位置**: MazeZone.py:41-113

**问题**: 每步都调用 measure() 获取宝藏位置，但宝藏位置不变

**建议**: 只在开始时调用一次 measure()

---

### 6. 缺少无人机并行

**问题**: 游戏支持多无人机 (spawn_drone)，但代码完全是单线程设计

**建议**: 对大地图，可用无人机并行处理不同区域

---

### 7. PumpkinZone 阻塞主循环

**位置**: PumpkinZone.farm()

**问题**: while 循环等待成熟，阻塞其他区域处理

**建议**: 改为状态机，每次主循环只检查一次

---

## 当前版本 v2.0 - 并行无人机架构

### 架构图

```
┌────────────────────────────────────────────┐
│                  main.py                    │
│            (主无人机 - 协调者)               │
├────────────────────────────────────────────┤
│         DroneManager - 无人机管理            │
│   spawn_worker / wait_all / parallel_patrol │
├──────────┬──────────┬──────────────────────┤
│ 南瓜无人机│ 巡逻无人机│ 巡逻无人机 ...        │
│(PumpkinDrone)│ (Row 0~3) │ (Row 4~7)         │
├──────────┴──────────┴──────────────────────┤
│         DroneWorker - 独立工作逻辑           │
│   process_tile / decide_plant / do_water    │
└────────────────────────────────────────────┘
```

### 新增模块

| 模块 | 功能 |
|------|------|
| DroneManager.py | 无人机生命周期管理、并行调度 |
| DroneWorker.py | 独立工作逻辑（不依赖共享缓存） |
| PumpkinDrone.py | 南瓜专用无人机（非阻塞） |

### 并行策略

1. **区域分区** - 按行划分地图，每个无人机负责一段
2. **专职无人机** - 南瓜由专用无人机独立处理
3. **主无人机职责** - 迷宫、解锁、协调

### 竞态条件处理

1. 区域隔离 - 每个无人机只处理分配的行
2. 资源竞争 - 种植前再次检查 num_items()
3. 南瓜区跳过 - 巡逻无人机跳过南瓜区

### 解决的问题

- ✅ 问题 6: 缺少无人机并行 → 已实现按行并行
- ✅ 问题 7: PumpkinZone 阻塞主循环 → 改为独立无人机

### 遗留问题

- 问题 1: 重复代码 → 待优化
- 问题 2: Executor 职责过重 → 部分缓解（DroneWorker 分担）
- 问题 3: 全局状态散落 → 待统一
- 问题 4: 硬编码 → 待优化
- 问题 5: 迷宫求解效率 → 待优化

---

## 历史版本 v1.0

### 模块结构

```
main.py          - 主循环入口
Config.py        - 全局配置
WorldModel.py    - 世界状态缓存
Executor.py      - 任务执行器
Planner.py       - 任务规划器
ResourceChain.py - 资源优先级计算
ZoneManager.py   - 区域管理
PumpkinZone.py   - 巨型南瓜种植
MazeZone.py      - 迷宫生成与求解
TimePredictor.py - 作物生长预测
UnlockManager.py - 自动解锁管理
```

### 优点

1. 关注点分离 - WorldModel 管状态，Executor 管执行，Planner 管决策
2. 配置集中 - Config.py 统一管理参数
3. 区域化设计 - ZoneManager 支持不同区域不同策略

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2025-12-27 | 初始架构记录 |
| v2.0 | 2025-12-27 | 并行无人机架构：DroneManager, DroneWorker, PumpkinDrone |
