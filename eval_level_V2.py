#Esta nueva version del paquete eval_level considera dos tipos de motivacion
#debida a dos tipos de recompensa:
# - recompensa_puntos y -recompensa_nivel
#La primera se relaciona con las bonificaciones, todos aquellos puntos obtenidos por
#interactuar con comida, enemigos, etc.
#La segunda se relaciona con los marcadores de nivel e intenta reflejarse
#la motivación por terminar el nivel


import numpy as np
import json
import copy
from pickle import dump, dumps, load, loads
import configPenguin
path = "/home/beto/Documentos/GameCreater/Test/levelsP"


# In[2]:


def leerMapa(archivo):
    with open(archivo) as json_data:
        d = json.load(json_data)
        data = json.dumps(d)
        mapa = json.loads(data)
    return mapa                   


# In[3]:


def revisaPuntos(punto, objetos):
    """Funcion auxiliar para verificar que un punto en la inspeccion 
    se encuentra o no contenido en algún objeto"""
    indicador = False
    for obj in objetos:
        for puntos in obj["puntos"]:                    
            if str(puntos[0]) == str(punto[0]) and str(puntos[1])==str(punto[1]):
                indicador = True
    
    return indicador
    


# In[4]:


def llena(lista,filaIni, filaFin, colIni, colFin):
    """
    Función auxiliar para llenar la huella y trayetcoria de plataformas 
    moviles, enemigos o en general bloques que ocupan más espacio
    """
    #Se le suma 1 a los limites superiores ya que el punto (filaFin,colFin) debe incluirse en el 
    for i in range(filaIni,filaFin+1): 
        for j in range(colIni,colFin+1):
            lista.append([str(i),str(j)])


# In[5]:


def detectaPlataformas(mapa, filename):     
    """
    --------------------------------------------------------------------------------------------------------------
    Esta funcion busca en la matriz de bloques del mapa, conjuntos de bloques que puedan ser agrupados para 
    formar un objeto y los codifica en un json.
    El json contiene los campos:
    - Id de bloque (numero consecutivo)
    - Tipo {piso, obstaculo, rebote, enemigo, enemigos, comida, sub-mision, meta, checkpoint, inicio}
    - Inicio [y,x] (esquina superior izquierda en la matriz de mapa) 
    - Grado de alcanzabilidad (este no se define en esta función, se da un valor por default = 0)        
    - Lista de puntos que lo forman
    - Lista de puntos de contorno (vacia) 
    - Lista de bloques alcanzables (alcanza)(anotando punto(s) de origen del bloque) (vacia)
    - Lista de bloques que lo alcanzan (alcanzado_por) (anotando punto(s) de destino en el bloque) (vacia)
    - Lista de puntos de paredes
    - Lista de puntos de piso
    - Lista de puntos de techo
    - Lista de puntas o esquinas del objeto
    --------------------------------------------------------------------------------------------------------------
    """
    #Creamos el diccionario para guardar la información a nivel de bloques para funcionalidad del nivel
    data = {"nivel":filename, "objetos":[]}
    
    i = 0; past_i = 0; cont_i = 0
    j = 0; past_j = 0; cont_j = 0
    id_bloque = 0    
    visitados = []
    #continuo_y = True
      
    finished = False
    #while(not finished):
    while(not finished):
        detect=False
        points=[]
    
        #Basado en la definición de distancia maxima en la bitacora de diseño    
        #Lim longitud de salto = 14
        limMax_x = 13 
        #Lim de altura de salto = 5
        limMax_y = 6 
        aux_type = ""
        dato ={}
       # print("Iniciando revision...")
        for fila in mapa:
            for columna in mapa[fila]:
               # print(fila, columna)
                #if mapa[fila][columna]!='x':
                    #print("Bloque: ", mapa[fila][columna],"detectado en (", fila,",", columna,")" )
                flag = revisaPuntos([fila,columna],data["objetos"] )
              #  if(flag):
               #     print("punto [",fila,columna,"]", "encontrado en ", data["objetos"])
               # else:
                #    print("punto [",fila,columna,"]", "no encontrado en ", data["objetos"])
                if mapa[fila][columna]!='x' and not(flag):
                    aux_type = str(mapa[fila][columna])                                        
                    initx = str(columna)
                    inity = str(fila)                    
                    #points.append([inity,initx])
                    detect = True
                  #  print("Bloque: ", mapa[inity][initx],"detectado en (", inity,",", initx,")" )                 
                    
                if (int(fila)==len(mapa)-1) and (int(columna) == len(mapa['0'])-1):
        #            print("Terminando revision ... ", int(fila), int(columna))
                    finished = True
                if(detect):
                  #  print("Interrumpiendo revision de columna por bloque detectado...")
                    break    
                    
            if(detect):
                #print("Interrumpiendo revision de fila por bloque detectado...")
                break
                        
        if detect:
            adyacentes = []
            contorno = []
            piso = []
            paredes = []
            techo = []
            puntasD = []
            puntasI = []
            continuo = True    
            #Para los bloques moviles y los enemigos surgen los siguientes componentes
            huella = [] #Es el espacio que la plataforma ocupa en realidad en pantalla, a partir del punto inicial en la matriz
            trayectoria = [] #Es el espacio total de bloques de la matriz de mapa que va a ocupar a lo largo de su movimiento
            fil = int(inity)
            col = int(initx)
            adyacentes.append([str(fil), str(col)])
            while(adyacentes!=[]):
                #Tomamos un elemento de la lista de adyacentes
                aux_point = adyacentes.pop()
                visitados.append(aux_point)
                fil = int(aux_point[0])
                col = int(aux_point[1])
                points.append(aux_point)                
                for i in range(-1,2):
                    for j in range(-1,2):
                        #Debe estar en los límites de la matriz del nivel
                        if(fil+i < len(mapa)) and (fil+i>=0) and (col+j>=0) and (col+j <len(mapa["0"])) :
                            if (str(mapa[str(fil+i)][str(col+j)])==aux_type) or ((aux_type=="i") and str(mapa[str(fil+i)][str(col+j)])=="iS") or ((aux_type=="iS") and str(mapa[str(fil+i)][str(col+j)])=="i") or ((aux_type=="f") and str(mapa[str(fil+i)][str(col+j)])=="fS") or ((aux_type=="fS") and str(mapa[str(fil+i)][str(col+j)])=="f"):
                                if(not [str(fil+i), str(col+j)] in visitados):
                                    adyacentes.append([str(fil+i),str(col+j)])
                                    visitados.append([str(fil+i),str(col+j)])
                                                
            #Detectamos el contorno del bloque detectado
            for bloque in points:
                agregado = False
                aux_x = int(bloque[1])
                aux_y = int(bloque[0])
                
                if bloque[0]=="0" and not bloque in contorno:
                    contorno.append(bloque)
                    agregado = True
                
                if bloque[0]==str((len(mapa)-1)) and not bloque in contorno:
                    contorno.append(bloque)
                    agregado = True
                
                if bloque[1]=="0" and not bloque in contorno:
                    contorno.append(bloque)
                    agregado = True
                
                if bloque[1]==str((len(mapa["0"])-1)) and not bloque in contorno:
                    contorno.append(bloque)
                    agregado = True
                    
                if not agregado:
                    
                    #Techo
                    if [str(int(aux_y+1)),str(int(aux_x))]not in points and not bloque in contorno:
                        contorno.append(bloque)
                                            
                    #Piso
                    elif [str(int(aux_y-1)),str(int(aux_x))]not in points and not bloque in contorno:
                        contorno.append(bloque)                                        
                    
                    #Pared por la derecha
                    elif [str(int(aux_y)),str(int(aux_x+1))] not in points and not bloque in contorno:
                        contorno.append(bloque)
                                                                    
                    #pared por la izquierda
                    elif [str(int(aux_y)),str(int(aux_x-1))]not in points and not bloque in contorno:
                        contorno.append(bloque)
        
            #Buscamos en el contorno los bloques de piso, puntas, techo y paredes
            for c in contorno:
                agregado = False
                aux_x = int(c[1])
                aux_y = int(c[0])
                
                if c[0]=="0" :            
                    piso.append(c)                
    
                if c[0]==str((len(mapa)-1)):
                    techo.append(c)                

                if c[1]=="0":
                    paredes.append(c)                

                if c[1]==str((len(mapa["0"])-1)):
                    paredes.append(c)                  
                    
                #Techo
                if aux_y+1< (len(mapa)-1):
                    if [str(int(aux_y+1)),str(int(aux_x))]not in points:
                        techo.append(c)

                #Piso
                if aux_y-1 >=0:
                    if [str(int(aux_y-1)),str(int(aux_x))]not in points:
                        piso.append(c)                
                                        
                #Pared por la derecha
                if aux_x+1 < len(mapa["0"]):
                    if [str(int(aux_y)),str(int(aux_x+1))] not in points and not c in paredes:
                        paredes.append(c)

                #pared por la izquierda
                if aux_x-1 >0:
                    if [str(int(aux_y)),str(int(aux_x-1))]not in points and not c in paredes:
                        paredes.append(c)
                        
            
            #Definimos el tipo de bloque que se detectó
            if aux_type=="i" or aux_type=="iS":
                dato["tipo"] = "piso"
                dato["riesgoNatural"] = 0  
                #Generamos una recompensa base para la plataforma
                dato["recompensa_puntos"] = 0 
                dato["recompensa_nivel"] = 0 
                
                
            elif aux_type=="rv" or aux_type=="rv1" or aux_type=="rh" or aux_type=="rh1":
                dato["tipo"] = "movil"
                dato["riesgoNatural"] = 0.2                
                #Generamos una recompensa base para la plataforma
                dato["recompensa_puntos"] = 0 
                dato["recompensa_nivel"] = 0 
                
            elif aux_type=="f" or aux_type=="fS":
                dato["tipo"] = "obstaculo"
                dato["riesgoNatural"] = 0.5
                #Generamos una recompensa base para la plataforma
                dato["recompensa_puntos"] = 0 
                dato["recompensa_nivel"] = 0 
                
            elif aux_type=="b":
                dato["tipo"] = "rebote"
                dato["riesgoNatural"] = 0.25
                #Generamos una recompensa base para la plataforma
                dato["recompensa_puntos"] = 0 
                dato["recompensa_nivel"] = 0 
                
                
            elif aux_type=="T"  or aux_type=="T1" :                            
                dato["tipo"] = "enemigoHorizontal"
                dato["riesgoNatural"] = 80
                dato["recompensa_puntos"] = 80 
                dato["recompensa_nivel"] = 0 
                
            
            elif aux_type=="O1" or aux_type=="O":
                dato["tipo"] = "enemigoHorizontal"
                dato["riesgoNatural"] = 100
                dato["recompensa_puntos"] = 50 
                dato["recompensa_nivel"] = 0 
                
            
            elif aux_type=="A1" or aux_type=="A" :
                dato["tipo"] = "enemigoVertical"
                dato["riesgoNatural"] = 50                
                dato["recompensa_puntos"] = 30 
                dato["recompensa_nivel"] = 0 
                
            elif aux_type=="enemigos":
                dato["tipo"] = "enemigos"
                dato["riesgoNatural"] = 300
                dato["recompensa_puntos"] = -200 
                dato["recompensa_nivel"] = 0 
                
            elif aux_type=="ws" or aux_type=="ps" or aux_type=="bf" or aux_type=="rf":
                dato["tipo"] = "comida"
                dato["riesgoNatural"] = 0
                if aux_type=="ws": 
                    dato["recompensa_puntos"] = 15
                    dato["recompensa_nivel"] = 0 
                if aux_type=="ps":
                    dato["recompensa_puntos"] = 30
                    dato["recompensa_nivel"] = 0 
                if aux_type=="bf": 
                    dato["recompensa_puntos"] = 10
                    dato["recompensa_nivel"] = 0 
                if aux_type=="rf":
                    dato["recompensa_puntos"] = 50
                    dato["recompensa_nivel"] = 0 
            
            elif aux_type=="G":
                dato["tipo"] = "meta"
                dato["riesgoNatural"] = 0
                #Generamos una recompensa base para la plataforma
                dato["recompensa_puntos"] = 0
                dato["recompensa_nivel"] = 500 
                
            elif aux_type=="c":
                dato["tipo"] = "checkpoint"
                dato["riesgoNatural"] = 0
                #Generamos una recompensa base para la plataforma
                dato["recompensa_puntos"] = 0
                dato["recompensa_nivel"] = 250 
                
            
            elif aux_type=="S":
                dato["tipo"] = "inicio"
                dato["riesgoNatural"] = 0
                #Generamos una recompensa base para la plataforma
                dato["recompensa_puntos"] = 0
                dato["recompensa_nivel"] = 0 
                
            else:
                if aux_type=="d":
                    dato["recompensa_puntos"] = 150
                    dato["recompensa_nivel"] = 0 
                elif aux_type=="p":
                    dato["recompensa_puntos"] = 300
                    dato["recompensa_nivel"] = 0 
                else:
                    dato["recompensa_puntos"] = 200
                    dato["recompensa_nivel"] = 0 
                    
                dato["tipo"] = "sub-mision"
                dato["riesgoNatural"] = 0
                        
            initx = int(initx)
            inity = int(inity)
            #La estructura es {"TipoDeBloque": [[limites de huella i-esima]],[[limites de trayectoria i-esima]]}
            limites={"T":[[[inity-2, inity, initx-2, initx]],[[inity-2, inity, initx-2, initx+5]]],  #Troll con movimiento a la derecha
                     "A":[[[inity-1, inity, initx-2, initx]],[[inity-1, inity+9, initx-2, initx]]],  #Aguila con movimiento hacia abajo 
                     "O":[[[inity-2, inity, initx-3, initx]],[[inity-2, inity, initx-3, initx+6]]],  #Oso con movimiento hacia la derecha
                     "T1":[[[inity-2, inity, initx-2, initx]],[[inity-2, inity, initx-7, initx]]], #Troll con movimiento a la izquierda
                     "A1":[[[inity-1, inity, initx-2, initx]],[[inity-10, inity, initx-2, initx]]], #Aguila con movimiento hacia arriba
                     "O1":[[[inity-2, inity, initx-3, initx]],[[inity-2, inity, initx-9, initx]]], #Oso con movimiento hacia la izquierda
                     "rv":[[[inity, inity, initx, initx+1]],[[inity, inity+5, initx, initx+1]]], #Plataforma movil con movimiento hacia abajo
                     "rv1":[[[inity, inity, initx, initx+1]],[[inity, inity-5, initx, initx+1]]], #Plataforma movil con movimiento hacia arriba
                     "rh":[[[inity, inity, initx, initx+1]],[[inity, inity, initx, initx+5]]], #Plataforma movil con movimiento hacia la derecha
                     "rh1":[[[inity, inity, initx, initx+1]],[[inity, inity, initx-5, initx+1]]], #Plataforma movil con movimiento hacia la izquierda                                                                        
                     "d": [[[inity,inity, initx, initx+1]]], #Pez dorado - equivalente a comida
                     "c": [[[inity,inity+1, initx, initx+1]]], #Checkpoint
                     "G": [[[inity-1, inity, initx, initx+1]]] #Meta
                    }
            #Hacemos la equivalencia entre bloques de comida y pez dorado
            if aux_type=="ws" or aux_type=="ps" or aux_type== "rf" or aux_type=="bf":
                aux_type = "d"  
            #Para los bloques moviles, llenamos la huella y la trayectoría
            #Para los bloqes que ocupan más de un espacio en matriz, sólo se llena su huella
            if aux_type in limites.keys():                                                                               
                #Obtenemos los limites para el bloque indicado                
                lim = limites[aux_type]
                
                #Llenamos las huellas del bloque
                for h in lim[0]:
                    huella={}                    
                    huella["minY"] = h[0]                    
                    huella["maxY"] = h[1]
                    huella["minX"] = h[2]
                    huella["maxX"] = h[3]
                    dato["puntos"]=[]
                    llena(dato["puntos"],huella["minY"], huella["maxY"], huella["minX"], huella["maxX"])
                    points = dato["puntos"]
                    #si es una plataforma movil, llenamos sus puntos de piso, contorno, techo y paredes...
                    if aux_type=="rv" or  aux_type=="rv1" or  aux_type=="rh"  or aux_type=="rh1":
                        dato["piso"] = []
                        dato["contorno"] = []
                        dato["techo"] = []
                        dato["paredes"] = []
                        llena(dato["piso"],huella["minY"], huella["maxY"], huella["minX"], huella["maxX"])
                        llena(dato["contorno"],huella["minY"], huella["maxY"], huella["minX"], huella["maxX"])
                        llena(dato["techo"],huella["minY"], huella["maxY"], huella["minX"], huella["maxX"])
                        llena(dato["paredes"],huella["minY"], huella["maxY"], huella["minX"], huella["maxX"])
                        piso = dato["piso"]
                        paredes = dato["paredes"]
                        techo = dato["techo"]
                        contorno = dato["contorno"]
                    #llena(huella[-1], filaIni=h[0], filaFin=h[1], colIni=h[2], colFin=h[3])
                
                #Verificamos que se trate de una plataforma con trayectoria 
                if len(lim)>1:
                    
                    #LLenamos las trayectorias
                    for t in lim[1]:
                        trayectoria={}                        
                        trayectoria["minY"] = t[0]                        
                        trayectoria["maxY"] = t[1]
                        trayectoria["minX"] = t[2]
                        trayectoria["maxX"] = t[3]
                        #trayectoria.append([])
                     #   llena(trayectoria[-1], filaIni=t[0], filaFin=t[1], colIni=t[2], colFin=t[3])                                                                                                                                                                                                                

                #Guardamos la huella del bloque   
                dato["huella"] = huella
                
                #Guardamos la trayectoria del bloque
                dato["trayectoria"]=trayectoria
            
            #Encontramos las puntas izquierda y derecha en los bloques de piso
            bloqPiso = 0
            maxIzq = 999            
            maxDer = -1
            while bloqPiso< len(piso):
                #print(piso[bloqPiso][1])
                if(int(piso[bloqPiso][1])>=maxDer):
                    maxDer = int(piso[bloqPiso][1])
                    idDer = bloqPiso
                if(int(piso[bloqPiso][1])<=maxIzq):
                    maxIzq = int(piso[bloqPiso][1])
                    idIzq = bloqPiso
                bloqPiso+=1
            puntasD.append(piso[idDer]) 
            puntasI.append(piso[idIzq])
            bloqPiso = 0            
            while bloqPiso <len(piso):                
                if(int(piso[bloqPiso][0])==int(puntasD[-1][0]) and int(piso[bloqPiso][1])==int(puntasD[-1][1])-1 ) and len(puntasD)<3:
                    puntasD.append(piso[bloqPiso])
                    bloqPiso = -1                            
                bloqPiso += 1
                
            bloqPiso = 0
            while bloqPiso <len(piso):
                
                if(int(piso[bloqPiso][0])==int(puntasI[-1][0]) and int(piso[bloqPiso][1])==int(puntasI[-1][1])+1 ) and len(puntasI)<3:
                    puntasI.append(piso[bloqPiso])
                    bloqPiso = -1                
                bloqPiso += 1
            
           #Guardamos el id_de bloque            
            dato["id"] = id_bloque
                                    
            #Guardamos su punto inicial
            dato["p_inicio"] = [inity, initx]
            #dato["p_final"] = [int(inity)+long_y-1, int(initx)+long_x-1]
            
            #Establecemos un grado de alcanzabilidad por default
            #dato["alcanzable"] = 0 
            #Se elimina temporalmente pues debe suplantarse por
            #una medida de alcanzabilidad con respecto a las demás plataformas
            
            #Guardamos el contorno del bloque
            dato["contorno"] = contorno
            
            #Generamos las listas alcanza y alncanzado por
            dato["alcanza"] = {}
            
            dato["alcanzado_por"] = {}
            
            #Guardamos los puntos de piso
            dato["piso"] = piso
            
            #Guardamos los puntos de techo
            dato["techo"] = techo
            
            #Guardamos los puntos de paredes
            dato["paredes"] = paredes
            
            #Guardamos el conjunto de puntos (centros de los bloques) que lo conforman
            dato["puntos"] = points
            
            #Guardamos la lista de puntas por la derecha
            dato["puntas_derecha"] = puntasD
            
            #Guardamos la lista de puntas por la izquierda
            dato["puntas_izquierda"] = puntasI                                                
            
            #Generamos un tiempo base para la plataforma
            dato["tiempo"] = 0 
            
            #Generamos una utilidad base para la plataforma
            dato["utilidad"] = 0
            
            #Generamos un riesgo base de 0 para la plataforma
            dato["riesgo"] = 0                        
                                         
            #print("Agregando bloque: \n", dato,"\n")
            data["objetos"].append(dato)
            id_bloque+=1
            
    return data    


