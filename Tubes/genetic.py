# genetic.py
from typing import List
from time import sleep, time
import random

# Pendefinisian variabel awal untuk algoritma 
shipWidth = 5
shipHeight = 7
shipMatrix = {(i, j): 0 for i in range(shipWidth) for j in range(shipHeight)} 
shipMaxCapacity = 100



# Genetic disimpan sebagai dictionary dengan key "genome" dan "fitness"
# Untuk memudahkan pengelolaan data individu dalam populasi
class Genetic:
    def __init__(self, genome: List[int]):
        self.genome = genome
        self.fitness = 0
        self.vehicles_placed = []

# Populasi adalah list dari individu genetik dengan jumlah awal sebanyak startPopulationNumber
population = List[Genetic]
vehicles = {
    1: {"id": "mobil", "dimensions": (1, 2),"orientation": "horizontal", "shippingFee": 20, "weight": 5, "eta": 2},
    2: {"id": "minibus", "dimensions": (1, 3),"orientation": "horizontal", "shippingFee": 30, "weight": 12, "eta": 2},
    3: {"id": "truk", "dimensions": (2, 3),"orientation": "horizontal","shippingFee": 60, "weight": 30, "eta": 2}
}

emptySlots = 8
vehicleStock = {1: 20, 2: 7, 3: 5, 0: emptySlots}
genomeLength = 17

def generate_genetic(p: population) -> None:
    pool = []
    for code, amount in vehicleStock.items():
        pool += [code] * amount
    individual = random.sample(pool, genomeLength)
    sleep(0.2)
    print(f"Menghasilkan: {individual}")
    p.append({"genome": individual, "fitness": 0})

# Fungsi generate_population
# Digunakan untuk menghasilkan populasi awal sebanyak startPopulationNumber 
def generate_population(startPopulationNumber: int) -> population:
    population = []
    for _ in range(startPopulationNumber):
        generate_genetic(population)
    return population

# Fungsi check_space
# Digunakan untuk memeriksa apakah kendaraan muat di dalam kapal
def check_space(vehicle: dict):
    vehicleWidth = vehicle["dimensions"][0]
    vehicleHeight = vehicle["dimensions"][1]
    positionX = 0;
    positionY = 0;
    canplace = False
    for i in range(shipWidth):
        for j in range(shipHeight):
            if shipMatrix[(i, j)] != 0:
                continue
            if i + vehicleWidth > shipWidth or j + vehicleHeight > shipHeight:
                continue
            canplace = True
            for k in range(vehicleWidth):
                for l in range(vehicleHeight):
                    if shipMatrix[(i + k, j + l)] != 0:
                        canplace = False
                        break
                if not canplace:
                    break
            if canplace:
                positionX = i
                positionY = j
                return canplace, positionX, positionY 
    return canplace, positionX, positionY

# Fungsi rotate_vehicle
# Digunakan untuk merotasi kendaraan dari horizontal ke vertikal atau sebaliknya
def rotate_vehicle(vehicle: dict) -> dict:
    rotatedVehicle = vehicle.copy()
    rotatedVehicle["dimensions"] = (vehicle["dimensions"][1], vehicle["dimensions"][0])
    rotatedVehicle["orientation"] = "vertical" if vehicle["orientation"] == "horizontal" else "horizontal"
    return rotatedVehicle

def place_vehicle(vehicle: dict, positionX: int, positionY: int, vehicleCode: int) -> None:
    vehicleWidth = vehicle["dimensions"][0]
    vehicleHeight = vehicle["dimensions"][1]
    for i in range(vehicleWidth):
        for j in range(vehicleHeight):
            shipMatrix[(positionX + i, positionY + j)] = vehicleCode

