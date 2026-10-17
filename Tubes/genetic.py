# genetic.py
from typing import List
import random

# Pendefinisian variabel awal untuk algoritma 
shipDimensions = {(i, j): 0 for i in range(5) for j in range(7)} 
shipMaxCapacity = 100
populationNumber = 3 
generationNumber = 3 
genetic = List[int] 
population = List[genetic]
vehicles = {
    1: {"id": "mobil", "dimensions": (1, 2),"orientation": "horizontal", "shippingFee": 20, "weight": 5, "eta": 2},
    2: {"id": "minibus", "dimensions": (1, 3),"orientation": "horizontal", "shippingFee": 30, "weight": 12, "eta": 2},
    3: {"id": "truk", "dimensions": (2, 3),"orientation": "horizontal","shippingFee": 60, "weight": 30, "eta": 2}
}

# Fungsi generate_genetic
# Digunakan untuk menghasilkan genetik individu acak 17 digit
def generate_genetic(populationNumber: int) -> genetic:
    individual = [random.randint(0, 3) for _ in range(17)] 
    print(f"Mengasilkan gen: {individual}")  
    return individual   

# Fungsi generate_population
# Digunakan untuk menghasilkan populasi awal sebanyak populationNumber 
def generate_population(populationNumber: int) -> population:
    population = [generate_genetic(populationNumber) for _ in range(populationNumber)]
    print(f"Populasi: {population}")
    return population

# Fungsi insert_to_ship
def insert_to_ship(individual: genetic) -> None:
    pass

# Fungsi visualisasi - print_matrix
def print_matrix(matrix: dict) -> None:
    for i in range(5):
        for j in range(7):
            print(matrix[(i, j)], end=" ")
        print()

# Fungsi calculate_fitness
# Digunakan untuk menghitung nilai fitness dari setiap individu dalam populasi
def calculate_fitness(individual: genetic) -> int:
    calculatedGen = List[int]
    shippingFee = 0
    for i in individual:
        if i == 1 :
            shippingFee += vehicles[1]["shippingFee"]
            calculatedGen.append(i)
        elif i == 2 : 
            shippingFee += vehicles[2]["shippingFee"]
            calculatedGen.append(i)
        elif i == 3 :
            shippingFee += vehicles[3]["shippingFee"]
            calculatedGen.append(i)
        else : shippingFee += 0
        #BINGUNG
        pass


# Fungsi main
def main():
    population = generate_population(populationNumber)
    print_matrix(shipDimensions)

if __name__ == "__main__":
    main()