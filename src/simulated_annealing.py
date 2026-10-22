from typing import List
from time import time
import math
import random

# data geladak kapal
# shipWidth = banyak baris (i), shipHeight = banyak kolom (j)
shipWidth = 5
shipHeight = 7
# shipMaxWeight = batas total berat kendaraan di kapal (ton)
# shipMaxCapacity = batas jumlah kendaraan di kapal (unit)
shipMaxWeight = 100
shipMaxCapacity = 500

# Vehicles adalah pendefinisian tipe kendaraan yang ada (format sama dengan genetic_algorithm.py)
# dimensions = (baris, kolom) untuk orientasi horizontal, vertikal = ditukar
vehicles = {
    1: {"id": "mobil", "dimensions": (1, 2),"orientation": "horizontal", "shippingFee": 20, "weight": 5, "eta": 2},
    2: {"id": "minibus", "dimensions": (1, 3),"orientation": "horizontal", "shippingFee": 30, "weight": 12, "eta": 2},
    3: {"id": "truk", "dimensions": (2, 3),"orientation": "horizontal","shippingFee": 60, "weight": 30, "eta": 2}
}

# Pendefinisian stock kendaraan (total 32 kendaraan)
vehicleStock = {1: 20, 2: 7, 3: 5}

# State adalah list berisi seluruh 32 kendaraan
# Tiap kendaraan menyimpan "position" = koordinat pojok kiri atas (baris, kolom) di geladak,
# atau None jika kendaraan berada di luar kapal
shipState = List[dict]

# numberRuns = berapa kali SA dijalankan ulang dari awal (tiap run memakai initial state acak baru)
# Spesifikasi meminta 3 run,tp bisa diubah sekarang untuk test =10,nantiganti.
numberRuns = 10


# Fungsi create_vehicles
# Digunakan untuk membuat 32 kendaraan dengan id unik, semuanya mula-mula di luar kapal
def create_vehicles() -> shipState:
    fleet = []
    for vehicleCode in (1, 2, 3):
        for k in range(vehicleStock[vehicleCode]):
            vehicle = vehicles[vehicleCode].copy()
            vehicle["id"] = f"{vehicles[vehicleCode]['id']}_{k + 1}"
            vehicle["type"] = vehicles[vehicleCode]["id"]
            vehicle["position"] = None
            fleet.append(vehicle)
    return fleet

# Fungsi rotate_vehicle
# Digunakan untuk merotasi copy of kendaraan dari horizontal ke vertikal atau sebaliknya
def rotate_vehicle(vehicle: dict) -> dict:
    rotatedVehicle = vehicle.copy()
    rotatedVehicle["dimensions"] = (vehicle["dimensions"][1], vehicle["dimensions"][0])
    rotatedVehicle["orientation"] = "vertical" if vehicle["orientation"] == "horizontal" else "horizontal"
    return rotatedVehicle

# Fungsi get_cells
# Digunakan untuk mendapatkan semua sel geladak yang ditempati sebuah kendaraan di dalam kapal
def get_cells(vehicle: dict) -> list:
    positionX, positionY = vehicle["position"]
    vehicleWidth = vehicle["dimensions"][0]
    vehicleHeight = vehicle["dimensions"][1]
    return [(positionX + i, positionY + j) for i in range(vehicleWidth) for j in range(vehicleHeight)]

# Fungsi is_valid
# Digunakan untuk memeriksa constraint: tidak overlap, di dalam batas geladak,
# total berat <= shipMaxWeight, dan jumlah kendaraan <= shipMaxCapacity
def is_valid(currentState: shipState) -> bool:
    occupiedCells = set()
    totalWeight = 0
    totalVehicle = 0
    for vehicle in currentState:
        if vehicle["position"] is None:
            continue
        totalWeight += vehicle["weight"]
        totalVehicle += 1
        if totalWeight > shipMaxWeight or totalVehicle > shipMaxCapacity:
            return False
        for (i, j) in get_cells(vehicle):
            if i < 0 or i >= shipWidth or j < 0 or j >= shipHeight:
                return False
            if (i, j) in occupiedCells:
                return False
            occupiedCells.add((i, j))
    return True

