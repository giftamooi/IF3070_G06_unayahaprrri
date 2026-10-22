from time import sleep, perf_counter, time
import random
import copy

# data geladak kapal
shipWidth = 5
shipLength = 7
shipMaxCapacity = 100

# cetakan untuk kendaraan
class Vehicle():
    def __init__(self, id, vhcType, width, length, shippingFee, weight, eta):
        # info tetap kendaraan
        self.id = id
        self.vhcType = vhcType
        self.width = width
        self.length = length
        self.shippingFee = shippingFee 
        self.weight = weight 
        self.eta = eta

        # info yang berubah
        self.orientation = "H"
        self.row = None
        self.column = None
        self.insideShip = False

    # fungsi yang mereturn list sel yang ditempati vehicle
    def get_cells(self):
        if (self.orientation == "H"):
            rowCount = self.width
            columnCount = self.length
        else:
            rowCount = self.length
            columnCount = self.width

        cells = []
        for r in range(rowCount):
            for c in range(columnCount):
                cells.append((self.row + r, self.column + c))

        return cells
     


def calculate_value(vehicles):
    totalShippingFee = 0
    for v in vehicles:
        # jika kendaraan di luar geladak, tidak perlu dihitung
        if(v.insideShip == False):
            continue
        else:
            totalShippingFee += v.shippingFee

    return totalShippingFee


def create_vehicles(): 
    vehicles = []

    # memasukkan mobil dengan stock 20
    for i in range(1, 21):
        vehicles.append(Vehicle("mobil_" + str(i), "mobil", 1, 2, 20, 5, 2))

    # memasukkan minibus dengan stock 7
    for i in range (1, 8):
        vehicles.append(Vehicle("minibus_" + str(i), "minibus", 1, 3, 30, 12, 2))

    # memasukkan truk dengan stock 5
    for i in range(1, 6):
        vehicles.append(Vehicle("truk_" + str(i), "truk", 2, 3, 60, 30, 2))

    return vehicles



def create_initial_state(vehicles):
    failCount = 0
    maxFail = 50     # maxFail berfungsi untuk memberhentikan looping saat geladak sudah dianggap penuh
    

    while(failCount < maxFail):
        vhcOutsideShip = []
        for v in vehicles:
            if(v.insideShip == False):
                vhcOutsideShip.append(v)
        if(vhcOutsideShip == []):
            break

        choosenVehicle = random.choice(vhcOutsideShip)
        choosenVehicle.insideShip = True
        choosenVehicle.row = random.randint(0, shipWidth - 1)
        choosenVehicle.column = random.randint(0, shipLength - 1)
        choosenVehicle.orientation = random.choice(["H", "V"])
        if(is_valid(vehicles)):
            failCount = 0
        else:
            choosenVehicle.insideShip = False
            choosenVehicle.row = None
            choosenVehicle.column = None
            choosenVehicle.orientation = "H"
            failCount += 1

    return vehicles



def is_valid(vehicles):
    totalWeight = 0
    cellUsedList = []

    for v in vehicles:
        if(v.insideShip == False):
            continue
        else:
            cells = v.get_cells()

            for c in cells:
                # cek apakah sel tersebut di dalam atau luar geladak
                if(c[0] < 0 or c[0] > shipWidth-1 or c[1] < 0 or c[1] > shipLength - 1):
                    return False

                # cek apakah sel tersebut udah pernah dipake
                if(c in cellUsedList):
                    return False
                else:
                    # klo belum pernah, ditambah ke list
                    cellUsedList.append(c)


            # menghitung total weight
            totalWeight += v.weight
            # cek apakah total weight melebih max capacity
            if(totalWeight > shipMaxCapacity):
                return False

    return True

def change_orientation(vehicles, index):
    copyVehicles = copy.deepcopy(vehicles)

    v = copyVehicles[index]
    if(v.orientation == "H"):
        v.orientation = "V"
    elif(v.orientation == "V"):
        v.orientation = "H"

    return copyVehicles


def move_vehicle(vehicles, index, newRow, newColumn):
    copyVehicles = copy.deepcopy(vehicles)

    v = copyVehicles[index]
    
    v.row = newRow
    v.column = newColumn

    return copyVehicles


