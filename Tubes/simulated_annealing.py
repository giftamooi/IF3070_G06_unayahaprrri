# simulated_annealing.py
from typing import List
from time import sleep, time
import math
import random

# Pendefinisian variabel awal untuk algoritma (sama dengan genetic.py)
# shipWidth = banyak baris (i), shipHeight = banyak kolom (j)
shipWidth = 5
shipHeight = 7
# shipMaxWeight = batas total berat kendaraan di kapal (ton)
# shipMaxCapacity = batas jumlah kendaraan di kapal (unit)
shipMaxWeight = 100
shipMaxCapacity = 500

# Vehicles adalah pendefinisian tipe kendaraan yang ada (format sama dengan genetic.py)
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

# runNumber = berapa kali SA dijalankan ulang dari awal (tiap run memakai initial state acak baru)
# Spesifikasi meminta 3 run, ubah angka ini untuk menjalankan lebih banyak, misal runNumber = 10
runNumber = 3


# Fungsi generate_fleet
# Digunakan untuk membuat 32 kendaraan dengan id unik, semuanya mula-mula di luar kapal
def generate_fleet() -> shipState:
    fleet = []
    for vehicleCode in (1, 2, 3):
        for k in range(vehicleStock[vehicleCode]):
            vehicle = vehicles[vehicleCode].copy()
            vehicle["vehicleNo"] = len(fleet) + 1
            vehicle["id"] = f"{vehicles[vehicleCode]['id']}-{k + 1}"
            vehicle["type"] = vehicleCode
            vehicle["position"] = None
            fleet.append(vehicle)
    return fleet

# Fungsi rotate_vehicle
# Digunakan untuk merotasi copy of kendaraan
# dari horizontal ke vertikal atau sebaliknya
def rotate_vehicle(vehicle: dict) -> dict:
    rotatedVehicle = vehicle.copy()
    rotatedVehicle["dimensions"] = (vehicle["dimensions"][1], vehicle["dimensions"][0])
    rotatedVehicle["orientation"] = "vertical" if vehicle["orientation"] == "horizontal" else "horizontal"
    return rotatedVehicle

# Fungsi get_occupied_cells
# Digunakan untuk mendapatkan semua sel geladak yang ditempati sebuah kendaraan di dalam kapal
def get_occupied_cells(vehicle: dict) -> list:
    positionX, positionY = vehicle["position"]
    vehicleWidth = vehicle["dimensions"][0]
    vehicleHeight = vehicle["dimensions"][1]
    return [(positionX + i, positionY + j) for i in range(vehicleWidth) for j in range(vehicleHeight)]

# Fungsi is_valid_state
# Digunakan untuk memeriksa constraint: tidak overlap, di dalam batas geladak,
# total berat <= shipMaxWeight, dan jumlah kendaraan <= shipMaxCapacity
def is_valid_state(currentState: shipState) -> bool:
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
        for (i, j) in get_occupied_cells(vehicle):
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

# Fungsi build_ship_matrix
# Digunakan untuk mengubah state menjadi matriks geladak (format sama dengan shipMatrix di genetic.py)
# Isi sel = vehicleNo kendaraan yang menempatinya, 0 = kosong
def build_ship_matrix(currentState: shipState) -> dict:
    shipMatrix = {(i, j): 0 for i in range(shipWidth) for j in range(shipHeight)}
    for vehicle in currentState:
        if vehicle["position"] is None:
            continue
        for cell in get_occupied_cells(vehicle):
            shipMatrix[cell] = vehicle["vehicleNo"]
    return shipMatrix

# Fungsi generate_initial_state
# Digunakan untuk membuat initial state acak: urutan kendaraan diacak, tiap kendaraan diberi orientasi
# dan koordinat acak, lalu tetap di luar kapal jika penempatannya melanggar constraint
def generate_initial_state() -> shipState:
    initialState = generate_fleet()
    order = list(range(len(initialState)))
    random.shuffle(order)
    for index in order:
        if random.random() < 0.5:
            initialState[index] = rotate_vehicle(initialState[index])
        initialState[index]["position"] = (random.randrange(shipWidth), random.randrange(shipHeight))
        if not is_valid_state(initialState):
            initialState[index]["position"] = None
    return initialState

