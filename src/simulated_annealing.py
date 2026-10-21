# simulated_annealing.py
from typing import List
from time import sleep, time
import json
import math
import os
import random
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Pendefinisian variabel awal untuk algoritma (sama dengan genetic.py)
# shipWidth = banyak baris (i), shipHeight = banyak kolom (j)
shipWidth = 5
shipHeight = 7
shipMaxCapacity = 100

# Jenis kendaraan, format sama dengan genetic.py
# dimensions = (baris, kolom) untuk orientasi horizontal, vertikal = ditukar
vehicles = {
    1: {"id": "mobil", "dimensions": (1, 2),"orientation": "horizontal", "shippingFee": 20, "weight": 5, "eta": 2},
    2: {"id": "minibus", "dimensions": (1, 3),"orientation": "horizontal", "shippingFee": 30, "weight": 12, "eta": 2},
    3: {"id": "truk", "dimensions": (2, 3),"orientation": "horizontal","shippingFee": 70, "weight": 30, "eta": 2}
}

# Jumlah unit tiap jenis kendaraan (total 32 kendaraan)
vehicleStock = {1: 20, 2: 7, 3: 5}

# State adalah list berisi seluruh 32 kendaraan
# Tiap kendaraan menyimpan "position" = koordinat pojok kiri atas (baris, kolom) di geladak,
# atau None jika kendaraan berada di luar kapal
shipState = List[dict]

# Folder penyimpanan hasil run (output/simulated_annealing di root repo)
outputDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "simulated_annealing")

# Warna tiap jenis kendaraan pada visualisasi
typeColors = {1: "tab:blue", 2: "tab:orange", 3: "tab:green"}


# Fungsi generate_fleet
# Digunakan untuk membuat 32 kendaraan dengan id unik, semuanya mula-mula di luar kapal
def generate_fleet() -> shipState:
    fleet = []
    for vehicleCode, stock in vehicleStock.items():
        for k in range(stock):
            vehicle = vehicles[vehicleCode].copy()
            vehicle["vehicleNo"] = len(fleet) + 1
            vehicle["id"] = f"{vehicles[vehicleCode]['id']}-{k + 1}"
            vehicle["type"] = vehicleCode
            vehicle["position"] = None
            fleet.append(vehicle)
    return fleet

# Fungsi rotate_vehicle (sama dengan genetic.py)
# Digunakan untuk merotasi kendaraan dari horizontal ke vertikal atau sebaliknya
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
# Digunakan untuk memeriksa 3 constraint: tidak overlap, di dalam batas geladak, total berat <= kapasitas
def is_valid_state(currentState: shipState) -> bool:
    occupiedCells = set()
    totalWeight = 0
    for vehicle in currentState:
        if vehicle["position"] is None:
            continue
        totalWeight += vehicle["weight"]
        if totalWeight > shipMaxCapacity:
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

# Fungsi visualisasi - print_matrix (sama dengan genetic.py)
def print_matrix(matrix: dict) -> None:
    cellWidth = max(2, len(str(max(matrix.values()))))
    segment = "─" * (cellWidth + 2)

    print("┌" + "┬".join([segment] * shipHeight) + "┐")
    for i in range(shipWidth):
        cells = [f" {str(matrix[(i, j)]).rjust(cellWidth)} " for j in range(shipHeight)]
        print("│" + "│".join(cells) + "│")
        if i < shipWidth - 1:
            print("├" + "┼".join([segment] * shipHeight) + "┤")
    print("└" + "┴".join([segment] * shipHeight) + "┘")

# Fungsi visualisasi - print_state
# Menampilkan geladak, daftar kendaraan di dalam & di luar kapal, serta value state di terminal
def print_state(currentState: shipState) -> None:
    print_matrix(build_ship_matrix(currentState))
    print("Kendaraan di dalam kapal:")
    for vehicle in currentState:
        if vehicle["position"] is not None:
            print(f"  [{vehicle['vehicleNo']:>2}] {vehicle['id']:<10} {vehicle['orientation']:<10} posisi {vehicle['position']}")
    outsideVehicles = [f"[{vehicle['vehicleNo']}] {vehicle['id']}" for vehicle in currentState if vehicle["position"] is None]
    print("Kendaraan di luar kapal:")
    print(textwrap.fill(", ".join(outsideVehicles), width=80, initial_indent="  ", subsequent_indent="  "))
    print(f"Value: {calculate_value(currentState)} juta, total berat: {calculate_weight(currentState)}/{shipMaxCapacity} ton")

# Fungsi visualisasi - plot_state
# Menyimpan gambar geladak (kiri) dan daftar kendaraan di luar kapal (kanan) beserta value state
def plot_state(currentState: shipState, title: str, filePath: str):
    fig, (axShip, axOutside) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [3, 2]})

    axShip.set_xlim(0, shipHeight)
    axShip.set_ylim(shipWidth, 0)
    axShip.set_xticks(range(shipHeight + 1))
    axShip.set_yticks(range(shipWidth + 1))
    axShip.set_aspect("equal")
    axShip.grid(True)
    for vehicle in currentState:
        if vehicle["position"] is None:
            continue
        positionX, positionY = vehicle["position"]
        axShip.add_patch(Rectangle((positionY, positionX), vehicle["dimensions"][1], vehicle["dimensions"][0],
                                   facecolor=typeColors[vehicle["type"]], edgecolor="black", alpha=0.7))
        axShip.text(positionY + vehicle["dimensions"][1] / 2, positionX + vehicle["dimensions"][0] / 2,
                    vehicle["vehicleNo"], ha="center", va="center")
    axShip.set_title("Geladak kapal (angka = vehicleNo)")

    outsideText = ""
    for vehicleCode, vehicleType in vehicles.items():
        outsideNo = [str(vehicle["vehicleNo"]) for vehicle in currentState if vehicle["type"] == vehicleCode and vehicle["position"] is None]
        outsideText += textwrap.fill(f"{vehicleType['id']} ({len(outsideNo)}): " + ", ".join(outsideNo), width=40) + "\n\n"
    axOutside.axis("off")
    axOutside.set_title("Kendaraan di luar kapal")
    axOutside.text(0, 1, outsideText, va="top", fontsize=9)

    fig.suptitle(f"{title} | Value = {calculate_value(currentState)} juta | Berat = {calculate_weight(currentState)}/{shipMaxCapacity} ton")
    fig.savefig(filePath)
    return fig

