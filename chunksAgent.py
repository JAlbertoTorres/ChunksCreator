import configPenguin
import numpy as np
import copy
import sympy
from sympy import *
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from matplotlib import cm

def init_level(limPlats, nBlocks, minBloques=2, maxBloques=5,filas=10, columnas=10, punto_inicio=[10,1], tamPlats=[6,6], punto_final=[]):
    """
    Esta funcion genera el estado inicial, esto es, una matriz con un numero de
    filas y columnas dado (si no es así, es de 10x10), en el que se agregan nBloques
    de piso y el punto inicial en una posicion fija. Además, con base en el punto inicial
    se establece un punto final.
    Recibe:
    - minBloques.- El número mínimo de plataformas a construir
    - maxBloques.- El número máximo de plataformas a construir
    - filas.- El numero de filas que conforman la rebanada de nivel (el estado del ambiente)
    - columnas.- El numero de columnas que conforman la rebanada de nivel (el estado del ambiente)
    - punto_inicio.- La posición del punto inicial
    - tamPlats.- El tamaño de la submatriz para crear plataformas
    - limPlats.- El diccionario que contiene el límite de plataformas de cada tipo
    - nBlocks.- El número aproximado de bloques a usar en cada plataforma
    - punto_final.- La posición del punto final, por defecto es vacio
    Entrega:
    - state.- El mapa que representa la rebanada creada
    - punto_inicio.- El punto donde se encuentra el objeto inicio
    - punto_final.- El punto donde se encuentra el objeto meta   
    """
    state = [['x']*columnas for i in range(filas)]
    #Se obtiene una proporcion del numero de plataformas que cabrian en el mapa
    nHor = int(filas/tamPlats[0])
    nVert = int(columnas/tamPlats[1])
    i=0
    if(minBloques> filas*columnas) or minBloques> maxBloques:        
        minBloques= int(0.25*nHor*nVer)
    if(maxBloques>filas*columnas):
        maxBloques= int(0.6*nHor*nVer)

   
    state[punto_inicio[0]][punto_inicio[1]] = 'S'
    state[punto_inicio[0]+1][punto_inicio[1]+1] = 'i'
    state[punto_inicio[0]+1][punto_inicio[1]] = 'i'
    state[punto_inicio[0]+1][punto_inicio[1]-1] = 'i'
    #Nos aseguramos que alrededor hacia arriba no haya nada
    state[punto_inicio[0]-1][punto_inicio[1]+1] = 'x'
    state[punto_inicio[0]-1][punto_inicio[1]] = 'x'
    state[punto_inicio[0]-1][punto_inicio[1]-1] = 'x'
    state[punto_inicio[0]][punto_inicio[1]+1] = 'x'
    state[punto_inicio[0]][punto_inicio[1]-1] = 'x'

   
    #Si el punto final no fue dado por el diseñador, este se define por defecto
    #en la esquina contraria al punto de inicio
    if punto_final==[]:     
        punto_final.append(filas - (punto_inicio[0]+1))        
        punto_final.append(columnas - (punto_inicio[1]+1))

    state[punto_final[0]][punto_final[1]] = 'G'
    state[punto_final[0]+1][punto_final[1]] = 'i'
    state[punto_final[0]+1][punto_final[1]+1] = 'i'
    state[punto_final[0]+1][punto_final[1]-1] = 'i'
    #Nos aseguramos que alrededor hacia arriba no haya nada
    state[punto_final[0]-1][punto_final[1]+1] = 'x'
    state[punto_final[0]-1][punto_final[1]] = 'x'
    state[punto_final[0]-1][punto_final[1]-1] = 'x'
    state[punto_final[0]][punto_final[1]+1] = 'x'
    state[punto_final[0]][punto_final[1]-1] = 'x'


    plats = np.random.randint(minBloques,maxBloques)
    while i < plats:
       
        plataformas,nPlats = detectaObjetos(tamPlats, state)        
        nState = inserta('i', state, limPlats, nPlats, tamPlats, nBlocks)                            
        state = copy.deepcopy(nState)

        i+=1   

    return state, punto_inicio, punto_final


# In[3]:

def creaPlat(tipo ="piso", fils=5, cols=5, nBlocks=10):
    """
    Esta funcion crea una plataforma de piso o de fuego procurando
    que todos los sprites que la componen sean adyecentes. 
    Para ello se elige una posicion inicial al azar y aparte de ella
    se llena el número de bloques solicitados por el usuario.
    Recibe:
    - tipo.- El tipo de plataforma a crear (puede ser 'piso' o 'fuego')
        Si el usuario ingresa alguna cadena desconocida, se asume que pidio fuego
    - cols.- El número de columnas que ocupará la platforma
    - fils.- El número de filas que ocupará la plataforma
    - nBlocks.- El número de sprites que se deben usar para construir la plataforma
    Entrega:
    - plat.- La matriz (una lista de listas) que contiene la plataforma construida
    """
    #Primero se define el dato con el que se construirá la plataforma
    if tipo =="piso":
        sprite = 'i'
    else: #Si el tipo definido no es 'piso', se asume que es 'fuego'
        sprite = 'f'
    plat = [['x']*cols for i in range(fils)]
    
    iniy = np.random.randint(0,fils)
    inix = np.random.randint(0,cols)
    plat[iniy][inix] = sprite
    block = 1
    piniy = copy.copy(iniy)
    pinix = copy.copy(inix)
    while block < nBlocks:
        #Se tienen 8 posibles opciones para que el bloque sea adyecente
        #para cubirlas todas, se hara con una probabilidad del 33% un
        #cambio positivo o uno negativo tanto en x como en y. El otro
        #33 porciento indica que para ese eje el valor no cambia
        randx = np.random.uniform()
        randy = np.random.uniform()
        #Cada moneda dos da tres posibilidades, si cae entre 0.33
        if randx <=0.33 and inix<(cols-1):
            inix+=1
        elif randx >=0.66 and inix>1:
            inix-=1
        if randy <=0.33 and iniy<(fils-1):
            iniy+=1
        elif randy >=0.66 and iniy>1:
            iniy-=1
        if inix != pinix or iniy !=piniy:
            block+=1
            piniy = copy.copy(iniy)
            pinix = copy.copy(inix)
        plat[iniy][inix] = sprite
    return plat                        