def swap_vehicle(vehicles, index1, index2):
    copyVehicles = copy.deepcopy(vehicles)
    tempRow1 = None
    tempColumn1 = None
    tempOrientation1 = None
    
    v1 = copyVehicles[index1]
    v2 = copyVehicles[index2]
    if(v1.insideShip == True and v2.insideShip == False):   #jika ditukar dengan kendaraan di luar geladak
        v2.row = v1.row
        v2.column = v1.column
        v2.orientation = v1.orientation
        v2.insideShip = True

        # membuat v1 menjadi default (karena dikeluarkan)
        v1.row = None
        v1.column = None
        v1.orientation = "H"
        v1.insideShip = False

    elif(v1.insideShip == True and v2.insideShip == True):   #jika ditukar dengan kendaraan lain di dalam geladak
        tempRow1 = v1.row
        tempColumn1 = v1.column
        tempOrientation1 = v1.orientation

        # untuk kasus ini, saya buat agar orientasi juga ditukar untuk menurunkan kemungkinan overlap
        v1.row = v2.row
        v1.column = v2.column
        v1.orientation = v2.orientation

        v2.row = tempRow1
        v2.column = tempColumn1
        v2.orientation = tempOrientation1

    return copyVehicles

def successor_maker(vehicles):
    successors = []

    for i in range(len(vehicles)):
        # kondisional buat memastikan yang diubah hanya kendaraan yang di dalam geladak saja
        if(vehicles[i].insideShip == False):
            continue

        # ubah orientasi
        newOrien = change_orientation(vehicles, i)
        if(is_valid(newOrien)):
            successors.append(newOrien)

        # pindah
        for y in range(shipWidth):    # cek tiap baris
            for x in range(shipLength):    # cek tiap kolom
                # kalo koordinat tujuan sama dengan koordinat sekarang, skip
                if(vehicles[i].row == y and vehicles[i].column == x):
                    continue
                else:
                    newMove = move_vehicle(vehicles, i, y, x)
                    if(is_valid(newMove)):
                        successors.append(newMove)

        # tukar
        for v in range(len(vehicles)):
            # kalo kendaraan awal sama kendaraan yg mau dituker itu sama, skip aja
            if(i == v):
                continue
            else:
                newSwap = swap_vehicle(vehicles, i, v)
                if(is_valid(newSwap)):
                    successors.append(newSwap)


    return successors


def steepest_ascent(vehicles):
    startTime = time()
    current = vehicles
    currentValue = calculate_value(vehicles)
    iterations = 0
    history = [currentValue]

    while True:
        successors = successor_maker(current)
        if(successors == []):
            break

        bestSucc = None
        bestValue = -1
        for s in successors:
            successorValue = calculate_value(s)
            if(successorValue > bestValue):
                bestValue = successorValue
                bestSucc = s

        if bestValue <= currentValue:
            break    
        else: 
            current = bestSucc
            currentValue = bestValue
            iterations += 1   # penghitungan iterasi tidak termasuk iterasi terakhir yang gagal
            history.append(currentValue)

    duration = time() - startTime
    return current, iterations, duration, history

# diambil dari genetic.py azza
def print_matrix(matrix: dict) -> None:
    cellWidth = max(2, len(str(max(matrix.values()))))
    segment = "─" * (cellWidth + 2)
    # Menggunakan unicode agar tabel menjadi rapih
    print("┌" + "┬".join([segment] * shipLength) + "┐")
    for i in range(shipWidth):
        cells = [f" {str(matrix[(i, j)]).rjust(cellWidth)} " for j in range(shipLength)]
        print("│" + "│".join(cells) + "│")
        if i < shipWidth - 1:
            print("├" + "┼".join([segment] * shipLength) + "┤")
    print("└" + "┴".join([segment] * shipLength) + "┘")


# diambil dari genetic.py azza
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

# diambil dari genetic.py azza
delayTime = 0.0

def pause(seconds: float) -> None:
    global delayTime
    startPause = perf_counter()
    sleep(seconds)
    delayTime += perf_counter() - startPause

