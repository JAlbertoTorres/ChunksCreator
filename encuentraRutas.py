#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np
import json
import math
import copy
from pickle import dump, dumps, load, loads
import configPenguin
import os, fnmatch
path = "/home/beto/Documentos/GameCreater/Test/nivelesEvaluados"
global contId 
contId=1

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)
    return result

def multiRoutes(grafo, nodo, ruta, finales):
    """
    Esta funcion calcula todas las posibles rutas para llegar de la plataforma de inicio
    a la plataforma meta, con base en las listas "alcanza" de cada plataforma.    
    """
    for n in grafo[int(nodo)]["alcanza"]:
        if int(n) not in ruta:                       
            newRoute=copy.deepcopy(ruta)           
            newRoute.append(int(n))
            if(grafo[int(n)]["tipo"]=="meta"):
                finales.append(newRoute)            
            multiRoutes(grafo, n, newRoute, finales)

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


# In[8]:


def addRewardsPlat(grafo, nodo, ruta):
    """
    Esta funcion revisa todos los bloques de piso de un nodo dado y agrega todos
    aquellos bloques de recompensa en la zona alcanzable desde ese bloque
    """
    for p in grafo[nodo]["piso"]:
        minX = int(p[1])-6
        minY = int(p[0])-6
        maxX = int(p[1])+6
        maxY = int(p[0])
        for reward in grafo[nodo]["alcanza"]:
            rewardBlock = grafo[int(reward)]
            if rewardBlock["tipo"]!= "piso" and rewardBlock["tipo"]!= "movil" and rewardBlock["tipo"]!= "rebota" and rewardBlock["tipo"]!= "obstaculo" and rewardBlock["tipo"]!= "checkpoint" and rewardBlock["tipo"]!= "meta":
                if(dentroRect([rewardBlock["p_inicio"][1], rewardBlock["p_inicio"][0]], [[minX,minY],[maxX,maxY]])):
                    if int(reward) not in ruta:
                        ruta.append(int(reward))
            if rewardBlock["tipo"]=="checkpoint":
                if(dentroRect([rewardBlock["p_inicio"][1], rewardBlock["p_inicio"][0]], [[minX,minY],[maxX,maxY]])):
                    if int(reward) not in ruta:
                        ruta.append(int(reward))
    return ruta                                


def addRewardsTrans(grafo, nodo1, nodo2, ruta):
    """
    Esta funcion revisa la transicion entre el nodo1 y el nodo2 y agrega todos
    aquellos bloques de recompensa en la zona de salto teorico entre dos plataformas
    """
    #print(grafo[nodo1]["alcanza"].keys())
    #print(len(grafo[nodo1]["alcanza"][str(nodo2)]["zona_salto"]))
    for puntoSalto in grafo[nodo1]["alcanza"][str(nodo2)]["zona_salto"]:
       # print(puntoSalto)
        for reward in grafo[nodo1]["alcanza"]:
            rewardBlock = grafo[int(reward)]
            if rewardBlock["tipo"]!= "piso" and rewardBlock["tipo"]!= "movil" and rewardBlock["tipo"]!= "rebota" and rewardBlock["tipo"]!= "obstaculo" and rewardBlock["tipo"]!= "checkpoint" and rewardBlock["tipo"]!= "meta":
                if(rewardBlock["p_inicio"]==puntoSalto):
                    if int(reward) not in ruta:
                        ruta.append(int(reward))
    return ruta


def ordenaCola(cola, case="min"):
    ordenados=[]
    for elem in sorted(cola.items(),  key=lambda x: x[1]) :
        ordenados.append(elem) 
    if case != "min":
        ordenados.reverse()
    return ordenados        