# In[6]:


nivel = "level8.json"
mapa = leerMapa(path+"/"+nivel)
#len(mapa["mapa"])


# In[7]:


#bloques = detectaPlataformas(mapa["mapa"],nivel)


# In[8]:


def curvaPingu(x,y, mapa):
    x = x*configPenguin.wbloque
    y = (y-1)*configPenguin.hbloque
    v = 21
    speed = 0.14
    m = 1
    factMov = 90
    factFall = 0.48
    subida = []
    bajada = []
    
    hor_psD = []
    hor_psI = []
    subida.append(y/configPenguin.hbloque)
    hor_psD.append(x/configPenguin.wbloque)
    hor_psI.append(x/configPenguin.wbloque)
    while(v>0):
        f = 0.5*int(speed*m*v*v)
        y -= f
        subida.append(y/configPenguin.hbloque)
        v -= 0.65
    bajada.append(subida[-1])
    while y<(len(mapa)*configPenguin.hbloque+configPenguin.hbloque):
        y += 2.5*int(speed*m*factMov*factFall)
        bajada.append(y/configPenguin.hbloque)
    i=0
    for p in subida:
        hor_psD.append(0) 
        hor_psI.append(0) 
        
        hor_psD[i+1] = (hor_psD[i]*configPenguin.wbloque +int(speed*factMov))/configPenguin.wbloque
        hor_psI[i+1] = (hor_psI[i]*configPenguin.wbloque -int(speed*factMov))/configPenguin.wbloque
        i+=1
        
    for p in bajada:
        hor_psD.append(0) 
        hor_psI.append(0) 
        
        hor_psD[i+1] = (hor_psD[i]*configPenguin.wbloque +int(speed*factMov))/configPenguin.wbloque
        hor_psI[i+1] = (hor_psI[i]*configPenguin.wbloque -int(speed*factMov))/configPenguin.wbloque
        i+=1
    
    for j in range (len(hor_psD)):
        
        if(int(hor_psD[j])>=len(mapa['0'])):
            hor_psD[j]= len(mapa['0'])-1
        
            
        if(int(hor_psI[j])<0):
            hor_psI[j]= 0    
                
    return subida, bajada, hor_psD, hor_psI

    


# In[9]:


yUs, yDs, xsD, xsI = curvaPingu(14, 12, mapa["mapa"] )
pointsL=[]
pointsR=[]
#print("Puntos de curva hacia la derecha")
i=0

for y in yUs:
    #print("(",xsD[i],",", y,")")
    if(not [int(y), int(xsD[i])] in pointsR):
        pointsR.append([int(y),int(xsD[i])])
    i+=1

for y in yDs:
    if(not [int(y), int(xsD[i])] in pointsR):
        pointsR.append([int(y), int(xsD[i])])
    i+=1
#print(len(pointsR))

#for p in pointsR:
 #   print(p)

#print("Puntos de curva hacia la izquierda")
j=0

for y in yUs:
    #print("(",xsI[j],",", y,")")
    if(not [int(y), int(xsI[j])] in pointsL):
        pointsL.append([int(y), int(xsI[j])])
    j+=1
#print(len(pointsL))

for y in yDs:
    #print("(",xsI[j],",", y,")")
    if(not [int(y), int(xsI[j])] in pointsL):
        pointsL.append([int(y), int(xsI[j])])
    j+=1



def dist(a,b):    
    d = np.sqrt(np.power(b[0]-a[0],2)+np.power(b[1]-a[1],2))
    return d


# In[13]:


def pendiente(a,b, mapa, valMax=9999):
    #En este caso a[0] y b[0] corresponden al valor "y" (filas) 
    # y a[1] y b[1] corresponden al valor "x" (columnas)
    if(b[1]!=a[1]):
        m = ((len(mapa)-b[0])-(len(mapa)-a[0]))/(b[1]-a[1])
    else:
        m = valMax
        
    return m    


# In[14]:


def pendienteB(a,b,valMax=9999):
    """
    En este caso a[0] y b[0] corresponden al valor "y" (filas) 
    y a[1] y b[1] corresponden al valor "x" (columnas)
    """
    if(int(b[1])!=int(a[1])):
        m = (int(b[0])-int(a[0]))/(int(b[1])-int(a[1]))
    else:
        m = configPenguin.maxValP        
    return m  


yU1 = yUs[0]
yU2 = yUs[-1]
yD1 = yDs[0]
yD2 = yDs[-1]
#print("yDs[0]",yDs[0])
pendUp =- (yU2-yU1)/(xsD[len(yUs)-1]-xsD[0])
pendDown =- (yD2-yD1)/(xsD[-1]-xsD[len(yUs)-1])

dMaxU1 = (yU2-yU1)
dMaxU2 = dist(np.array([yU2,xsD[len(yUs)-1]]),np.array([yU1, xsD[0]]))
dMaxU3 = xsD[len(yUs)-1]-xsD[0]
dMaxD = dist(np.array([yD2,xsD[-1]]),np.array([yD1, xsD[len(yUs)-1]]))




def alcanza(p1,p2,yMax, points, pendUp, pendDown,mapa):
    alc = []
   
    A = points[str(p1)]
    B = points[str(p2)]
   # #print(A)
   # #print(B)
    m = pendiente(B,A,mapa)
    d = dist(A,B)
    yMax =(A[0]-6)
    dMax = 0
    #print("d",d)
    #print("m",m)
    #print("yMax", yMax)
    #Caso 1 el bloque p2 está a la derecha de p1
    if B[1]>A[1]:
        
        #print("Derecha")
        if(m>=pendUp):
            #print("caso 1")
            #if(m<0)
            xn = (yMax/m)-A[1]
            #else:
                
         #   #print("xMax", xn)
            #El punto está en el area antes o igual del punto maximo en el salto 
            dMax = dist(A,np.array([yMax,xn]))
            #print("dMax",dMax)
        else:
            #print("caso 2")
            #El punto está después del punto maximo de salto
            #caso 2.1
            if(m>pendDown):
                xn = (2*(yMax)/(m - pendDown))
                yn = m*xn
                dMax = dist(A, np.array([yn,xn])) 
            else:
                alc.append(p2)    
            #print("dMax",dMax)

        if(int(d)<=int(dMax)):
            alc.append(p2)
    else:
        
        #print("Izquierda")
        #m =- m
        pendUp =- pendUp
        pendDown =- pendDown
        if(m<=pendUp) and m!=0:
            #print("caso 1")
            #El punto está en el area antes o igual del punto maximo en el salto 
            #if(m>0):
            xn = (yMax/m)+A[1]
            #else: 
             #   xn = yMax+A[1]
            #print("xn", xn)
            dMax = dist(A,np.array([yMax, xn]))
            #print("dMax",dMax)
        else:
            #print("caso 2")
            #El punto está después del punto maximo de salto
            #caso 2.1 La pendiente es mayor a la pendiente de caida
            if(m < pendDown ):
                xn = (2*(yMax)/(m - pendDown))
                yn = m*xn
                dMax = dist(A, np.array([yn,xn])) 
                #print("dMax",dMax)
            else:
                alc.append(p2)        

        if(int(d)<=int(dMax)):
            alc.append(p2)        
    return alc   


# In[123]:


def alcanzaBloques(p1, p2, yMax, pendUp, pendDown,mapa):
    alc = False
    A = np.array([len(mapa)-int(p1[0]), int(p1[1])])
    B = np.array([len(mapa)-int(p2[0]), int(p2[1])])
    vMax=9999
    m = pendienteB(A,B, valMax=vMax)
    d = dist(A,B)
    yMax =(A[0]+6)
    dMax = 0
    #Caso 1 el bloque p2 está a la derecha de p1
    if B[1]>A[1]:        
        if(m>=pendUp):         
            xn = ((yMax-A[0])/m)+A[1]            
            #El punto está en el area antes o igual del punto maximo en el salto 
            dMax = dist(A,np.array([yMax,xn]))

        else:

            #El punto está después del punto maximo de salto
            #caso 2.1
            if(m>pendDown):
                xn = (((yMax+6)-A[0])/(m -pendDown))+A[1]
                yn = (m*(xn-A[1]))+A[0]
                dMax = dist(A, np.array([yn,xn])) 
            else:
                if(A[0]>B[0]):
                    alc = True
        if(int(d)<=int(dMax)):
            alc = True

    else:
        
        pendUp =- pendUp
        pendDown =- pendDown
        if(m<=pendUp) and m!=0:
            #El punto está en el area antes o igual del punto maximo en el salto             
            xn = ((yMax-A[0])/m)+A[1]
            dMax = dist(A,np.array([yMax, xn]))
        else:
            #El punto está después del punto maximo de salto
            #caso 2.1 La pendiente es mayor a la pendiente de caida
            if(m <= pendDown ):                
                xn = (((yMax+6)-A[0])/(m -pendDown))+A[1]
                yn = (m*(xn-A[1]))+A[0]
                dMax = dist(A, np.array([yn,xn])) 
            else:
                if m==vMax:
                    xn = A[1]
                    dMax = dist(A,np.array([yMax, xn]))
                
                elif(A[0]>B[0]):
                    alc = True    

        if(int(d)<=int(dMax)):
            alc = True
        elif(A[1]==B[1] and B[0]==A[1]-1):
            alc = True

    return alc, dMax, d  


# In[22]:


def alcanzabilidad(bloques, mapa):    
    for plataforma in bloques["objetos"]:              
        if ((plataforma["tipo"]=="piso") or (plataforma["tipo"]=="movil") or (plataforma["tipo"]=="rebote")or (plataforma["tipo"]=="obstaculo")):
            #Por cada punto/objeto de tipo piso en el objeto, se verifica a donde se puede llegar
            for plat in bloques["objetos"]:         
                alcanza = 0               
                distMin = 999999
                if (plat["id"]!=plataforma["id"]):              
                    pObsMin = 99
                    pSaltoMin = 99
                    #Caso 1.- Ninguna de las plataformas es movil
                    if plat["tipo"]!="movil" and plataforma["tipo"]!="movil":
                        for piso in plataforma["piso"]:                                                             
                            for p in plat["piso"]:        
                                llega, distMax, dReal = alcanzaBloques(piso,p,dMaxU1,pendUp,pendDown,mapa["mapa"])
                                if (llega):
                                    d = dist(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]))
                                    if(d<distMin):
                                        distMin = d
                                    alcanza+=1
                                    #Encontramos la probabilidad de que haya obstaculos en el camino de plataforma a plat
                                    pObs = evaluaObstaculos(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]),plataforma["id"], plat["id"],bloques, mapa)
                                    #Encontramos los posibles bloqueos de salto entre plataforma y plat
                                    pSalto = bloqueoSalto(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]),plataforma["id"], plat["id"],bloques, mapa)

                                    if(pObs<pObsMin):
                                        pObsMin = pObs
                                    if(pSalto<pSaltoMin):
                                        pSaltoMin = pSalto           
                    #Caso 2.- plataforma es movil
                    elif plat["tipo"]!="movil" and plataforma["tipo"]=="movil":
                        #Si es plataforma movil vertical...
                        if(plataforma["trayectoria"]["maxX"]-plataforma["trayectoria"]["minX"]==1):                                                                             
                            plataformaAux = newPlatMovil(plataforma, False)                         
                        #Si es plataforma movil horizontal...
                        else:                                                  
                            plataformaAux = newPlatMovil(plataforma, True)
                        plat1=0
                        while plat1 < len(plataformaAux):
                            for piso in plataformaAux[plat1]["piso"]:                                                             
                                for p in plat["piso"]:   
                                    llega, distMax, dReal = alcanzaBloques(piso,p,dMaxU1,pendUp,pendDown,mapa["mapa"])
                                    if (llega):
                                        d = dist(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]))
                                        if(d<distMin):
                                            distMin = d
                                        alcanza+=1
                                        #Encontramos la probabilidad de que haya obstaculos en el camino de plataforma a plat
                                        pObs = evaluaObstaculos(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]),plataforma["id"], plat["id"],bloques, mapa)
                                        #Encontramos los posibles bloqueos de salto entre plataforma y plat
                                        pSalto = bloqueoSalto(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]),plataforma["id"], plat["id"],bloques, mapa)

                                        if(pObs<pObsMin):
                                            pObsMin = pObs
                                        if(pSalto<pSaltoMin):
                                            pSaltoMin = pSalto           
                            plat1+=1

                    #Caso 3.- plat es movil
                    elif plat["tipo"]=="movil" and plataforma["tipo"]!="movil":
                        #Si es plataforma movil vertical...
                        if(plat["trayectoria"]["maxX"]-plat["trayectoria"]["minX"]==1):                                                                             
                            platAux = newPlatMovil(plat, False)                         
                        #Si es plataforma movil horizontal...
                        else:                                                  
                            platAux = newPlatMovil(plat, True)                            
                                                
                        for piso in plataforma["piso"]:                                                             
                            plat2=0
                            while plat2 < len(platAux):
                                for p in platAux[plat2]["piso"]:   
                                    llega, distMax, dReal = alcanzaBloques(piso,p,dMaxU1,pendUp,pendDown,mapa["mapa"])
                                    if (llega):
                                        d = dist(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]))
                                        if(d<distMin):
                                            distMin = d
                                        alcanza+=1
                                        #Encontramos la probabilidad de que haya obstaculos en el camino de plataforma a plat
                                        pObs = evaluaObstaculos(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]),plataforma["id"], plat["id"],bloques, mapa)
                                        #Encontramos los posibles bloqueos de salto entre plataforma y plat
                                        pSalto = bloqueoSalto(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]),plataforma["id"], plat["id"],bloques, mapa)

                                        if(pObs<pObsMin):
                                            pObsMin = pObs
                                        if(pSalto<pSaltoMin):
                                            pSaltoMin = pSalto           
                                plat2+=1
                    #Caso 4.- ambas son moviles
                    elif plat["tipo"]=="movil" and plataforma["tipo"]=="movil":
                         #Si es plataforma movil vertical...
                        if(plataforma["trayectoria"]["maxX"]-plataforma["trayectoria"]["minX"]==1):                                                                             
                            plataformaAux = newPlatMovil(plataforma, False)                         
                        #Si es plataforma movil horizontal...
                        else:                                                  
                            plataformaAux = newPlatMovil(plataforma, True)     
                        #Si es plataforma movil vertical...
                        if(plat["trayectoria"]["maxX"]-plat["trayectoria"]["minX"]==1):                                                                             
                            platAux = newPlatMovil(plat, False)                         
                        #Si es plataforma movil horizontal...
                        else:                                                  
                            platAux = newPlatMovil(plat, True)    
                        plat1=0
                        while plat1 < len(plataformaAux):
                            plat2=0
                            while plat2<len(platAux):
                                for piso in plataformaAux[plat1]["piso"]:                                                             
                                    for p in platAux[plat2]["piso"]:   
                                        llega, distMax, dReal = alcanzaBloques(piso,p,dMaxU1,pendUp,pendDown,mapa["mapa"])
                                        if (llega):
                                            d = dist(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]))
                                            if(d<distMin):
                                                distMin = d
                                            alcanza+=1
                                            #Encontramos la probabilidad de que haya obstaculos en el camino de plataforma a plat
                                            pObs = evaluaObstaculos(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]),plataforma["id"], plat["id"],bloques, mapa)
                                            #Encontramos los posibles bloqueos de salto entre plataforma y plat
                                            pSalto = bloqueoSalto(np.array([int(piso[0]), int(piso[1])]), np.array([int(p[0]), int(p[1])]),plataforma["id"], plat["id"],bloques, mapa)

                                            if(pObs<pObsMin):
                                                pObsMin = pObs
                                            if(pSalto<pSaltoMin):
                                                pSaltoMin = pSalto           
                                plat2+=1
                            plat1+=1

                if(alcanza>0):                                
                    plataforma["alcanza"][plat["id"]] = {"precision":0, "riesgo":0, "obstruccion":pObsMin+pSaltoMin, "distancia":distMin, "recompensa_puntos": 0, "recompensa_nivel":0 , "tiempo":0, "motivacion_puntos":0, "motivacion_nivel":0}
                    plat["alcanzado_por"][plataforma["id"]] ={"precision":0, "riesgo":0, "obstruccion":pObsMin+pSaltoMin, "distancia":distMin,  "recompensa_puntos": 0, "recompensa_nivel":0, "tiempo":0, "motivacion_puntos":0, "motivacion_nivel":0}