# In[4]:


def muevePlat(plat, mapa, tamPlat=[5,5]):
    """
    Esta función toma una plataforma y la mueve en alguna localidad adyacente
    en el mapa.
    Para ello, se serciora que hay suficiente espacio para colocar los sprites
    de esta plataforma sin que afecte al resto de los objetos en el mapa.
    Además, si intenta con todas las posiciones adyacentes y no se ha logrado
    efectuar la acción, entonces no es posible ejecutarla y debe regresar el 
    mapa sin cambios.
    Recibe:
    - plat.- La plataforma a mover
    - mapa.- La matriz que contiene la rebanada que se esta creando
    Entrega:
    - nMapa.- La matriz modificada 
    """
    #Hacemos un primer filtro, si lo que esta arriba de esta plataforma es el 
    #inicio o fin, entonces no se moverá
    cancelled = False
    for p in plat["puntos"]:
        if mapa[int(p[0])-1][p[1]]=='S' or mapa[int(p[0])-1][p[1]]=='G':   	
            cancelled = True
    nMapa = copy.deepcopy(mapa)

    #para hacer la revision de la submatriz, se buscand primero los bloques
    plats, nPlats = detectaObjetos(tamPlat, mapa)          
    platStart = encuentraPlatMarcador(plats, 'S')      
    platGoal = encuentraPlatMarcador(plats, 'G')

    #El rectangulo que define la seccion del mapa donde se pueden efectuar acciones
    #esta definido por, 
    # el valor maximo en X de la plataforma de inicio,
    # el valor minimo en X de la plataforma de meta
    # los valores mínimo y maximo de Y del mapa
    rectanguloValido = [[platStart["huella"]["maxX"]+1,0],[platGoal["huella"]["minX"]-1, len(mapa)-1]]

    if not cancelled:
        #Lo primero es encontrar el rectangulo en el que esta la plataforma
        #Si el objeto ya tiene una "huella", podemos aprovechar y solo consultarla
        if "huella" in list(plat.keys()):
            minX = copy.copy(plat["huella"]["minX"])
            minY = copy.copy(plat["huella"]["minY"])
            maxX = copy.copy(plat["huella"]["maxX"])
            maxY = copy.copy(plat["huella"]["maxY"])
        #Si no es así, se tendrá que calcular, con base en los puntos que conforman
        #a la plataforma cuáles son son límites inferiores y superiores
        else:
            minX=999; maxX=-99; minY=999; maxY=-99
            for p in plat["puntos"]:
                if int(p[0])< minY:
                    minY = int(p[0])
                if int(p[0])> maxY:
                    maxY = int(p[0])
                if int(p[1])< minX:
                    minX = int(p[1])
                if int(p[1])> maxX:
                    maxX = int(p[1])    
        ini_p = copy.copy(plat["p_inicio"])
        
        #Se identifica el tipo de plataforma a mover
        sprite = copy.copy(mapa[ini_p[0]][ini_p[1]])
        #print("El sprite a escribir es:", sprite)		
        moved = False
        tried = []
        while not moved and len(tried)<8:   
            randx = np.random.uniform()
            randy = np.random.uniform()
            if([randx,randy] not in tried):
                tried.append([randx,randy])
            #Cada moneda dos da tres posibilidades, si cae entre 0.33
            nMinX = copy.copy(minX)
            nMinY = copy.copy(minY)
            if randx <=0.33 and maxX<=(len(mapa[0])-1):
                nMinX += 1
            elif randx >=0.66 and minX>=1:
                nMinX -= 1
            if randy <=0.33 and maxY<=(len(mapa)-1):
                nMinY += 1
            elif randy >=0.66 and minY>=1:
                nMinY -= 1
            nP_inicio =[nMinY,nMinX]    
            #Se revisa a qué direccion se quiere mover la plataforma en cada eje
            if nP_inicio[0]>=minY:
                signoY = +1
            else:
                signoY = -1
            if nP_inicio[1]>=minX:
                signoX = +1
            else:
                signoX = -1
            difX = signoX*abs(nP_inicio[1]-minX)
            difY = signoY*abs(nP_inicio[0]-minY)
            
            #Se revisa que la posición en la que se quiere mover la plataforma sea adecuada
            libre = True
            if maxY+difY < len(mapa) and maxX+difX<len(mapa[0]) and minX+difX>=0 and minY+difY>=0:            
                for p in plat["puntos"]:
                    if [p[0]+difY, p[1]+difX] not in plat["puntos"]:
                        #El espacio total de la plataforma debe estar libre (=='x')
                        if(mapa[p[0]+difY][p[1]+difX]!='x'):
                            libre = False
                        #Pero también debe estar dentro del rectangulo valido
                        if not dentroRect([p[1]+difX,p[0]+difY], rectanguloValido):
                            libre = False
            else:
                libre = False
            if nMinY==minY and nMinX==minX:
                libre=False
            #Si hay suficnete espacio libre en el mapa, movemos la plataforma a esa posicion
            if libre:
                moved = True
        
                #Primero, se borra la plataforma del mapa
                fila = minY 
                while fila <= maxY:
                    col = minX
                    while col <= maxX:
                        if nMapa[fila][col]==sprite:
                            nMapa[fila][col]='x'
                        col+=1
                    fila+=1        
                #Ahora se modifican los puntos que conforman a la plataforma
                #Eso implica modificar: p_inicio, puntos y huella(en caso de que exista)
                for p in plat["puntos"]:
                    p[0] += difY
                    p[1] += difX
                plat["p_inicio"][0] += difY
                plat["p_inicio"][1] += difX
                if "huella" in list(plat.keys()):
                    plat["huella"]["minX"] += difX
                    plat["huella"]["maxX"] += difX
                    plat["huella"]["minY"] += difY
                    plat["huella"]["maxY"] += difY
                minX += difX
                maxX += difX
                minY += difY
                maxY += difY
                #Finalmente, se agregan los nuevos puntos en el mapa resultante
        
                for p in plat["puntos"]:
                    nMapa[p[0]][p[1]]=sprite

            if plat["tipo"]=='T' or plat["tipo"]=='T1' or plat["tipo"]=='O1' or plat["tipo"]=='O':
                limits = configPenguin.limites
                 #Si es un enemigo horizontal, se coloca piso para cubrir la trayectoria                                        
                colPiso = plat['p_inicio'][1]+limits[plat["tipo"]][1][0][2]
                while colPiso <= limits[plat["tipo"]][1][0][3]:
                    if colPiso< len(mapa[0]):
                        if nMapa[plat['p_inicio'][0]+1][colPiso]!='G' and nMapa[plat['p_inicio'][0]+1][colPiso]!='S': 
                            nMapa[plat['p_inicio'][0]+1][colPiso] = 'i'
                    colPiso+=1

    return nMapa