def dijkstra(grafo, visitados, noVisitados, distancias, cola, atributo, anteriores,case):
    """
    Aplicacion del algoritmo de Dijkstra para casos de rutas mínimas o máximas
    sobre un atributo dado
    """
    if case == "min":
        esMejor = lambda new,old : new < old
    else:
        esMejor = lambda new,old : new > old
    while(cola!={}):        
        orden= ordenaCola(cola,case)        
        nodoOrigen = orden[0][0]
        distOrigen = cola.pop(nodoOrigen)
        visitados.append(int(nodoOrigen)) 
        for n in grafo[int(nodoOrigen)]["alcanza"]:
            if int(n) not in visitados and grafo[(int(nodoOrigen))]["alcanza"][n]["obstruccion"]<=0.8:
                if grafo[n]["tipo"]!='obstaculo':
                    pesoA = grafo[int(nodoOrigen)]["alcanza"][n][atributo]
                    pesoExtra=0

                    if atributo=="tiempo" or atributo=="riesgo" or atributo=="recompensa":
                        pesoExtra+=grafo[int(nodoOrigen)][atributo]
                    peso1 = pesoA+ distOrigen+ pesoExtra
                    peso2 = copy.deepcopy(distancias[str(n)])
                    if esMejor(peso1, peso2):
                        distancias[str(n)] = peso1                
                        anteriores[str(n)] = nodoOrigen
                        if(int(n) not in list(cola.keys())) and int(n) not in visitados:
                            cola[str(n)] = distancias[str(n)]                            
                              
    return anteriores

def aplicaDijkstra():
    case = "max"
    visited = copy.deepcopy(ruta)
    unvisited=[]
    distancias={}
    anteriores={}
    i=0
    while i <len(grafo):
        if i not in ruta:
            unvisited.append(i)
            distancias[str(i)] = float('-inf')
        else:
            distancias[str(i)] = float('inf')
        anteriores[str(i)]=None
        i+=1
    anteriores[str(ruta[1])]=ruta[0]
    cola={str(visited[-1]):distancias[str(visited[-1])]}           
    rutas[atrib+"_"+case]= dijkstra(grafo, visited, unvisited, distancias, cola, atrib, anteriores, case)


# In[14]:


def bestRoutes(grafo, ruta):
    """
    Esta funcion aplica el algoritmo de disjktra en busca de las rutas óptimas
    para llegar de la plataforma de inicio a la plataforma meta. Se define óptima
    como una ruta que tiene un valor mínimo o máximo en un atributo dado 
    (riesgo, precisión, motivación, etc).
    """
    rutas={}
    llaves = list(grafo[ruta[-1]]["alcanza"].keys())
    atributos = list(grafo[ruta[-1]]["alcanza"][llaves[0]])
    for atrib in atributos:
        if atrib!="zona_salto":
            visited = copy.deepcopy(ruta)
            unvisited=[]
            distancias={}
            anteriores={}
            i=0
            case = "min"
            while i <len(grafo):
                if i not in ruta:
                    unvisited.append(i)
                    distancias[str(i)] = float('inf')
                else:
                    distancias[str(i)] = 0
                anteriores[str(i)]=None
                i+=1
            anteriores[str(ruta[1])]=ruta[0]
            cola={str(visited[-1]):distancias[str(visited[-1])]}           
            rutas[atrib+"_"+case]= dijkstra(grafo, visited, unvisited, distancias, cola, atrib, anteriores, case)
            
            visited = copy.deepcopy(ruta)
            unvisited=[]
            distancias={}
            anteriores={}
            i=0
            case = "max"
            while i <len(grafo):
                if i not in ruta:
                    unvisited.append(i)
                    distancias[str(i)] = float('-inf')
                else:
                    distancias[str(i)] = 0
                anteriores[str(i)]=None
                i+=1
            anteriores[str(ruta[1])]=ruta[0]
            cola={str(visited[-1]):distancias[str(visited[-1])]}           
            rutas[atrib+"_"+case]= dijkstra(grafo, visited, unvisited, distancias, cola, atrib, anteriores, case)            
    return rutas