# In[23]:


def evaluaObstaculos(p1, p2, id1, id2, bloques, mapa) :
    """
    ---------------------------------------------------------------------------------------
    En esta funcion se revisa, dado un bloque de origen de movimiento p1 y un punto destino p2,
    cual es la probabilidad de que haya un obstáculo para alcanzar p2.
    Para ello, se necesita saber los puntos alcanzables desde p1.
    Por ello, la función recibe:
        - p1. Un punto (x1,y1) en la plataforma inicial
        - p2. Un punto (x2,y2) en la plataforma destino
        - id1. El id del bloque de inicio
        - id2. El id del bloque destino
        - bloques. Diccionario con la información completa de las plataformas
        - mapa. La matriz del mapa, que se usa para calcular las pendientes
    La función regresa:
        - La probabilidad de que, dado el punto p1 haya un obstáculo para llegar a p2.
    ---------------------------------------------------------------------------------------
    """
    #Nota: los puntos tienen la forma [y,x]
    m5 = pendiente(p2, np.array([p2[0]-4, p2[1]+2]), mapa)
    m6 = pendiente(p2, np.array([p2[0]-4, p2[1]+1]), mapa)
    d3 = dist(p2, np.array([p2[0]-3,p2[1]+1])) 
    d4 = dist(p2, np.array([p2[0]-2,p2[1]+1]))
    d7 = dist(p2, np.array([p2[0]-3,p2[1]+3]))
    d6 = dist(p2, np.array([p2[0]-4, p2[1]+1]))
    dMeta = dist(p2,p1) #La distancia entre el punto de origen y el punto destino
    mLim = pendiente(p1,p2, mapa)
    prob = 0
       
    for obst in bloques["objetos"]:
        if(obst!= id2) and ((bloques["objetos"][obst['id']]["tipo"]=="piso") or (bloques["objetos"][obst['id']]["tipo"]=="movil") or (bloques["objetos"][obst['id']]["tipo"]=="rebote")or (bloques["objetos"][obst['id']]["tipo"]=="obstaculo")):
            iniP=prob   
            for point in bloques["objetos"][obst['id']]["puntos"]:   
                alfa = 1
                d1 = dist(p2, np.array([int(point[0]), int(point[1])]))
                dObst = dist(p1, np.array([int(point[0]), int(point[1])])) 
                mObst = pendiente(p1,np.array([int(point[0]), int(point[1])]), mapa)
                m1 = pendiente(p2, np.array([int(point[0]), int(point[1])]), mapa)   
                if((mObst<mLim  and p2[1]<p1[1] and int(point[1])<int(p2[1])) or (mObst>mLim and p2[1]>p1[1] and int(point[1])>p1[1])):                    
                    #if(mObst!=configPenguin.maxValP):
                    if(d1 <= dMeta) and (dObst <=dMeta) and (np.power(d1,2)+np.power(dObst,2)<np.power(dMeta,2)):
                        if(d1>d7):
                            alfa = 1-(d1/dMeta)                      
                        #Caso 1, el punto destino está antes del máximo en x del salto
                        if  (p2[1]>(p1[1]-6)) and (p2[1]<(p1[1]+6)):
                
                            if (m1<=m6 and m1 >=m5) or (m1<=-m5 and m1 >=-m6):
                                if d1<=d3 and d1>=d4:
                                    prob+=alfa*0.45
                
                            elif (m1>=m6 and m1 <=-m6) or (m1==configPenguin.maxValP):
                                prob+=alfa*0.33
                                
                            elif d1<=d7:
                                prob+=alfa*0.05                                

                        #Caso 2, el punto destino está a la misma altura o por encima del punto de origen 
                        # despues del maximo en x
                        elif p2[0]<=p1[0]:
                            #print("caso 2")
                            if (m1<=m6 and m1 >=m5) or (m1<=-m5 and m1 >=-m6):
                                if d1<=d3 and d1>=d4:
                                    prob+=alfa*0.5
                                    
                            elif (m1>=m6 and m1 <=-m6) or (m1==configPenguin.maxValP):
                                prob+=alfa*0.4
                                
                            elif d1<=d7:
                                prob+=alfa*0.1                                

                        #Caso 3, el punto destino está después del máximo en x del salto 
                        # por debajo del punto de origen
                        elif  (p2[1]>=(p1[1]+6) and p2[0]>p1[0]) or (p2[1]<=(p1[1]-6) and p2[0]>p1[0]):                            
                            m6=-m6
                            m5=-m5
                            if m1<=m6 and m1 >=m5:
                                if d1<=d3 and d1>=d4:
                                    prob+=alfa*0.45
                                    
                            elif (m1>=m6 and m1 <=-m6) or (m1==configPenguin.maxValP):
                                prob+=alfa*0.33
                                
                            elif d1<=d7:
                                prob+=alfa*0.05
        
    return prob            


# In[24]:


def evaluaObstaculos_v2(p1, p2, bloques, mapa) :
    """
    ---------------------------------------------------------------------------------------
    En esta funcion se revisa, dado un bloque de origen de movimiento p1 y un punto destino p2,
    cual es la probabilidad de que haya un obstáculo para alcanzar p2.
    Para ello, se necesita saber los puntos alcanzables desde p1.
    Por ello, la función recibe:
        - p1. Un punto (x1,y1) en la plataforma inicial
        - p2. Un punto (x2,y2) en la plataforma destino        
        - bloques. Diccionario con la información completa de las plataformas
        - mapa. La matriz del mapa, que se usa para calcular las pendientes
    La función regresa:
        - La probabilidad de que, dado el punto p1 haya un obstáculo para llegar a p2.
    ---------------------------------------------------------------------------------------
    """
   
    #Nota: los puntos tienen la forma [y,x]
    m5 = pendiente(p2, np.array([p2[0]-4, p2[1]+2]), mapa)
    m6 = pendiente(p2, np.array([p2[0]-4, p2[1]+1]), mapa)
    d3 = dist(p2, np.array([p2[0]-3,p2[1]+1])) 
    d4 = dist(p2, np.array([p2[0]-2,p2[1]+1]))
    d7 = dist(p2, np.array([p2[0]-3,p2[1]+3]))
    d6 = dist(p2, np.array([p2[0]-4, p2[1]+1]))
    dMeta = dist(p2,p1) #La distancia entre el punto de origen y el punto destino
    mLim = pendiente(p1,p2, mapa)
    prob = 0
    
    for obst in bloques["objetos"]:
        if((bloques["objetos"][obst['id']]["tipo"]=="piso") or (bloques["objetos"][obst['id']]["tipo"]=="movil") or (bloques["objetos"][obst['id']]["tipo"]=="rebote")or (bloques["objetos"][obst['id']]["tipo"]=="obstaculo")):
            iniP=prob   
            for point in bloques["objetos"][obst['id']]["puntos"]:   
                alfa = 1
                d1 = dist(p2, np.array([int(point[0]), int(point[1])]))
                dObst = dist(p1, np.array([int(point[0]), int(point[1])])) 
                mObst = pendiente(p1,np.array([int(point[0]), int(point[1])]), mapa)
                m1 = pendiente(p2, np.array([int(point[0]), int(point[1])]), mapa)   
                if((mObst<mLim  and p2[1]<p1[1] and int(point[1])<int(p2[1])) or (mObst>mLim and p2[1]>p1[1] and int(point[1])>p1[1])):                    

                    if(d1 <= dMeta) and (dObst <=dMeta) and (np.power(d1,2)+np.power(dObst,2)<np.power(dMeta,2)):
                        if(d1>d7):
                            alfa = 1-(d1/dMeta)                      
                        #Caso 1, el punto destino está antes del máximo en x del salto
                        if  (p2[1]>(p1[1]-6)) and (p2[1]<(p1[1]+6)):
                
                            if (m1<=m6 and m1 >=m5) or (m1<=-m5 and m1 >=-m6):
                                if d1<=d3 and d1>=d4:
                                    prob+=alfa*0.45
                
                            elif (m1>=m6 and m1 <=-m6) or (m1==configPenguin.maxValP):
                                prob+=alfa*0.33
                                
                            elif d1<=d7:
                                prob+=alfa*0.05                                

                        #Caso 2, el punto destino está a la misma altura o por encima del punto de origen 
                        # despues del maximo en x
                        elif p2[0]<=p1[0]:

                            if (m1<=m6 and m1 >=m5) or (m1<=-m5 and m1 >=-m6):
                                if d1<=d3 and d1>=d4:
                                    prob+=alfa*0.5
                                    
                            elif (m1>=m6 and m1 <=-m6) or (m1==configPenguin.maxValP):
                                prob+=alfa*0.4
                                
                            elif d1<=d7:
                                prob+=alfa*0.1                                

                        #Caso 3, el punto destino está después del máximo en x del salto 
                        # por debajo del punto de origen
                        elif  (p2[1]>=(p1[1]+6) and p2[0]>p1[0]) or (p2[1]<=(p1[1]-6) and p2[0]>p1[0]):                            
                            m6=-m6
                            m5=-m5
                            if m1<=m6 and m1 >=m5:
                                if d1<=d3 and d1>=d4:
                                    prob+=alfa*0.45
                                    
                            elif (m1>=m6 and m1 <=-m6) or (m1==configPenguin.maxValP):
                                prob+=alfa*0.33
                                
                            elif d1<=d7:
                                prob+=alfa*0.05
        
    return prob            


# In[25]:


def bloqueoSalto(puntoO, puntoD, id1, id2, bloques, mapa):
    """
    ---------------------------------------------------------------------------------------
    En esta funcion se revisa, dado un bloque de origen de movimiento puntoO y un punto destino puntoD,
    cual es la probabilidad de que haya un obstáculo durante el salto para alcanzar puntoD.
    Para ello, se necesita saber los puntos alcanzables desde p1.
    Por ello, la función recibe:
        - puntoO. Un punto (x1,y1) en la plataforma inicial
        - puntoD. Un punto (x2,y2) en la plataforma destino
        - id1. El id del bloque de inicio
        - id2. El id del bloque destino
        - bloques. Diccionario con la información completa de las plataformas
        - mapa. La matriz del mapa, que se usa para calcular las pendientes
    La función regresa:
        - La probabilidad de que, dado el punto puntoO, haya un obstáculo en el salto para llegar a puntoD.
    ---------------------------------------------------------------------------------------
    """

    #Se necesitan tres pendientes con vertices de la zona de bloqueo de salto
    m1 = pendienteB(puntoO, np.array([puntoO[0]-3.75, puntoO[1]+1]))
    m2 = pendienteB(puntoO, np.array([puntoO[0]-3.75, puntoO[1]+2.25]))
    m6 = pendienteB(puntoO, np.array([puntoO[0]-5, puntoO[1]+8]))
    d1 = dist(puntoO,np.array([puntoO[0]-3.75, puntoO[1]+1]))
    d3 = dist(puntoO,np.array([puntoO[0]-5, puntoO[1]+3]))
    d5 = dist(puntoO,np.array([puntoO[0]-6, puntoO[1]+8]))
    p = 0  
    for obst in bloques["objetos"][id1]["alcanza"]:
        if(obst != id2) and ((bloques["objetos"][obst]["tipo"]=="piso") or (bloques["objetos"][obst]["tipo"]=="movil") or (bloques["objetos"][obst]["tipo"]=="rebote")or (bloques["objetos"][obst]["tipo"]=="obstaculo")):                                                             
            for point in bloques["objetos"][obst]["puntos"]:
                d = dist(puntoO, np.array([int(point[0]), int(point[1])])) 
                m = pendienteB(puntoO, np.array([int(point[0]), int(point[1])]))
                #Con los bloques a la derecha
                iniP=p
                #Es un punto por encima del punto de origen de salto
                if(int(point[0])<puntoO[0]):
                    if(m<=m1 and m>=m6):
                        #Esta en el angulo de las pendiente de la zona de riesgo
                        #Caso 1: El bloque está despues del punto de salto máximo y en la zona de reisgo
                        if (puntoD[1]>=puntoO[1]+6):
                                if(d>=d1 and d<=d5):
                                    p+=1
                        else:
                            p+=0.05
                            if(d>=d1 and d<=d5):
                                if(m>m2):
                                    p+=0.33
                                elif(d>=d3):
                                    p+=.5                            

                    #Con los bloques a la izquierda
                    elif(m>=-m1 and m<=-m6):
                        #Esta en el angulo de las pendiente de la zona de riesgo
                        #Caso 1: El bloque está despues del punto de salto máximo y en la zona de reisgo
                        if (puntoD[1]>=puntoO[1]-6):
                                if(d>=d1 and d<=d5):
                                    p+= 1
                        else:
                            p+=0.05
                            if(d>=d1 and d<=d5):
                                if(m<-m2):
                                    p+=0.33
                                elif(d>=d3):
                                    p+=0.5                  
    return p


# In[191]:


def bloqueoSalto_v2(puntoO, puntoD, bloques, mapa, obstaculos):
    """
    ---------------------------------------------------------------------------------------
    En esta funcion se revisa, dado un bloque de origen de movimiento puntoO y un punto destino puntoD,
    cual es la probabilidad de que haya un obstáculo durante el salto para alcanzar puntoD.
    Para ello, se necesita saber los puntos alcanzables desde p1.
    Por ello, la función recibe:
        - puntoO. Un punto (x1,y1) en la plataforma inicial
        - puntoD. Un punto (x2,y2) en la plataforma destino        
        - bloques. Diccionario con la información completa de las plataformas
        - mapa. La matriz del mapa, que se usa para calcular las pendientes
    La función regresa:
        - La probabilidad de que, dado el punto puntoO, haya un obstáculo en el salto para llegar a puntoD.
    ---------------------------------------------------------------------------------------
    """

    #Se necesitan tres pendientes con vertices de la zona de bloqueo de salto
    m1 = pendienteB(puntoO, np.array([puntoO[0]-3, puntoO[1]+0]))
    m2 = pendienteB(puntoO, np.array([puntoO[0]-4, puntoO[1]+3]))
    m6 = pendienteB(puntoO, np.array([puntoO[0]-5, puntoO[1]+8]))
    d1 = dist(puntoO,np.array([puntoO[0]-3, puntoO[1]+0]))
    d3 = dist(puntoO,np.array([puntoO[0]-5, puntoO[1]+3]))
    d5 = dist(puntoO,np.array([puntoO[0]-6, puntoO[1]+8]))
    p = 0      
    
    for point in obstaculos:
        d = dist(puntoO, np.array([int(point[0]), int(point[1])])) 
        m = pendienteB(puntoO, np.array([int(point[0]), int(point[1])]))
        #Con los bloques a la derecha
        iniP=p
        #Es un punto por encima del punto de origen de salto
        if(int(point[0])<puntoO[0]):

            if(m<=m1 and m>=m6):

                #Esta en el angulo de las pendiente de la zona de riesgo
                #Caso 1: El bloque está despues del punto de salto máximo y en la zona de reisgo
                if (puntoD[1]>=puntoO[1]+6):
                    if(d>=d1 and d<=d5):
                        p+=1
                else:
                    p+=0.05
                    if(d>=d1 and d<=d5):
                        if(m>m2):
                            p+=0.33
                        elif(d>=d3):
                            p+=.5                            

            #Con los bloques a la izquierda
            elif(m>=-m1 and m<=-m6):

                #Esta en el angulo de las pendiente de la zona de riesgo
                #Caso 1: El bloque está despues del punto de salto máximo y en la zona de reisgo
                if (puntoD[1]<=puntoO[1]-6):
                    if(d>=d1 and d<=d5):
                        p+= 1
                else:
                    p+=0.05
                    if(d>=d1 and d<=d5):
                        if(m<-m2):
                            p+=0.33
                        elif(d>=d3):
                            p+=0.5

    return p