def loading(message: str, seconds: float = 1.5) -> None:
    global delayTime
    startLoading = perf_counter()
    frames = ["   ", ".  ", ".. ", "..."]
    endTime = time() + seconds
    i = 0
    while time() < endTime:
        print(f"\r{message}{frames[i % 4]}", end="", flush=True)
        sleep(0.3)
        i += 1
    print(f"\r{message}...")   
    delayTime += perf_counter() - startLoading


# diambil dari genetic.py azza
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

# diambil dari genetic.py azza
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

def build_ship_matrix(vehicles):
    matrix = {(i, j): 0 for i in range(shipWidth) for j in range(shipLength)}      
    number = 1         

    for v in vehicles:
        if v.insideShip == False:
            continue
        cells = v.get_cells()        
        for c in cells:
            matrix[c] = number
        number += 1

    return matrix

def build_vehicle_lists(vehicles):
    placed = []
    counter = {"mobil" : 0, "minibus" : 0, "truk" : 0}
    number = 1

    for v in vehicles:
        if v.insideShip:
            placed.append((number, v.vhcType))
            number += 1
        else:
            counter[v.vhcType] += 1

    unplaced = []
    for jenis in counter:
        if counter[jenis] > 0:
            unplaced.append((f"{counter[jenis]}x", jenis))

    return placed, unplaced


# diambil dari plot_fitness_cli genetic.py azza
def plot_history(history, height: int = 12) -> None:
    low = min(history)
    high = max(history)
    if high == low:
        high = low + 1
    columnGap = 6 if len(history) <= 12 else 4
    width = len(history) * columnGap

    
    grid = [[" "] * width for _ in range(height + 1)]
    for idx in range(len(history)):
        x = idx * columnGap + 2
        y = round((history[idx] - low) / (high - low) * height)
        grid[height - y][x] = "*"
    print("Grafik value terhadap iterasi   (* = value)")
    for row in range(height + 1):
        value = high - (high - low) * row / height
        print(f"{value:7.1f} │" + "".join(grid[row]))
    print("        └" + "─" * width)
    labels = "".join(str(i).ljust(columnGap) for i in range(len(history)))
    print("         " + labels + " (iterasi)")



def main():
    numberRuns= 3
    results = []

    for run in range(numberRuns):
        divider(f"RUN {run + 1}")

        loading("Membuat state awal", 2)
        vehicles = create_vehicles()  # buat kendaraan
        vehicles = create_initial_state(vehicles)  # beberapa masu ke geladak sebagai initial state
        initialState = copy.deepcopy(vehicles)

        divider("STATE AWAL")
        matrix = build_ship_matrix(initialState)
        placed, unplaced = build_vehicle_lists(initialState)

        loading("Membuat matriks", 2)
        print_matrix(matrix)

        loading("Membuat daftar kendaraan yang masuk geladak dan yang di luar", 2)
        print_vehicle_tables(placed, unplaced)

        loading("Menjalankan steepest ascent", 2)
        endState, iterations, duration, history = steepest_ascent(vehicles)

        divider("STATE AKHIR")
        matrix = build_ship_matrix(endState)
        placed, unplaced = build_vehicle_lists(endState)
        print_matrix(matrix)
        print_vehicle_tables(placed, unplaced)

        loading("Ringkasan run ke-" + str(run+1), 2)
        print(f"Value awal : {history[0]}")
        print(f"Value akhir : {history[-1]}")
        print(f"Banyak iterasi : {iterations}")
        print(f"Durasi : {duration:.2f} detik")
        plot_history(history)

        results.append({
            "initialState" : initialState,
            "endState" : endState,
            "startValue" : history[0],
            "endValue" : history[-1],
            "iterations" : iterations,
            "duration" : duration,
            "history" : history,
        })

    divider("RINGKASAN EKSPERIMEN")
    print(f"{'Run':<6}{'Value awal':>12}{'Value akhir':>13}{'Iterasi':>9}{'Durasi (s)':>12}")
    for i in range(len(results)):
        r = results[i]
        print(f"{i + 1:<6}{r['startValue']:>12}{r['endValue']:>13}{r['iterations']:>9}{r['duration']:>12.2f}")




if __name__ == "__main__":
    main()