# Fungsi visualisasi - plot_value
# Menyimpan plot value current state terhadap iterasi
def plot_value(valueHistory: list, title: str, filePath: str):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(range(len(valueHistory)), valueHistory)
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("Value (juta rupiah)")
    ax.set_title(title)
    fig.savefig(filePath)
    return fig

# Fungsi visualisasi - plot_probability
# Menyimpan plot e^(deltaE/T) terhadap iterasi (hanya iterasi dengan deltaE < 0)
def plot_probability(probabilityHistory: list, title: str, filePath: str):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.scatter([t for t, _ in probabilityHistory], [p for _, p in probabilityHistory], s=4)
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("e^(ΔE/T)")
    ax.set_title(title)
    fig.savefig(filePath)
    return fig

# Fungsi save_result
# Menyimpan state awal, state akhir, value, durasi, dan frekuensi stuck satu run ke file JSON
def save_result(result: dict, parameters: dict, filePath: str) -> None:
    stateKeys = ["vehicleNo", "id", "orientation", "dimensions", "position", "shippingFee", "weight", "eta"]
    data = {
        "parameters": parameters,
        "initialValue": result["initialValue"],
        "finalValue": result["finalValue"],
        "iteration": result["iteration"],
        "duration": result["duration"],
        "stuckCount": result["stuckCount"],
        "initialState": [{key: vehicle[key] for key in stateKeys} for vehicle in result["initialState"]],
        "finalState": [{key: vehicle[key] for key in stateKeys} for vehicle in result["finalState"]]
    }
    with open(filePath, "w") as file:
        json.dump(data, file, indent=2)

# Fungsi input_parameter
# Digunakan untuk membaca parameter dari user, memakai nilai default jika input kosong
def input_parameter(message: str, default, cast):
    userInput = input(f"{message} (default {default}): ").strip()
    return cast(userInput) if userInput else default

# Divider (sama dengan genetic.py)
# biar cakep
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

# Loading (sama dengan genetic.py)
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
# Menjalankan SA sebanyak 3 kali dengan parameter yang sama, lalu menyimpan hasil tiap run ke output/
def main():
    divider("SIMULATED ANNEALING")
    initialTemperature = input_parameter("Masukkan suhu awal", 100.0, float)
    coolingRate = input_parameter("Masukkan laju pendinginan (0 < rate < 1)", 0.999, float)
    minTemperature = input_parameter("Masukkan suhu minimum", 0.01, float)
    maxIteration = input_parameter("Masukkan batas iterasi", 20000, int)
    stuckThreshold = input_parameter("Masukkan batas iterasi tanpa perbaikan (stuck)", 200, int)
    showPlot = input("Tampilkan plot setiap run? (y/n): ").strip().lower() == "y"
    parameters = {
        "initialTemperature": initialTemperature,
        "coolingRate": coolingRate,
        "minTemperature": minTemperature,
        "maxIteration": maxIteration,
        "stuckThreshold": stuckThreshold
    }

    results = []
    for run in range(1, 4):
        divider(f"RUN {run}")
        loading(f"Menjalankan simulated annealing run ke-{run}", 1)
        result = simulated_annealing(initialTemperature, coolingRate, minTemperature, maxIteration, stuckThreshold)
        results.append(result)

        divider("INITIAL STATE")
        print_state(result["initialState"])

        divider("FINAL STATE")
        print_state(result["finalState"])

        divider("HASIL")
        print(f"Value akhir           : {result['finalValue']} juta")
        print(f"Banyak iterasi        : {result['iteration']}")
        print(f"Durasi pencarian      : {result['duration']:.4f} detik")
        print(f"Frekuensi stuck       : {result['stuckCount']} kali (tanpa perbaikan {stuckThreshold} iterasi)")

        runDir = os.path.join(outputDir, f"run_{run}")
        os.makedirs(runDir, exist_ok=True)
        plot_state(result["initialState"], f"Run {run} - Initial State", os.path.join(runDir, "initial_state.png"))
        plot_state(result["finalState"], f"Run {run} - Final State", os.path.join(runDir, "final_state.png"))
        plot_value(result["valueHistory"], f"Run {run} - Value terhadap Iterasi", os.path.join(runDir, "value_plot.png"))
        plot_probability(result["probabilityHistory"], f"Run {run} - e^(ΔE/T) terhadap Iterasi", os.path.join(runDir, "probability_plot.png"))
        save_result(result, parameters, os.path.join(runDir, "result.json"))
        print(f"Hasil run disimpan di {os.path.normpath(runDir)}")

        if showPlot:
            plt.show()
        plt.close("all")

    divider("RINGKASAN 3 RUN")
    print(f"{'Run':<5}{'Value awal':<13}{'Value akhir':<13}{'Iterasi':<10}{'Durasi (s)':<13}{'Stuck':<6}")
    for run, result in enumerate(results, start=1):
        print(f"{run:<5}{result['initialValue']:<13}{result['finalValue']:<13}{result['iteration']:<10}{result['duration']:<13.4f}{result['stuckCount']:<6}")

if __name__ == "__main__":
    main()