def separaPlat(plataformaBase, piso):
    """
    Esta funcion auxiliar separa una plataforma en dos, donde
    los puntos del piso de entrada forman una plataforma y aquellos 
    que no forman parte de él, forman otra.
    """
    subPlat1={}
    subPlat2={}
    #Llenamos las plataformas nuevas con la base
    key=0
    while key < len(plataformaBase):
        #Se copian los valores de las evaluaciones de la plataforma base, que deben de estar vacio y sólo sirven para tener la plantilla completa
        #de las plataformas
        if(type(plataformaBase[list(plataformaBase.keys())[key]])!= list) and (type(plataformaBase[list(plataformaBase.keys())[key]])!= dict):
            #El id lo adquiriran despues...
            if(list(plataformaBase.keys())[key]=="id"):
                subPlat1[list(plataformaBase.keys())[key]]=""
                subPlat2[list(plataformaBase.keys())[key]]=""
            else:
                subPlat1[list(plataformaBase.keys())[key]] = plataformaBase[list(plataformaBase.keys())[key]]
                subPlat2[list(plataformaBase.keys())[key]] = plataformaBase[list(plataformaBase.keys())[key]]
        #Si se trata de una lista o un diccionario, se trata de los sprites que componen a la plataforma y de los diccionarios 
        #de las plataformas con las que interactua, respectivamente
        elif type(plataformaBase[list(plataformaBase.keys())[key]])== list:
            #Lo unicio que se dejara vacio, son las puntas, las cuales deberán volver a calcularse
            if (list(plataformaBase.keys())[key]!="puntas_izquierda") and (list(plataformaBase.keys())[key]!="puntas_derecha") and (list(plataformaBase.keys())[key]!="p_inicio"):
                subPlat1[list(plataformaBase.keys())[key]]=piso
                #A la plataforma 2 le quitamos todos aquellos puntos que sean parte de "piso" 
                subPiso2=0
                puntos=[]
                while subPiso2<len(plataformaBase[list(plataformaBase.keys())[key]]):
                    if(plataformaBase[list(plataformaBase.keys())[key]][subPiso2] not in piso):
                        puntos.append(plataformaBase[list(plataformaBase.keys())[key]][subPiso2])
                    subPiso2+=1
                subPlat2[list(plataformaBase.keys())[key]] = puntos
        #Se trata de un diccionario...
        else: 
            subPlat1[list(plataformaBase.keys())[key]] = {}
            subPlat2[list(plataformaBase.keys())[key]] = {}
        key+=1
    subPlats = [subPlat1, subPlat2]
    #Llenamos los datos faltantes de las plataformas
    #Encontramos las puntas izquierda y derecha en los bloques de piso
    
    sP=0
    while sP <len(subPlats):
        bloqPiso = 0
        maxIzq = 999                
        maxDer = -1
        puntasD = []    
        puntasI = []
        piso= subPlats[sP]["piso"]
        if(piso==[]):
            punto=0
            while punto< len(subPlats[sP]["puntos"]):
                if([subPlats[sP]["puntos"][punto][0] ,str(int(subPlats[sP]["puntos"][punto][1])-1)] not in subPlats[sP]["puntos"]):
                    piso.append(subPlats[sP]["puntos"][punto])                    
                punto+=1
            subPlats[sP]["piso"]=piso
            
        while bloqPiso< len(piso):         
            if(int(piso[bloqPiso][1])>=maxDer):
                maxDer = int(piso[bloqPiso][1])
                idDer = bloqPiso
            if(int(piso[bloqPiso][1])<=maxIzq):
                maxIzq = int(piso[bloqPiso][1])            
                idIzq = bloqPiso
                subPlats[sP]["p_inicio"]= [int(piso[bloqPiso][0]),int(piso[bloqPiso][1])]
            bloqPiso+=1
        puntasD.append(piso[idDer]) 
        puntasI.append(piso[idIzq])
        bloqPiso = 0            
        while bloqPiso <len(piso):                
            if(int(piso[bloqPiso][0])==int(puntasD[-1][0]) and int(piso[bloqPiso][1])==int(puntasD[-1][1])-1 ) and len(puntasD)<3:
                puntasD.append(piso[bloqPiso])
                bloqPiso = -1                            
            bloqPiso += 1

        bloqPiso = 0
        while bloqPiso <len(piso):
            if(int(piso[bloqPiso][0])==int(puntasI[-1][0]) and int(piso[bloqPiso][1])==int(puntasI[-1][1])+1 ) and len(puntasI)<3:
                puntasI.append(piso[bloqPiso])
                bloqPiso = -1                
            bloqPiso += 1
        subPlats[sP]["puntas_izquierda"]= puntasI
        subPlats[sP]["puntas_derecha"]= puntasD
        sP+=1
    return subPlat1, subPlat2        


def reenumeraPlats(plataformas):
    """
    Esta funcion auxiliar vuelve a etiquetar las plataformas para adecuar los id al tamaño de
    la lista de plataformas
    """
    plat=0
    while plat < len(plataformas):
        plataformas[plat]["id"]=plat
        plat+=1


# In[98]:


def transitable(blocks,pendUp,pendDown, mapa, dMax=5):
    """
    Esta funcion revisa cada plataforma y decide si es transitable, es decir, si a partir de sus diferentes niveles de piso, 
    el resto de sus pisos son alcanzables.
    En caso de no ser así, debe separarse la zona no alcanzable en una nueva plataforma. Misma que tendrá que volver a evaluarse,
    posteriormente, por esta función.    
    Recibe: 
    - blocks.- Diccionario de bloques o sprites del nivel, sin ninguna evaluacion previa.
    - pendUp.- La pendiente del salto máximo (subida)
    - pendDown.- La pendiente del salto máximo (bajada)
    - mapa.- el json con la matriz del mapa
    - dMax.- La distancia máxima del salto    
    Entrega:
    Diccionario midificado de plataformas, con las plataformas separadas por transitividad.
    """
    #Lo primero, es detectar los niveles de pisos
    plat1=0
    plataformas= blocks["objetos"]
    while plat1 < len(plataformas):
        if(plataformas[plat1]["tipo"]=="piso"):
            niveles = []
            pointPiso = 0
            auxNivel = []
            while pointPiso < len(plataformas[plat1]["piso"]):            
                auxPiso = plataformas[plat1]["piso"][pointPiso]
                if(auxNivel==[]):
                    auxNivel.append(auxPiso)
                    pastX = int(auxPiso[1])
                    pastY = int(auxPiso[0])
                else:
                    #Es continuo en X y esta en el mismo nivel en Y
                    if(abs(int(auxPiso[1])-pastX)==1) and (int(auxPiso[0])==pastY):
                        auxNivel.append(auxPiso)
                        pastX = int(auxPiso[1])
                        pastY = int(auxPiso[0])
                    #Sino, se ha detectado un nuevo nivel
                    else:
                        niveles.append(copy.deepcopy(auxNivel))
                        auxNivel=[]
                        auxNivel.append(auxPiso)
                        pastX = int(auxPiso[1])
                        pastY = int(auxPiso[0])

                pointPiso+=1
            niveles.append(copy.deepcopy(auxNivel))
            #Ahorqa refinamos los niveles, puede que algunos en realidad sean un mismo piso...
            nivelx=0
            while nivelx < len(niveles):
                nively= nivelx+1
                while nively<len(niveles):
                    if(niveles[nivelx][-1][0]==niveles[nively][0][0]) and ((int(niveles[nivelx][-1][1])==int(niveles[nively][0][1])-1)):
                        newNivel=niveles[nivelx]+niveles[nively]
                        niveles.remove(niveles[nivelx])
                        niveles.remove(niveles[nively-1])
                        niveles.append(newNivel)
                        nivelx=0
                        nively=len(niveles)
                    nively+=1
                nivelx+=1
        
            #Ya con los niveles detectados, es posible saber si entre estos son alcanzables
            nivelI=0
            while nivelI < len(niveles):
                nivelJ=nivelI+1
                while nivelJ<len(niveles):
                    pisoI=0
                    alcanza=0
                    pObs=0
                    pSalto=0                    
                    subPlat1, subPlat2 = separaPlat(plataformas[plat1], niveles[nivelI])                
                    lastId = plataformas[-1]["id"]
                    subPlat1["id"]=lastId+1
                    subPlat2["id"]=lastId+2
                    #print("Se crearon las plataformas ", subPlat1["id"], "y", subPlat2["id"])                
                    blocks["objetos"].append(subPlat1)
                    blocks["objetos"].append(subPlat2)
                    #print("Ahora el conjunto de bloques['objetos'], tiene : ", len(blocks["objetos"]), "elementos")
                    while pisoI< len(niveles[nivelI]):
                        pisoJ=0                    
                        while pisoJ< len(niveles[nivelJ]):
                            #Revisamos si son alcanzables
                            piso1 = niveles[nivelI][pisoI]
                            piso2 =  niveles[nivelJ][pisoJ]
                            llega1, distMax, dReal = alcanzaBloques(piso1,piso2,dMaxU1,pendUp,pendDown,mapa["mapa"])
                            llega2, distMax, dReal = alcanzaBloques(piso2,piso1,dMaxU1,pendUp,pendDown,mapa["mapa"])                        
                            if (llega1 and llega2):
                                alcanza+=1
                                #Si son alcanzables, entonces verificamos que no existan obstaculos entre ellas....
                                #Encontramos la probabilidad de que haya obstaculos en el camino de plataforma a plat
                                pObs = evaluaObstaculos(np.array([int(piso1[0]), int(piso1[1])]), np.array([int(piso2[0]), int(piso2[1])]),subPlat1["id"],subPlat2["id"],blocks, mapa)
                                #Encontramos los posibles bloqueos de salto entre plataforma y plat
                                pSalto = bloqueoSalto(np.array([int(piso1[0]), int(piso1[1])]), np.array([int(piso2[0]), int(piso2[1])]),subPlat1["id"], subPlat2["id"],blocks, mapa)                     
                            pisoJ+=1                   
                        pisoI+=1
                    #Si despues de revisar todos los bloques de piso, se determina que no hay alcanzabilidad, quiere decir que se deben separar
                    #Se conservan las plataformas nuevas y se elimina la vieja y se reinicia el ciclo con el nuevo nivel...
                    if(alcanza==0):
                        blocks["objetos"].remove(plataformas[plat1]) 
                        reenumeraPlats(blocks["objetos"])
                        nivelJ=len(niveles)
                        nivelI=len(niveles)
                        plat1=-1
                    else:
                       #Si la suma de las probabilidades de obstruccion es menor a 0.7, se considera como dos niveles transitables
                        #Por lo tanto, se desechan las plataformas nuevas
                        if(pObs+pSalto< 0.7):
                            blocks["objetos"].remove(subPlat1)
                            blocks["objetos"].remove(subPlat2)                                
                            #reenumeraPlats(blocks["objetos"])

                        #De lo contrario, debemos remover la plataforma original del conjunto de plataformas                            
                        else:          
                            blocks["objetos"].remove(plataformas[plat1])
                            reenumeraPlats(blocks["objetos"])
                            #Se reinicia el ciclo con el nuevo nivel...
                            nivelJ=len(niveles)
                            nivelI=len(niveles)
                            plat1=-1
                    nivelJ+=1
                nivelI+=1                                                
        plat1+=1 


# In[269]:


def transitable_v2(plat,blocks,pendUp,pendDown, mapa, dMax=5):
    """
    Esta funcion recibe una plataforma y encuentra todas las posibles subplataformas en ella.
    Para cada par de subplataformas se revisa si son alcanzables y con obstrucción menor al 70%,
    de ser así, las une.
    De lo contrario, las mantiene separadas
    Recibe: 
    - plat.- La plataforma base a evaluar.
    - blocks.- Diccionario de bloques o sprites del nivel, sin ninguna evaluacion previa.
    - pendUp.- La pendiente del salto máximo (subida)
    - pendDown.- La pendiente del salto máximo (bajada)
    - mapa.- el json con la matriz del mapa
    - dMax.- La distancia máxima del salto    
    Entrega:
    Lista de plataformas finales y una bandera que permite saber si es necesario actualizar el conjunto
    completo de plataformas.
    """
    
    xPoints=[]
    yPoints=[]
    change = False
    for p in plat["puntos"]:            
        if(int(p[1]) not in xPoints):
            xPoints.append(int(p[1]))
        if(int(p[0]) not in yPoints):
            yPoints.append(int(p[0]))
    yPoints.sort()
    xPoints.sort()
    y=0
    while y< len(yPoints):
        yPoints[y]=str(yPoints[y])
        y+=1
    x=0
    while x< len(xPoints):
        xPoints[x]=str(xPoints[x])
        x+=1
        
    subPlats = []
    for fila in yPoints:
        auxSubP = []
        for columna in xPoints:
            if [fila, columna] in plat["piso"] and auxSubP==[]:
                auxSubP.append([fila, columna])
            elif auxSubP!=[] and fila== auxSubP[-1][0] and int(columna)==int(auxSubP[-1][1])+1 and [fila, columna] in plat["piso"]:
                auxSubP.append([fila,columna])
        if(auxSubP!=[]):
            subPlats.append(auxSubP)  
    subPlats.reverse()
    if len(subPlats)>1:
        sp1 = 0        
        while sp1<len(subPlats):        
            unir = False
            alcanza = 0
            sp2 = sp1+1
            while sp2 < len(subPlats):
                alcanza=0                          
                piso1 = 0
                pObs = []
                pSalto = []
                while piso1 < len(subPlats[sp1]):                    
                    piso2 = 0                
                    while piso2 < len(subPlats[sp2]):
                        p1 = subPlats[sp1][piso1]
                        p2 = subPlats[sp2][piso2]
                        llega1, distMax, dReal = alcanzaBloques(p1,p2,dMaxU1,pendUp,pendDown,mapa["mapa"])
                        llega2, distMax, dReal = alcanzaBloques(p2,p1,dMaxU1,pendUp,pendDown,mapa["mapa"])                        
                        if (llega1 and llega2):                          
                            alcanza+=1
                            obstaculos= plat["puntos"]
                            #Si son alcanzables, entonces verificamos que no existan obstaculos entre ellas....
                            #Encontramos la probabilidad de que haya obstaculos en el camino de plataforma a plat
                            pObs.append(evaluaObstaculos_v2(np.array([int(p1[0]), int(p1[1])]), np.array([int(p2[0]), int(p2[1])]),blocks, mapa))
                            #Encontramos los posibles bloqueos de salto entre plataforma y plat
                            pSalto.append(bloqueoSalto_v2(np.array([int(p1[0]), int(p1[1])]), np.array([int(p2[0]), int(p2[1])]),blocks, mapa, obstaculos))
                        piso2+=1
                    piso1+=1
                pObs = np.array(pObs)
                pSalto = np.array(pSalto)
                if(alcanza>0):    

                #Si la suma de las probabilidades de obstruccion es menor a 0.7, se considera como dos niveles transitables
                #Por lo tanto, se pueden unir las plataformas nuevas
                    if(pObs.min()+pSalto.min()< 0.7):                    
                        unir= True                                                                                 
                #De lo contrario, debemos remover la plataforma original del conjunto de plataformas                            
                    if unir:     
                        base1 = copy.deepcopy(subPlats[sp1])
                        base2 = copy.deepcopy(subPlats[sp2])
                        nueva = base1+base2
                        subPlats.remove(subPlats[sp1])
                        subPlats.remove(subPlats[sp2-1])
                        subPlats.append(nueva)                                        
                        sp2=len(subPlats)
                        sp1-=1           
                sp2+=1
                #Si despues de revisar todos los bloques de piso, se determina que no hay alcanzabilidad, quiere decir que se deben separar
                #Se conservan las plataformas nuevas y se elimina la vieja y se reinicia el ciclo con el nuevo nivel...                                 
            sp1+=1
    
    
    cambiar = False
    if len(subPlats)>1:
        cambiar = True
    
    if cambiar:
        #Si es necesario hacer nuevas plataformas:
        #Llenamos las plataformas nuevas con la base
        finals=[]
        for sp in subPlats:
            finals.append({'piso':sp})
        key=0
        while key < len(plat):
            #Se copian los valores de las evaluaciones de la plataforma base, que deben de estar vacio y sólo sirven para tener la plantilla completa
            #de las plataformas
            if(type(plat[list(plat.keys())[key]])!= list) and (type(plat[list(plat.keys())[key]])!= dict):
                #El id lo adquiriran despues...
                if(list(plat.keys())[key]=="id"):
                    for f in finals:                    
                        f[list(plat.keys())[key]]=""
                else:
                    for f in finals:                    
                        f[list(plat.keys())[key]]= plat[list(plat.keys())[key]]                
            #Si se trata de una lista o un diccionario, se trata de los sprites que componen a la plataforma y de los diccionarios 
            #de las plataformas con las que interactua, respectivamente
            elif type(plat[list(plat.keys())[key]])== list:
                #Solo la lista de puntos de piso ya se conoce  
                if list(plat.keys())[key] !='piso':            
                    for f in finals:
                        f[list(plat.keys())[key]]=[]
            #Se trata de un diccionario...
            else: 
                for f in finals:                    
                    f[list(plat.keys())[key]]={}            
            key+=1
        #Para determinar los puntos de las plataformas, se debe conocer la sub matriz donde estos existen, por
        #ello, es necesario, para cada una, establecer un min y max tanto en x como en y y a partir de eso construir
        for f in finals:
            subMinX = 999; subMaxX = -1
            subMinY = 999; subMaxY = -1
            for f_p in f['piso']:            
                if(int(f_p[0]) < subMinY):
                    subMinY = int(f_p[0])
                if(int(f_p[0]) > subMaxY):
                    subMaxY = int(f_p[0]) 
                if(int(f_p[1]) < subMinX):
                    subMinX = int(f_p[1]) 
                if(int(f_p[1]) > subMaxX):
                    subMaxX = int(f_p[1]) 
            for subY in range(subMinY, subMaxY+1):
                for subX in range(subMinX, subMaxX+1):                    
                    if f['p_inicio']==[] and [str(subY), str(subX)] in plat['puntos']:
                        f['p_inicio']= [subY, subX]
                    if([str(subY), str(subX)] in plat['piso']) and [str(subY), str(subX)] not in f['piso']:
                        f['piso'].append([str(subY), str(subX)])
                    if([str(subY), str(subX)] in plat['puntos']):
                        f['puntos'].append([str(subY), str(subX)])
                    if([str(subY), str(subX)] in plat['contorno']):
                        f['contorno'].append([str(subY), str(subX)])
                    if([str(subY), str(subX)] in plat['techo']):
                        f['techo'].append([str(subY), str(subX)])
                    if([str(subY), str(subX)] in plat['paredes']):
                        f['paredes'].append([str(subY), str(subX)])
                    if len(f['puntas_izquierda'])<3 and [str(subY), str(subX)] in plat['piso']:
                        f['puntas_izquierda'].append([str(subY), str(subX)])
                if len(f['puntas_derecha'])<3:
                    rev=subMaxX+1
                    while rev>=subMinX:
                        if len(f['puntas_derecha'])<3 and [str(subY), str(rev)] in plat['piso']:
                            f['puntas_derecha'].append([str(subY), str(rev)])
                        rev-=1
                        
        #Todos aquellos puntos que aun no forman parte de ninguna subplataforma, se agregaran a la primera de ellas
        resto = copy.deepcopy(plat['puntos'])
        for f in finals:
            for f_p in f['puntos']:
                if f_p in resto:
                    resto.remove(f_p)
       # print("resto: \n\n",resto)
        for r in resto:
            if(r in plat['contorno']):
                finals[0]['contorno'].append(r)
            if(r in plat['techo']):
                finals[0]['techo'].append(r)
            if(r in plat['paredes']):
                finals[0]['paredes'].append(r)
            if(r in plat['piso']):
                finals[0]['piso'].append(r)
            if(r in plat['puntos']):
                finals[0]['puntos'].append(r)
         #Ya que se tiene el cascaron de las plataformas finales, es necesario recalcular       
        return finals, cambiar
    else:
        #Si no era necesario cambiar la plataforma original, se regresa ésta en una lista
        #y el indicadorde que no se necesitan cambios
        return [plat], cambiar