def calculate_fitness(gen: dict):
    shipCurrWeight = 0
    shippingFee = 0
    numberVehiclePlaced = 0
    gen["vehicles_placed"] = []
    gen["vehicles_unplaced"] = []
    unplacedCount = 0
    for gene in gen["genome"]:
        if gene == 0:
            continue
        vehicle = vehicles[gene]
        canPlace, positionX, positionY = check_space(vehicle)
        if not canPlace:
            vehicle = rotate_vehicle(vehicle)
            canPlace, positionX, positionY = check_space(vehicle)
        if canPlace and shipCurrWeight + vehicle["weight"] <= shipMaxCapacity:
            numberVehiclePlaced += 1
            place_vehicle(vehicle, positionX, positionY, numberVehiclePlaced)
            gen["vehicles_placed"].append((numberVehiclePlaced, vehicle["id"]))
            shipCurrWeight += vehicle["weight"]
            shippingFee += vehicle["shippingFee"]
        else:
            unplacedCount += 1
            gen["vehicles_unplaced"].append((unplacedCount, vehicle["id"]))
    gen["fitness"] = shippingFee

def reset_ship() -> None:
    global shipMatrix
    shipMatrix = {(i, j): 0 for i in range(shipWidth) for j in range(shipHeight)}

# Fungsi visualisasi - print_matrix
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

# Divider
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

#helper table
def build_table(title: str, rows: list) -> list:
    codeW = max([4] + [len(str(c)) for c, _ in rows])
    typeW = max([4] + [len(t) for _, t in rows])
    totalW = codeW + typeW + 7
    border = lambda l, m, r: l + "─" * (codeW + 2) + m + "─" * (typeW + 2) + r

    lines = [
        title.center(totalW),
        border("┌", "┬", "┐"),
        f"│ {'Code'.ljust(codeW)} │ {'Type'.ljust(typeW)} │",
        border("├", "┼", "┤"),
    ]
    for c, t in rows:
        lines.append(f"│ {str(c).rjust(codeW)} │ {t.ljust(typeW)} │")
    if not rows:
        lines.append(f"│ {'-'.center(codeW)} │ {'-'.center(typeW)} │")
    lines.append(border("└", "┴", "┘"))
    return lines

#helper vehicle table
def print_vehicle_tables(placed: list, unplaced: list) -> None:
    left = build_table("PLACED", placed)
    right = build_table("UNPLACED", unplaced)
    height = max(len(left), len(right))
    while len(left) < height:
        left.append(" " * len(left[0]))
    while len(right) < height:
        right.append(" " * len(right[0]))
    for a, b in zip(left, right):
        print(a + "    " + b)

def calculate_successor(population: population) -> list:
    totalFitness = 0
    for gen in population:
        totalFitness += gen["fitness"]

    for gen in population:
        chance = gen["fitness"] / totalFitness if totalFitness > 0 else 0
        gen["chance"] = chance

    parent1 = random.choices(population, weights=[gen["chance"] for gen in population], k=1)[0]

    kandidat = [gen for gen in population if gen["genome"] != parent1["genome"]]
    if len(kandidat) == 0:
        return [parent1, parent1]

    bobot = [gen["chance"] for gen in kandidat]
    if sum(bobot) == 0:
        parent2 = random.choice(kandidat)
    else:
        parent2 = random.choices(kandidat, weights=bobot, k=1)[0]
    return [parent1, parent2]

# build child
# menghitung anak dengan stock handlingnya juga
def build_child(first: list, second: list, p: int) -> list:
    genome = first[:p] + second[p:]
    sisa = vehicleStock.copy()
    for i in range(genomeLength):
        g = genome[i]
        if sisa[g] > 0:
            sisa[g] -= 1
        else:
            # stok jenis something habis, ganti dengan jenis yang masih sisa
            pilihan = [c for c in sisa if sisa[c] > 0]
            baru = random.choice(pilihan)
            genome[i] = baru
            sisa[baru] -= 1
    return genome

def crossover(parentA: dict, parentB: dict):
    p = random.randint(1, genomeLength - 1)
    genomeA = build_child(parentA["genome"], parentB["genome"], p)
    genomeB = build_child(parentB["genome"], parentA["genome"], p)
    return {"genome": genomeA, "fitness": 0}, {"genome": genomeB, "fitness": 0}

