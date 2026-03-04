import random

# =====================================
# CONFIGURATION
# =====================================
GRID_SIZE = 10
BATTERY_MAX = 100
FOOD_COUNT = 5
HOLE_COUNT = 3
WALL_COUNT = 8
MAX_STEPS = 100

# =====================================
# WORLD GENERATOR
# =====================================
def generate_positions(count, forbidden):
    positions = set()
    while len(positions) < count:
        pos = (random.randint(0, GRID_SIZE-1),
               random.randint(0, GRID_SIZE-1))
        if pos not in forbidden:
            positions.add(pos)
    return list(positions)


# Robot start random
robot_pos = (random.randint(0, GRID_SIZE-1),
             random.randint(0, GRID_SIZE-1))

forbidden = {robot_pos}

# Charger
charger_pos = generate_positions(1, forbidden)[0]
forbidden.add(charger_pos)

# Food
foods = generate_positions(FOOD_COUNT, forbidden)
forbidden.update(foods)

# Hole
holes = generate_positions(HOLE_COUNT, forbidden)
forbidden.update(holes)

# Wall
walls = generate_positions(WALL_COUNT, forbidden)

# =====================================
# DISPLAY WORLD (untuk analisis)
# =====================================
print("===== WORLD CONFIGURATION =====")
print("Robot   :", robot_pos)
print("Charger :", charger_pos)
print("Food    :", foods)
print("Holes   :", holes)
print("Walls   :", walls)
print("================================\n")

# =====================================
# SENSOR (PARTIAL OBSERVABILITY)
# =====================================
def get_sensors(position):
    x, y = position
    directions = {
        "UP": (x-1, y),
        "DOWN": (x+1, y),
        "LEFT": (x, y-1),
        "RIGHT": (x, y+1)
    }

    sensors = {}

    for d, pos in directions.items():
        if not (0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE):
            sensors[d] = "WALL"
        elif pos in walls:
            sensors[d] = "WALL"
        elif pos in holes:
            sensors[d] = "HOLE"
        elif pos in foods:
            sensors[d] = "FOOD"
        elif pos == charger_pos:
            sensors[d] = "CHARGER"
        else:
            sensors[d] = "EMPTY"

    return sensors

# =====================================
# REFLEX AGENT
# =====================================
def get_action(sensors, battery_level):

    # 1️ SURVIVAL: hindari hole & wall
    safe_moves = []
    for direction, obj in sensors.items():
        if obj not in ["WALL", "HOLE"]:
            safe_moves.append(direction)

    if not safe_moves:
        return "STAY", "[MENGHINDARI LUBANG] Terjebak, tidak ada jalan aman."

    # 2️ ENERGI KRITIS
    if battery_level <= 20:
        for direction, obj in sensors.items():
            if obj == "CHARGER":
                return "MOVE_" + direction, "[MENCARI CHARGER] Baterai kritis (≤20%) → menuju charger untuk mengisi daya."

    # 3️ MAKAN
    for direction, obj in sensors.items():
        if obj == "FOOD":
            return "MOVE_" + direction, "[MENCARI MAKAN] Makanan terdeteksi → bergerak ke arah makanan."

    # 4️ DEFAULT EKSPLORASI
    move = random.choice(safe_moves)
    return "MOVE_" + move, "[EKSPLORASI ACAK] Jalan aman ditemukan → berpindah ke arah acak (menghindari lubang dan dinding)."

# =====================================
# APPLY ACTION
# =====================================
def apply_action(position, action):
    x, y = position

    if action == "MOVE_UP":
        return (x-1, y)
    elif action == "MOVE_DOWN":
        return (x+1, y)
    elif action == "MOVE_LEFT":
        return (x, y-1)
    elif action == "MOVE_RIGHT":
        return (x, y+1)
    return position

# =====================================
# SIMULATION
# =====================================
battery = BATTERY_MAX
score = 0
step = 0
visited_positions = []

print("===== START SIMULATION =====\n")

while battery > 0 and step < MAX_STEPS:
    step += 1
    battery -= 1

    sensors = get_sensors(robot_pos)
    action, reason = get_action(sensors, battery)
    new_pos = apply_action(robot_pos, action)

    robot_pos = new_pos
    status = "Berpindah."

    # Cek Hole
    if robot_pos in holes:
        print(f"[Step {step}] Pos:{robot_pos} | Batt:{battery}%")
        print("Aksi       :", action)
        print("Keputusan  :", reason)
        print("Status     : [MENGHINDARI LUBANG - GAGAL] Robot masuk lubang → GAME OVER\n")
        break

    # Cek Food
    if robot_pos in foods:
        foods.remove(robot_pos)
        score += 10
        status = "[MAKAN] Makanan berhasil dikonsumsi (+10 poin)."

    # Cek Charger
    if robot_pos == charger_pos:
        battery = BATTERY_MAX
        status = "[MENGISI BATERAI] Baterai diisi penuh di charger (100%)."

    print(f"[Step {step}] Pos:{robot_pos} | Batt:{battery}%")
    print("Aksi       :", action)
    print("Keputusan  :", reason)
    print("Status     :", status)
    print("--------------------------------------\n")

    visited_positions.append(robot_pos)

else:
    print("Simulasi berhenti.\n")

# =====================================
# ANALISIS HASIL
# =====================================
print("===== HASIL AKHIR =====")
print("Total langkah :", step)
print("Skor akhir    :", score)
print("Sisa baterai  :", battery)

if battery == 0:
    print("Agent mati karena kehabisan energi.")
elif robot_pos in holes:
    print("Agent mati karena masuk lubang.")
elif step >= MAX_STEPS:
    print("Agent berhenti karena batas langkah (kemungkinan loop).")
else:
    print("Agent berhenti normal.")

print("Sisa makanan :", len(foods))