# In[256]:


def refinaPlats (bloques, pendUp,pendDow, mapa):
    b=0
    while b < len(bloques["objetos"]):
        if bloques["objetos"][b]["tipo"]=="piso":
            antes = copy.deepcopy(bloques['objetos'][:b])
            despues = copy.deepcopy(bloques['objetos'][b+1:])
            plats, cambio = transitable_v2(bloques["objetos"][b],bloques, pendUp, pendDown, mapa)
            if cambio:
                bloques["objetos"]=[]
                bloques["objetos"].extend(antes)
                bloques["objetos"].extend(plats)
                bloques["objetos"].extend(despues)
                b-=1
            for p in plats:
                b+=1
            reenumeraPlats(bloques["objetos"])
        b+=1

    return bloques

def dentroRect(bloque, rect):
    """
    Esta funcion auxiliar determina si un bloque está dentro de un rectangulo.
    El bloque está definido por sus coordenadas en una lista [x,y]
    El rectangulo está definido por sus puntos extremos, superior izquierda e
    inferior derecho en una lista [[minX,minY],[maxX, maxY]]
    """ 

    if (int(bloque[0])>=rect[0][0] and int(bloque[0])<=rect[1][0]) and (int(bloque[1])>=rect[0][1] and int(bloque[1])<=rect[1][1]):       
        return True
    else:        
        return False


# In[209]:


def recalculaTrayectorias(plataformas):
    """
    Esta funcion auxiliar sirve para encontrar la verdadera ruta que tendrán los enemigos, 
    ya que estos sprites pueden rebotar con las plataformas con las que colisionan, alterando
    la ruta que fue calculada originalmente.        
    """

    revisados={}
    for plat1 in plataformas:
        #Los enemigos horizontales chocan con paredes o con lava        
        if(plat1["tipo"]=='enemigoHorizontal'):            
            rectEnem = [[plat1["trayectoria"]["minX"],plat1["trayectoria"]["minY"]],[plat1["trayectoria"]["maxX"], plat1["trayectoria"]["maxY"]]]
            paredD = False
            paredI = False
            revisados[plat1["id"]] = 0
            plat2 = 0
            while  plat2 < len(list(plat1["alcanzado_por"].keys())):              
                contParedes = 0                
                if(plataformas[list(plat1["alcanzado_por"].keys())[plat2]]["tipo"]=="piso") or (plataformas[list(plat1["alcanzado_por"].keys())[plat2]]["tipo"]=="obstaculo"):                
                    for pared in plataformas[list(plat1["alcanzado_por"].keys())[plat2]]["paredes"]:
                        #Si la trayectoria a revisar esta marcada como no revisada                    
                        if(plataformas[list(plat1["alcanzado_por"].keys())[plat2]]["tipo"]=="obstaculo"):
                            #Para los obstaculos, pensemos que podemos moverlos hacia arriba en un cuadro.
                            pared = copy.deepcopy(pared)
                            pared[0]= int(pared[0])-1                        
                        #if not revisados[plat1["id"]]==len(plat1["alcanzado_por"]):
                            #La pared colisiona con el enemigo y no ha sido previamente revisada                 
                        if(dentroRect([int(pared[1]), int(pared[0])], rectEnem)) and int(pared[1]) < int(plat1["p_inicio"][1]) and not paredI :                       
                            dif = int(pared[1])- (int(plat1["trayectoria"]["minX"])-1)                       
                            plat1["trayectoria"]["minX"]+=dif
                            if not paredD:
                                plat1["trayectoria"]["maxX"]+=dif
                            paredI = True                                
                            plat2 = 0

                        elif(dentroRect([int(pared[1]), int(pared[0])], rectEnem)) and int(pared[1])>= int(plat1["p_inicio"][1]) and not paredD:
                            #Por la derecha (se recorren los limites en X hacia la izquierda (disminuyen))                                
                            dif = (int(plat1["trayectoria"]["maxX"])) - (int(pared[1])-1)                                
                            plat1["trayectoria"]["maxX"]-=dif
                            if not paredI:
                                plat1["trayectoria"]["minX"]-=dif                                
                            paredD = True
                            plat2 = 0                                

                        else:
                            contParedes+=1
                            if(contParedes==len(plataformas[list(plat1["alcanzado_por"].keys())[plat2]]["paredes"])):
                                revisados[plat1["id"]] += 1
                                contParedes=0
                plat2+=1


            #Los enemigos verticales chocan con piso  o techo (puede ser movil)
        elif(plat1["tipo"]=="enemigoVertical"):            
            rectEnem = [[plat1["trayectoria"]["minX"],plat1["trayectoria"]["minY"]],[plat1["trayectoria"]["maxX"], plat1["trayectoria"]["maxY"]]]          
            techo = False
            piso = False
            revisados[plat1["id"]] = 0
            plat2 = 0
            while  plat2 < len(plataformas):                                              
                if(plataformas[plat2]["tipo"]=="piso") or (plataformas[plat2]["tipo"]=="movil"):                
                    contParedes = 0
                    if plataformas[plat2]["tipo"]=="piso":
                        techoPlat = plataformas[plat2]["techo"]
                        pisoPlat = plataformas[plat2]["piso"]
                    else:
                        techoPlat=[]
                        pisoPlat=[]
                        i = plataformas[plat2]["trayectoria"]["minX"] 
                        while i <= plataformas[plat2]["trayectoria"]["maxX"] :                            
                            j= plataformas[plat2]["trayectoria"]["minY"] 
                            while j<= plataformas[plat2]["trayectoria"]["maxY"]:
                                techoPlat.append([j,i])
                                pisoPlat.append([j,i])
                                j+=1
                            i+=1
                    for pared in techoPlat :

                        if(dentroRect([int(pared[1]), int(pared[0])], rectEnem)) and int(pared[0]) < int(plat1["p_inicio"][0]) and not techo :                       
                            #COn techo (se recorren los limites en Y hacia abajo (aumentan))

                            dif = int(pared[0])- (int(plat1["trayectoria"]["minY"])-1)                                  
                            plat1["trayectoria"]["maxY"]+=dif
                            if not piso:
                                plat1["trayectoria"]["minY"]+=dif
                            techo = True                                
                            plat2 = 0
                            
                    contParedes = 0               
                    for pared in pisoPlat:                       
                        #El piso colisiona con el enenigo y no ha sido revisado antes                                                                          
                        if(dentroRect([int(pared[1]), int(pared[0])], rectEnem)) and int(pared[0])>= int(plat1["p_inicio"][0]) and not piso:
                            #Con piso (se recorren los limites en Y hacia arriba (disminuyen))                                

                            dif = int(plat1["trayectoria"]["maxY"])- (int(pared[0])-1)
                            plat1["trayectoria"]["minY"]-=dif
                            if not techo:
                                plat1["trayectoria"]["maxY"]-=dif                                
                            piso = True
                            plat2 = 0                                
                plat2+=1                     

def insertaAtaques(plataformas):
    """
    Esta funcion agrega al conjunto de plataformas los posibles ataques para cada enemigo Troll.
    Es decir, se genera un sprite nuevo, si es que existen Trolls en el conjunto de plataformas.
    El sprite "ataque" se generará en los extremos izquierdo y derecho de la trayectoria de los
    Troll. Se calculará su trayectoria, que cubre 15 bloques a lo largo, incluyendo los de inicio de movimiento
    es decir, 13 extras a los dos que ocupa la huella.
    Se recalculará también la trayectoria del ataque, ya que si golpea algún sprite o plataforma (que no sea otro enemigo),
    este desaparece.
    """
    plat = 0
    
    while plat < len(plataformas):
        #Para diferenciar a un Oso de un Troll se consulta el riesgo. El riesgo del Oso es mayor al del Troll.
        #De momento el valor del riesgoNatural del Troll es de 80, pero este podría cambiar, lo mejor sería guardar este 
        #riesgo en configPenguin
        if(plataformas[plat]["tipo"]=="enemigoHorizontal") and plataformas[plat]["riesgoNatural"]==80:
            #Creamos un nuevo objeto, el ataque por la izquierda
            ataque = {}
            ataque["id"] = len(plataformas)
            ataque["tipo"] = "ataque"
            ataque["recompensa_puntos"] = 0
            ataque["recompensa_nivel"] = 0 
            #Pongamos como riesgo 1/2 del riesgo del Troll, es decir, 40
            ataque["riesgoNatural"] = 40
            #Su punto de inicio es la esquina inferior derecha de la huella del Troll,
            #En el ataque por la izquierda eso es minX+2, de la trayectoria del Troll y MaxY        
            ataque["p_inicio"] = [plataformas[plat]["trayectoria"]["maxY"], plataformas[plat]["trayectoria"]["minX"]+2]
            ataque["huella"] = {"minY":ataque["p_inicio"][0]-1, "maxY":ataque["p_inicio"][0], "minX":ataque["p_inicio"][1]-1, "maxX":ataque["p_inicio"][1]}
            ataque["trayectoria"] = {"minY":ataque["p_inicio"][0]-1, "maxY":ataque["p_inicio"][0], "minX":ataque["p_inicio"][0]-14, "maxX":ataque["p_inicio"][1]}
            ataque["tiempo"] = 0
            ataque["utilidad"] = 0
            ataque["riesgo"]=0
            ataque["puntos"]=[]
            ataque["alcanza"]=[]            
            llena(ataque["puntos"], ataque["huella"]["minY"], ataque["huella"]["maxY"], ataque["huella"]["minX"], ataque["huella"]["maxX"])
            ataque["piso"]=[]
            llena(ataque["piso"], ataque["huella"]["minY"], ataque["huella"]["maxY"], ataque["huella"]["minX"], ataque["huella"]["maxX"])
            plataformas.append(ataque)
            #Ahora creamos el ataque por la derecha
            ataque = {}
            ataque["id"] = len(plataformas)
            ataque["tipo"] = "ataque"
            ataque["recompensa_puntos"] = 0
            ataque["recompensa_nivel"] = 0 
            #Pongamos como riesgo 1/2 del riesgo del Troll, es decir, 40
            ataque["riesgoNatural"] = 40
            #Su punto de inicio es la esquina inferior derecha de la huella del Troll,
            #En el ataque por la derecha eso es maxX, de la trayectoria del Troll y MaxY        
            ataque["p_inicio"] = [plataformas[plat]["trayectoria"]["maxY"], plataformas[plat]["trayectoria"]["maxX"]]
            ataque["huella"] = {"minY":ataque["p_inicio"][0]-1, "maxY":ataque["p_inicio"][0], "minX":ataque["p_inicio"][1]-1, "maxX":ataque["p_inicio"][1]}
            ataque["trayectoria"] = {"minY":ataque["p_inicio"][0]-1, "maxY":ataque["p_inicio"][0], "minX":ataque["p_inicio"][0]-1, "maxX":ataque["p_inicio"][1]+13}
            ataque["tiempo"] = 0
            ataque["utilidad"] = 0
            ataque["puntos"]=[]
            ataque["riesgo"]=0
            ataque["alcanza"]=[]            
            llena(ataque["puntos"], ataque["huella"]["minY"], ataque["huella"]["maxY"], ataque["huella"]["minX"], ataque["huella"]["maxX"])
            ataque["piso"]=[]
            llena(ataque["piso"], ataque["huella"]["minY"], ataque["huella"]["maxY"], ataque["huella"]["minX"], ataque["huella"]["maxX"])
            plataformas.append(ataque)
        plat+=1
    #Una vez que se agregaron los ataques a la lista de plataformas, se revisan para ver si las paredes de alguna 
    #plataforma interactuan con ellos
    plat1 = 0 #Lo usaremos para identificar a los ataques
    while plat1< len(plataformas):
        if(plataformas[plat1]["tipo"]=="ataque"):
            plat2 =0 #Lo usaremos para identificar el resto de las plataformas
            while plat2<len(plataformas):
                if(plataformas[plat2]["tipo"]=="piso") or (plataformas[plat2]["tipo"]=="movil") or (plataformas[plat2]["tipo"]=="rebote") or (plataformas[plat2]["tipo"]=="obstaculo"):
                    #Creamos el rectangulo de la trayectoria del ataque
                    rectAtaque = [[plataformas[plat1]["trayectoria"]["minX"],plataformas[plat1]["trayectoria"]["minY"]],[plataformas[plat1]["trayectoria"]["maxX"], plataformas[plat1]["trayectoria"]["maxY"]]]                    
                    #Revisamos las paredes de la plataforma plat2
                    puntoPared = 0
                    while puntoPared< len(plataformas[plat2]["paredes"]):
                        punto = [plataformas[plat2]["paredes"][puntoPared][1],plataformas[plat2]["paredes"][puntoPared][0]]
                        #Si la pared está a la derecha, cambia el maxX de la trayectoria...
                        if dentroRect(punto, rectAtaque) and plataformas[plat1]["p_inicio"][1]<= int(plataformas[plat2]["paredes"][puntoPared][1]):
                            plataformas[plat1]["trayectoria"]["maxX"]= int(plataformas[plat2]["paredes"][puntoPared][1])-1
                            #Actualizamos el rectangulo
                            rectAtaque = [[plataformas[plat1]["trayectoria"]["minX"],plataformas[plat1]["trayectoria"]["minY"]],[plataformas[plat1]["trayectoria"]["maxX"], plataformas[plat1]["trayectoria"]["maxY"]]]   
                        #Si la pared esta a la izquierda, cambia el minX de la trayectoria
                        elif dentroRect(punto, rectAtaque) and plataformas[plat1]["p_inicio"][1]> int(plataformas[plat2]["paredes"][puntoPared][1]):
                            plataformas[plat1]["trayectoria"]["minX"]= int(plataformas[plat2]["paredes"][puntoPared][1])+1
                            #Actualizamos el rectangulo
                            rectAtaque = [[plataformas[plat1]["trayectoria"]["minX"],plataformas[plat1]["trayectoria"]["minY"]],[plataformas[plat1]["trayectoria"]["maxX"], plataformas[plat1]["trayectoria"]["maxY"]]]           
                        puntoPared+=1
                plat2+=1
        plat1+=1


# In[212]:


def tamRect(rect):
    """
    Esta funcion auxiliar regresa el numero de cuadros que
    hay dentro de un rectangulo
    El rectangulo esta definido por sus esquinas:
    rect = [[minX,minY],[maxX,maxY]]
    """
    cuadros = 0
    i=rect[0][0]
    while i <=rect[1][0]:
        j=rect[0][1]
        while j<rect[1][1]:
            cuadros+=1    
            j+=1
        i+=1
    return cuadros


# In[213]:


