from os import listdir, getcwd, chdir, walk
from os.path import isfile, join, join, isdir, abspath, dirname
from re import search
import json

def get_file_path(surface1, surface2, a_val, h_perc, k_val):
    
    with open('data/json/surf_dict.json', 'r') as json_file:
        surf_dict = json.load(json_file)

    if surface1 == surface2: 
        surface2 = list(surf_dict.keys())[list(surf_dict.keys())!=surface1]
        k_val = '0'
        
    with open('data/json/variables.json', 'r') as json_file: main_folder_path = json.load(json_file)["analysis_files"]
    
    folder_name_arr = listdir(main_folder_path)

    search_pattern = f'{surf_dict[surface1]}_{surf_dict[surface2]}_{a_val}_{str(k_val).replace(".","")}_Perc{h_perc}'

    file_name =  folder_name_arr[next((i for i, s in enumerate(folder_name_arr) if search_pattern in s), -1)]

    print(file_name)
    return join(main_folder_path,file_name)

def findFilePath(startWith,endWith,current_dir=None):
    if current_dir==None:
        chdir(dirname(abspath(__file__)))
        mypath=getcwd()
    else:
        mypath=current_dir
    subFolders=[x for x in list(listdir(mypath)) if isdir(join(mypath,x))]
    filePathArr=[]
    for fol in range(len(subFolders)):
        subPath=join(mypath,subFolders[fol])
        allFiles = [f for f in listdir(subPath) if isfile(join(subPath,f))]
        for x in allFiles:
            if search("^{}.*{}$".format(startWith,endWith),x):
                fileName=x
                filePathArr.append(join(mypath,subFolders[fol],fileName))
    return filePathArr

def getSingleData(xCol,yCol,FilePath):
    dataFile=open(FilePath,"r").read()
    dataList=[x.split(" ") for x in list(dataFile.split("\n"))]
    return float(dataList[xCol-1][yCol-1])

def getDataS(timeStep, filePath):
    dataFile = open(filePath, "r").read()
    dataList = [x.split() for x in dataFile.split("\n")]
    numberOfSteps = dataList.count(['ITEM:', 'TIMESTEP'])
    dataLen = int((len(dataList) - 1) / numberOfSteps)
    timeStepData = dataList[(((timeStep - 1) * dataLen) + 9):timeStep * dataLen]
    return timeStepData

def getDataSRealSize(timeStep, filePath):
    dataFile = open(filePath, "r").read()
    dataList = [x.split() for x in dataFile.split("\n")]
    numberOfSteps = dataList.count(['ITEM:', 'TIMESTEP'])
    dataLen = int((len(dataList) - 1) / numberOfSteps)
    sizeData = dataList[(((timeStep - 1) * dataLen)):(((timeStep - 1) * dataLen) + 8)]
    size_data = [[float(y) for y in x] for x in sizeData[5:]]
    timeStepData = dataList[(((timeStep - 1) * dataLen) + 9):timeStep * dataLen]
    sizes = [x[1]-x[0] for x in size_data]
    timestep_data_edited = [[x[0],x[1],float(x[2])*sizes[0]+size_data[0][0],float(x[3])*sizes[1]+size_data[1][0],float(x[4])*sizes[2]+size_data[2][0]] for x in timeStepData]
    return timestep_data_edited

def find_with_extension(directory, extension):
    # List to store files with the given extension
    files_with_extension = []
    
    # Walk through the directory
    for root, dirs, files in walk(directory):
        for file in files:
            # Check if the file has the desired extension
            if file.endswith(extension):
                files_with_extension.append(join(root, file))
    
    # Check if no files or more than one file are found
    if len(files_with_extension) == 0:
        raise FileNotFoundError(f"No files with extension {extension} found in {directory}")
    elif len(files_with_extension) > 1:
        raise Exception(f"More than one file with extension {extension} found in {directory}")
    
    # Return the single file
    return files_with_extension[0]
    
def read_json_file(file_path):
    with open(file_path, 'r') as json_file: data = json.load(json_file)
    return data

def dump_json_file(file_path,dict):
    with open(file_path, 'w') as json_file: json.dump(dict, json_file, indent=4)


def update_db_dir(new_file_path):
    data = read_json_file('data/json/variables.json')
    data['database'] = new_file_path
    dump_json_file('data/json/variables.json',data)