def mutate(child: dict, rate: float) -> dict:
    genome = child["genome"].copy()
    sisa = vehicleStock.copy()
    for g in genome:
        sisa[g] -= 1

    for i in range(genomeLength):
        if random.random() < rate:
            if random.random() < 0.5:
                j = random.randint(0, genomeLength - 1)
                genome[i], genome[j] = genome[j], genome[i]
            else:
                baru = random.randint(0, 3)
                if sisa[baru] > 0:
                    sisa[genome[i]] += 1
                    sisa[baru] -= 1
                    genome[i] = baru
    return {"genome": genome, "fitness": 0}


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
def main():
    divider("GENETIC ALGORITHM")
    startPopulationNumber = int(input("Masukkan jumlah populasi awal: "))
    generationNumber = int(input("Masukkan jumlah generasi: "))

    sleep(1)
    divider("POPULASI AWAL")
    loading("Menghasilkan populasi awal sebanyak " + str(startPopulationNumber)+" genetik", 1)
    population = generate_population(startPopulationNumber)

    sleep(1)
    divider("KONDISI KAPAL AWAL")
    loading(f"Mengecek kondisi awal kapal", 1)
    print(f"Kondisi kapal ukuran {shipHeight} x {shipWidth} dengan kapasitas maksimal {shipMaxCapacity} ton:")
    print_matrix(shipMatrix)

    sleep(1)
    divider("FITNESS FUNCTION POPULASI")
    loading("Menghitung fitness function untuk tiap individu pada populasi", 1)
    for gen in population:  
        calculate_fitness(gen)
        print(f"Genetik: {gen['genome']}, Fitness: {gen['fitness']}")
        sleep(0.2)
        # print(f"Vehicles placed: {gen['vehicles_placed']}") 
        # print(f"Matriks kapal setelah penempatan kendaraan:")
        # print_matrix(shipMatrix)
        reset_ship()

    sleep(1)
    divider("ITERASI GENERASI")
    loading("Memulai iterasi untuk " + str(generationNumber) + " generasi", 1)
    for generation in range(generationNumber):
        sleep(1)
        divider(f"GENERASI {generation + 1}")          
        sleep(1)
        divider("PARENT")  
        loading(f"Memilih dua individu terbaik menjadi parent")      
        successors = calculate_successor(population)
        print(f"PARENT1:{successors[0]['genome']}\nPARENT2:{successors[1]['genome']}")

        sleep(1)
        divider("CROSSOVER")  
        loading("Menjalankan fungsi crossover pada parent", 1)
        children = crossover(successors[0], successors[1])
        for child in children:
            calculate_fitness(child)
            reset_ship()
        print(f"Memperoleh 2 children hasil crossover kedua parent")
        print(f"CHILD1:{children[0]['genome']}\nCHILD2:{children[1]['genome']}")
        population.extend(children)
        loading("Menambahkan children ke dalam populasi", 1)
        print(f"Berhasil menambahkan children ke dalam populasi, total populasi: {len(population)}") 

        sleep(1)
        divider("MUTATION")  
        loading(f"Menjalankan fungsi mutate pada children")
        mutatedChildren = [mutate(child, 0.1) for child in children]
        print(f"Memperoleh 2 mutated children hasil mutasi kedua child:")
        print(f"MUTATED1:{mutatedChildren[0]['genome']}\nMUTATED2:{mutatedChildren[1]['genome']}")
        population.extend(mutatedChildren)
        loading("Menambahkan mutated children ke dalam populasi", 1)
        print(f"Berhasil menambahkan mutated ke dalam populasi, total populasi: {len(population)}") 

    sleep(1)
    divider("ITERASI SELESAI")
    print(f"Iterasi untuk {generationNumber} generasi selesai, populasi akhir: {len(population)}")
    loading("Menghitung fitness function untuk tiap individu pada populasi akhir", 1)
    for gen in population:
        calculate_fitness(gen)
        print(f"Genetik: {gen['genome']}, Fitness: {gen['fitness']}")
        sleep(0.2)
        reset_ship()

    sleep(1)
    divider("BEST GENETIC")
    best = max(population, key=lambda gen: gen["fitness"])
    print(f"Fitness function tertinggi pada populasi akhir: {best['fitness']}")
    print(f"Diraih oleh individu dengan genetik: {best['genome']}")
    
    calculate_fitness(best)
    print_vehicle_tables(best["vehicles_placed"], best["vehicles_unplaced"])
    print(f"Matriks kapal setelah penempatan kendaraan:")
    print_matrix(shipMatrix)
    reset_ship()

if __name__ == "__main__":
    main()