# Fungsi calculate_value
# Objective function: total shippingFee kendaraan yang berada di dalam kapal
def calculate_value(currentState: shipState) -> int:
    return sum(vehicle["shippingFee"] for vehicle in currentState if vehicle["position"] is not None)

# Fungsi calculate_weight
# Digunakan untuk menghitung total berat kendaraan yang berada di dalam kapal
def calculate_weight(currentState: shipState) -> int:
    return sum(vehicle["weight"] for vehicle in currentState if vehicle["position"] is not None)

# Fungsi create_initial_state
# Digunakan untuk membuat initial state acak: urutan kendaraan diacak, tiap kendaraan diberi orientasi dan koordinat acak, lalu tetap di luar kapal jika penempatannya melanggar constraint
def create_initial_state(currentState: shipState) -> shipState:
    initialState = [vehicle.copy() for vehicle in currentState]
    order = list(range(len(initialState)))
    random.shuffle(order)
    for index in order:
        if random.random() < 0.5:
            initialState[index] = rotate_vehicle(initialState[index])
        initialState[index]["position"] = (random.randrange(shipWidth), random.randrange(shipHeight))
        if not is_valid(initialState):
            initialState[index]["position"] = None
    return initialState

# Move 1 - swap_vehicle
# Menukar posisi dua kendaraan acak (di dalam maupun di luar kapal), orientasi masing-masing tetap

# Pasangan dengan posisi yang sama (misal sama-sama di luar kapal) tidak dipilih karena state tidak berubah
def swap_vehicle(currentState: shipState) -> shipState:
    neighbor = currentState.copy()
    a = random.randrange(len(neighbor))
    candidates = [b for b in range(len(neighbor)) if neighbor[b]["position"] != neighbor[a]["position"]]
    if not candidates:
        return neighbor
    b = random.choice(candidates)
    neighbor[a] = {**currentState[a], "position": currentState[b]["position"]}
    neighbor[b] = {**currentState[b], "position": currentState[a]["position"]}
    return neighbor

# Move 2 - move_vehicle
# Memindahkan sebuah kendaraan acak ke koordinat lain di geladak, atau ke luar kapal (None)
def move_vehicle(currentState: shipState) -> shipState:
    neighbor = currentState.copy()
    index = random.randrange(len(neighbor))
    destinations = [(i, j) for i in range(shipWidth) for j in range(shipHeight)] + [None]
    destinations.remove(currentState[index]["position"])
    neighbor[index] = {**currentState[index], "position": random.choice(destinations)}
    return neighbor

# Move 3 - change_orientation
# Mengubah orientasi sebuah kendaraan acak, posisi pojok kiri atasnya tetap
def change_orientation(currentState: shipState) -> shipState:
    neighbor = currentState.copy()
    index = random.randrange(len(neighbor))
    neighbor[index] = rotate_vehicle(currentState[index])
    return neighbor

# Fungsi generate_neighbor
# Digunakan untuk memilih salah satu dari 3 move secara acak

# Neighbor yang melanggar constraint ditolak lalu di-generate ulang, sehingga state selalu valid
def generate_neighbor(currentState: shipState) -> shipState:
    moves = [swap_vehicle, move_vehicle, change_orientation]
    while True:
        neighbor = random.choice(moves)(currentState)
        if is_valid(neighbor):
            return neighbor

# Fungsi schedule
# Jadwal pendinginan geometrik: T(t) = initialTemperature * coolingRate^t
def schedule(t: int, initialTemperature: float, coolingRate: float) -> float:
    return initialTemperature * (coolingRate ** t)

