# genetic.py
from typing import List
from time import sleep, time
import random

# Pendefinisian variabel awal untuk algoritma 
# shipWidth, shipHeight dan shipMaxCapacity
shipWidth = 5
shipHeight = 7
shipMatrix = {(i, j): 0 for i in range(shipWidth) for j in range(shipHeight)} 
shipMaxCapacity = 100

# Populasi adalah list dari genetik [dengan representasi dict]
population = List[dict]

# Vehicles adalah pendefinisian tipe kendaraan yang ada
# dibatasi menjadi tiga jenis yaitu Mobil, Minibus, dan Truk
vehicles = {
    1: {"id": "mobil", "dimensions": (1, 2),"orientation": "horizontal", "shippingFee": 20, "weight": 5, "eta": 2},
    2: {"id": "minibus", "dimensions": (1, 3),"orientation": "horizontal", "shippingFee": 30, "weight": 12, "eta": 2},
    3: {"id": "truk", "dimensions": (2, 3),"orientation": "horizontal","shippingFee": 60, "weight": 30, "eta": 2}
}

# Pendefinisian stock mobil
# emptyslots agar genome bisa memiliki digit 0
# Digit 0 menandakan slot kosong
emptySlots = 8
vehicleStock = {1: 20, 2: 7, 3: 5, 0: emptySlots}

# genomeLength adalah jumlah kendaraan terbanyak
# Terkecil = mobil, maksimum mobil = 17
genomeLength = 17

# Fungsi generate_genetic
# Digunakan untuk menghasilkan genetik
def generate_genetic(p: population) -> None:
    pool = []
    # Generation memperhatikan jumlah stock kendaraan yang ada
    for code, amount in vehicleStock.items():
        pool += [code] * amount
    # Mengambil dari pool sebanyak genomeLength
    individual = random.sample(pool, genomeLength)
    print(f"Menghasilkan: {individual}")
    p.append({"genome": individual, "fitness": 0})

# Fungsi generate_population
# Digunakan untuk menghasilkan populasi awal sebanyak startPopulationNumber 
def generate_population(startPopulationNumber: int) -> population:
    population = []
    # Memanggil fungsi generate_genetic
    for _ in range(startPopulationNumber):
        generate_genetic(population)
        sleep(0.2)
    return population

# Fungsi check_space
# Digunakan untuk memeriksa apakah kendaraan muat di dalam kapal
def check_space(vehicle: dict):
    vehicleWidth = vehicle["dimensions"][0]
    vehicleHeight = vehicle["dimensions"][1]
    positionX = 0;
    positionY = 0;
    canplace = False
    # Mengecek setiap koordinat i, j pada kapal
    for i in range(shipWidth):
        for j in range(shipHeight):
            # Jika koordinat terisi, skip
            if shipMatrix[(i, j)] != 0:
                continue
            # Jika koordinat mentok (sudah tidak muat kendaraan), skip
            if i + vehicleWidth > shipWidth or j + vehicleHeight > shipHeight:
                continue
            canplace = True
            # Jika koordinat kosong, koordinat sekitarnya
            # juga dicek sesuai size kendaraan yang akan di place
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
# Digunakan untuk merotasi copy of kendaraan
# dari horizontal ke vertikal atau sebaliknya
def rotate_vehicle(vehicle: dict) -> dict:
    rotatedVehicle = vehicle.copy()
    rotatedVehicle["dimensions"] = (vehicle["dimensions"][1], vehicle["dimensions"][0])
    rotatedVehicle["orientation"] = "vertical" if vehicle["orientation"] == "horizontal" else "horizontal"
    return rotatedVehicle

# Fungsi place_vehicle
# Digunakan untuk menaruh vehicle setelah di check
def place_vehicle(vehicle: dict, positionX: int, positionY: int, vehicleCode: int) -> None:
    vehicleWidth = vehicle["dimensions"][0]
    vehicleHeight = vehicle["dimensions"][1]
    for i in range(vehicleWidth):
        for j in range(vehicleHeight):
            shipMatrix[(positionX + i, positionY + j)] = vehicleCode

# Fungsi calculate_fitness
# Digunakan untuk menghitung fitness function dari
# genome pada populasi
def calculate_fitness(gen: dict):
    shipCurrWeight = 0
    shippingFee = 0
    numberVehiclePlaced = 0
    placedCount = {1: 0, 2: 0, 3: 0}
    gen["vehicles_placed"] = []
    # Mengiterasikan setiap digit dari genome
    for gene in gen["genome"]:
        if gene == 0:
            continue
        # Jika digit tidak 0, panggil fungsi check_space
        vehicle = vehicles[gene]
        canPlace, positionX, positionY = check_space(vehicle)
        # Kalau masih belum bisa di place, coba di rotate
        if not canPlace:
            vehicle = rotate_vehicle(vehicle)
            canPlace, positionX, positionY = check_space(vehicle)
        # Jika bisa dan weight dari ship masih memadai, panggil place_vehicle
        if canPlace and shipCurrWeight + vehicle["weight"] <= shipMaxCapacity:
            numberVehiclePlaced += 1
            placedCount[gene] += 1
            place_vehicle(vehicle, positionX, positionY, numberVehiclePlaced)
            gen["vehicles_placed"].append((numberVehiclePlaced, vehicle["id"]))
            shipCurrWeight += vehicle["weight"]
            shippingFee += vehicle["shippingFee"]
    # Menghitung vehicles yang tidak di place juga
    # Untuk mengetahui sisa stock kendaraan 
    gen["vehicles_unplaced"] = []
    for code in (1, 2, 3):
        sisa = vehicleStock[code] - placedCount[code]
        if sisa > 0:
            gen["vehicles_unplaced"].append((f"{sisa}x", vehicles[code]["id"]))
    gen["fitness"] = shippingFee

