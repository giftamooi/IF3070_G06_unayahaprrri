import time
import random

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


def calculate_weight():
    pass

def calculate_value():
    pass

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
        choosenVehicle.row = random.randint(0, 4)
        choosenVehicle.column = random.randint(0, 6)
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