# Fungsi simulated_annealing
# Implementasi SA sesuai salindia kuliah (masalah maksimasi):
#   - neighbor lebih baik (deltaE > 0) selalu diterima
#   - selain itu diterima dengan probabilitas e^(deltaE / T)
# Berhenti saat T < minTemperature atau iterasi mencapai maxIteration
# Stuck = value terbaik tidak naik selama stuckThreshold iterasi berturut-turut (counter di-reset setelah dihitung)
def simulated_annealing(initialState: shipState, initialTemperature: float, coolingRate: float,
                        minTemperature: float, maxIteration: int, stuckThreshold: int):
    startTime = time()
    current = initialState
    currentValue = calculate_value(current)
    bestValue = currentValue
    history = [currentValue]
    probabilityHistory = []
    stuckCount = 0
    iterationWithoutImprovement = 0
    iterations = 0

    for t in range(1, maxIteration + 1):
        temperature = schedule(t, initialTemperature, coolingRate)
        if temperature < minTemperature:
            break
        iterations = t

        neighbor = generate_neighbor(current)
        neighborValue = calculate_value(neighbor)
        deltaE = neighborValue - currentValue

        if deltaE > 0:
            current, currentValue = neighbor, neighborValue
        else:
            probability = math.exp(deltaE / temperature)
            # e^(deltaE/T) hanya dicatat saat deltaE < 0 (saat deltaE = 0 nilainya selalu 1)
            if deltaE < 0:
                probabilityHistory.append((t, probability))
            if random.random() < probability:
                current, currentValue = neighbor, neighborValue
        history.append(currentValue)

        # Pencatatan frekuensi stuck di local optima
        if currentValue > bestValue:
            bestValue = currentValue
            iterationWithoutImprovement = 0
        else:
            iterationWithoutImprovement += 1
            if iterationWithoutImprovement == stuckThreshold:
                stuckCount += 1
                iterationWithoutImprovement = 0

    duration = time() - startTime
    return current, iterations, duration, history, probabilityHistory, stuckCount

# Fungsi print_matrix (visualisasi, sama dengan genetic_algorithm.py)
# Digunakan untuk memunjukkan kondisi ship dan posisi kendaraan yang ada
def print_matrix(matrix: dict) -> None:
    cellWidth = max(2, len(str(max(matrix.values()))))
    segment = "─" * (cellWidth + 2)
    # Menggunakan unicode agar tabel menjadi rapih
    print("┌" + "┬".join([segment] * shipHeight) + "┐")
    for i in range(shipWidth):
        cells = [f" {str(matrix[(i, j)]).rjust(cellWidth)} " for j in range(shipHeight)]
        print("│" + "│".join(cells) + "│")
        if i < shipWidth - 1:
            print("├" + "┼".join([segment] * shipHeight) + "┤")
    print("└" + "┴".join([segment] * shipHeight) + "┘")

# Fungsi divider (visualisasi, sama dengan genetic_algorithm.py)
# Digunakan untuk membantu memisahkan output dan menjadi judul besar yang jelas
def divider(title: str = "", width: int = 60, char: str = "═") -> None:
    if title == "":
        print(char * width)
        return
    label = f" {title} "
    left = (width - len(label)) // 2
    right = width - len(label) - left
    print()
    print(char * left + label + char * right)
    print()

# Fungsi build_table (visualisasi, sama dengan genetic_algorithm.py)
# Digunakan untuk membuat tabel
def build_table(title: str, headers: tuple, rows: list) -> list:
    codeW = max([len(headers[0])] + [len(str(c)) for c, _ in rows])
    typeW = max([len(headers[1])] + [len(t) for _, t in rows])
    totalW = codeW + typeW + 7
    border = lambda l, m, r: l + "─" * (codeW + 2) + m + "─" * (typeW + 2) + r
    lines = [
        title.center(totalW),
        border("┌", "┬", "┐"),
        f"│ {headers[0].ljust(codeW)} │ {headers[1].ljust(typeW)} │",
        border("├", "┼", "┤"),
    ]
    for c, t in rows:
        lines.append(f"│ {str(c).rjust(codeW)} │ {t.ljust(typeW)} │")
    if not rows:
        lines.append(f"│ {'-'.center(codeW)} │ {'-'.center(typeW)} │")
    lines.append(border("└", "┴", "┘"))
    return lines