# Move 1 - swap_vehicles
# Menukar posisi dua kendaraan acak (di dalam maupun di luar kapal), orientasi masing-masing tetap
# Pasangan dengan posisi yang sama (misal sama-sama di luar kapal) tidak dipilih karena state tidak berubah
def swap_vehicles(currentState: shipState) -> shipState:
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
    moves = [swap_vehicles, move_vehicle, change_orientation]
    while True:
        neighbor = random.choice(moves)(currentState)
        if is_valid_state(neighbor):
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
def simulated_annealing(initialTemperature: float, coolingRate: float, minTemperature: float, maxIteration: int, stuckThreshold: int) -> dict:
    initialState = generate_initial_state()
    currentState = initialState
    currentValue = calculate_value(currentState)
    bestValue = currentValue
    valueHistory = [currentValue]
    probabilityHistory = []
    stuckCount = 0
    iterationWithoutImprovement = 0
    iteration = 0

    startTime = time()
    for t in range(1, maxIteration + 1):
        temperature = schedule(t, initialTemperature, coolingRate)
        if temperature < minTemperature:
            break
        iteration = t

        neighbor = generate_neighbor(currentState)
        neighborValue = calculate_value(neighbor)
        deltaE = neighborValue - currentValue

        if deltaE > 0:
            currentState, currentValue = neighbor, neighborValue
        else:
            probability = math.exp(deltaE / temperature)
            # e^(deltaE/T) hanya dicatat saat deltaE < 0 (saat deltaE = 0 nilainya selalu 1)
            if deltaE < 0:
                probabilityHistory.append((t, probability))
            if random.random() < probability:
                currentState, currentValue = neighbor, neighborValue
        valueHistory.append(currentValue)

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

    return {
        "initialState": initialState,
        "finalState": currentState,
        "initialValue": calculate_value(initialState),
        "finalValue": currentValue,
        "iteration": iteration,
        "duration": duration,
        "stuckCount": stuckCount,
        "valueHistory": valueHistory,
        "probabilityHistory": probabilityHistory
    }

# Fungsi print_matrix (visualisasi)
# Digunakan untuk memunjukkan kondisi ship
# dan posisi kendaraan yang ada
def print_matrix(matrix: dict) -> None:
    cellWidth = max(2, len(str(max(matrix.values()))))
    segment = "─" * (cellWidth + 2)
    # Menggunakan ASCII agar tabel menjadi rapih
    print("┌" + "┬".join([segment] * shipHeight) + "┐")
    for i in range(shipWidth):
        cells = [f" {str(matrix[(i, j)]).rjust(cellWidth)} " for j in range(shipHeight)]
        print("│" + "│".join(cells) + "│")
        if i < shipWidth - 1:
            print("├" + "┼".join([segment] * shipHeight) + "┤")
    print("└" + "┴".join([segment] * shipHeight) + "┘")

# Fungsi divider (visualisasi)
# Digunakan untuk membantu memisahkan output
# dan menjadi judul besar yang jelas
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

# Fungsi build_table (visualisasi)
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

# Fungsi print_vehicle_tables
# Digunakan untuk memprint dua table di akhir
# Tabel yang menunjukkan kendaraan placed dan unplaced
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

# Fungsi print_state (visualisasi)
# Digunakan untuk menampilkan kendaraan di dalam & di luar kapal, matriks geladak, dan value state
def print_state(currentState: shipState) -> None:
    placed = [(vehicle["vehicleNo"], f"{vehicle['id']} ({vehicle['orientation']})") for vehicle in currentState if vehicle["position"] is not None]
    unplaced = []
    for vehicleCode in (1, 2, 3):
        sisa = sum(1 for vehicle in currentState if vehicle["type"] == vehicleCode and vehicle["position"] is None)
        if sisa > 0:
            unplaced.append((f"{sisa}x", vehicles[vehicleCode]["id"]))
    print_vehicle_tables(placed, unplaced)
    print(f"Matriks kapal (angka = Code kendaraan):")
    print_matrix(build_ship_matrix(currentState))
    print(f"Value: {calculate_value(currentState)} juta, total berat: {calculate_weight(currentState)}/{shipMaxWeight} ton, "
          f"jumlah kendaraan: {len(placed)}/{shipMaxCapacity}")

