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

def get_strain_energy(stressList,strainList): 
    max_index=stressList.index(max(stressList))

    strain_energy=0
    for ind in range(1,len(stressList)):
        ort_stress=(stressList[ind]+stressList[ind-1])/2
        thickness=(strainList[ind]-strainList[ind-1])
        
        strain_energy+=ort_stress*thickness
        
        if ind==max_index:
            elastic_strain_energy=strain_energy
    return elastic_strain_energy,strain_energy

def normalize_dataFrame(df_path,save_path=None):
    df = pd.read_csv(df_path)
    df['k_Value']=df['k_Value'].astype(float)

    compdf=df[df['k_Value']==0][["Geom1","length","Density","Norm_Density","Max_Stress","Young_Modulus","Elastic_Strain_Energy","Strain_Energy"]].drop_duplicates()
    #dfHybrid=df[df['k_Value']!=0]
    dfHybrid=df.copy()
    
    if len(compdf)!=12:
        print('Some non hybrid values are diffrent.')
        quit()

    max_stress_geom1=[]
    max_stress_geom2=[]
    max_young_geom1=[]
    max_young_geom2=[]
    el_strain_en_geom1=[]
    el_strain_en_geom2=[]
    strain_en_geom1=[]
    strain_en_geom2=[]
    dens_geom1=[]
    dens_geom2=[]

    for index, row in dfHybrid.iterrows():
        max_stress_geom1.append(float(compdf[(compdf['Geom1']==row['Geom1']) & (compdf['length']==row['length'])]['Max_Stress']))
        max_stress_geom2.append(float(compdf[(compdf['Geom1']==row['Geom2']) & (compdf['length']==row['length'])]['Max_Stress']))
        max_young_geom1.append(float(compdf[(compdf['Geom1']==row['Geom1']) & (compdf['length']==row['length'])]['Young_Modulus']))
        max_young_geom2.append(float(compdf[(compdf['Geom1']==row['Geom2']) & (compdf['length']==row['length'])]['Young_Modulus']))
        el_strain_en_geom1.append(float(compdf[(compdf['Geom1']==row['Geom1']) & (compdf['length']==row['length'])]['Elastic_Strain_Energy']))
        el_strain_en_geom2.append(float(compdf[(compdf['Geom1']==row['Geom2']) & (compdf['length']==row['length'])]['Elastic_Strain_Energy']))
        strain_en_geom1.append(float(compdf[(compdf['Geom1']==row['Geom1']) & (compdf['length']==row['length'])]['Strain_Energy']))
        strain_en_geom2.append(float(compdf[(compdf['Geom1']==row['Geom2']) & (compdf['length']==row['length'])]['Strain_Energy']))
        dens_geom1.append(float(compdf[(compdf['Geom1']==row['Geom1']) & (compdf['length']==row['length'])]['Density']))
        dens_geom2.append(float(compdf[(compdf['Geom1']==row['Geom2']) & (compdf['length']==row['length'])]['Density']))

    dfHybrid['max_stress_geom1']=np.array(max_stress_geom1)
    dfHybrid['max_stress_geom2']=np.array(max_stress_geom2)
    dfHybrid['max_young_geom1']=np.array(max_young_geom1)
    dfHybrid['max_young_geom2']=np.array(max_young_geom2)
    dfHybrid['el_strainEn_geom1']=np.array(el_strain_en_geom1)
    dfHybrid['el_strainEn_geom2']=np.array(el_strain_en_geom2)
    dfHybrid['strainEn_geom1']=np.array(strain_en_geom1)
    dfHybrid['strainEn_geom2']=np.array(strain_en_geom2)
    dfHybrid['density_geom1']=np.array(dens_geom1)
    dfHybrid['density_geom2']=np.array(dens_geom2)
    
    
    dfHybrid['norm_stress_geom1']=dfHybrid['Max_Stress']/dfHybrid['max_stress_geom1']
    dfHybrid['norm_stress_geom2']=dfHybrid['Max_Stress']/dfHybrid['max_stress_geom2']
    dfHybrid['norm_young_geom1']=dfHybrid['Young_Modulus']/dfHybrid['max_young_geom1']
    dfHybrid['norm_young_geom2']=dfHybrid['Young_Modulus']/dfHybrid['max_young_geom2']
    
    dfHybrid['norm_elEn_geom1']=dfHybrid['Elastic_Strain_Energy']/dfHybrid['el_strainEn_geom1']
    dfHybrid['norm_elEn_geom2']=dfHybrid['Elastic_Strain_Energy']/dfHybrid['el_strainEn_geom2']
    dfHybrid['norm_Ener_geom1']=dfHybrid['Strain_Energy']/dfHybrid['strainEn_geom1']
    dfHybrid['norm_Ener_geom2']=dfHybrid['Strain_Energy']/dfHybrid['strainEn_geom2']
    
    dfHybrid['norm_dens_stress_geom1']=dfHybrid['norm_stress_geom1']/(dfHybrid['Density']/dfHybrid['density_geom1'])
    dfHybrid['norm_dens_stress_geom2']=dfHybrid['norm_stress_geom2']/(dfHybrid['Density']/dfHybrid['density_geom2'])
    dfHybrid['norm_dens_young_geom1']=dfHybrid['norm_young_geom1']/(dfHybrid['Density']/dfHybrid['density_geom1'])
    dfHybrid['norm_dens_young_geom2']=dfHybrid['norm_young_geom2']/(dfHybrid['Density']/dfHybrid['density_geom2'])
    
    dfHybrid['norm_dens_elEn_geom1']=dfHybrid['norm_elEn_geom1']/(dfHybrid['Density']/dfHybrid['density_geom1'])
    dfHybrid['norm_dens_elEn_geom2']=dfHybrid['norm_elEn_geom2']/(dfHybrid['Density']/dfHybrid['density_geom2'])
    dfHybrid['norm_dens_Ener_geom1']=dfHybrid['norm_Ener_geom1']/(dfHybrid['Density']/dfHybrid['density_geom1'])
    dfHybrid['norm_dens_Ener_geom2']=dfHybrid['norm_Ener_geom2']/(dfHybrid['Density']/dfHybrid['density_geom2'])

    if save_path==None:
        absPath=getcwd()
        save_path_norm=join(absPath,"out_files",'Normalized','out_{}.csv'.format(date()))
    else:
        save_path_norm=save_path
        
    dfHybrid.to_csv(save_path_norm) 
    
    return save_path_norm