# In[5]:


def remuevePlat(plat, mapa):
    """
    Esta funcion sirve para convertir los puntos que conforman a una plataforma
    en espacios vacios.
    Recibe:
    - plat.- La plataforma a borrar
    - mapa.- La matriz que representa la rebanada de nivel a crear
    Entrega:
    - nMapa.- El mapa modificado
    """
    #Hacemos un primer filtro, si lo que esta arriba de esta plataforma es el 
    #inicio o fin, entonces no se moverá
    cancelled = False
    for p in plat["puntos"]:
        if mapa[int(p[0])-1][int(p[1])]=='S' or mapa[int(p[0])-1][int(p[1])]=='G':
            cancelled = True
    nMapa = copy.deepcopy(mapa)
    if not cancelled:
        #Se identifica el tipo de plataforma a quitar		
        for punto in plat["puntos"]:
            #Si se trata de una plataforma de piso y hay un enemigo H arriba de ella,
            #el enemigo tambień se elimina
            p=[int(punto[0]), int(punto[1])]

            if plat["tipo"]=='i':    
                if nMapa[p[0]-1][p[1]]=="T" or nMapa[p[0]-1][p[1]]=="T1" or nMapa[p[0]-1][p[1]]=="O" or nMapa[p[0]-1][p[1]]=="O1":
                    nMapa[p[0]-1][p[1]]=="x"
            nMapa[p[0]][p[1]]='x'

    return nMapa


# In[6]:


def cambia(plat, mapa, valores):
    """
    Esta funcion cambia sobre las diferentes opciones que tiene la plataforma,
    por ello debe ejecutarse sólo sobre plataformas de tipo:
    * comida (calamares rosa y blanco, pez azul y rojo) ++Sólo para cambio de tipo
    * bloque movil (vertical u horizontal) ++ Para cambio de tipo y de dirección
    * enemigo horizontal (Oso o Troll) ++ Para cambio de tipo y de dirección
    * enemigo vertical (aguila) ++ Sólo para cambiode direccion
    Recibe:
    - plat.- La plataforma a modificar
    - mapa.- La matriz que representa la rebanada de nivel a crear
    - valores.- Las diferentes opciones sobre la plataforma, ya sea de tipo o de dirección
    Entrega:
    - nMapa.- El mapa modificado    
    """
    val = mapa[plat["p_inicio"][0]][plat["p_inicio"][1]]
    
    newVal = np.random.randint(0,len(valores))
    while valores[newVal]==val:
        newVal = np.random.randint(0,len(valores))    
    nMapa = copy.deepcopy(mapa)
    nMapa[plat["p_inicio"][0]][plat["p_inicio"][1]] = valores[newVal]
    return nMapa


def dentroRect(bloque, rect):
    """
    Esta funcion auxiliar determina si un bloque está dentro de un rectangulo.
    El bloque está definido por sus coordenadas en una lista [x,y]
    El rectangulo está definido por sus puntos extremos, superior izquierda e
    inferior derecho en una lista [[minX,minY],[maxX, maxY]]
    """ 

    if (int(bloque[0])>rect[0][0] and int(bloque[0])<rect[1][0]) and (int(bloque[1])>rect[0][1] and int(bloque[1])<rect[1][1]):       
        return True
    else:        
        return False



