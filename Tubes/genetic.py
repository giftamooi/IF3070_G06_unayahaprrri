# genetic.py
from typing import List, Dict, Union
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
            if shipMatrix[(i, j)] == 1:
                continue
            if i + vehicleWidth > shipWidth or j + vehicleHeight > shipHeight:
                continue
            canplace = True
            for k in range(vehicleWidth):
                for l in range(vehicleHeight):
                    if shipMatrix[(i + k, j + l)] == 1:
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
    spaceUsed = 0
    numberVehiclePlaced = 0;
    for gene in gen["genome"]:
        if gene == 0:
            continue
        vehicle = vehicles[gene]
        canPlace, positionX, positionY = check_space(vehicle)
        if not canPlace:
            rotatedVehicle = rotate_vehicle(vehicle)
            canPlace, positionX, positionY = check_space(rotatedVehicle)
            if canPlace and shipCurrWeight + rotatedVehicle["weight"] <= shipMaxCapacity:
                numberVehiclePlaced += 1
                place_vehicle(rotatedVehicle, positionX, positionY, numberVehiclePlaced)
                gen["vehicles_placed"].append(f"Vehicle {numberVehiclePlaced}: {vehicle['id']}")
                shipCurrWeight += rotatedVehicle["weight"]
                shippingFee += rotatedVehicle["shippingFee"]
                spaceUsed += rotatedVehicle["dimensions"][0] * rotatedVehicle["dimensions"][1]
            else:
                continue
        else:
            continue
    fitness = shippingFee + spaceUsed
    gen["fitness"] = fitness
    gen["vehicles_placed"] = numberVehiclePlaced 

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
        reset_ship()
        sleep(1)

if __name__ == "__main__":
    main()