def CalcRiesgoSalto(plataformas, plat1, plat2, distMax=6):
    """
    Esta funcion cálcula el riesgo del salto entre dos plataformas dadas.
    Requiere:
    plataformas - conjunto de objetos(sprites) del nivel
    plat1 - la plataforma origen
    plat2 - la plataforma destino
    Entrega:
    Un estimado del riesgo dependiendo de la zona de salto
    Adicionalmente, añade la utilidad de los enemigos por riesgo en el salto
    """

    #Lo primero es definir la zona de salto ideal para la transición.
    #La zona de salto esta definida como un triangulo con la altura igual a distMax y de base igual a la distancia entre las dos plataformas
    #Hay tres pendientes, una entre la punta extrema izquierda de la plataforma origen y el punto max de salto,
    #la punta extrema derecha y el max de salto y otra entre las dos puntas                                         

    #La pendiente entre puntas y la distancia entre ellas es independiente de en donde se ubiquen las plataformas origen y destino
    riesgo = 0    
    #Para las otras pendientes existen varios casos
    #Caso 1.- La plataforma destino está a la izquierda                
    caidaLibre = False
    if(int(plat2["p_inicio"][1])< int(plat1["p_inicio"][1])):                
        pOrigen = plat1["puntas_izquierda"][0]
        pDestino = plat2["puntas_derecha"][0]
        puntasOrigen = plat1["puntas_izquierda"]
        puntasDestino = plat2["puntas_derecha"]
        difX = int(pOrigen[1])-int(pDestino[1])
        col = int(pDestino[1])        
        fila=int(pOrigen[0])-distMax        
        colMax = int(pOrigen[1])
        pDer = pDestino
        pIzq = pOrigen
        if(int(pDestino[0])>=int(pOrigen[0])):
            filMax = int(pDestino[0])
        else:
            filMax = int(pOrigen[0])
        #Sub-caso 1.- La plataforma destino está antes del punto de salto máximo (distMax)
        if(difX < distMax):                    
            dCorte = float((0.5)*difX)                                    
        #Sub-caso 2.- La plataforma destino está después del punto de salto máximo (distMax)
        else: 
            dCorte = distMax  
        pendDer = pendienteB(pOrigen, [int(pOrigen[0])-distMax,int(pOrigen[1])-dCorte])
        pendIzq = pendienteB(pDestino, [int(pOrigen[0])-distMax,int(pOrigen[1])-dCorte])

    #Caso 2.- La plataforma destino está a la derecha
    elif(int(plat2["p_inicio"][1])> int(plat1["p_inicio"][1])):               
        pOrigen = plat1["puntas_derecha"][0]
        pDestino = plat2["puntas_izquierda"][0]
        puntasOrigen = plat1["puntas_derecha"]
        puntasDestino = plat2["puntas_izquierda"]
        difX = int(pDestino[1])-int(pOrigen[1])
        col = int(pOrigen[1])       
        fila=int(pOrigen[0])-distMax       
        pDer = pOrigen
        pIzq = pDestino
        colMax = int(pDestino[1])
        if(int(pDestino[0])>=int(pOrigen[0])):
            filMax = int(pDestino[0])
        else:
            filMax = int(pOrigen[0])                
        #Sub-caso 1.- La plataforma destino está antes del punto de salto máximo (distMax)        
        if(difX<distMax):
            dCorte = float((0.5)*difX)                    
        #Sub-caso 2.- La plataforma destino está después del punto de salto máximo (distMax)
        else:
            dCorte = distMax
        pendIzq = pendienteB([int(pOrigen[0])-distMax, int(pOrigen[1])+dCorte], pOrigen)
        pendDer = pendienteB(pDestino, [int(pOrigen[0])-distMax, int(pOrigen[1])+dCorte])                                 
    
    ##Están en la misma posicion en X
    else:
        caidaLibre= True #Suponemos que será una caída libre (sin moverse en las columnas)
        #Pero usamos los datos como si la plataforma destino estuviera a la derecha
        pOrigen = plat1["puntas_derecha"][0]
        pDestino = plat2["puntas_izquierda"][0]
        puntasOrigen = plat1["puntas_derecha"]
        puntasDestino = plat2["puntas_izquierda"]        
        fila=int(pOrigen[0])-distMax
        if(int(pDestino[0])>=int(pOrigen[0])):
            filMax = int(pDestino[0])
        else:
            filMax = int(pOrigen[0])  
        col = int(pOrigen[1])   
        colMax = int(pDestino[1])
        
    zona_Salto=[]
    if not caidaLibre:
        pendPuntas = pendienteB(pOrigen,pDestino)       
        contCol = copy.deepcopy(col)
        contCol-=1
        while contCol <= colMax:
            contFila = copy.deepcopy(fila)
            contFila-=1
            while contFila <= filMax:        
                pendPoint=0
                if((contCol-int(pDer[1]))<=dCorte):                 
                    pendPoint = pendienteB([contFila,contCol],pDer)                
                    if(pendPoint>=pendIzq and pendPoint<= pendPuntas):
                        zona_Salto.append([contFila, contCol])
                else:
                    pendPoint = pendienteB([contFila,contCol],pIzq)
                    if (pendPoint<=pendDer and pendPoint>= pendPuntas):
                        zona_Salto.append([contFila, contCol])
                contFila+=1
            contCol+=1
    else:
        contFila= copy.deepcopy(fila)        
        while contFila<=filMax:
            zona_Salto.append([contFila,int(pOrigen[1])])
            contFila+=1
    #EXTENSIÓN DE LA ZONA DE SALTO
    #El calculo de la zona de salto con base en las pendientes es correcto, sin embargo
    #deja un espacio muy pequeño para el salto teórico. Para agrandar un poco dicho salto,
    #se agregarán los bloques adyacentes para cada bloque que lo compone. Es decir, se agregará
    #el contorno para agrandar la zona de salto teórico en espera que el resultado sea más realista
    extendedSalto=copy.deepcopy(zona_Salto)
    for punto in zona_Salto: 
        for i in range(punto[0]-1, punto[0]+2):
            for j in range(punto[1]-1, punto[1]+2):                
                if [i,j] not in zona_Salto:
                    if[i,j] not in extendedSalto:
                        extendedSalto.append([i,j])
    zona_Salto= extendedSalto
    enems=0
    while enems<len(plataformas):
        utilidadE=0
        if(plataformas[enems]["tipo"]=="enemigoVertical") or (plataformas[enems]["tipo"]=="ataque") or (plataformas[enems]["tipo"]=="enemigoHorizontal") :
            rectEnem = [[plataformas[enems]["trayectoria"]["minX"],plataformas[enems]["trayectoria"]["minY"]],[plataformas[enems]["trayectoria"]["maxX"], plataformas[enems]["trayectoria"]["maxY"]]]
            i = 0
            contRiesgo=0
            while i < len(zona_Salto):
                if(dentroRect([zona_Salto[i][1],zona_Salto[i][0]], rectEnem)):
                    contRiesgo+=1
                i+=1
            try:
                riesgo += plataformas[enems]["riesgoNatural"]*(contRiesgo/tamRect(rectEnem))*(contRiesgo/len(zona_Salto))
                utilidadE += contRiesgo/tamRect(rectEnem)
            except:
                riesgo += 0
        plataformas[enems]["utilidad"]+=utilidadE
        enems+=1
    
    return riesgo, col, fila, colMax, puntasOrigen, puntasDestino, zona_Salto



def CalcRiesgoVoid(plataformas, col, colMax, fila):
    """
    Esta funcion calcula el riesgo del vacio entre dos plataformas
    Requiere:
    plataformas - conjunto de objetos(sprites) del nivel
    plat1 - la plataforma origen
    plat2 - la plataforma destino
    col - coordenada en x de la punta más a la izquierda del salto
    colMax - coordenada en x de la punta más a la derecha del salto
    fila - coordenada en y del punto más alto en el salto
    Entrega:
    Un estimado del riesgo dependiendo de la zona de salto    
    """
    #print("Calculando riesgo de vacio")
    #La segunda parte es el riesgo por el pizo debajo de la zona de salto
    riesgoAcumPiso = 0
    riesgoPiso = 0.5*(colMax-col) #Se agregan 0.5 de riesgo por cada bloque de piso o vacio en la caida
    profMax=-1 #La profundidad maxima de las plataformas del nivel
    i=0
    #Encontramos la profundidad maxima en las plataformas        
    while i < len(plataformas):
        j=0
        while j <len(plataformas[i]["puntos"]):
            if(int(plataformas[i]["puntos"][j][0])>profMax):
                profMax = int(plataformas[i]["puntos"][j][0]) 
            j+=1
        i+=1
    #Buscamos, en la brecha entre plat1 y plat2 las platafomas que obstruyen la caida
    contCol = copy.copy(col)

    while contCol <= colMax:
        contFila = copy.copy(fila)
        encontrado = False
        while contFila <= profMax:            

            if not encontrado:
                plat = 0
                while plat < len(plataformas):

                    pisoPlat=0
                    while pisoPlat<len(plataformas[plat]["piso"]):                        
                        #Si el sprite de piso [pisoPlat] está en la posicion de la columna
                        #del vacio, entonces lo tomamos como el piso potencial y añadimos
                        #su riesgoNatural al acumulado
                        if(int(plataformas[plat]["piso"][pisoPlat][1])==contCol) and int(plataformas[plat]["piso"][pisoPlat][0])>=contFila:
                            riesgoAcumPiso+=plataformas[plat]["riesgoNatural"]
                            encontrado = True
                        pisoPlat+=1
                    plat+=1
            contFila+=1
        #No hay piso en esta transicion
        if not encontrado:
            riesgoAcumPiso+=1
        contCol+=1    
    return riesgoAcumPiso*riesgoPiso            


def CalcRiesgoPuntas(puntas, plataformas):
    """
    Esta funcion calcula el riesgo que existe en un conjunto de puntas de una plataforma
    (pudiendo estas ser de la plataforma origen o de la destino, de una transicion).
    Recibe:
    - puntas.- Lista de puntos que conforman las puntas a analizar
    - plataformas.- Lista de bloques (sprites) del nivel   
    Entrega:
    - Riesgo de las puntas
    - Adicionalmente añade la utilidad a los enemigos por riesgo en puntas
    """
    
    enem = 0
    puntasCubiertas = 0
    riesgoPuntas=0
    while enem< len(plataformas):
        utilidadE = 0
        if(plataformas[enem]["tipo"]=="enemigoVertical") or (plataformas[enem]["tipo"]=="enemigoHorizontal") or (plataformas[enem]["tipo"]=="enemigos") or (plataformas[enem]["tipo"]=="ataque"):            
            punto = 0
            
            rectEnem = [[plataformas[enem]["trayectoria"]["minX"],plataformas[enem]["trayectoria"]["minY"]],[plataformas[enem]["trayectoria"]["maxX"], plataformas[enem]["trayectoria"]["maxY"]]]
            while punto<len(puntas):
                if(dentroRect([puntas[punto][1], int(puntas[punto][0])-1], rectEnem)):                    
                    puntasCubiertas+=1
                punto+=1
            try:
                riesgoPuntas = (puntasCubiertas/tamRect(rectEnem))*(puntasCubiertas/len(puntas))
                utilidadE += (puntasCubiertas/tamRect(rectEnem))
            except:
                riesgoPuntas = 0
        plataformas[enem]["utilidad"]+=utilidadE
        enem+=1   
    return riesgoPuntas
    


# In[218]:


def newPlatMovil(platBase, tipo=False):
    """
    Esta funcion calcula los movimientos de las plataformas moviles,
    es decir, modifica los puntos que las componen, ya sea horizontales
    o verticales.
    Recibe:
    - platBase: la plataforma original
    - mov: cuanto se ha movido 
    - tipo: False= Arriba y abajo, True = izquierda y derecha
    Entrega:
    -platsMov: Una lista con las nuevas plataformas calculadas
    """
    platsMov = []
    mov=0
    #Movimiento vertical
    if(not tipo):
        trayect = platBase["trayectoria"]["minY"]                                                
        while trayect < platBase["trayectoria"]["maxY"]:
            newPlat = copy.deepcopy(platBase)
            p=0
            while p< len(newPlat["piso"]):
                newPlat["p_inicio"][0] = str(trayect)
                newPlat['piso'][p][0] = str(trayect)            
                newPlat['puntas_derecha'][p][0]  = str(trayect)
                newPlat['puntas_izquierda'][p][0]  = str(trayect)
                p+=1
            platsMov.append(newPlat)
            trayect+=1
    #Movimiento horizontal
    else:
        trayect = platBase["trayectoria"]["minX"]                                                
        while trayect < platBase["trayectoria"]["maxX"]:
            newPlat = copy.deepcopy(platBase)
            p=0
            while p < len(newPlat["piso"]):
                newPlat["p_inicio"][1] = str(trayect)
                newPlat['piso'][p][1] = str(trayect)            
                newPlat['puntas_derecha'][p][1]  = str(trayect)
                newPlat['puntas_izquierda'][p][1]  = str(trayect)
                p+=1
            platsMov.append(newPlat)
            trayect+=1
    return platsMov


# In[219]:


def riesgoTrans(plataformas, distMax = 6):
    """
    Esta funcion calcula el riesgo para todas las transiciones detectadas entre plataformas.
    Recibe el diccionario "plataformas" que contiene cada una de éstas del nivel.
    calcula el espacio ideal de salto entre dos plataformas, una plataforma destino y otra
    origen, usando la lista "alcanza" de cada plataforma. También, se almacena la zona de salto
    calculada.
    """
    plat1 = 0
    while plat1 < len(plataformas):        
        if(plataformas[plat1]["tipo"]=="piso") or (plataformas[plat1]["tipo"]=="movil") or (plataformas[plat1]["tipo"]=="rebote") or (plataformas[plat1]["tipo"]=="obstaculo"):
            plat2 = 0
            while plat2 < len(list(plataformas[plat1]["alcanza"].keys())):             
                riesgoIr = 0
                riesgoSalto = 0
                riesgoVoid = 0
                riesgoLlegar = 0
                zona_salto = []                
                if(plataformas[plat1]["tipo"]!="movil"):                   
                    #Caso 1.- La plataforma de origen no es movil y la destino tampoco...            
                    if plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["tipo"]!="movil":
                        riesgoSalto, col, fila, colMax, puntasOrigen, puntasDestino, zona_salto = CalcRiesgoSalto(plataformas, plataformas[plat1], plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]], distMax)                
                        riesgoVoid = CalcRiesgoVoid(plataformas, col, colMax, fila)
                        riesgoIr = CalcRiesgoPuntas(puntasOrigen, plataformas)
                        riesgoLlegar = CalcRiesgoPuntas(puntasDestino, plataformas)
                    
                    #Caso 2.- La plataforma de origen no es movil y la de destino sí...
                    else:
                        mov=0                    
                        #Si es plataforma movil vertical...
                        if(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["trayectoria"]["maxX"]-plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["trayectoria"]["minX"]==1):                                                                             
                            plat2Aux = newPlatMovil(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]], False)                         
                        #Si es plataforma movil horizontal...
                        else:                                                  
                            plat2Aux = newPlatMovil(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]], True)                            
                        
                        subPlat2 =0
                        while subPlat2<len(plat2Aux):
                            riesgoSaltoAux, col, fila, colMax, puntasOrigen, puntasDestino, zona_saltoAux = CalcRiesgoSalto(plataformas,plataformas[plat1] , plat2Aux[subPlat2], distMax)                                            
                            riesgoVoid += CalcRiesgoVoid(plataformas, col, colMax, fila)
                            riesgoSalto += riesgoSaltoAux 
                            riesgoIr += CalcRiesgoPuntas(puntasOrigen, plataformas)
                            riesgoLlegar += CalcRiesgoPuntas(puntasDestino, plataformas)  
                            saltoAuxCont=0
                            while saltoAuxCont< len(zona_saltoAux):
                                if(zona_saltoAux[saltoAuxCont] not in zona_salto):
                                    zona_salto.append(zona_saltoAux[saltoAuxCont])
                                saltoAuxCont+=1
                            subPlat2+=1
                        riesgoSalto/=len(plat2Aux)
                        riesgoVoid/=len(plat2Aux)
                        riesgoIr /=len(plat2Aux)
                        riesgoLlegar/=len(plat2Aux)

                else:                                                           
                    #Caso 3.- La plataforma origen es movil y la destino no....
                    if plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["tipo"]!="movil":
                        mov=0                    
                        #Si es plataforma movil vertical...
                        if(plataformas[plat1]["trayectoria"]["maxX"]-plataformas[plat1]["trayectoria"]["minX"]==1):                                                                             
                            plat1Aux = newPlatMovil(plataformas[plat1], False)                             
                        #Si es plataforma movil horizontal...
                        else:                                                   
                            plat1Aux = newPlatMovil(plataformas[plat1], True)                         
                        subPlat1=0
                        while subPlat1 < len(plat1Aux):
                            riesgoSaltoAux, col, fila, colMax, puntasOrigen, puntasDestino, zona_saltoAux = CalcRiesgoSalto(plataformas,plat1Aux[subPlat1] , plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]], distMax)                
                            riesgoVoid += CalcRiesgoVoid(plataformas, col, colMax, fila)
                            riesgoSalto += riesgoSaltoAux 
                            riesgoIr += CalcRiesgoPuntas(puntasOrigen, plataformas)
                            riesgoLlegar += CalcRiesgoPuntas(puntasDestino, plataformas)                                
                            saltoAuxCont=0
                            while saltoAuxCont< len(zona_saltoAux):
                                if(zona_saltoAux[saltoAuxCont] not in zona_salto):
                                    zona_salto.append(zona_saltoAux[saltoAuxCont])
                                saltoAuxCont+=1
                            subPlat1+=1                            
                        riesgoSalto/=len(plat1Aux)
                        riesgoVoid/=len(plat1Aux)
                        riesgoIr /=len(plat1Aux)
                        riesgoLlegar/=len(plat1Aux)
                    
                    #Caso 4.- La plataforma origen y la destino son moviles
                    else:                       
                        trayect = plataformas[plat1]["trayectoria"]["minX"] 
                        #Si es plataforma movil 1 vertical...
                        if(plataformas[plat1]["trayectoria"]["maxX"]-plataformas[plat1]["trayectoria"]["minX"]==1):                                                                             
                            plat1Aux = newPlatMovil(plataformas[plat1], False)                             
                        #Si es plataforma movil 1 horizontal...
                        else:                                                   
                            plat1Aux = newPlatMovil(plataformas[plat1], True)  
                         #Si es plataforma movil 2 vertical...
                        if(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["trayectoria"]["maxX"]-plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["trayectoria"]["minX"]==1):                                                                             
                            plat2Aux = newPlatMovil(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]], False)                         
                        #Si es plataforma movil 2 horizontal...
                        else:                                                  
                            plat2Aux = newPlatMovil(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]], True)  
                                               
                        subPlat1=0
                        while subPlat1< len(plat1Aux):
                            subPlat2=0
                            while subPlat2<len(plat2Aux):
                                riesgoSaltoAux, col, fila, colMax, puntasOrigen, puntasDestino, zona_saltoAux = CalcRiesgoSalto(plataformas,plat1Aux[subPlat1] , plat2Aux[subPlat2], distMax)                
                                riesgoVoid += CalcRiesgoVoid(plataformas, col, colMax, fila)
                                riesgoSalto += riesgoSaltoAux 
                                riesgoIr += CalcRiesgoPuntas(puntasOrigen, plataformas)
                                riesgoLlegar += CalcRiesgoPuntas(puntasDestino, plataformas)
                                saltoAuxCont=0
                                while saltoAuxCont< len(zona_saltoAux):
                                    if(zona_saltoAux[saltoAuxCont] not in zona_salto):
                                        zona_salto.append(zona_saltoAux[saltoAuxCont])
                                    saltoAuxCont+=1
                                subPlat2+=1
                            subPlat1+=1
                        riesgoSalto/=(len(plat1Aux)*len(plat2Aux))
                        riesgoVoid/=(len(plat1Aux)*len(plat2Aux))
                        riesgoIr /=(len(plat1Aux)*len(plat2Aux))
                        riesgoLlegar/=(len(plat1Aux)*len(plat2Aux))
                plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["riesgo"] = riesgoIr + riesgoSalto + riesgoVoid + riesgoLlegar
                plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["alcanzado_por"][plat1]["riesgo"] = riesgoIr + riesgoSalto + riesgoVoid + riesgoLlegar
                plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["zona_salto"] = zona_salto
                plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["alcanzado_por"][plat1]["zona_salto"] = zona_salto
                plat2+=1
        plat1+=1            
                