def encuentraPlatMarcador(bloques, marcador):    
    """
    Esta funcion encuentra la plaforma de piso que esta debajo de un marcador de inicio o fin de nivel
    Recibe:
    - bloques.- El conjunto de plataformas de la rebanada
    - marcador.- Un caracter que denota si se trata del inicio (S) o el fin del nivel (G)
    Entrega:
    - platMarcador.- La plataforma que esta debajo del inicio o el fin de nivel.
    """
    platMarcador = {}
    if marcador != 'S' and marcador!='G':
        return None

    else:
        for plataforma in bloques:
            if(plataforma["tipo"]==marcador):
                start_point =[copy.copy(plataforma["p_inicio"][0]),copy.copy(plataforma["p_inicio"][1])]
        found=False
        i=0
        while not found and i<len(bloques):        
            plataforma = bloques[i]
            for piso in plataforma["puntos"]:
                if int(piso[0])==int(start_point[0])+1 and int(piso[1])==int(start_point[1]) and not found:
                    platMarcador = copy.deepcopy(plataforma)
                    found=True
            i+=1
        #if list(platMarcador.keys())==[]:
         #   print("NO SE ENCONTRO LA PLATAFORMA", marcador)

        return platMarcador



def inserta(tipo, mapa, limPlats, nPlats, tamPlat=[5,5], nBlocks= 10):
    """
    Esta función inserta un bloque en una posición aleatoria y libre en el mapa.
    Para ello, toma varias consideraciones:
    1.- Para insertar en enemigo horizontal se debe poner una cantidad de piso tal que cubra su trayectoria.
    2.- Si se colocará un enemigo, este debe estar en un lugar que asegure que puede moverse,
        al menos en un 30% de su trayectoria.
    3.- Para colocar una plataforma de piso o fuego, esta debe crearse primero.
    4.- Existe un límite de plataformas a agregar de cada tipo a la rebanada, si el numero actual de plataformas
        en la rebanada es igual dicho límite, esta función no se ejecuta, regresa la rebnada original.
    5.- El "tipo" no debe ser un marcador de inicio o fin de nivel.    
    6.- Todo aquello que se inserte debe estar dentro de una submatriz definida por los limites
        de las plataformas de inicio y fin de nivel
    Recibe:
    - tipo.- El tipo de sprite que se va a agregar. 
    		Puede tomar los valores:
    		i - piso de hielo
    		f - piso de fuego
    		b - rebote
    		(ps, ws, rf, bf, d) - comida
    		p - pingüino rosa
    		A, A1 - Aguila, enemigo vertical (se mueve hacia arriba (A1) o hacia abajo (A))
    		O, O1 - Oso, enemigo horizontal (se mueve hacia la derecha (O) o hacia la izquierda (O1))
    		T, T1 - Troll, enemigo horizontal (se mueve hacia la derecha (T) o hacia la izquierda (T1))
    		rh, rh1 - Plataforma movil horizontal (se mueve hacia derecha (rh) o hacia la izquierda (rh1))
    		rv, rv1 - Plataforma movil vertical (se mueve hacia arriba (rv1) o hacia abajo (rv))
    		c - Punto de salvado (checkpoint)
    		l - vida extra
    - mapa.- La matriz que representa la rebanada de nivel a crear
    - limPlats.- Un diccionario que contiene, para cada tipo de plataforma, el límite que puede tener.
                (limPlats tiene valores predefinidos: 'S':1, 'G':1, 'c':1, 'p':1, el resto puede variar dependiendo del diseño)
    - nPlats.- Un diccionario que se construye después de revisar el nivel, indica cuantas plataformas hay de cada tipo en el mapa
             de entrada.
    - tamPlat.- Es el tamaño de la submatriz en la que se puede construir una plataforma de piso. 
                El formato es [filas, columnas], con numeros enteros
    - nBlocks.- El número de sprites que se deben usar para construir la plataforma
    Entrega:
    - nMapa.- El mapa modificado
    """
    nMapa = copy.deepcopy(mapa)
    #Lo primero es revisar el límite de plataformas del tipo que se quiere agregar
    #Se asume que se puede colocar
    reject = False
    if nPlats[tipo]>=limPlats[tipo] or tipo=='S' or tipo=="G":
        #Si el límite es igual al número actual de plataformas de ese tipo en la rebanada, se rechaza su insercion
        reject = True
    

     #para hacer la revision de la submatriz, se buscand primero los bloques
    plats, nPlats = detectaObjetos(tamPlat, mapa)    
    platStart = encuentraPlatMarcador(plats, 'S')      
    platGoal = encuentraPlatMarcador(plats, 'G')
    

    #El rectangulo que define la seccion del mapa donde se pueden efectuar acciones
    #esta definido por, 
    # el valor maximo en X de la plataforma de inicio,
    # el valor minimo en X de la plataforma de meta
    # los valores mínimo y maximo de Y del mapa
    rectanguloValido = [[platStart["huella"]["maxX"]+1,0],[platGoal["huella"]["minX"]-1, len(mapa)-1]]
    

    libre = 0
    i=0
    while i <len(mapa):
        j=0
        while j<len(mapa[0]):
            if(mapa[i][j]=='x') and dentroRect([j,i], rectanguloValido):
                libre+=1
            j+=1
        i+=1
    
   

    
    tried=[]
    if not reject:        
        #Importamos una estructura de configPenguin, la cual indica cual es la huella y trayectoria de los bloques
        #(en caso de que cuenten con ella)
        limites = copy.deepcopy(configPenguin.limites)
        #La estructura es {"TipoDeBloque": [[limites de huella i-esima]],[[limites de trayectoria i-esima]]}
                                        #[[minY, maxY, minX,maxX],[minY, maxY, minX,maxX]]            
        accepted = False        
        while not accepted:
            if len(tried)>= 0.9*libre:
                #print("Rechazando por exceso de intentos ")
                return nMapa
                
            #Generamos una posición aleatoria en el mapa
            pos = [np.random.randint(0, len(mapa)), np.random.randint(0, len(mapa[0]))]
            if pos not in tried:
                tried.append(pos)

            
            
            #El primer paso es verificar que la posicion inicial este dentro del rectangulo valido            
            #print("Tratando con posicion:", pos)
            #El segundo paso es verificar que esa posicion no este ocupada
            if dentroRect([pos[1],pos[0]], rectanguloValido):
                #print("El punto inicial", pos, "esta dentro del rectangulo valido")
                if nMapa[pos[0]][pos[1]]=='x':
                    accepted = True

            #else:
               # print("El punto inicial", pos, "NO esta dentro del rectangulo valido")
            #Al pasar el filtro básico, se pasa a verificar que haya espacio para agregar el 
            #bloque solicitado
            if accepted:
                #Los bloques más gentiles, son la vida extra y el rebote, pues cada uno sólo ocupa el pixel donde se encuentra su etiqueta.
                #Si pasó el primer filtro y es de tipo 'l' o 'b', se agrega sin más cálculos
                if tipo=='l' or tipo=='b':
                    #print("Agregando bloque en posicion:", pos)
                    nMapa[pos[0]][pos[1]] = tipo
                    
                #El segundo filtro es revisar los límites de la plataforma.
                #Esto se hace de dos maneras                
                #Si es de piso o fuego, entonces se crea la platforma y se revisan los limites
                elif tipo=='f' or tipo=='i':
                    if tipo=='f':
                        tipoPlat = 'fuego'
                    else:
                        tipoPlat = 'piso'
                    nPlat = creaPlat(tipoPlat, tamPlat[0], tamPlat[1],nBlocks)
                    minX=999; maxX=-99; minY=999; maxY=-99
                    fila=0
                    while fila< tamPlat[0]:
                        col=0
                        while col<tamPlat[1]:
                            if nPlat[fila][col]!='x':
                                if fila< minY:
                                    minY = fila
                                if fila> maxY:
                                    maxY = fila
                                if col< minX:
                                    minX = col
                                if col> maxX:
                                    maxX = col
                            col+=1
                        fila+=1
                    if pos[0]+maxY<len(mapa) and pos[1]+maxX<len(mapa[0]):                        
                        #La plataforma no revasa los límites.
                        #Ahora se revisa que los puntos donde existe la platforma no esten ocupados en el mapa
                        #Ademas de que esten dentro del rectangulo valido
                        fila=0
                        while fila< tamPlat[0]:
                            col=0
                            while col<tamPlat[1]:
                                if nPlat[fila][col]!='x':
                                    if nMapa[pos[0]+fila][pos[1]+col]!='x':
                                        accepted = False
                                    if not dentroRect([pos[1]+col,pos[0]+fila], rectanguloValido):
                                        #print("El punto ", [pos[0]+fila,pos[1]+col], "no esta dentro del rectangulo valido")
                                        #print("rechazando platafomra...")
                                        accepted = False
                                col+=1
                            fila+=1

                        #Si no fue rechazada, entonces se procede a escirbir la plataforma nueva en el mapa
                        if accepted:
                            #print("Agregando plataforma en posicion:", pos)
                            #print(nPlat)
                            fila=0
                            while fila< tamPlat[0]:
                                col=0
                                while col<tamPlat[1]:
                                    if nPlat[fila][col]!='x':
                                        nMapa[pos[0]+fila][pos[1]+col] = nPlat[fila][col]
                                    col+=1
                                fila+=1
                    else:
                        #print("Rechazando por que la plataforma revasa los limites")
                        accepted = False
                #EL otro caso, es que es una plataforma con huella, en cuyo caso se revisan los limites de ésta
                else:
                    #Si se trata de un bloque de comida, sus limites son los mismos que los del pez dorado
                    if tipo=='rf' or tipo=='bf' or tipo=='ws' or tipo=='ps':
                        tipoH = 'd'
                    else:
                        tipoH = tipo
                    #Se ajustan los limites con el punto elegido al azar
                    minY = pos[0]+limites[tipoH][0][0][0]; maxY = pos[0]+limites[tipoH][0][0][1]
                    minX = pos[1]+limites[tipoH][0][0][2]; maxX = pos[1]+limites[tipoH][0][0][3]                    
                    if pos[0]+maxY<len(mapa) and pos[1]+maxX<len(mapa[0]):
                        

                        #La huella esta dentro del mapa
                        #print("La huella esta dentro del mapa...")
                        #El siguiente paso es revisar si es un bloque que tiene trayectoria...
                        if len(limites[tipoH])==2:
                            #Sí tiene trayectoria
                            #En caso de que se quiera agregar un enemigo, la trayectoria debe estar libre en un 30%
                            if tipo=="O" or tipo=="O1" or tipo=="T" or tipo=="T1" or tipo=="A" or tipo=="A1":
                                libertadTrayect = 0
                                total=0
                                minYT = pos[0]+limites[tipoH][1][0][0]; maxYT = pos[0]+limites[tipoH][1][0][1]
                                minXT = pos[1]+limites[tipoH][1][0][2]; maxXT = pos[1]+limites[tipoH][1][0][3]                    
                                #Revisamos que todo el recantgulo de la trayectoria del enemigo este dentro del rectangulo valido
                                if not dentroRect([minXT,minYT], rectanguloValido) or not dentroRect([maxXT,maxYT], rectanguloValido):
                                 #   print("La trayectoria del enemigo sale del rectangulo valido")
                                    accepted = False

                                #Se ajustan estos limites...
                                if minYT<0:
                                    minYT = 0
                                if minXT<0:
                                    minXT = 0
                                if maxYT>=len(mapa):
                                    maxYT = len(mapa)-1
                                if maxXT>=len(mapa[0]):
                                    maxXT = len(mapa[0])-1
                                filT = minYT
                                while filT<=maxYT:
                                    colT = minXT                                
                                    while colT<=maxXT:
                                        total+=1
                                        if(mapa[filT][colT]=='x'):
                                            libertadTrayect+=1
                                        colT+=1
                                    filT+=1
                                if libertadTrayect/total<0.3:
                                    accepted = False
                                #Ahora se revisa que haya espacio en la huella para colocar el enemigo
                                if accepted:
                                    fila = minY
                                    while fila<=maxY:
                                        col = minX
                                        while col<=maxX:
                                            if nMapa[fila][col]!='x':
                                                #print("Rechazando por que no hay espacio libre")
                                                accepted = False
                                            col+=1
                                        fila+=1
                                 #Si no es rechazado, se agrega el objeto en la posicion
                                if accepted:
                                    if tipo!='A' and tipo!='A1':
                                        #Se revisa que la fila elegida no sea la ultima, los enemigos horizontales
                                        #requieren que se ponga piso debajo de ellos
                                        if pos[0]==len(mapa)-1:
                                            #print("Rechazando por que el en_H no flota")
                                            accepted = False
                                        if accepted:
                                            nMapa[pos[0]][pos[1]] = tipo
                                            #Si es un enemigo horizontal, se coloca piso para cubrir la trayectoria                                        
                                            colPiso = minXT
                                            while colPiso <=maxXT:
                                                if colPiso< len(mapa[0]):
                                                    if nMapa[pos[0]+1][colPiso]!='G' and nMapa[pos[0]+1][colPiso]!='S': 
                                                        nMapa[pos[0]+1][colPiso] = 'i'
                                                colPiso+=1
                                    else:
                                        #Si es un aguila, sólo se coloca
                                        #print("Agregando bloque en posicion:", pos)
                                        nMapa[pos[0]][pos[1]] = tipo
                            #si no es un enemigo, es un bloque movil, en cuyo caso no hay problema con la trayectoria
                            else:
                                #En esta caso, solo se verifica que no haya nada dentro de los límites del objeto
                                fila = minY
                                while fila<=maxY:
                                    col = minX
                                    while col<=maxX:
                                        if nMapa[fila][col]!='x':
                                            #print("Rechazando por que no hay espacio libre")
                                            accepted = False
                                        col+=1
                                    fila+=1
                                #Si no es rechazado, se agrega el objeto en la posicion
                                if accepted:
                                    #print("Agregando bloque en posicion:", pos)
                                    nMapa[pos[0]][pos[1]] = tipo
                                
                        else:
                            #print("Es un bloque sin trayectoria...")
                            #No tiene trayectoria
                            #En esta caso, solo se verifica que no haya nada dentro de los límites del objeto
                            fila = minY
                            while fila<=maxY:
                                col = minX
                                while col<=maxX:
                                    if nMapa[fila][col]!='x':
                                        #print("Rechazando por que no hay espacio libre")
                                        accepted = False
                                    col+=1
                                fila+=1
                            #Si no es rechazado, se agrega el objeto en la posicion
                            if accepted:
                                #print("Agregando bloque en posicion:", pos)
                                nMapa[pos[0]][pos[1]] = tipo
                    else:
                        accepted = False
    else:
        #Al rechazar la inserción de la plataforma, se regresa el mapa sin hacerle modificaciones
        #print("Rechazando por limite alcanzado")
        return nMapa
    return nMapa        

