import pandas as pd
from os import  getcwd, chdir
from os.path import  join, realpath, join, pardir, abspath, dirname
from re import X, search
from scripts.utils.mechanical_properties import *
from scripts.utils.file_utils import *
from scripts.utils.progress_bar import *
from scripts.utils.get_date import *



def getData(dataDict,StressFilePathArr,GeomFilePathArr,spesificStrainRate):
    l=len(StressFilePathArr)
    for i,filePath in enumerate(StressFilePathArr):
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
        titleName=filePath.split("/")[-2]
        dataFile=open(filePath,"r").read()
        dataList=[x.split(" ") for x in list(dataFile.split("\n"))]
        parentPath=join(filePath, pardir)
        parPath=realpath(parentPath)
        strainList=[float(dataList[x][0])-float(dataList[1][0]) for x in range(1,len(dataList)-1)]
        stressList=[float(dataList[x][1])-float(dataList[1][1]) for x in range(1,len(dataList)-1)]
        stepNumAtSSR=round(len(strainList)/(max(strainList)/spesificStrainRate))
        try:
            privateKey=int(titleName.split('_')[0])
            hybrid=titleName.split('_')[1]=="Hybrid"
            geom1=titleName.split('_')[2]
            geom2=titleName.split('_')[3]
            length=titleName.split('_')[4]
            kValue=converKValue(titleName.split('_')[5])
            hybPerc=int(titleName.split('_')[6].replace("Perc",""))
            hybCellCnt=int(titleName.split('_')[7])
            nonHybCellCnt=int(titleName.split('_')[8])
            dimLow=getSingleData(5,1,GeomFilePathArr[i])
            dimHigh=getSingleData(5,2,GeomFilePathArr[i])
            maxStress=max(stressList)
            strainAtMaxStress=strainList[stressList.index(maxStress)]
            atomCount=getSingleData(2,1,GeomFilePathArr[i])
            strainatSSR=strainList[stepNumAtSSR]
            stressAtSSR=stressList[stepNumAtSSR]
            volume=calculateVol(dimLow,dimHigh)
            density,normDens=normDensityCalc(volume,atomCount)
            normStress=normStressCalc(maxStress)
            youngModulus=stressAtSSR/strainatSSR
            normYM=normYMCalc(youngModulus)
            

            dataDict["Private_Key"].append(privateKey)
            dataDict["Hybrid"].append(hybrid)
            dataDict["Geom1"].append(geom1)
            dataDict["Geom2"].append(geom2)
            dataDict["length"].append(length)
            dataDict["k_Value"].append(kValue)
            dataDict["Hybrid_Perc"].append(hybPerc)
            dataDict["NonHyb_Cell_Count"].append(nonHybCellCnt)
            dataDict["Hyb_Cell_Count"].append(hybCellCnt)
            dataDict["TotalAtom"].append(atomCount)
            dataDict["DimLow"].append(dimLow)
            dataDict["DimHigh"].append(dimHigh)
            dataDict["Volume"].append(volume)
            dataDict["Density"].append(density)
            dataDict["Norm_Density"].append(normDens)
            dataDict["Max_Stress"].append(maxStress)
            dataDict["Norm_Stress"].append(normStress)
            dataDict["Strain_At_Max_Stress"].append(strainAtMaxStress)
            dataDict["Strain_At_SSR"].append(strainatSSR)
            dataDict["Stress_At_SSR"].append(stressAtSSR)
            dataDict["Young_Modulus"].append(youngModulus)
            dataDict["Norm_Young_Modulus"].append(normYM)
            dataDict["Folder"].append(parPath)
            dataDict["Geom_File"].append(GeomFilePathArr[i])
            dataDict["Stress_File"].append(parentPath)
            

        except:
            print("{} does not have all data.".format(titleName))
    return dataDict

def save_dataset():
    variables = read_json_file('data/json/variables.json')
    keyList = variables['keylist']

    dataDict = {}

    for i in keyList:
        dataDict[i] = []


    workin_dir = variables['analysis_files']
    filePathArr = findFilePath('stress','out',workin_dir)
    GeomfilePathArr = findFilePath('','dat',workin_dir)

    dataDict=getData(dataDict,filePathArr,GeomfilePathArr,0.05)

    dataDictDF=pd.DataFrame(dataDict,columns=keyList,index=dataDict["Private_Key"])
    dataDictDF=dataDictDF.sort_values(by=['Private_Key'])

    file_path = join('data/database',f'out_{date()}.csv')

    dataDictDF.to_csv(file_path)

    update_db_dir(file_path)