# Fungsi print_ascii_plot (visualisasi)
# Digunakan untuk menggambar plot titik (iterasi, nilai) di CLI
# Iterasi dikelompokkan menjadi plotWidth kolom dan nilai dibagi menjadi plotHeight baris
def print_ascii_plot(points: list, title: str, plotWidth: int = 60, plotHeight: int = 12) -> None:
    print(title)
    if not points:
        print("(tidak ada data)")
        return
    maxX = max(x for x, _ in points)
    minY = min(y for _, y in points)
    maxY = max(y for _, y in points)
    rangeY = maxY - minY if maxY > minY else 1
    grid = [[" "] * plotWidth for _ in range(plotHeight)]
    for x, y in points:
        column = min(plotWidth - 1, x * plotWidth // (maxX + 1))
        row = plotHeight - 1 - round((y - minY) / rangeY * (plotHeight - 1))
        grid[row][column] = "*"
    topLabel = f"{maxY:.4g}"
    bottomLabel = f"{minY:.4g}"
    labelW = max(len(topLabel), len(bottomLabel))
    for row in range(plotHeight):
        label = topLabel if row == 0 else bottomLabel if row == plotHeight - 1 else ""
        print(f"{label.rjust(labelW)} │" + "".join(grid[row]))
    print(" " * labelW + " └" + "─" * plotWidth)
    print(" " * labelW + "  0" + str(maxX).rjust(plotWidth - 1))
    print(" " * labelW + "  " + "Iterasi".center(plotWidth))

# Fungsi input_parameter
# Digunakan untuk membaca parameter dari user, memakai nilai default jika input kosong
def input_parameter(message: str, default, cast):
    userInput = input(f"{message} (default {default}): ").strip()
    return cast(userInput) if userInput else default

# Fungsi loading (visualisasi)
def loading(message: str, seconds: float = 1.5) -> None:
    frames = ["   ", ".  ", ".. ", "..."]
    endTime = time() + seconds
    i = 0
    while time() < endTime:
        print(f"\r{message}{frames[i % 4]}", end="", flush=True)
        sleep(0.3)
        i += 1
    print(f"\r{message}...")

# Fungsi main
# Menjalankan SA sebanyak runNumber kali dengan parameter yang sama dan menampilkan hasil tiap run di CLI
def main():
    divider("SIMULATED ANNEALING")
    initialTemperature = input_parameter("Masukkan suhu awal", 100.0, float)
    coolingRate = input_parameter("Masukkan laju pendinginan (0 < rate < 1)", 0.999, float)
    minTemperature = input_parameter("Masukkan suhu minimum", 0.01, float)
    maxIteration = input_parameter("Masukkan batas iterasi", 20000, int)
    stuckThreshold = input_parameter("Masukkan batas iterasi tanpa perbaikan (stuck)", 200, int)

    results = []
    for run in range(1, runNumber + 1):
        sleep(1)
        divider(f"RUN {run}")
        loading(f"Menjalankan simulated annealing run ke-{run}", 1)
        result = simulated_annealing(initialTemperature, coolingRate, minTemperature, maxIteration, stuckThreshold)
        results.append(result)

        sleep(1)
        divider("INITIAL STATE")
        print_state(result["initialState"])

        sleep(1)
        divider("FINAL STATE")
        print_state(result["finalState"])

        sleep(1)
        divider("PLOT VALUE")
        print_ascii_plot(list(enumerate(result["valueHistory"])), "Value (juta rupiah) terhadap iterasi")

        sleep(1)
        divider("PLOT e^(ΔE/T)")
        print_ascii_plot(result["probabilityHistory"], "e^(ΔE/T) terhadap iterasi (hanya saat ΔE < 0)")

        sleep(1)
        divider("HASIL")
        print(f"Value akhir           : {result['finalValue']} juta")
        print(f"Banyak iterasi        : {result['iteration']}")
        print(f"Durasi pencarian      : {result['duration']:.4f} detik")
        print(f"Frekuensi stuck       : {result['stuckCount']} kali (tanpa perbaikan {stuckThreshold} iterasi)")

    sleep(1)
    divider(f"RINGKASAN {runNumber} RUN")
    print(f"{'Run':<5}{'Value awal':<13}{'Value akhir':<13}{'Iterasi':<10}{'Durasi (s)':<13}{'Stuck':<6}")
    for run, result in enumerate(results, start=1):
        print(f"{run:<5}{result['initialValue']:<13}{result['finalValue']:<13}{result['iteration']:<10}{result['duration']:<13.4f}{result['stuckCount']:<6}")

if __name__ == "__main__":
    main()