def encuentraInicio(bloques):    
    initId = 99
    for plataforma in bloques:
        if(plataforma["tipo"]=="inicio"):
            initId= plataforma["id"]
    found=False
    for alcanzaIni in bloques[initId]["alcanzado_por"]:
        for piso in bloques[int(alcanzaIni)]["piso"]:
            if int(piso[0])==int(bloques[initId]["p_inicio"][0])+1 and not found:
                platInicio = alcanzaIni            
                found=True
    return initId,platInicio


def encuentraMeta(bloques):
    for plataforma in bloques:
        if(plataforma["tipo"]=="meta"):
            #print("La plataforma meta es la plataforma:", plataforma["id"])
            meta= plataforma["id"]
    return meta

def get_route(ruta, meta, inicio):
    """
    Esta funcion extrae el camino desde el nodo inicio hasta el nodo meta
    en una ruta. 
    """
    camino=[]
    camino.append(meta)
    thisNodo = copy.deepcopy(meta)
    while thisNodo != None:
        if(ruta[thisNodo]!=None):
            camino.append(str(ruta[thisNodo]))
            thisNodo=copy.deepcopy(str(ruta[thisNodo]))
        else:
            thisNodo=None
    camino.reverse()
    #print("El inicio es el bloque:", inicio)
    #print("La meta es el bloque:", meta)
    #print("El camino encontrado es:\n",camino)

    if not (str(inicio) in camino and str(meta) in camino):
        camino.append("unreachable_goal")
    return camino
    
def evalRitmo(camino, bloques, rasgo):
    """
    Esta funcion debe evaluar el ritmo de una característica dada.
    El ritmo se define a partir del número de fluctuaciones o cambios en 
    la dirección (ascenso y descenso) de la característica a lo largo
    del camino a analizar.
    Recibe: 
    - camino.- Secuencia de ids de plataformas a recorrer
    - bloques.- El conjunto completo de plataformas a revisar
    - rasgo.- La caracterísica específica a medir
    Entrega:
    - ritmo.- El numero de fluctuaciones que tiene la característica 
            a lo largo del camino dado
    - valMin.- EL valor mínimo de la característica medida
    - valMax.- EL valor máximo de la característica medida
    - castigo.- Una bandera que indica si el camino es no terminable
    """

    vals = []
    plat1 = 0
    plat2 = 1
    castigo = False
    tam = len(camino)
    if camino[-1]=="unreachable_goal":
        castigo = True
        tam-=1
    while plat2<tam:
        #print("Pasando del bloque",bloques[int(camino[plat1])]["id"], "al bloque", bloques[int(camino[plat2])]['id'])
        if(rasgo in list(bloques[int(camino[plat1])].keys())):
            vals.append(bloques[int(camino[plat1])][rasgo])
        if(plat1==0):
         #   print("La caracteristica tiene valor de: ", bloques[int(camino[plat1])]["alcanzado_por"][int(camino[plat2])][rasgo])
            if(rasgo in list(bloques[int(camino[plat1])]["alcanzado_por"][int(camino[plat2])].keys())):
                vals.append(bloques[int(camino[plat1])]["alcanzado_por"][int(camino[plat2])][rasgo])
            #vals.append(copy.copy(bloques[int(camino[plat1])]["alcanzado_por"][int(camino[plat2])][rasgo]))
        else:
          #  print("La caracteristica tiene valor de: ", bloques[int(camino[plat1])]["alcanza"][int(camino[plat2])][rasgo])
            if(rasgo in list(bloques[int(camino[plat1])]["alcanza"][int(camino[plat2])].keys())):
                vals.append(bloques[int(camino[plat1])]["alcanza"][int(camino[plat2])][rasgo])
            #vals.append(copy.copy(bloques[int(camino[plat1])]["alcanza"][int(camino[plat2])][rasgo]))
        plat1+=1
        plat2+=1
    if vals==[]:
        valsArr = np.array([0])
        fluct = copy.copy(valsArr[0])
    else:
        valsArr = np.array(vals)
        fluct = copy.copy(valsArr[0])
    ritmo=0
    i=1
    while i < len(valsArr):
        if i==1:
            if(valsArr[i]>fluct):
                change=False #Significa que va a la alsa
            else:
                change=True #Significa que va en descenso
        else:
            #El valor anterior iba en ascenso, pero ahora descendio
            if not change and valsArr[i]<fluct: 
                change=True
                ritmo+=1
                
            #El valor anterior iba en descenso, pero ahora ascendio
            if change and valsArr[i]>fluct:
                change=False
                ritmo+=1
        fluct = copy.copy(valsArr[i])
        i+=1
    #print("valsArr",valsArr)
    minVal = valsArr.min()
    maxVal = valsArr.max()
    
    return ritmo, minVal, maxVal, castigo

