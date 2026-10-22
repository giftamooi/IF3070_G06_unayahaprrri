import time
import random
import copy

# data geladak kapal
shipWidth = 5
shipLength = 7
shipMatrix = {(i, j): 0 for i in range(shipWidth) for j in range(shipLength)} 
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
     


def calculate_fee(vehicles):
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
                if(c[0] < 0 or c[0] > 4 or c[1] < 0 or c[1] > 6):
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
    startTime = time.time()
    current = vehicles
    currentFee = calculate_fee(vehicles)
    iterations = 0
    history = [currentFee]

    while True:
        successors = successor_maker(current)
        if(successors == []):
            break

        bestSucc = None
        bestFee = -1
        for s in successors:
            successorFee = calculate_fee(s)
            if(successorFee > bestFee):
                bestFee = successorFee
                bestSucc = s

        if bestFee <= currentFee:
            break    
        else: 
            current = bestSucc
            currentFee = bestFee
            iterations += 1   # penghitungan iterasi tidak termasuk iterasi terakhir yang gagal
            history.append(currentFee)

    duration = time.time() - startTime
    return current, iterations, duration, history

        


def main():
    pass



if __name__ == "__main__":
    main()

