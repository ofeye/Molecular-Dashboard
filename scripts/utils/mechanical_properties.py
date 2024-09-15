def converKValue(text):
    if len(text)==len(str(int(text))):
        kValue=int(text)
    else:
        kValue=int(text)/(10**(len(text)-1))
    return kValue

def normYMCalc(youngModulus):
    return youngModulus/1020

def calculateVol(dimLow,dimHigh):
    return (dimHigh-dimLow)**3

def normDensityCalc(volumeInA,atomCount):
    angstromToCm=10**(-24)
    atomicToMg=1.66053907*(10**(-21))
    carbonWe=12.011
    atomWei=carbonWe*atomCount
    densityMgCm3=(atomWei*atomicToMg)/((volumeInA*angstromToCm))
    grapheneDens=2300
    return densityMgCm3,densityMgCm3/grapheneDens

def normStressCalc(actualStress):
    grapheneStre=130
    return float(actualStress)/grapheneStre