# Fungsi print_vehicle_tables (visualisasi, sama dengan genetic_algorithm.py)
# Digunakan untuk memprint dua table Tabel yang menunjukkan kendaraan placed dan unplaced
def print_vehicle_tables(placed: list, unplaced: list) -> None:
    left = build_table("PLACED", ("Code", "Type"), placed)
    right = build_table("UNPLACED", ("Jumlah", "Jenis"), unplaced)
    height = max(len(left), len(right))
    while len(left) < height:
        left.append(" " * len(left[0]))
    while len(right) < height:
        right.append(" " * len(right[0]))
    for a, b in zip(left, right):
        print(a + "    " + b)

# Fungsi build_ship_matrix (visualisasi, sama dengan hill_climbing.py)
# Digunakan untuk mengubah state menjadi matriks geladak Isi sel = nomor urut kendaraan di dalam kapal (sama dengan Code pada tabel PLACED), 0 = kosong
def build_ship_matrix(currentState: shipState) -> dict:
    matrix = {(i, j): 0 for i in range(shipWidth) for j in range(shipHeight)}
    number = 1
    for vehicle in currentState:
        if vehicle["position"] is None:
            continue
        for cell in get_cells(vehicle):
            matrix[cell] = number
        number += 1
    return matrix

# Fungsi build_vehicle_lists (visualisasi, sama dengan hill_climbing.py)
# Digunakan untuk membuat daftar kendaraan placed (Code, Type) dan unplaced (Jumlah, Jenis)
def build_vehicle_lists(currentState: shipState):
    placed = []
    counter = {"mobil": 0, "minibus": 0, "truk": 0}
    number = 1
    for vehicle in currentState:
        if vehicle["position"] is not None:
            placed.append((number, vehicle["type"]))
            number += 1
        else:
            counter[vehicle["type"]] += 1
    unplaced = []
    for jenis in counter:
        if counter[jenis] > 0:
            unplaced.append((f"{counter[jenis]}x", jenis))
    return placed, unplaced

# Fungsi print_state (visualisasi)
# Digunakan untuk menampilkan matriks geladak dan tabel kendaraan di dalam & di luar kapal
def print_state(currentState: shipState) -> None:
    placed, unplaced = build_vehicle_lists(currentState)
    print_matrix(build_ship_matrix(currentState))
    print_vehicle_tables(placed, unplaced)
    print(f"Value : {calculate_value(currentState)}, total berat : {calculate_weight(currentState)}/{shipMaxWeight} ton, "
          f"jumlah kendaraan : {len(placed)}/{shipMaxCapacity}")