def puleNivel(plats, mapa):
    """
    Esta funcion convierte los sprites i y f que no son piso en iS y fS, respectivamente
    """
    nMapa = copy.deepcopy(mapa)

    for p in plats:
        if p["tipo"]=='f' or p["tipo"]=='i':
            tipoN = p["tipo"]+'S'
            piso = []
            for punto1 in p["puntos"]:
                libre = True
                for punto2 in p["puntos"]:
                    if(punto1 != punto2):
                        #revisamos que, para ningun punto2 éste esté por encima
                        #de punto1
                        if punto2[0]==punto1[0]-1 and punto2[1]==punto1[1]:
                            libre=False
                if libre:
                    piso.append(punto1)
            for point in p["puntos"]:
                if point not in piso:
                    nMapa[point[0]][point[1]]=tipoN

    return nMapa



def detectaObjetos(tamPlats, mapa):
    """
    Esta funcion encuentra los objetos presentes en un mapa del juego.
    Para ello, revisa que sean sprites adyacentes y equivalentes, en un espacio
    menor o igual al definido en tamPlats.
    Recibe:
    - tamPlats.- El tamaño máximo que pueden tener los objetos detectados ([filas,columnas])
    - mapa.- La matriz que representa la rebanada de nivel a crear
    Entrega:
    - plats.- Una lista que contiene a todas las plataformas detectadas.
              Cada plataforma tiene el formato: 
              + { "tipo":"piso", "p_inicio":[y,x], "huella":{"minX":xMin ,"maxX":xMax, "minY":yMin, "maxY":yMax}, "puntos":[[x0,y0],...,[xn,yn]] }
    - nPlats.- Un diccionario que dice, para cada tipo de plataforma, cuantos elementos hay de ella en el mapa.
    """
    #Hacemos una lista que contendrá a todos los puntos que ya pertenecen a una plataforma,
    #de este modo no seran considerados dos veces
    visitados = [] 
    plats = []
    #En nPlats existe una etiqueta para cada tipo de plataforma
    nPlats={'S':0, 'G':0, 'c':0, 'p':0, 'l':0, 'i':0, 'f':0, 'd':0,\
            'A':0, 'A1':0, 'O':0, 'O1':0, 'T':0, 'T1':0, \
            'ws':0, 'ps':0, 'bf':0, 'rf':0, \
            'b':0, 'rv':0, 'rv1':0, 'rh':0, 'rh1':0}
    finished = False
    while not finished:
        detect = False
        fila = 0    
        while fila < len(mapa):
            columna = 0
            while columna < len(mapa[0]):         
                if(fila==len(mapa)-1) and (columna == len(mapa[0])-1):
                    finished = True
                                    
                if mapa[fila][columna]!='x' and [fila,columna] not in visitados:
                    aux_type = mapa[fila][columna]                                        
                    initx = copy.copy(columna)
                    inity = copy.copy(fila)                                     
                    #print("Se detecto punto inicial en:", [inity, initx])
                    #print("Plataforma numero:", len(plats)+1)
                    detect = True
                
                if(detect):                
                    break                                    
                columna+=1
                
            if(detect):            
                break
            fila+=1

        if detect:
            exceded = False
            adyacentes = []
            points = []
            #print("plataforma en ", inity, initx)
            adyacentes.append([inity, initx])
            minX= copy.copy(initx); minY = copy.copy(inity); maxX=copy.copy(initx); maxY= copy.copy(inity)
            while(adyacentes!=[]):
                #Tomamos un elemento de la lista de adyacentes
                aux_point = adyacentes.pop()
               # print("Revisando punto adyacente", aux_point)
                if not exceded:
                    #visitados.append(aux_point)
                    fil = copy.copy(aux_point[0])
                    col = copy.copy(aux_point[1])
                    if fil > maxY:
                        maxY = copy.copy(fil)
                    if fil < minY:
                        minY = copy.copy(fil)
                    if col > maxX:
                        maxX = copy.copy(col)
                    if col < minX:
                        minX = copy.copy(col)
                    
                if (maxX-minX) <=tamPlats[1] and (maxY-minY) <=tamPlats[0]:
                    points.append(aux_point) 
                    visitados.append(aux_point)
                    lastMinx = copy.copy(minX)
                    lastMaxx = copy.copy(maxX)
                    lastMiny = copy.copy(minY)
                    lastMaxy = copy.copy(maxY)
                    for i in range(-1,2):
                        for j in range(-1,2):
                            #Debe estar en los límites de la matriz del nivel
                            if(fil+i < len(mapa)) and (fil+i>=0) and (col+j>=0) and (col+j <len(mapa[0])) :
                                if (mapa[fil+i][col+j]==aux_type):
                                    if(not [fil+i, col+j] in visitados):
                                        adyacentes.append([fil+i,col+j])
                                        #visitados.append([fil+i,col+j])
                else:
                    exceded = True        
                          

            minX = lastMinx
            minY = lastMiny
            maxX = lastMaxx
            maxY = lastMaxy
            fila = lastMiny
            #print("puntos, antes de revision:", points)
            #print("visitados, antes de revision:", visitados)
            while fila <= lastMaxy:
                col= lastMinx
                while col<=lastMaxx:
                    if (mapa[fila][col]==aux_type):
             #           print("revisando punto ", [fila,col])
                        if([fila, col] not in visitados):                            
                            #print("agregando punto", [fila, col])
                            points.append([fila,col])
                            visitados.append([fila,col])
                    col+=1
                fila+=1
            #print("puntos, despues de revision", points)
            #print("visitados, despues de revision:", visitados)
            plats.append({"tipo": aux_type, "p_inicio":[inity,initx], "puntos": points, "huella": {"minX": minX, "maxX": maxX, "minY":minY, "maxY":maxY}})
            nPlats[aux_type]+=1
    return plats, nPlats