def riesgoPlat(plataformas):
    """
    Esta función cálcula el riesgo de la plataforma. Es decir, determina el
    riesgo asociado a atravesar una plataforma de tipo piso, movil o de rebote.
    Dicho riesgo se calcula en terminos del porcentaje de sprites de piso cubiertos por los enemigos,
    y sus ataques, en caso de que alguno tenga contacto con ellos.
    Recibe:
    - plataformas.- Lista de sprites u objetos del nivel
    Entrega:
    - No entrega nada, pero a cada sprite de tipo piso, movil o rebote le asigna su correspondiente riesgo    
    - Adicionalmente añade utilidad a los enemigos sobre las plataformas
    """
    plat1=0
    while plat1<len(plataformas):        
        if (plataformas[plat1]["tipo"]=="movil") or (plataformas[plat1]["tipo"]=="rebote") or (plataformas[plat1]["tipo"]=="piso"): 
            enem=0
            pointsRectEnems=0
            riesgoPlatAcum=0
            while enem< len(plataformas):
                utilidadE = 0
                if (plataformas[enem]["tipo"]=="enemigoVertical") or (plataformas[enem]["tipo"]=="enemigoHorizontal") or (plataformas[enem]["tipo"]=="ataque"):                    
                    riesgoPlat=0
                    puntoPiso=0
                    rectEnem = [[plataformas[enem]["trayectoria"]["minX"],plataformas[enem]["trayectoria"]["minY"]],[plataformas[enem]["trayectoria"]["maxX"], plataformas[enem]["trayectoria"]["maxY"]]]
                    pointsRectEnems+= tamRect(rectEnem)                    
                    #Caso 1.- La plataforma es de rebote o de piso
                    if(plataformas[plat1]["tipo"]!="movil"):
                        while puntoPiso < len(plataformas[plat1]["piso"]):                        
                            if(dentroRect([plataformas[plat1]["piso"][puntoPiso][1],int(plataformas[plat1]["piso"][puntoPiso][0])-1],rectEnem)):
                                riesgoPlat+=plataformas[enem]["riesgoNatural"]
                            puntoPiso+=1
                        try:
                            riesgoPlatAcum+= (riesgoPlat/pointsRectEnems)*(riesgoPlat/len(plataformas[plat1]["piso"]))
                            utilidadE+= (riesgoPlat/plataformas[enem]["riesgoNatural"])/pointsRectEnems
                        except:
                            riesgoPlatAcum+= 0
                    #La plataforma es movil
                    else:
                        #Si es plataforma movil vertical...
                        if(plataformas[plat1]["trayectoria"]["maxX"]-plataformas[plat1]["trayectoria"]["minX"]==1):                                                                             
                            plat1Aux = newPlatMovil(plataformas[plat1], False)                             
                        #Si es plataforma movil horizontal...
                        else:                                                   
                            plat1Aux = newPlatMovil(plataformas[plat1], True)  
                        subPlat1=0
                        while subPlat1< len(plat1Aux):
                            while puntoPiso < len(plat1Aux[subPlat1]["piso"]):                        
                                if(dentroRect([plat1Aux[subPlat1]["piso"][puntoPiso][1],int(plat1Aux[subPlat1]["piso"][puntoPiso][0])-1],rectEnem)):
                                    riesgoPlat+=plataformas[enem]["riesgoNatural"]
                                puntoPiso+=1
                            subPlat1+=1
                                                   
                        try:
                            riesgoPlatAcum+= ((riesgoPlat/pointsRectEnems)*(riesgoPlat/len(plataformas[plat1]["piso"])))/len(plat1Aux)
                            utilidadE+= (riesgoPlat/plataformas[enem]["riesgoNatural"])/pointsRectEnems
                        except:
                            riesgoPlatAcum+= 0                        
                plataformas[enem]["utilidad"]+=utilidadE
                enem+=1
            plataformas[plat1]["riesgo"]=riesgoPlatAcum
        plat1+=1


def calculaRecompensaPuntosPlat(plataformas):
    """
    Esta funcion revisa todos los sprite alcanzables de una plataforma
    que esten dentro de sus coordenadas mínima y máxima en X. Si alguno
    de estos sprites contiene un valor de recompensa_puntos, se le suma como
    recompensa a la plataforma.
    """
    plat1 = 0
    while plat1<len(plataformas):
        if (plataformas[plat1]["tipo"]=="movil") or (plataformas[plat1]["tipo"]=="rebote") or (plataformas[plat1]["tipo"]=="piso"): 
            plat2 = 0            
            reward = 0                        
            while plat2 < len(plataformas[plat1]["alcanza"]):
                platDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]
                if platDestino["tipo"]!="movil" and platDestino["tipo"]!="rebote" and platDestino["tipo"]!="piso":
                    utilidadR = 0
                    pInicioPlat2 = platDestino["p_inicio"]
                    #El punto inicial de la plataforma objetivo está dentro del rango del piso de la plataforma origen
                    if(int(pInicioPlat2[1])>= int(plataformas[plat1]["puntas_izquierda"][0][1])) and (int(pInicioPlat2[1])<=int(plataformas[plat1]["puntas_derecha"][0][1])):
                        #La plataforma destino ofrece una recompensa...
                        reward+= plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["recompensa_puntos"]
                        utilidadR+=1
                    plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["utilidad"]+=utilidadR
                plat2+=1
            plataformas[plat1]["recompensa_puntos"]=reward
        plat1+=1

def calculaRecompensaNivelPlat(plataformas):
    """
    Esta funcion revisa todos los sprite alcanzables de una plataforma
    que esten dentro de sus coordenadas mínima y máxima en X. Si alguno
    de estos sprites contiene un valor de recompensa_nivel, se le suma como
    recompensa a la plataforma.
    """
    plat1 = 0
    while plat1<len(plataformas):
        if (plataformas[plat1]["tipo"]=="movil") or (plataformas[plat1]["tipo"]=="rebote") or (plataformas[plat1]["tipo"]=="piso"): 
            plat2 = 0            
            reward = 0                        
            while plat2 < len(plataformas[plat1]["alcanza"]):
                platDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]
                if platDestino["tipo"]!="movil" and platDestino["tipo"]!="rebote" and platDestino["tipo"]!="piso":
                    utilidadR = 0
                    pInicioPlat2 = platDestino["p_inicio"]
                    #El punto inicial de la plataforma objetivo está dentro del rango del piso de la plataforma origen
                    if(int(pInicioPlat2[1])>= int(plataformas[plat1]["puntas_izquierda"][0][1])) and (int(pInicioPlat2[1])<=int(plataformas[plat1]["puntas_derecha"][0][1])):
                        #La plataforma destino ofrece una recompensa...
                        reward+= plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["recompensa_nivel"]
                        utilidadR+=1
                    plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["utilidad"]+=utilidadR
                plat2+=1
            plataformas[plat1]["recompensa_nivel"]=reward
        plat1+=1


def calculaRecompensaPuntosTrans(plataformas):
    """
    Esta función revisa las zonas de salto de todas las transiciones entre plataformas
    y calcula con ello el valor de las recompensa_puntos de las transiciones.
    """
    plat1 = 0
    while plat1<len(plataformas):                            
        if (plataformas[plat1]["tipo"]=="movil") or (plataformas[plat1]["tipo"]=="rebote") or (plataformas[plat1]["tipo"]=="piso") or (plataformas[plat1]["tipo"]=="rebote"): 
            plat2 = 0                        
            while plat2 < len(list(plataformas[plat1]["alcanza"].keys())):
                platR = 0
                reward=0                
                while platR < len(list(plataformas[plat1]["alcanza"].keys())):
                    utilidadR = 0
                    pInicioPlatR = plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]["p_inicio"]
                    #El punto inicial de la plataforma de recompensa potencial está fuera del rango del piso de la plataforma origen
                    if(int(pInicioPlatR[1])< int(plataformas[plat1]["puntas_izquierda"][0][1])) or (int(pInicioPlatR[1])>int(plataformas[plat1]["puntas_derecha"][-1][1])):
                        #Caso 1.- Es un bloque normal de recompensa
                        if (plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]["tipo"]!="enemigoVertical") and (plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]["tipo"]!="ataque"):
                            #Se revisa si el punto inicial esta dentro de la zona de salto de la transicion entre plat1 y plat2
                            if(pInicioPlatR in plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["zona_salto"]):
                                reward+= plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]["recompensa_puntos"]                                                                
                                utilidadR+=1                                
                        #Caso 2.- Es un enemigo o ataque
                        else:
                            #Se revisa el porcentaje de bloques de la zona de salto que afecta el enemigo
                            saltoPoint=0
                            enem =  plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]
                            rectEnem = [[enem["trayectoria"]["minX"],enem["trayectoria"]["minY"]],[enem["trayectoria"]["maxX"], enem["trayectoria"]["maxY"]]]                            
                            percentEnem=0
                            while saltoPoint < len(plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["zona_salto"]):
                                punto = plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["zona_salto"][saltoPoint]                                
                                if(dentroRect([punto[1],punto[0]],rectEnem)):
                                    percentEnem+=1
                                saltoPoint+=1
                            reward+=(percentEnem/tamRect(rectEnem))*enem["recompensa_puntos"]                                                                                
                            utilidadR+=(percentEnem/tamRect(rectEnem))
                        plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]["utilidad"]+=utilidadR
                    platR+=1
                plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["recompensa_puntos"] = reward
                plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["alcanzado_por"][plat1]["recompensa_puntos"] = reward
                plat2+=1                        
        plat1+=1


def calculaRecompensaNivelTrans(plataformas):
    """
    Esta función revisa las zonas de salto de todas las transiciones entre plataformas
    y calcula con ello el valor de las recompensa_nivel de las transiciones.
    """
    plat1 = 0
    while plat1<len(plataformas):                            
        if (plataformas[plat1]["tipo"]=="movil") or (plataformas[plat1]["tipo"]=="rebote") or (plataformas[plat1]["tipo"]=="piso") or (plataformas[plat1]["tipo"]=="rebote"): 
            plat2 = 0                        
            while plat2 < len(list(plataformas[plat1]["alcanza"].keys())):
                platR = 0
                reward=0                
                while platR < len(list(plataformas[plat1]["alcanza"].keys())):
                    utilidadR = 0
                    pInicioPlatR = plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]["p_inicio"]
                    #El punto inicial de la plataforma de recompensa potencial está fuera del rango del piso de la plataforma origen
                    if(int(pInicioPlatR[1])< int(plataformas[plat1]["puntas_izquierda"][0][1])) or (int(pInicioPlatR[1])>int(plataformas[plat1]["puntas_derecha"][-1][1])):
                        #Caso 1.- Es un bloque normal de recompensa
                        if (plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]["tipo"]!="enemigoVertical") and (plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]["tipo"]!="ataque"):
                            #Se revisa si el punto inicial esta dentro de la zona de salto de la transicion entre plat1 y plat2
                            if(pInicioPlatR in plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["zona_salto"]):
                                reward+= plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]["recompensa_nivel"]                                                                
                                utilidadR+=1                                
                        #Caso 2.- Es un enemigo o ataque
                        else:
                            #Se revisa el porcentaje de bloques de la zona de salto que afecta el enemigo
                            saltoPoint=0
                            enem =  plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]
                            rectEnem = [[enem["trayectoria"]["minX"],enem["trayectoria"]["minY"]],[enem["trayectoria"]["maxX"], enem["trayectoria"]["maxY"]]]                            
                            percentEnem=0
                            while saltoPoint < len(plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["zona_salto"]):
                                punto = plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["zona_salto"][saltoPoint]                                
                                if(dentroRect([punto[1],punto[0]],rectEnem)):
                                    percentEnem+=1
                                saltoPoint+=1
                            reward+=(percentEnem/tamRect(rectEnem))*enem["recompensa_nivel"]                                                                                
                            utilidadR+=(percentEnem/tamRect(rectEnem))
                        plataformas[list(plataformas[plat1]["alcanza"].keys())[platR]]["utilidad"]+=utilidadR
                    platR+=1
                plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["recompensa_nivel"] = reward
                plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["alcanzado_por"][plat1]["recompensa_nivel"] = reward
                plat2+=1                        
        plat1+=1

def calculaPrecision(plataformas, pendUp, pendDown, mapa, dMax=5):
    """
    Esta funcion calcula la precision requerida para llegar de una plataforma
    origen (plat1) a una plataforma destino (plat2).
    Recibe:
    - plataformas.- Lista de sprites (objetos) del nivel
    - pendUp.- La pendiente del salto máximo (subida)
    - pendDown.- La pendiente del salto máximo (bajada)
    - mapa.- el json con la matriz del mapa
    - dMax.- La distancia máxima del salto
    Entrega:
    nada pero para cada transicion detectada entre plataformas, calcula el grado de precision requerido, 
    en términos de la distancia máxima que puede haber entre dichas plataformas
    """
    #Lo primero es contar el numero de caminos entre las puntas (izquierda o derecha) de sprites
    #alcanzables desde plat1 hacia plat2 y obtener una probabilidad prob1 de llegar de plat1 a plat2,
    #en terminos de la alcanzabilidad por número de caminos disponibles. 
    #Despues, para esos mismos caminos, debe existir una distancia máxima y una distancia real,
    #dichas distancias ayudan a definir un margen de error. En este caso, se obtendrá ese margen
    #en terminos de una probabilidad, al normalizar dichas distancias y promediarlas en prob2.
    #Finalmente, se promedian ambas probabilidad para obtener la precision de la transicion            
    plat1=0
    while plat1<len(plataformas):
       
        if (plataformas[plat1]["tipo"]=="movil") or (plataformas[plat1]["tipo"]=="rebote") or (plataformas[plat1]["tipo"]=="piso") or (plataformas[plat1]["tipo"]=="rebote"): 
            plat2=0
            probs = []
            while plat2 < len(plataformas[plat1]["alcanza"]):
                conjPuntasOrigen = []
                conjPuntasDestino = []
       
                #Caso 1.- Las plataformas plat1 y plat2 son estáticas
                if(plataformas[plat1]["tipo"]!="movil") and (plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["tipo"]!="movil"):
                    #Subcaso 1.- La plataforma origen esté a la izquierda de la plataforma destino
                    pOrigen = plataformas[plat1]["p_inicio"]
                    pDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["p_inicio"]                
                    if(int(pOrigen[1])< int(pDestino[1])):
                        psOrigen = plataformas[plat1]["puntas_derecha"]
                        psDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["puntas_izquierda"]
                        conjPuntasOrigen.append(psOrigen)
                        conjPuntasDestino.append(psDestino)
                    #Subcaso2.- La platfaorma origen está a la derecha de la plataforma destino
                    else:
                        psOrigen = plataformas[plat1]["puntas_izquierda"]
                        psDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["puntas_derecha"]
                        conjPuntasOrigen.append(psOrigen)
                        conjPuntasDestino.append(psDestino)
                
                #Caso 2.- La plataforma plat1 es movil pero la plataforma plat2 es estatica
                elif(plataformas[plat1]["tipo"]=="movil") and (plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["tipo"]!="movil"):
                    #Si es plataforma movil vertical...
                    if(plataformas[plat1]["trayectoria"]["maxX"]-plataformas[plat1]["trayectoria"]["minX"]==1):                                                                             
                        plat1Aux = newPlatMovil(plataformas[plat1], False)                         
                    #Si es plataforma movil horizontal...
                    else:                                                  
                        plat1Aux = newPlatMovil(plataformas[plat1], True)                            
                    subPlat1= 0
                    while subPlat1< len(plat1Aux):
                        pOrigen = plat1Aux[subPlat1]["p_inicio"]
                        pDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["p_inicio"]                
                        if(int(pOrigen[1])< int(pDestino[1])):
                            psOrigen = plataformas[plat1]["puntas_derecha"]
                            psDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["puntas_izquierda"]
                            conjPuntasOrigen.append(psOrigen)
                            conjPuntasDestino.append(psDestino)
                        #Subcaso2.- La platfaorma origen está a la derecha de la plataforma destino
                        else:
                            psOrigen = plataformas[plat1]["puntas_izquierda"]
                            psDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["puntas_derecha"]
                            conjPuntasOrigen.append(psOrigen)
                            conjPuntasDestino.append(psDestino)
                        subPlat1+=1
                
                #Caso 3.- La plataforma plat1 es estatica pero la plataforma plat2 es movil
                elif (plataformas[plat1]["tipo"]!="movil") and (plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["tipo"]=="movil"):
                    #Si es plataforma movil vertical...
                    if(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["trayectoria"]["maxX"]-plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["trayectoria"]["minX"]==1):                                                                             
                        plat2Aux = newPlatMovil(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]], False)                         
                    #Si es plataforma movil horizontal...
                    else:                                                  
                        plat2Aux = newPlatMovil(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]], True)        
                    
                    subPlat2=0   
                    while subPlat2< len(plat2Aux):
                        pOrigen = plataformas[plat1]["p_inicio"]
                        pDestino = plat2Aux[subPlat2]["p_inicio"]                
                        if(int(pOrigen[1])< int(pDestino[1])):
                            psOrigen = plataformas[plat1]["puntas_derecha"]
                            psDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["puntas_izquierda"]
                            conjPuntasOrigen.append(psOrigen)
                            conjPuntasDestino.append(psDestino)
                        #Subcaso2.- La platfaorma origen está a la derecha de la plataforma destino
                        else:
                            psOrigen = plataformas[plat1]["puntas_izquierda"]
                            psDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["puntas_derecha"]
                            conjPuntasOrigen.append(psOrigen)
                            conjPuntasDestino.append(psDestino)
                        subPlat2+=1
                
                #Caso 4.- Ambas plataformas, plat1 y plat2 son moviles
                elif(plataformas[plat1]["tipo"]=="movil") and (plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["tipo"]=="movil"):
                    #Si es plataforma plat1 movil vertical...
                    if(plataformas[plat1]["trayectoria"]["maxX"]-plataformas[plat1]["trayectoria"]["minX"]==1):                                                                             
                        plat1Aux = newPlatMovil(plataformas[plat1], False)                         
                    #Si es plataforma plat1 movil horizontal...
                    else:                                                  
                        plat1Aux = newPlatMovil(plataformas[plat1], True)    
                    #Si es plataforma plat2 movil vertical...
                    if(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["trayectoria"]["maxX"]-plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["trayectoria"]["minX"]==1):                                                                             
                        plat2Aux = newPlatMovil(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]], False)                         
                    #Si es plataforma plat2 movil horizontal...
                    else:                                                  
                        plat2Aux = newPlatMovil(plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]], True)        
                    
                    subPlat1=0
                    while subPlat1 < len(plat1Aux):
                        pOrigen = plat1Aux[subPlat1]["p_inicio"]
                        subPlat2=0
                        while subPlat2< len(plat2Aux):
                            pDestino = plat2Aux[subPlat2]["p_inicio"]                
                            if(int(pOrigen[1])< int(pDestino[1])):
                                psOrigen = plataformas[plat1]["puntas_derecha"]
                                psDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["puntas_izquierda"]
                                conjPuntasOrigen.append(psOrigen)
                                conjPuntasDestino.append(psDestino)
                            #Subcaso2.- La platfaorma origen está a la derecha de la plataforma destino
                            else:
                                psOrigen = plataformas[plat1]["puntas_izquierda"]
                                psDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["puntas_derecha"]
                                conjPuntasOrigen.append(psOrigen)
                                conjPuntasDestino.append(psDestino)
                            subPlat2+=1
                        subPlat1+=1                       
                contConjOrigen=0
                while contConjOrigen< len(conjPuntasOrigen):                    
                    puntasOrigen = conjPuntasOrigen[contConjOrigen]
                    contConjDestino=0
                    while contConjDestino< len(conjPuntasDestino):                        
                        puntasDestino = conjPuntasDestino[contConjDestino]
                        caminos = 0 #Este contador acumula el numero de camino viables de plat1 a plat2
                        precMargenError =0 #Este contador permitirá acumular las precisiones por margenes de error de cada camino                
                        #Ahora se calculan los caminos posibles entre cada par de puntos, así como sus distancias reales y maximas
                        puntaOrigenCont=0 #Sera nuestro "i"                        
                        while puntaOrigenCont<len(puntasOrigen):                            
                            puntaDestinoCont=0 #Sera nuestro "j"
                            while puntaDestinoCont <len(puntasDestino):                                
                                llega, distMax, dReal = alcanzaBloques(puntasOrigen[puntaOrigenCont],puntasDestino[puntaDestinoCont],dMax,pendUp,pendDown,mapa["mapa"])
                                if (llega): 
                                    caminos+=1
                                    #Sabemos que distMax/distMax=1, entonces lo usamos de esa manera
                                    if(distMax>0):                                
                                        precMargenError+= 1-((1)-(dReal/distMax))
                                    else:
                                        precMargenError+=1
                                else:
                                    precMargenError+= 1
                                puntaDestinoCont+=1
                            puntaOrigenCont+=1
                        #Usando la metrica de precision, almacenamos, para este conjunto de puntas, la precision
                        #Donde la precision es  p= (precision caminos + precision por distancias)/2
                        probs.append(((caminos/9)+(precMargenError/9))/2)
                        contConjDestino+=1
                    contConjOrigen+=1
                p=0
                precision=0
                while p < len(probs):
                    precision+=probs[p]
                    p+=1
                precision/=len(probs)
                plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["precision"] = precision
                plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["alcanzado_por"][plat1]["precision"] = precision
                plat2+=1
        plat1+=1