# Fungsi plot_history_cli (visualisasi, format sama dengan plot_history dan plot_fitness_cli)
# Digunakan untuk menggambar grafik titik (iterasi, nilai) langsung di CLI
# Karena iterasi SA mencapai ribuan, iterasi dikelompokkan menjadi plotWidth kolom
def plot_history_cli(points: list, title: str, decimals: int = 1, height: int = 12, plotWidth: int = 60) -> None:
    print(title)
    if not points:
        print("(tidak ada data)")
        return
    maxX = max(x for x, _ in points)
    low = min(y for _, y in points)
    high = max(y for _, y in points)
    if high == low:
        high = low + 1
    grid = [[" "] * plotWidth for _ in range(height + 1)]
    for x, y in points:
        column = min(plotWidth - 1, x * plotWidth // (maxX + 1))
        row = round((y - low) / (high - low) * height)
        grid[height - row][column] = "*"
    for row in range(height + 1):
        value = low + (high - low) * (height - row) / height
        print(f"{value:7.{decimals}f} │" + "".join(grid[row]))
    print("        └" + "─" * plotWidth)
    # label sumbu x setiap 10 kolom
    labels = ""
    for column in range(0, plotWidth, 10):
        labels += str(column * (maxX + 1) // plotWidth).ljust(10)
    print("         " + labels + str(maxX) + " (iterasi)")

# Fungsi input_number (helper, mirip input_integer pada genetic_algorithm.py)
# Digunakan untuk memastikan input berupa angka dan minimal sekian,

# memakai nilai default jika input kosong
def input_number(prompt: str, default, minimum, maximum=None):
    while True:
        userInput = input(f"{prompt} (default {default}): ").strip()
        if userInput == "":
            return default
        try:
            value = type(default)(userInput)
            if value >= minimum and (maximum is None or value <= maximum):
                return value
            if maximum is None:
                print(f"Masukkan angka minimal {minimum}.")
            else:
                print(f"Masukkan angka antara {minimum} dan {maximum}.")
        except ValueError:
            print("Input harus berupa angka.")

# Fungsi main
# Menjalankan SA sebanyak numberRuns kali dengan parameter yang sama dan menampilkan hasil tiap run di CLI
def main():
    divider("SIMULATED ANNEALING")
    initialTemperature = input_number("Masukkan suhu awal", 100.0, 0.0001)
    coolingRate = input_number("Masukkan laju pendinginan (0 < rate < 1)", 0.999, 0.0001, 0.9999)
    minTemperature = input_number("Masukkan suhu minimum", 0.01, 0.0001)
    maxIteration = input_number("Masukkan batas iterasi", 20000, 1)
    stuckThreshold = input_number("Masukkan batas iterasi tanpa perbaikan (stuck)", 200, 1)

    results = []
    for run in range(numberRuns):
        divider(f"RUN {run + 1}")

        print("Membuat state awal...")
        initialState = create_initial_state(create_vehicles())

        divider("STATE AWAL")
        print_state(initialState)

        print("Menjalankan simulated annealing...")
        endState, iterations, duration, history, probabilityHistory, stuckCount = simulated_annealing(
            initialState, initialTemperature, coolingRate, minTemperature, maxIteration, stuckThreshold)

        divider("STATE AKHIR")
        print_state(endState)

        print("Ringkasan run ke-" + str(run + 1) + "...")
        print(f"Value awal : {history[0]}")
        print(f"Value akhir : {history[-1]}")
        print(f"Banyak iterasi : {iterations}")
        print(f"Durasi : {duration:.2f} detik")
        print(f"Frekuensi stuck : {stuckCount} kali (tanpa perbaikan {stuckThreshold} iterasi)")
        plot_history_cli(list(enumerate(history)), "Grafik value terhadap iterasi   (* = value)")
        print()
        plot_history_cli(probabilityHistory, "Grafik e^(ΔE/T) terhadap iterasi   (* = e^(ΔE/T), hanya saat ΔE < 0)", decimals=2)

        results.append({
            "initialState": initialState,
            "endState": endState,
            "startValue": history[0],
            "endValue": history[-1],
            "iterations": iterations,
            "duration": duration,
            "stuckCount": stuckCount,
            "history": history,
            "probabilityHistory": probabilityHistory,
        })

    divider("RINGKASAN EKSPERIMEN")
    print(f"{'Run':<6}{'Value awal':>12}{'Value akhir':>13}{'Iterasi':>9}{'Durasi (s)':>12}{'Stuck':>8}")
    for i in range(len(results)):
        r = results[i]
        print(f"{i + 1:<6}{r['startValue']:>12}{r['endValue']:>13}{r['iterations']:>9}{r['duration']:>12.2f}{r['stuckCount']:>8}")

if __name__ == "__main__":
    main()