# In[30]:
def traduceMap(mapa):
    """
    Esta funcion cambia el formato de la estructura "mapa" para que sea
    compatible con las funciones de implementacion de métricas, que se 
    aplican sobre niveles ya construidos en formato json
    Recibe:
    - mapa .- La matriz que representa la rebanada de nivel a crear
    Entrega:
    - level.- El diccionario que representa la rebanada de nivel a crear
    """
    level={}
    fila = 0
    while fila <len(mapa):
        columna = 0
        while columna<len(mapa[0]):
            if str(fila) not in list(level.keys()):
                level[str(fila)] = {}
            level[str(fila)][str(columna)]= mapa[fila][columna]
            columna+=1
        fila+=1
    return level

def reward(ritmo, ritmoObj,varRitmo, limSup, limInf, limSupObj, limInfObj, alpha=0.5, beta=0.5, castigo=False, pVal=0.5):
    """
    Esta función evalua el desempeño del generador con base en el ritmo y el valor medio.
    Esta función sirve para una característica solamente.
    Recibe:
    - ritmo.- El ritmo, expresado en número de fluctuaciones, obetnido por el generador.
    - ritmoObj.- El ritmo obejtivo, expresado en número de fluctuaciones, definido por el diseñador.
    - varRitmo.- El numero maximo de variaciones deseadas en el ritmo.
    - limSup.- El límite superior del valor medio medido.
    - limInf.- El límite inferior del valor medio medido.
    - limSupObj.- El límite superior del valor medio objetivo.
    - limInfObj.- El límite inferior del valor medio objetivo.
    - castigo.- Una bandera que indica si la recompensa debe penalizarse o no por 
                tratarse de una ruta no terminable
    Entrega:
    - reward.- Un valor entre 0 y 1 que le indica al generador qué tan bueno fue el resultado para esta característica.
    """
    if castigo:
        #print("El nivel no es terminable en la ruta objetivo")
        penalty = pVal
       
    else:
        penalty=1

    #Primero se definen las varibales para evaluar el ritmo
    x = Symbol('x') #variable
    m = ritmoObj#Symbol('m') #media
    p = (1/3)*varRitmo#Symbol('p') #desviacion estandar
    R = (1/(p*sqrt(2)*pi))*sympy.exp((-1/2)*((x-m)/p)**2)
    #print("R",R)
    objetivo = R.subs([[x, ritmo]]) #,[m, Parametros[1]],[p, Parametros[2]]])
    vMax = float((1/(p*sqrt(2)*pi))*math.exp((-1/2)*((m-m)/p)**2))
    rewardRitmo = objetivo/vMax
    #Ahora se calcula l arecompensa con base en el valor medio

    centroReal = (1/2)*(limSup-limInf)+limInf
    centroObj = (1/2)*(limSupObj-limInfObj)+limInfObj
    dist = abs(centroObj-centroReal)
    if limSup>limSupObj:
        maxLim = limSup
    else:
        maxLim=limSupObj
    #maxLim=limSupObj
    areaReal = limSup - limInf
    areaObj = limSupObj - limInfObj        
    if maxLim>0:  
        rewardValMedio = (1/2)*(1- (dist/maxLim))+ (1/2)*(1-(abs(areaObj-areaReal)/maxLim))
    else:
        rewardValMedio = (1/2)*(1- (dist))+ (1/2)*(1-(abs(areaObj-areaReal)))
    return float(penalty*((alpha)*rewardRitmo + (beta)*rewardValMedio))