def calculaTiempo(plataformas):
    """
    Esta funcion aplica la metrica de tiempo tanto para transiciones como para plataformas.
    La metrica a usar es:
        tiempo = 1.25*(numero de sprites de piso/756 + (riesgo medido * 3)/(riesgo natural maximo = 300))
        Para el caso de las transiciones se piensa en el "numero de sprites de piso" como la suma de los sprites
        verticales y horizontales que separan a las plataformas
    Recibe:
    - plataformas.- Lista de sprites (objetos) del nivel (que ya debe de contener el cálculo de riesgo)
    Entrega:
    - Nada pero agrega a las plataformas y sus transiciones con el cálculo de tiempo    
    """
    plat1=0
    while plat1 < len(plataformas):
        if (plataformas[plat1]["tipo"]=="movil") or (plataformas[plat1]["tipo"]=="rebote") or (plataformas[plat1]["tipo"]=="piso") or (plataformas[plat1]["tipo"]=="rebote"): 
            plataformas[plat1]["tiempo"] =  1.25*(((len(plataformas[plat1]["piso"])*configPenguin.wbloque)/756) + ((plataformas[plat1]["riesgo"]*3)/300) )
            plat2=0
            while plat2 < len(plataformas[plat1]["alcanza"]):
                iniPlat1 = plataformas[plat1]["p_inicio"]
                iniPlat2 = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["p_inicio"]
                #La plataforma origen esta a la izquierda
                if(iniPlat1[1]<iniPlat2[1]):
                    pOrigen = plataformas[plat1]["puntas_derecha"][0]
                    pDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["puntas_izquierda"][0]
                else:
                    pOrigen = plataformas[plat1]["puntas_izquierda"][0]
                    pDestino = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["puntas_derecha"][0]
                difX = abs(int(pOrigen[1])-int(pDestino[1]))
                if(pDestino[0]>pOrigen[0]):
                    yMax = int(pDestino[0])
                else:
                    yMax = int(pOrigen[0])
                difY = abs(yMax-(int(pOrigen[0])-5))
                tiempo = 1.25*(((difX+difY)*configPenguin.wbloque)/756) + ((plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["riesgo"]*3)/300)
                plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["tiempo"] = tiempo
                plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["alcanzado_por"][plat1]["tiempo"] = tiempo
                plat2+=1
        plat1+=1            



def calculaMotivacionPuntos(plataformas):
    """
    Esta funcion cálcula la motivacion de ir de una plataforma origen a una destino
    La métrica es:
     motivacion = (recompensa * (0.6/precision))- (riesgo*constante de riesgo(1))
    Recibe:
    - plataformas.- Lista de sprites u objetos del nivel, que deben estar anotadas 
                con el grado de precision, riesgo y recompensa entre transiciones
    Entrega:
    - Nada, pero asigna a cada transicion entre plataformas un grado de motivacion
    """
    plat1=0
    while plat1<len(plataformas):
        plat2=0
        while plat2< len(plataformas[plat1]["alcanza"]):
            recompensaPlat = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["recompensa_puntos"]
            recompensaTrans = plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["recompensa_puntos"]
            riesgo = plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["riesgo"]
            prec = plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["precision"]        
            try:
                if(prec<0.6):
                    motivacion = recompensaPlat + (recompensaTrans * (1+0.5*(1-prec))) - riesgo
                else:
                    motivacion = recompensaPlat + (recompensaTrans * (0.6/prec)) - riesgo
            except:
                motivacion = recompensaPlat + recompensaTrans - riesgo
            plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["motivacion_puntos"] = motivacion
            plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["alcanzado_por"][plat1]["motivacion_puntos"] = motivacion
            plat2+=1
        plat1+=1

def calculaMotivacionNivel(plataformas):
    """
    Esta funcion cálcula la motivacion de ir de una plataforma origen a una destino
    La métrica es:
     motivacion = (recompensa * (0.6/precision))- (riesgo*constante de riesgo(1))
    Recibe:
    - plataformas.- Lista de sprites u objetos del nivel, que deben estar anotadas 
                con el grado de precision, riesgo y recompensa entre transiciones
    Entrega:
    - Nada, pero asigna a cada transicion entre plataformas un grado de motivacion
    """
    plat1=0
    while plat1<len(plataformas):
        plat2=0
        while plat2< len(plataformas[plat1]["alcanza"]):
            recompensaPlat = plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["recompensa_nivel"]
            recompensaTrans = plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["recompensa_nivel"]
            riesgo = plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["riesgo"]
            prec = plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["precision"]        
            try:
                if(prec<0.6):
                    motivacion = recompensaPlat + (recompensaTrans * (1+0.5*(1-prec))) - riesgo
                else:
                    motivacion = recompensaPlat + (recompensaTrans * (0.6/prec)) - riesgo
            except:
                motivacion = recompensaPlat + recompensaTrans - riesgo
            plataformas[plat1]["alcanza"][list(plataformas[plat1]["alcanza"].keys())[plat2]]["motivacion_nivel"] = motivacion
            plataformas[list(plataformas[plat1]["alcanza"].keys())[plat2]]["alcanzado_por"][plat1]["motivacion_nivel"] = motivacion
            plat2+=1
        plat1+=1



def calculaUtilidad(plataformas):
    """
    Esta funcion cálcula la utilidad de las plataformas que NO son enemigos, o bloques de recompensa
    (submisiones, marcadores de nivel o comida).
    La utilidad de los enemigos debe calcularse cuando se hace el calculo de riesgo, para los 
    bloques de recompensa, su utilidad debe calcularse cuando se calculan las recompensas. 
    Una plataforma se considera util si:
    - Se trata de piso, rebote, obstaculo o plataforma móvil, y es alcanzable al menos por una plataforma
    y alcanza otra plataforma diferente a la que lo alcanzó.     
    """
    plat1=0
    while plat1 < len(plataformas):        
        if (plataformas[plat1]["tipo"]=="movil") or (plataformas[plat1]["tipo"]=="rebote") or (plataformas[plat1]["tipo"]=="piso") or (plataformas[plat1]["tipo"]=="rebote"): 
            diferencias=0
            plat2 = 0
            while plat2 < len(plataformas[plat1]["alcanzado_por"]):
                plat3=0
                while plat3<len(plataformas[plat1]["alcanza"]):
                    if(plataformas[list(plataformas[plat1]["alcanzado_por"].keys())[plat2]] != plataformas[list(plataformas[plat1]["alcanza"].keys())[plat3]]):
                        diferencias+=1

                    plat3+=1
                plat2+=1
            plataformas[plat1]["utilidad"]+= diferencias
        plat1+=1


def rasgos(nivel, bloques):
    """
    Esta función recibe la información completa de un nivel y arma su patron, el cual incluye:    
    - Peso del nivel (Num de bloques ocupados/num total de bloques)
    - Numero de enemigos
    - Numero de bonificaciones (comida)
    - Numero de bloques de submision
    - Numero de bloques de salto
    - Numero de bloques de fuego (obstaculo)
    - Disperción de los enemigos 
    - Disperción de los bonus (comida)
    - Dispersión de los bloques de submision
    - Dispersión de los bloques de salto
    - Dispersión de los bloques de fuego (obstaculo)
    ---------------------------------------------------------------------------------------
    """
    ocup = 0
    xEnems = []
    xBonus = []
    xSubm = []
    xFire = []
    xJumps = []
    promAlcanz = 0
    totalBloques = len(nivel["mapa"])*len(nivel["mapa"]["0"])
    
    for fila in nivel["mapa"]:
        for col in nivel["mapa"][fila]:
            if(nivel["mapa"][fila][col]!="x"):
                ocup+=1
    peso = ocup/totalBloques
    numObjs = len(bloques["objetos"])
    for bloque in bloques["objetos"]:
        if bloque["tipo"]=="enemigo" or bloque["tipo"]=="enemigos":
            xEnems.append(int(bloque["p_inicio"][1]))
        elif bloque["tipo"]== "comida":
            xBonus.append(int(bloque["p_inicio"][1]))
        elif bloque["tipo"]=="sub-mision":
            xSubm.append(int(bloque["p_inicio"][1]))
        elif bloque["tipo"]=="obstaculo":
            xFire.append(int(bloque["p_inicio"][1]))
        elif bloque["tipo"]=="rebote":
            xJumps.append(int(bloque["p_inicio"][1]))
            
        promAlcanz += float(len(bloque["alcanzado_por"])/numObjs)
        bloque["alcanzable"]= float(len(bloque["alcanzado_por"])/numObjs)
    
    promAlcanz = promAlcanz/(numObjs/(len(nivel["mapa"])/12))
    
    numEnems = len(xEnems)
    numBonus = len(xBonus)
    numSubm = len(xSubm)
    numFire = len(xFire)
    numJumps = len(xJumps)
    xEnems = np.array(xEnems)
    xBonus = np.array(xBonus)
    xSubm = np.array(xSubm)
    xFire = np.array(xFire)
    xJumps = np.array(xJumps)
    
    sparsityEnem =  0
    sparsityBonus = 0
    sparsitySubm = 0
    sparsityFire = 0
    sparsityJumps = 0
    
    for e in xEnems:
        sparsityEnem+= (e - xEnems.mean())
    try:
        sparsityEnem/=len(xEnems)
    except:
        sparsityEnem = 0
     
    for b in xBonus:
        sparsityBonus+= (b - xBonus.mean())
    try:
        sparsityBonus/=len(xBonus)
    except:
        sparsityBonus = 0
    
    for s in xSubm:
        sparsitySubm+= (s - xSubm.mean())
    try:
        sparsitySubm/=len(xSubm)
    except:
        sparsitySubm = 0
    
    for f in xFire:
        sparsityFire+= (f - xFire.mean())
    try:
        sparsityFire/=len(xFire)
    except:
        sparsityFire = 0
    
    for j in xJumps:
        sparsityJumps+= (j - xJumps.mean())
    try:
        sparsityJumps/=len(xJumps)
    except:
        sparsityJumps = 0
    
    
    return promAlcanz, peso, numEnems, numBonus, numSubm, numFire, numJumps, sparsityEnem, sparsityBonus, sparsitySubm, sparsityFire, sparsityJumps
    


# In[245]:


def evalua(plats):
    """
    Esta funcion genera un diccionario que contiene la evaluacion de un nivel. Esta evaluacion contiene una sumatoria global 
    de las metricas aplicadas tanto a plataformas como a transiciones, que se revisarán con la lista ["alcanza"] de cada plataforma.
    Recibe: 
    - plats.- Lista con los bloques o plataformas con la aplicacion de todas las metricas    
    Entrega:
    - evaluacion.- Diccionario con {nombre del nivel, diccionario de evalaucion de plataformas:{}, diccionario de evaluacion de transiciones: {}}
    
    Donde se almacenan por cada nivel:
    - diccionario de evaluacion de plataformas
        - suma de riesgo
        - suma de recompensa
        - suma de tiempo
        - suma de utilidad
    - diccionario de evaluacion de transiciones
        - suma de precision
        - suma de riesgo
        - suma de obstruccion
        - suma de distancia
        - suma de recompensa
        - suma de tiempo
        - suma de motivacion    
    """
    #Diccionario de plataformas
    plataformas={}    
    plataformas["riesgo"]= 0
    plataformas["recompensa"] = 0
    plataformas["tiempo"] = 0
    plataformas["utilidad"] = 0
    transiciones={}
    transiciones["precision"] = 0
    transiciones["riesgo"] = 0
    transiciones["obstruccion"] = 0
    transiciones["distancia"] = 0
    transiciones["recompensa"] = 0
    transiciones["tiempo"] = 0
    transiciones["motivacion"] = 0
    #Contador de plataformas
    block = 0
    totalTrans = 0
    while block < len(plats):
        plataformas["riesgo"]+= plats[block]["riesgo"]
        plataformas["recompensa"] += plats[block]["recompensa"]
        plataformas["tiempo"] += plats[block]["tiempo"]
        plataformas["utilidad"] += plats[block]["utilidad"]
        #Se revisan las transiciones de cada plataforma
        trans = 0
        while trans < len(plats[block]["alcanza"]):
            idAlc = list(plats[block]["alcanza"].keys())[trans]
            transiciones["precision"] += plats[block]["alcanza"][idAlc]["precision"]
            transiciones["riesgo"] += plats[block]["alcanza"][idAlc]["riesgo"]
            transiciones["obstruccion"] += plats[block]["alcanza"][idAlc]["obstruccion"]
            transiciones["distancia"] += plats[block]["alcanza"][idAlc]["distancia"]
            transiciones["recompensa"] += plats[block]["alcanza"][idAlc]["recompensa"]
            transiciones["tiempo"] += plats[block]["alcanza"][idAlc]["tiempo"]
            transiciones["motivacion"] += plats[block]["alcanza"][idAlc]["motivacion"]        
            trans+=1
            totalTrans += 1
        block+=1
    #promediamos todas las evaluaciones excepto las de tiempo y recompensa en plataformas
    plataformas["riesgo"] /= len(plats)
    plataformas["utilidad"] /= len(plats)
    transiciones["precision"] /= totalTrans
    transiciones["riesgo"] /= totalTrans
    transiciones["obstruccion"] /= totalTrans
    transiciones["distancia"] /= totalTrans
    transiciones["recompensa"] /= totalTrans
    transiciones["tiempo"] /= totalTrans
    transiciones["motivacion"] /= totalTrans
    return {"plataformas":plataformas, "transiciones":transiciones}