# Fungsi reset_ship
# Digunakan mengosongkan kendaraan pada ship 
def reset_ship() -> None:
    global shipMatrix
    shipMatrix = {(i, j): 0 for i in range(shipWidth) for j in range(shipHeight)}

# Fungsi print_matrix (visualisasi)
# Digunakan untuk memunjukkan kondisi ship
# dan posisi kendaraan yang ada
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

# Fungsi calculate_successor
# Digunakan untuk mencari suksesor dari populasi untuk menjadi parent
def calculate_successor(population: population) -> list:
    totalFitness = 0
    for gen in population:
        totalFitness += gen["fitness"]
    # chance adalah probabilitas genome terpilih sebagai suksesor
    for gen in population:
        chance = gen["fitness"] / totalFitness if totalFitness > 0 else 0
        gen["chance"] = chance
    parent1 = random.choices(population, weights=[gen["chance"] for gen in population], k=1)[0]
    # mencari kandidat parent 2 yang tidak sama dengan parent 1
    candidateParent2 = [gen for gen in population if gen["genome"] != parent1["genome"]]
    if len(candidateParent2) == 0:
        return [parent1, parent1]
    chanceParent2 = [gen["chance"] for gen in candidateParent2]
    if sum(chanceParent2) == 0:
        parent2 = random.choice(candidateParent2)
    else:
        parent2 = random.choices(candidateParent2, weights=chanceParent2, k=1)[0]
    return [parent1, parent2]

# Fungsi build_child
# Digunakan untuk mengenerate hasill crossover nanti
# Generate anak dengan stock handlingnya
def build_child(first: list, second: list, p: int) -> list:
    genome = first[:p] + second[p:]
    # Mengecek stock dari vehicle dari genome
    leftovers = vehicleStock.copy()
    for i in range(genomeLength):
        g = genome[i]
        if leftovers[g] > 0:
            leftovers[g] -= 1
        else:
            # Jika stok jenis suatu habis, maka
            # ganti dengan jenis yang masih tersisa pada stock
            leftoverDigit = [c for c in leftovers if leftovers[c] > 0]
            newDigit = random.choice(leftoverDigit)
            genome[i] = newDigit
            leftovers[newDigit] -= 1
    return genome


# Fungsi crossover
# Digunakan untuk menukar sekian digit parentA dan B (crossing over)
# Memanggil build_child untuk memastikan anak yang di generate sesuai stock vehicle
def crossover(parentA: dict, parentB: dict):
    p = random.randint(1, genomeLength - 1)
    genomeA = build_child(parentA["genome"], parentB["genome"], p)
    genomeB = build_child(parentB["genome"], parentA["genome"], p)
    return {"genome": genomeA, "fitness": 0}, {"genome": genomeB, "fitness": 0}

# Fungsi mutate
# Digunakan untuk memutasi salah satu digit random dari genome
# Mutasi memperhatikan sisa stock mobil
def mutate(child: dict, rate: float) -> dict:
    genome = child["genome"].copy()
    leftovers = vehicleStock.copy()
    for g in genome:
        leftovers[g] -= 1
    for i in range(genomeLength):
        if random.random() < rate:
            if random.random() < 0.5:
                j = random.randint(0, genomeLength - 1)
                genome[i], genome[j] = genome[j], genome[i]
            else:
                # Memastikan digit baru mutasi memenuhi stok vehicle
                newDigit = random.randint(0, 3)
                if leftovers[newDigit] > 0:
                    leftovers[genome[i]] += 1
                    leftovers[newDigit] -= 1
                    genome[i] = newDigit
    return {"genome": genome, "fitness": 0}

# Fungsi loading (visualisasi)
# Digunakan untuk membuat loading pada CLI menjadi lebih rapi
def loading(message: str, seconds: float = 1.5) -> None:
    frames = ["   ", ".  ", ".. ", "..."]
    endTime = time() + seconds
    i = 0
    while time() < endTime:
        print(f"\r{message}{frames[i % 4]}", end="", flush=True)
        sleep(0.3)
        i += 1
    print(f"\r{message}...")   

# Fungsi input_integer (helper)
# Digunakan untuk memastikan input tidak salah
# input integer dan wajib minimal sekian
def input_integer(prompt: str, minimum: int) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value >= minimum:
                return value
            print(f"Masukkan angka minimal {minimum}.")
        except ValueError:
            print("Input harus berupa angka bulat.")

# Fungsi main
def main():
    divider("GENETIC ALGORITHM")
    startPopulationNumber = input_integer("Masukkan jumlah populasi awal: ", 2) # Minimum 2 populasi awal
    generationNumber = input_integer("Masukkan jumlah generasi: ", 1) # Minimum 1 generasi iterasi

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
        loading(f"Memilih dua individu sesuai chance untuk menjadi parent")      
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
        for mutant in mutatedChildren:
            calculate_fitness(mutant)
            reset_ship()
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