def escalaDatos(nivel):
    data_plats =[[],("plataformas", [])]
    data_trans =[[],("transiciones", [])]    
    escalas_plats=[]
    escalas_trans=[]
    
    measure=[]
    for label in nivel["plataformas"]:        
        if(nivel["plataformas"][label]>1):
            escalaReal = pow(10,math.floor(math.log10(abs(nivel["plataformas"][label]))))
        else:
            escalaReal=0.1
        escalas_plats.append(escalaReal)
        measure.append(nivel["plataformas"][label]/escalaReal)        
        data_plats[0].append(label+"/"+str(escalaReal))
    data_plats[1][1].append(measure)
    measure=[]
    for label in nivel["transiciones"]:
        
        if(nivel["transiciones"][label]>1):
            escalaReal = pow(10,math.floor(math.log10(abs(nivel["transiciones"][label]))))
        else:
            escalaReal=0.1
        escalas_trans.append(escalaReal)
        measure.append(nivel["transiciones"][label]/escalaReal)        
        data_trans[0].append(label+"/"+str(escalaReal))
    data_trans[1][1].append(measure)
    return data_plats, escalas_plats, data_trans, escalas_trans

def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            #FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)

    return theta


# In[ ]:


def graficaLevel(nivel, plats):
    data_plats, escalas_plats, data_trans, escalas_trans = escalaDatos(plats)

    N = len(escalas_plats)
    theta = radar_factory(N, frame='polygon')
    spoke_labels = data_plats.pop(0)

    fig, axs = plt.subplots(figsize=(9, 9), nrows=1, ncols=1,
                            subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(wspace=0.25, hspace=0.5, top=0.85, bottom=0.05)

    colors = ['b', 'r', 'g', 'm', 'y']
    # Plot the four cases from the example data on separate axes
    #for ax, (title, case_data) in zip(axs.flat, data):
    axs.set_rgrids([0,1,2,3,4,5,6,7,8,9,10 ])
    axs.set_title(data_plats[0][0], weight='bold', size='medium', position=(0.5, 1.1),
                 horizontalalignment='center', verticalalignment='center')
        #for d, color in zip(case_data, colors):
    axs.plot(theta, data_plats[0][1][0], color=colors[0])
    axs.fill(theta, data_plats[0][1][0], facecolor=colors[0], alpha=0.25)
    axs.set_varlabels(spoke_labels)
    labels = ['Area caracteristica del nivel']
    legend = axs.legend(labels, loc=(0.9, .95),
                              labelspacing=0.1, fontsize='small')
    titulo = 'Evaluacion del nivel '+nivel
    fig.text(0.5, 0.965, titulo,
             horizontalalignment='center', color='black', weight='bold',
             size='large')
    N2 = len(escalas_trans)
    theta2 = radar_factory(N2, frame='polygon')
    spoke_labels2 = data_trans.pop(0)
    fig, axs = plt.subplots(figsize=(9, 9), nrows=1, ncols=1,
                            subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(wspace=0.25, hspace=0.5, top=0.85, bottom=0.05)


    axs.set_rgrids([0,1,2,3,4,5,6,7,8,9,10 ])
    axs.set_title(data_trans[0][0], weight='bold', size='medium', position=(0.5, 1.1),
                 horizontalalignment='center', verticalalignment='center')
        #for d, color in zip(case_data, colors):
    axs.plot(theta2, data_trans[0][1][0], color=colors[0])
    axs.fill(theta2, data_trans[0][1][0], facecolor=colors[0], alpha=0.25)
    axs.set_varlabels(spoke_labels2)

    # add legend relative to top-left plot
    labels = ['Area caracteristica del nivel']
    legend = axs.legend(labels, loc=(0.9, .95),
                              labelspacing=0.1, fontsize='small')
    titulo = 'Evaluacion del nivel '+nivel
    fig.text(0.5, 0.965, titulo,
             horizontalalignment='center', color='black', weight='bold',
             size='large')

def plotFeaturePlat(ruta, rasgo, grafo, level, nameRoute):
    t = np.arange(0.0, len(ruta), 1)
    s=[]
    if(rasgo in grafo[0]):
        for plat in ruta:
            #print("rasgo", rasgo)
#            print(grafo[int(plat)][rasgo])
            s.append(grafo[int(plat)][rasgo])
    else:
        print("No es un rasgo de plataforma, es de transicion")

    fig, ax = plt.subplots()
    ax.plot(t, s)
    titulo= "Avance del rasgo: "+ rasgo+" en las plataformas"
    xL = 'Transiciones en la ruta: '+nameRoute
    ax.set(xlabel=xL, ylabel=rasgo,
           title=titulo)
    ax.grid()
    dirName1 = str(level)
    dirName2 = level+"/"+nameRoute
    try:        
        # Create target Directory
        os.mkdir(level)
        print("Directory " , level ,  " Created ") 
    except FileExistsError:
        print("Directory " , level,  " already exists")
    try:        
        # Create target Directory
        os.mkdir(dirName2)
        print("Directory " , dirName2 ,  " Created ") 
    except FileExistsError:
        print("Directory " , dirName2,  " already exists")
    fig.savefig(level+"/"+nameRoute+"/"+rasgo+"_plats.png")
    plt.show()


def plotFeatureTrans(ruta, rasgo, grafo, level, nameRoute):
    t = np.arange(0.0, len(ruta)-1, 1)
    s=[]
    llaves= list(grafo[0]["alcanzado_por"].keys())
    print("llaves", llaves)
    if(rasgo in grafo[0]["alcanzado_por"][llaves[0]]):        
        i=0; j=1
        while j<len(ruta):
            #print("rasgo", rasgo)
#            print(grafo[int(plat)][rasgo])
            if i==0:
                s.append(grafo[int(ruta[i])]["alcanzado_por"][ruta[j]][rasgo])
            else:
                s.append(grafo[int(ruta[i])]["alcanza"][ruta[j]][rasgo])
            i+=1
            j+=1
    else:
        print("No es un rasgo de transicion, es de plataforma")

    fig, ax = plt.subplots()
    ax.plot(t, s)
    titulo= "Avance del rasgo: "+ rasgo+" en las transiciones"
    xL = 'Transiciones en la ruta: '+nameRoute
    ax.set(xlabel= xL, ylabel=rasgo,
           title=titulo)
    ax.grid()
    dirName1 = str(level)
    dirName2 = level+"/"+nameRoute
    try:        
        # Create target Directory
        os.mkdir(level)
        print("Directory " , level ,  " Created ") 
    except FileExistsError:
        print("Directory " , level,  " already exists")
    try:        
        # Create target Directory
        os.mkdir(dirName2)
        print("Directory " , dirName2 ,  " Created ") 
    except FileExistsError:
        print("Directory " , dirName2,  " already exists")
    fig.savefig(level+"/"+nameRoute+"/"+rasgo+"_trans.png")
    plt.show()

