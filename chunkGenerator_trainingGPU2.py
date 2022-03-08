#!/usr/bin/env python
# coding: utf-8

# In[1]:


import chunksGenerator
from IPython.core.display import display, HTML
display(HTML("<style>.container {width:100% !important; }</style>"))


# In[2]:


#En nPlats existe una etiqueta para cada tipo de plataforma
limPlats = {'S':1, 'G':1, 'c':1, 'p':1, 'l':1, 'i':8, 'f':3, 'd':1,
            'A':1, 'A1':1, 'O':1, 'O1':1, 'T':1, 'T1':1, 
            'ws':2, 'ps':2, 'bf':2, 'rf':2, 
            'b':0, 'rv':0, 'rv1':0, 'rh':0, 'rh1':0}

#Expresamos la lista de acciones para imprimirlas en el entrenamiento
actions = ['inserta_piso','mueve_piso','quita_piso',
            'inserta_fuego','mueve_fuego','quita_fuego',
            'inserta_comida','mueve_comida','quita_comida','cambia_tipo_comida',
            'inserta_movil','mueve_movil','quita_movil','cambia_tipo_movil', 'cambia_dir_movil',
            'inserta_enH','mueve_enH','quita_enH','cambia_tipo_enH', 'cambia_dir_enH',
            'inserta_enV','mueve_enV','quita_enV','cambia_dir_enV',
            'inserta_pingu','mueve_pingu','quita_pingu',                   
            'inserta_checkpoint','mueve_checkpoint','quita_checkpoint',
            'inserta_rebote','mueve_rebote','quita_rebote',
            'inserta_dorado','mueve_dorado','quita_dorado',
            'inserta_extra','mueve_extra','quita_extra']

#Creamos un diccionario, que muestra, para cada caracteristica, las fluctuaciones en su ritmo
# y sus valores minimo y máximo. #Estas corresponden a la experiencia: simple

caracteristicas = {"recompensa_nivel":{"ritmo":2, "varRitmo":3, "limSup":916, "limInf":0, "ponderacion":0.29, "alpha":0.95, "beta":0.05},
                   "motivacion_nivel" :{"ritmo":0, "varRitmo":3, "limSup":1406, "limInf":0, "ponderacion":0.26, "alpha":0.75, "beta":0.25},
                   "riesgo":{"ritmo":2, "varRitmo":0.001, "limSup":2491, "limInf":0, "ponderacion":0.22, "alpha":0.65, "beta":0.35},
                   #"motivacion_puntos":{"ritmo":1, "varRitmo":0.001, "limSup":160, "limInf":-184, "ponderacion":0.15, "alpha":0.35, "beta":0.65},                   
                   "recompensa_puntos":{"ritmo":2, "varRitmo":2, "limSup":265, "limInf":0, "ponderacion":0.15, "alpha":0.85, "beta":0.15},
                   "distancia":{"ritmo":4, "varRitmo":4, "limSup":5, "limInf":1, "ponderacion":0.08, "alpha":0, "beta":1}
                   }


# In[3]:


filas= 16
columnas=29
env = chunksGenerator.Environment(filas=filas, columnas=columnas, initPoint=[13,1], minBlock=4, maxBlock=limPlats['i'],
                  tamPlats= [3,6],limPlats=limPlats, nBlocks=12 , caracteristicas=caracteristicas, ruta_obj="recompensa_nivel_max",
                  rewardsFile="histR_simpleConvV4_2_16x29.npy", totalRFile="histTotalR_simpleConvV4_2_16x29.npy", promRFile ="histPromR_simpleConvV4_2_16x29.npy",
                  goalPoint=[11,26], utilidadMin = 1, pVal=0.5)

agent = chunksGenerator.Agent(gamma=0.78, epsilon=1, alpha= 0.0005, input_dims=[filas,columnas], n_actions=len(actions),
                              platform_height = 3, platform_width=6,
                              mem_size=150000, batch_size=64, epsilon_dec=0.998, epsilon_end=0.01, fname='dqn_simpleConvV4_2_16x29.h5')


# In[4]:

#Esta linea es para entrenar el modelo
chunksGenerator.trainModel(env, agent, actions, filas, columnas, n_games=2000, lim=300, load=False, epocTrain=5,                            
                           epocSave= 150, gameLevel=280, minReward=0.725, exp='SimpleV4_2', sameInit="True" )


# In[ ]:
#Esta linea es para correr el modelo
chunksGeneratorV2.runModel(env, agent, actions, filas, columnas, n_games=50, lim=75, exp= 'SimpleV4_2', sameInit=True )