# In[31]:


#float(reward(ritmo=3, ritmoObj=3, varRitmo=2, limSup=110, limInf=10, limSupObj=100, limInfObj=50))


# In[109]:



def gauss(Parametros):
    x = Symbol('x') #variable
    m = Symbol('m') #media
    p = Symbol('p') #desviacion estandar
    R = (1/(p*sqrt(2)*pi))*sympy.exp((-1/2)*((x-m)/p)**2)
    #print("R",R)
    objetivo=R.subs([[x, Parametros[0]],[m, Parametros[1]],[p, Parametros[2]]])
    vMax= float((1/(p*sqrt(2)*pi))*math.exp((-1/2)*((m-m)/p)**2))
    #print("obj",objetivo)
    return (objetivo/vMax)


# In[93]:


def searchSpace(objective,dsignParms, titleX, titleY, titleZ):
  if len(dsignParms)==1:
    x = np.linspace(dsignParms[0][0], dsignParms[0][1], (dsignParms[0][1]-dsignParms[0][0])+1)
    z=np.zeros(x.shape)
    for index,value in enumerate(x):
      
      z[index]=objective([value])
    fig=plt.figure()  
    axes=fig.add_axes([0.1,0.1,0.8,0.8])
    axes.set_xlabel(titleX)
    axes.set_ylabel(titleY)
    axes.plot(x,z)

    axes.scatter(x,z)
    
  if len(dsignParms)==2:
    x = np.linspace(dsignParms[0][0], dsignParms[0][1], 60)
    y = np.linspace(dsignParms[1][0], dsignParms[1][1], 60)
    xv,yv = np.meshgrid(x, y)
  
    mi,mj=xv.shape
    z=np.zeros(xv.shape)
    for i in range(mi):
      for j in range(mj):
        z[i,j]=objective([xv[i,j],yv[i,j]])
    
    fig=plt.figure()  
    axes=Axes3D(fig)
    axes.set_xlabel(titleX)
    axes.set_ylabel(titleY)
    axes.set_zlabel(titleZ)
    #surf = axes.scatter(xv,yv,z)
    surf = axes.plot_surface(xv, yv, z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)
  return fig,axes




