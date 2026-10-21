# genetic.py
from typing import List
from time import sleep
import random

# Pendefinisian variabel awal untuk algoritma 
shipWidth = 5
shipHeight = 7
shipMatrix = {(i, j): 0 for i in range(shipWidth) for j in range(shipHeight)} 
shipMaxCapacity = 100


startPopulationNumber = 3
generationNumber = 3

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

# Fungsi generate_genetic
# Digunakan untuk menghasilkan genetik individu acak 17 digit
def generate_genetic(p: population) -> None:
    individual = [random.randint(0, 3) for _ in range(17)] 
    sleep(1)  
    print(f"Mengasilkan gen: {individual}")  
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
            gen["vehicles_placed"].append(f"Vehicle {numberVehiclePlaced}: {vehicle['id']}")
            shipCurrWeight += vehicle["weight"]
            shippingFee += vehicle["shippingFee"]
    gen["fitness"] = shippingFee

def reset_ship() -> None:
    global shipMatrix
    shipMatrix = {(i, j): 0 for i in range(shipWidth) for j in range(shipHeight)}

# Fungsi visualisasi - print_matrix
def print_matrix(matrix: dict) -> None:
    for i in range(shipWidth):
        for j in range(shipHeight):
            print(matrix[(i, j)], end=" ")
        print()
    pass

def calculate_successor(population: population) -> list:
    totalFitness = 0
    for gen in population:
        totalFitness += gen["fitness"]

    for gen in population:
        chance = gen["fitness"] / totalFitness if totalFitness > 0 else 0
        gen["chance"] = chance


    successors = random.choices(population, weights=[gen["chance"] for gen in population], k=2)
    return successors

def crossover(parentA: dict, parentB: dict):
    p = random.randint(1, 16)
    genomeA = parentA["genome"][:p] + parentB["genome"][p:]
    genomeB = parentB["genome"][:p] + parentA["genome"][p:]
    return {"genome": genomeA, "fitness": 0}, {"genome": genomeB, "fitness": 0}

def mutate(child: dict, rate: float) -> dict:
    genome = child["genome"].copy()          
    for i in range(len(genome)):
        if random.random() < rate:
            genome[i] = random.randint(0, 3)
    return {"genome": genome, "fitness": 0}

# Fungsi main
def main():
    population = generate_population(startPopulationNumber)

    sleep(1)
    print(f"Matriks kapal awal:")
    print_matrix(shipMatrix)

    sleep(1)
    print(f"Calculating fitness...")
    sleep(1)
    for gen in population:  
        calculate_fitness(gen)
        print(f"Gen: {gen['genome']}, Fitness: {gen['fitness']}")
        # print(f"Vehicles placed: {gen['vehicles_placed']}") 
        # print(f"Matriks kapal setelah penempatan kendaraan:")
        # print_matrix(shipMatrix)
        reset_ship()
        sleep(1)

    for generation in range(generationNumber):
        print(f"Generation {generation + 1} / {generationNumber}, population size: {len(population)}")            
        successors = calculate_successor(population)
        print(f"Selected parents: {successors[0]['genome']} and {successors[1]['genome']}")
        print(f"Crossing over parents to produce children...")
            
        children = crossover(successors[0], successors[1])
        for child in children:
            calculate_fitness(child)
        reset_ship()

        print(f"Children produced: {children[0]['genome']} and {children[1]['genome']}")
        population.extend(children)
        print(f"Inserted children into population, current population: {len(population)}") 

        print(f"Mutating children...")
        mutatedChildren = [mutate(child, 0.1) for child in children]
        print(f"Mutated children: {mutatedChildren[0]['genome']} and {mutatedChildren[1]['genome']}")
        population.extend(mutatedChildren)
        print(f"Inserted mutated children into population, current population: {len(population)}") 

    

if __name__ == "__main__":
    main()