import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU') 
tf.config.set_visible_devices(physical_devices[0:1], 'GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)
from tensorflow.python.client import device_lib
import keras
from keras.layers import Dense, Activation, Conv2D, Flatten, InputLayer
from keras.models import Sequential, load_model
from keras.optimizers import Adam
import numpy as np
import time
import copy
import glob
import configPenguin
import encuentraRutas as rutas
import eval_level_V2 as evlvl
import chunksAgent as ckAgnt 
import json 
from pickle import dump, dumps, load, loads

drivePath = 'resultados/'

class ReplayBuffer(object):
    def __init__(self,max_size, input_shape, n_actions, discrete=False):
        self.mem_size= max_size
        self.mem_cntr = 0
        self.input_shape = input_shape
        self.discrete = discrete
        self.state_memory = np.array([np.zeros(input_shape) for i in range(self.mem_size)])
        self.new_state_memory = np.array([np.zeros(input_shape) for i in range(self.mem_size)])
        dtype = np.int8 if self.discrete else np.float32
        self.action_memory = np.zeros((self.mem_size, n_actions), dtype=dtype) 
        self.reward_memory = np.zeros(self.mem_size) 
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.float32) 
    
    def store_transition(self, state, action, reward, state_, done):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.terminal_memory[index] = 1-int(done)
        if self.discrete:
            actions= np.zeros(self.action_memory.shape[1])
            actions[action]= 1.0
            self.action_memory[index] = actions
        else:
            self.action_memory[index] = actions
        self.mem_cntr += 1
        
    def sample_buffer(self, batch_size):
        max_mem = min(self.mem_cntr, self.mem_size)
        batch = np.random.choice(max_mem, batch_size)
        states = self.state_memory[batch]
        states_ = self.new_state_memory[batch]
        rewards = self.reward_memory[batch]
        actions = self.action_memory[batch]
        terminal = self.terminal_memory[batch]
        
        return states, actions, rewards, states_, terminal


# In[15]:


def build_dqn(lr, n_actions, input_dims, fc1_dims, fc2_dims):
    model = Sequential([
                Dense(fc1_dims, input_shape= (input_dims, )),
                Activation('relu'),
                Dense(fc2_dims),
                Activation('relu'),
                Dense(n_actions)])
    model.compile(optimizer= Adam(lr=lr), loss='mse')

    return model


def build_dqn2(lr, n_actions, input_dims, conv1_dims, conv2_dims, conv3_dims, conv4_dims, fc1_dims, fc2_dims):
  """
  En las entradas conv1_dims el formato es conv1_dims=[platform_width, platform_height, filters]
  """
  model = Sequential([
              InputLayer(input_shape=(input_dims[0], input_dims[1],1)),
              Conv2D(strides = ((int(conv1_dims[0]/2), int(conv1_dims[1]/2))), 
                      kernel_size = (conv1_dims[0], conv1_dims[1]),
                      filters = conv1_dims[2],
                      padding ='same', 
                      input_shape = (input_dims[0], input_dims[1],1)),
              
              Conv2D(strides = (2,2), 
                      kernel_size = (3,3),
                      filters = conv2_dims[2],
                      padding = 'same', 
                      input_shape = (conv2_dims[0], conv2_dims[1], conv1_dims[2])),
              
              Conv2D(strides = (2,2), 
                      kernel_size = (3,3),
                      filters = conv3_dims[2],
                      padding ='same', 
                      input_shape = (conv3_dims[0], conv3_dims[1], conv2_dims[2])),
              
              Conv2D(strides = (2,2), 
                      kernel_size = (3,3),
                      filters = conv4_dims[2],
                      padding ='same', 
                      input_shape = (conv4_dims[0], conv4_dims[1], conv3_dims[2])),
              Flatten(),           
              Dense(fc1_dims),
              Activation('relu'),
              Dense(fc2_dims),
              Activation('relu'),
              Dense(n_actions)])
  model.summary()
  model.compile(optimizer= Adam(lr=lr), loss='mse')
  return model
# In[26]:


class Agent(object):
    def __init__(self, alpha, gamma, n_actions, epsilon, batch_size,
                 platform_width, platform_height, 
                 input_dims, epsilon_dec=0.996, epsilon_end=0.01,
                mem_size=10000, fname='dqn_model.h5'):
        self.action_space = [i for i in range(n_actions)]
        self.n_actions = n_actions
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_dec =epsilon_dec
        self.epsilon_min = epsilon_end
        self.batch_size = batch_size
        self.model_file = fname
        self.plat_height = platform_height
        self.plat_width = platform_width
        self.memory = ReplayBuffer(mem_size, input_dims, n_actions, discrete = True)
        self.q_eval = build_dqn2(alpha, n_actions, input_dims, 
                                [platform_height, platform_width, 32],
                                [platform_height, platform_width, 64],
                                [platform_height, platform_width, 128],
                                [platform_height, platform_width, 256],
                                256, 256)
        
    def remember(self, state, action, reward, new_state, done):
        self.memory.store_transition(state, action, reward, new_state, done)
        
    def choose_action(self, state):
        #state = state[np.newaxis, :]
        rand = np.random.random()
        if rand < self.epsilon:
            action = np.random.choice(self.action_space)
        else:
            state = np.array([state])
            state = np.expand_dims(state, -1)
            actions = self.q_eval.predict(state)
            action = np.argmax(actions)
            
        return action
    
    def learn(self):
        if self.memory.mem_cntr > self.batch_size:
            
          state, action, reward, new_state, done= self.memory.sample_buffer(self.batch_size)
          action_values= np.array(self.action_space, dtype=np.int8)
          actions_indices = np.dot(action, action_values)
          
          #Se hace un ajuste en las dimensiones de los datos para asegurar que estan en la
          #forma correcta para procesarse en la RNA
          state = np.expand_dims(state,-1)
          new_state = np.expand_dims(new_state,-1)


          #La predicción de las recompensas acumuladas en el estado actual
          q_eval = self.q_eval.predict(state)
          #La predicción de las recompensas acumuladas en el estado siguiente
          q_next = self.q_eval.predict(new_state)
                    
          q_target = q_eval.copy()
          
          batch_index = np.arange(self.batch_size, dtype=np.int32)
          
          q_target[batch_index, actions_indices] = reward+self.gamma*np.max(q_next, axis=1)*done
          
          _ = self.q_eval.fit(state, q_target, verbose=0)
          
          self.epsilon = self.epsilon*self.epsilon_dec if self.epsilon>self.epsilon_min else self.epsilon_min
        
    def save_model(self):
        self.q_eval.save(drivePath+''+self.model_file)
        
    def load_model(self):
        print("Cargando modelo...")
        self.q_eval = load_model(drivePath+''+self.model_file)                        
        print("Modelo cargado :D")
    


# In[17]:


class Environment(object):
  '''
  El ambiente propuesto es una matriz de n*m en la que
  cada casilla representa un sprite de un nivel.

  '''
  def __init__(self, filas, columnas, initPoint,minBlock, maxBlock, tamPlats, 
               limPlats, nBlocks, caracteristicas, ruta_obj, minReward=0.75,
               rewardsFile="historicoR.npy", totalRFile="historicoRT.npy", promRFile ="historicoRProm.npy", 
               goalPoint=[], utilidadMin=1, pVal=0.5):
    self.filas = filas
    self.columnas = columnas
    self.minB = minBlock
    self.maxB = maxBlock
    self.initPoint = initPoint
    self.goalPoint = goalPoint
    self.tamPlat = tamPlats
    self.limPlats = limPlats
    self.nBlocks = nBlocks
    self.caracteristicas = caracteristicas
    self.ruta_obj = ruta_obj
    self.rewardsFile = rewardsFile
    self.totalRFile = totalRFile
    self.promRFile = promRFile
    self.minReward = minReward
    self.maxReward = -99
    self.bestLevel = []
    self.counter=0
    self.expCounter=0
    self.bestMove=-1
    self.bestExp=-1
    self.utilidadMin = utilidadMin #Un valor de utilidad mínima para las plataformas 
    self.pVal = pVal #Un valor de penalizacion para la recompensa si el nivel no es terminable
    #Se crean dos estructuras "gemelas", map y state
    #state y mapa contienen la misma informacion, la matriz de la rebanada que se esta creando
    #Sin embargo, state contiene informacion numerica y map es una matriz de caracteres
    self.map = [np.zeros(self.columnas) for i in range(self.filas)]
    self.state = [np.zeros(self.columnas) for i in range(self.filas)]
    #Las acciones corresponden con aquellas que haría el diseñador
    #Se propone como un par de valores primero la accion en bruto
    #y despues el tipo de bloque al que puede afectar
    self.actions = ['inserta_piso','mueve_piso','quita_piso',
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
    

  def mapToState(self):
    state = []
    translate ={'x':0, 'i':1, 'f':2, 'b':3, 'rh':4, 'rh1':5, 'rv':6, 'rv1':7,
                'ws':8, 'ps':9, 'rf':10, 'bf':11, 'd':12, 'p':13, 'l':14,
                'T':15, 'T1':16, 'O':17, 'O1':18, 'A':19, 'A1':20,
                'c':21, 'S':22, 'G':23}
    #print("Translating map to state...")
    fila=0
    while fila <len(self.map):
      columna=0
      state.append([])
      while columna<len(self.map[0]):
        state[-1].append(translate[self.map[fila][columna]])
        #print("adding:", self.map[fila][columna],"->", translate[self.map[fila][columna]])
        columna+=1
      fila+=1
    state = np.array(state)
    return state

  def StateToMap(self, state):
    mapa = []
    translate ={'x':0, 'i':1, 'f':2, 'b':3, 'rh':4, 'rh1':5, 'rv':6, 'rv1':7,
                'ws':8, 'ps':9, 'rf':10, 'bf':11, 'd':12, 'p':13, 'l':14,
                'T':15, 'T1':16, 'O':17, 'O1':18, 'A':19, 'A1':20,
                'c':21, 'S':22, 'G':23}

    translate = list(translate.keys())
    #print("Translating map to state...")
    fila=0
    while fila <len(state):
      columna=0
      mapa.append([])
      while columna<len(state[0]):
        mapa[-1].append(translate[state[fila][columna]])
        #print("adding:", self.map[fila][columna],"->", translate[self.map[fila][columna]])
        columna+=1
      fila+=1
    #mapa = np.array(state)
    return mapa

  def reset(self):
    self.map, self.initPoint, self.goalPoint = ckAgnt.init_level(self.limPlats, self.nBlocks, self.minB, self.maxB,
                      self.filas, self.columnas, self.initPoint, self.tamPlat, self.goalPoint)
    self.state = self.mapToState() 
    self.maxReward= -99
    self.counter=0
    self.expCounter=0
    self.bestMove=-1
    self.bestExp=-1
    return self.state
  
  def dist(self, a, b):
    sum = 0
    i=0
    while i<len(a):
      sum+= (a[i]-b[i])**2
      i+=1
    return np.sqrt(sum) 
  
  def loadResults(self):
    #Se cargan las recompensas
    with open(drivePath+'/'+self.rewardsFile,'rb') as f:
      fsz = os.fstat(f.fileno()).st_size
      outRewards = np.load(f)
      while f.tell() < fsz:
          outRewards = np.vstack((outRewards, np.load(f)))
    return outRewards
  
  
  def step(self, action, pastReward, need_reward=True):
    '''
    Basado en funcion step usada en fuente, debe regresar:
    - observation_ : el estado despues de ejecutar la acción
    - reward : la evaluación del ambiente modificado 
              (recompensa por ejecutar la accion)
    - done : bandera que indica si es un estado final 
    - info : idk, pero voy a mandar un 0 porque no lo usa xD
    '''
    action = self.actions[action] 
    #print("Ejecutando accion:", action)
    comida =["ws", "rf", "ps", "bf"]
    aguila = ["A", "A1"]
    oso = ["O", "O1"]
    troll = ["T", "T1"]
    enemigosH = ["T", "T1","O", "O1"]
    rocaV = ["rv1", "rv"]
    rocaH = ["rh", "rh1"]
    roca = ["rv1", "rv", "rh", "rh1"]
    #Paso 1: Se ejecuta la acción, en este caso se modifica la matriz
    #un paso necesario en todas las acciones, es detectar las plataformas presentes
    #en el mapa
    plats, nPlats = ckAgnt.detectaObjetos(self.tamPlat, self.map)
    if action=='inserta_piso':      
      self.map = ckAgnt.inserta('i', self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)

    elif action=='mueve_piso':
      #Se selecciona una plataforma de piso
      pisos=[]
      for p in plats:
        if p["tipo"]=="i":
          pisos.append(p)
      if len(pisos)>0:
        sel = np.random.randint(0,len(pisos))
        selectedPlat = pisos[sel]
        self.map = ckAgnt.muevePlat(selectedPlat,self.map,self.tamPlat)

    elif action=='quita_piso':
      #Se selecciona una plataforma de piso
      pisos=[]
      for p in plats:
        if p["tipo"]=="i":
          pisos.append(p)
      if len(pisos)>0:
        sel = np.random.randint(0,len(pisos))
        selectedPlat = pisos[sel]
        self.map = ckAgnt.remuevePlat(selectedPlat,self.map)
      
    elif action=='inserta_fuego':
      self.map = ckAgnt.inserta('f', self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)

    elif action=='mueve_fuego':
      #Se selecciona una plataforma de fuego
      fuegos=[]
      for p in plats:
        if p["tipo"]=="f":
          fuegos.append(p)
      if len(fuegos)>0:
        sel = np.random.randint(0,len(fuegos))
        selectedPlat = fuegos[sel]
        self.map = ckAgnt.muevePlat(selectedPlat,self.map,self.tamPlat)

    elif action=='quita_fuego':
      #Se selecciona una plataforma de fuego
      fuegos=[]
      for p in plats:
        if p["tipo"]=="f":
          fuegos.append(p)
      if len(fuegos)>0:
        sel = np.random.randint(0,len(fuegos))
        selectedPlat = fuegos[sel]
        self.map = ckAgnt.remuevePlat(selectedPlat,self.map)

    elif action=='inserta_comida':
      sel = np.random.randint(0,len(comida))
      selectedFood = comida[sel]
      self.map = ckAgnt.inserta(selectedFood, self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)

    elif action=='mueve_comida':
      #Se selecciona una plataforma de comida
      comidas=[]
      for p in plats:
        if p["tipo"] in comida:
          comidas.append(p)
      if len(comidas)>0:
        sel = np.random.randint(0,len(comidas))
        selectedPlat = comidas[sel]
        self.map = ckAgnt.muevePlat(selectedPlat,self.map,self.tamPlat)

    elif action=='quita_comida':
      #Se selecciona una plataforma de comida
      comidas=[]
      for p in plats:
        if p["tipo"] in comida:
          comidas.append(p)
      if len(comidas)>0:
        sel = np.random.randint(0,len(comidas))
        selectedPlat = comidas[sel]
        self.map = ckAgnt.remuevePlat(selectedPlat,self.map)
      
    elif action=='cambia_tipo_comida':
      comidas=[]
      for p in plats:
        if p["tipo"] in comida:
          comidas.append(p)
      if len(comidas)>0:
        sel = np.random.randint(0,len(comidas))
        selectedPlat = comidas[sel]
        self.map = ckAgnt.cambia(selectedPlat,self.map, comida)

    elif action=='inserta_movil':
      sel = np.random.randint(0,len(roca))
      selectedMov = roca[sel]
      self.map = ckAgnt.inserta(selectedMov, self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)      

    elif action=='mueve_movil':
      #Se selecciona una plataforma movil
      moviles=[]
      for p in plats:
        if p["tipo"] in roca:
          moviles.append(p)
      if len(moviles)>0:
        sel = np.random.randint(0,len(moviles))
        selectedPlat = moviles[sel]
        self.map = ckAgnt.muevePlat(selectedPlat,self.map,self.tamPlat)

    elif action=='quita_movil':
      #Se selecciona una plataforma movil
      moviles=[]
      for p in plats:
        if p["tipo"] in roca:
          moviles.append(p)
      if len(moviles)>0:
        sel = np.random.randint(0,len(moviles))
        selectedPlat = moviles[sel]
        self.map = ckAgnt.remuevePlat(selectedPlat,self.map)

    elif action=='cambia_tipo_movil':
      #Para cambiar la plataforma movil, detectamos primero
      #Si era vertical u horizontal
      moviles=[]
      for p in plats:
        if p["tipo"] in roca:
          moviles.append(p)
      if len(moviles)>0:
        sel = np.random.randint(0,len(moviles))
        selectedPlat = moviles[sel]
        if selectedPlat["tipo"]=="rh" or   selectedPlat["tipo"]=="rh1":
          #Pasa de ser horizontal a vertical
          self.map = ckAgnt.cambia(selectedPlat,self.map, rocaV)
        else:
          #Pasa de ser vertical a horizontal
          self.map = ckAgnt.cambia(selectedPlat,self.map, rocaH)

    elif action=='cambia_dir_movil':
      #Para cambiar la direccion plataforma movil, detectamos primero
      #Si era vertical u horizontal
      moviles=[]
      for p in plats:
        if p["tipo"] in roca:
          moviles.append(p)
      if len(moviles)>0:
        sel = np.random.randint(0,len(moviles))
        selectedPlat = moviles[sel]
        if selectedPlat["tipo"]=="rh" or   selectedPlat["tipo"]=="rh1":
          #Cambia solo su direccion
          self.map = ckAgnt.cambia(selectedPlat,self.map, rocaH)
        else:
          #Cambia solo su direccion
          self.map = ckAgnt.cambia(selectedPlat,self.map, rocaV)

    elif action=='inserta_enH':
      sel = np.random.randint(0,len(enemigosH))
      selectedEnH = enemigosH[sel]
      self.map = ckAgnt.inserta(selectedEnH, self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)

    elif action=='mueve_enH':
      #Se selecciona un enemigo horizontal
      ensH=[]
      for p in plats:
        if p["tipo"] in enemigosH:
          ensH.append(p)
      if len(ensH)>0:
        sel = np.random.randint(0,len(ensH))
        selectedPlat = ensH[sel]
        self.map = ckAgnt.muevePlat(selectedPlat,self.map,self.tamPlat)

    elif action=='quita_enH':
      #Se selecciona un enemigo horizontal
      ensH=[]
      for p in plats:
        if p["tipo"] in enemigosH:
          ensH.append(p)
      if len(ensH)>0:
        sel = np.random.randint(0,len(ensH))
        selectedPlat = ensH[sel]
        self.map = ckAgnt.remuevePlat(selectedPlat,self.map)

    elif action=='cambia_tipo_enH':
      #Para cambiar de enemigo H, detectamos primero
      #Si era oso o troll
      ensH=[]
      for p in plats:
        if p["tipo"] in enemigosH:
          ensH.append(p)
      if len(ensH)>0:
        sel = np.random.randint(0,len(ensH))
        selectedPlat = ensH[sel]
        if selectedPlat["tipo"]=="O" or   selectedPlat["tipo"]=="O1":
          #Pasa de ser Oso a Troll
          self.map = ckAgnt.cambia(selectedPlat,self.map, troll)
        else:
          #Pasa de ser Troll a oso
          self.map = ckAgnt.cambia(selectedPlat,self.map, oso)

    elif action=='cambia_dir_enH':
      #Para cambiar la direccion de enemigo H, detectamos primero
      #Si era oso o troll
      ensH=[]
      for p in plats:
        if p["tipo"] in enemigosH:
          ensH.append(p)
      if len(ensH)>0:
        sel = np.random.randint(0,len(ensH))
        selectedPlat = ensH[sel]
        if selectedPlat["tipo"]=="O" or   selectedPlat["tipo"]=="O1":
          #Solo cambia su direccion
          self.map = ckAgnt.cambia(selectedPlat,self.map, oso)
        else:
          #Solo cambia su direccion
          self.map = ckAgnt.cambia(selectedPlat,self.map, troll)

    elif action=='inserta_enV':
      sel = np.random.randint(0,len(aguila))
      selectedEnV = aguila[sel]
      self.map = ckAgnt.inserta(selectedEnV, self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)

    elif action=='mueve_enV':
      #Se selecciona un aguila
      aguilas=[]
      for p in plats:
        if p["tipo"] in aguila:
          aguilas.append(p)
      if len(aguilas)>0:
        sel = np.random.randint(0,len(aguilas))
        selectedEnV = aguilas[sel]
        self.map = ckAgnt.muevePlat(selectedEnV,self.map,self.tamPlat)

    elif action=='quita_enV':
      #Se selecciona un aguila
      aguilas=[]
      for p in plats:
        if p["tipo"] in aguila:
          aguilas.append(p)
      if len(aguilas)>0:
        sel = np.random.randint(0,len(aguilas))
        selectedEnV = aguilas[sel]
        self.map = ckAgnt.remuevePlat(selectedEnV,self.map)

    elif action=='cambia_dir_enV':
      aguilas=[]
      for p in plats:
        if p["tipo"] in aguila:
          aguilas.append(p)
      if len(aguilas)>0:
        sel = np.random.randint(0,len(aguilas))
        selectedEnV = aguilas[sel]
        self.map = ckAgnt.cambia(selectedEnV,self.map, aguila)

    elif action=='inserta_pingu':
      self.map = ckAgnt.inserta('p', self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)

    elif action=='mueve_pingu':
      #Se selecciona un pingüino rosa (aunque en teoria sólo debe existir uno)
      pingus=[]
      for p in plats:
        if p["tipo"]=="p":
          pingus.append(p)
      if len(pingus)>0:
        sel = np.random.randint(0,len(pingus))
        selectedPingu = pingus[sel]
        self.map = ckAgnt.muevePlat(selectedPingu,self.map, self.tamPlat)

    elif action=='quita_pingu':
      #Se selecciona un pingüino rosa (aunque en teoria sólo debe existir uno)
      pingus=[]
      for p in plats:
        if p["tipo"]=="p":
          pingus.append(p)
      if len(pingus)>0:
        sel = np.random.randint(0,len(pingus))
        selectedPingu = pingus[sel]
        self.map = ckAgnt.remuevePlat(selectedPingu,self.map)

    elif action=='inserta_checkpoint':
      self.map = ckAgnt.inserta('c', self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)

    elif action=='mueve_checkpoint':
      #Se selecciona un checkpoint (aunque en teoria sólo debe existir uno)
      ckpts = []
      for p in plats:
        if p["tipo"]=="c":
          ckpts.append(p)
      if len(ckpts)>0:
        sel = np.random.randint(0,len(ckpts))
        selectedCkpt = ckpts[sel]
        self.map = ckAgnt.muevePlat(selectedCkpt,self.map, self.tamPlat)

    elif action=='quita_checkpoint':
      #Se selecciona un checkpoint (aunque en teoria sólo debe existir uno)
      ckpts = []
      for p in plats:
        if p["tipo"]=="c":
          ckpts.append(p)
      if len(ckpts)>0:
        sel = np.random.randint(0,len(ckpts))
        selectedCkpt = ckpts[sel]
        self.map = ckAgnt.remuevePlat(selectedCkpt,self.map)

    elif action=='inserta_rebote':
      self.map = ckAgnt.inserta('b', self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)

    elif action=='mueve_rebote':
      #Se selecciona un rebote 
      bounces = []
      for p in plats:
        if p["tipo"]=="b":
          bounces.append(p)
      if len(bounces)>0:
        sel = np.random.randint(0,len(bounces))
        selectedBounce = bounces[sel]
        self.map = ckAgnt.muevePlat(selectedBounce,self.map, self.tamPlat)

    elif action=='quita_rebote':
      #Se selecciona un rebote 
      bounces = []
      for p in plats:
        if p["tipo"]=="b":
          bounces.append(p)
      if len(bounces)>0:
        sel = np.random.randint(0,len(bounces))
        selectedBounce = bounces[sel]
        self.map = ckAgnt.remuevePlat(selectedBounce,self.map)

    elif action=='inserta_dorado':
      self.map = ckAgnt.inserta('d', self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)

    elif action=='mueve_dorado':
      #Se selecciona un pez dorado
      goldens = []
      for p in plats:
        if p["tipo"]=="d":
          goldens.append(p)
      if len(goldens)>0:
        sel = np.random.randint(0,len(goldens))
        selectedGold = goldens[sel]
        self.map = ckAgnt.muevePlat(selectedGold,self.map,self.tamPlat)

    elif action=='quita_dorado':
      #Se selecciona un pez dorado
      goldens = []
      for p in plats:
        if p["tipo"]=="d":
          goldens.append(p)
      if len(goldens)>0:
        sel = np.random.randint(0,len(goldens))
        selectedGold = goldens[sel]
        self.map = ckAgnt.remuevePlat(selectedGold,self.map)

    elif action=='inserta_extra':
      self.map = ckAgnt.inserta('i', self.map, self.limPlats, nPlats, self.tamPlat, self.nBlocks)

    elif action=='mueve_extra':
      #Se selecciona una vida extra
      xtras = []
      for p in plats:
        if p["tipo"]=="l":
          xtras.append(p)
      if len(xtras)>0:
        sel = np.xtrasm.randint(0,len(xtras))
        selectedLife = xtras[sel]
        self.map = ckAgnt.muevePlat(selectedLife,self.map,self.tamPlat)

    elif action=='quita_extra':
      #Se selecciona una vida extra
      xtras = []
      for p in plats:
        if p["tipo"]=="l":
          xtras.append(p)
      if len(xtras)>0:
        sel = np.random.randint(0,len(xtras))
        selectedLife = xtras[sel]
        self.map = ckAgnt.remuevePlat(selectedLife,self.map)

    #print("Mapa modificado...")
    #for n in self.map:
    #  print(n)
    #print("Traduciendo mapa a estado...")
    self.state = self.mapToState()

    if need_reward:
      #Paso 2: Se evalua la matriz
      name = "nivel_rfLearning"
      #Primero, se transforma el mapa al formato para aplicar las metricas
      level = ckAgnt.traduceMap(self.map)
      escenario={}
      escenario["mapa"]=level
      #Aplicamos las metricas
      bloques = evlvl.detectaPlataformas(level,name)
      bloques = evlvl.refinaPlats(bloques,evlvl.pendUp, evlvl.pendDown, escenario) 
      evlvl.alcanzabilidad(bloques,escenario)
      evlvl.recalculaTrayectorias(bloques["objetos"])
      evlvl.insertaAtaques(bloques["objetos"])
      evlvl.riesgoTrans(bloques["objetos"])
      evlvl.riesgoPlat(bloques["objetos"])
      evlvl.calculaRecompensaPuntosPlat(bloques["objetos"])
      evlvl.calculaRecompensaPuntosTrans(bloques["objetos"])
      evlvl.calculaRecompensaNivelPlat(bloques["objetos"])
      evlvl.calculaRecompensaNivelTrans(bloques["objetos"])
      evlvl.calculaPrecision(bloques["objetos"], evlvl.pendUp, evlvl.pendDown, escenario)
      evlvl.calculaTiempo(bloques["objetos"])    
      evlvl.calculaMotivacionPuntos(bloques["objetos"])
      evlvl.calculaMotivacionNivel(bloques["objetos"])
      evlvl.calculaUtilidad(bloques["objetos"])
      
      #Se aplica el filtro de utilidad minima
      translate ={"piso":'i',"obstaculo":"f", "rebote":"b", "movil":['rh','rh1','rv','rv1'],
                  "comida":['ws', 'ps', 'rf', 'bf'], "sub-mision":['d', 'p', 'l'],
                  "enemigoHorizontal":['T', 'T1', 'O', 'O1'], "enemigoVertical":['A', 'A1'],
                  "checkpoint":'c', "inicio":'S', "meta":'G'}
      for plat in bloques["objetos"]:
        if(plat["utilidad"] < self.utilidadMin) and plat["tipo"]!='ataque':
          #print("Removiendo plataformas por poca utilidad...")
          if type(translate[plat["tipo"]]) == list:
            for tipo in translate[plat["tipo"]]:
              plat["tipo"]= tipo
              self.map = ckAgnt.remuevePlat(plat, self.map)
          else:
            plat["tipo"] = translate[plat["tipo"]]
            self.map = ckAgnt.remuevePlat(plat, self.map)

      #Se calculan las rutas optimas
      initId, platInicio = rutas.encuentraInicio(bloques["objetos"])
      #print("La plataforma incial es: ", platInicio)
      meta = rutas.encuentraMeta(bloques["objetos"])
      #print("La plataforma meta es:", meta)
      rutasOptimas = rutas.bestRoutes(bloques["objetos"], [int(initId),int(platInicio)])
      caminos={}
      namesRoutes=[]
      #print("La rebanada tiene los bloques:")
      #for b in bloques['objetos']:
       # print(b["tipo"])
        #print(b["id"])
        #print(b["p_inicio"])
      for rute in rutasOptimas:
        caminos[rute]= rutas.get_route(rutasOptimas[rute],str(meta), int(initId))
        namesRoutes.append(rute)
      rewardCar = []
      rewardHistoric = []
      evalInfo = {}
      evalInfo["accion"]= action
      for c in self.caracteristicas:

        nFlucts, minVal, maxVal, castigo = rutas.evalRitmo(caminos[self.ruta_obj], bloques['objetos'], c)
        #Con la evaluacion de ritmo se define el reward
        reward = ckAgnt.reward(nFlucts, self.caracteristicas[c]['ritmo'], self.caracteristicas[c]['varRitmo'],
                               maxVal, minVal,self.caracteristicas[c]['limSup'], self.caracteristicas[c]['limInf'],
                               self.caracteristicas[c]['alpha'], self.caracteristicas[c]['beta'], castigo, self.pVal)
        evalInfo[c]={"nFlucts":int(nFlucts), "minVal":float(minVal), "maxVal":float(maxVal), "reward": float(reward)}
        rewardHistoric.append(reward)
        rewardCar.append(reward*self.caracteristicas[c]['ponderacion'])

      rewardCar=np.array(rewardCar)
      rewardFinal = rewardCar.sum()

      rewardHistoric.append(rewardFinal)
      #Se guarda el mejor nivel, asociado a la recompensa maxima de entrenamiento
      if rewardFinal > self.maxReward:
          self.maxReward = copy.copy(rewardFinal)
          self.bestLevel = copy.copy(self.map)
          self.bestMove = copy.copy(self.counter)
          self.bestExp = copy.copy(self.expCounter)

      evalInfo["Total"]= float(rewardFinal)
  	
      #Almacenamos el historico de recompensas

      #with open(drivePath+''+self.rewardsFile,'ab') as f:
       #   np.save(f, np.array(rewardHistoric))


      done = True
      if rewardFinal >= self.minReward:
          done = False
      rewardFinal = rewardFinal- pastReward
    else:
      rewardFinal = 0
      evalInfo = 0
      done = True
    self.counter+=1
    return self.state, rewardFinal, done, evalInfo



def trainModel(env, agent, actions, filas, columnas, n_games, lim, load=False, epocTrain=5, epocSave=1000, gameLevel=100, minReward=0.75, exp="Salto", sameInit=False):
  """
  Esta funcion ejecuta un entrenamiento de un agente basado en RL para la generación automática de niveles.
  Recibe:
  - env.- El ambiente, un objeto de la clase Environment. Debe estar inicializado de acuerdo al problema a resolver
  - agent.- El agente, un objeto de la clase Agent. Debe estar inicializado de acuerdo al problema a resolver
  - actions.- La lista de acciones que puede ejecutar el agente.
  - filas.- El número de filas del nivel.
  - columnas.- El número de columnas del nivel.
  - n_games.- El número de experimentos a realizar, cada experimento significa un nivel creado desde cero. 
  - lim.- El número de acciones a ejecutar en cada experimento.
  - load=False.- Un indicador para saber si el modelo ha sido entrenado previamente y se desea sobreescribir o 
		 si se desea construir desde cero. 
  - epocTrain=5.- El número de pasos para entrenar la red neuronal.
		  Por defecto, es cada 5 epocas
  - epocSave=1000.- El número de pasos para actualizar el archivo de la red neuronal, debe ser un numero entre 1 y c.
	  	    Por defecto es 1000
  - gameLevel=100.- El número de pasos para almacenar un nivel con evaluación superior a minReward.
		    Por defecto es 100 
  - minReward=0.75.- El valor de la recompensa mínima para almacenar un nivel.
  - exp="Salto".- La experiencia de juego que se intenta aprender.
  Entrega:
  No entrega nada, pero genera archivos de:
	- Arquitectura de la RNA entrenada en un archivo *.h5
	- Historico de recompensas del agente en un archivo *.npy
	- Proceso(s) de creacion de nivel(es) en archivo(s) *.npy
	- Información sobre evaluación de nivel(es) creado(s) en archivo(s) *.json
	- Nivel(es) creado(s) en archivo(s) *.json
  """
  if load:
    agent.load_model()

  env.minReward = minReward
  if sameInit:
    observationZero = env.reset()
    mapZero  = copy.deepcopy(env.map)
    print("Se almacenara el nivel inicial")
    print("Guardando nivel...")
    n= {"dificultad":"facil","tiempo":100,"next_level":"bestlevelSalto_train6",
        "record": {"puntos":0, "dorados":[], "bonus":False, "tiempo":9999},"mapa":{}}

    plats, nPlats = ckAgnt.detectaObjetos([agent.plat_height, agent.plat_width],mapZero)     
    levelFinal = ckAgnt.puleNivel(plats, mapZero)
    n["mapa"] = {}
    for fila in range(filas):
      n["mapa"][str(fila)]={}
      for col in range(columnas):
        n["mapa"][str(fila)][str(col)]= levelFinal[fila][col]    
        cont = 0
    while cont<2:
      name= "initiallevel"+exp
      f = open(drivePath+"/"+name+".json", "w+")
      nivel=json.dumps(n)
      f.write(nivel)
      f.close()      
      cont+=1
  scores= []
  eps_history= []
  init= time.time()
  print("Iniciando en:", time.ctime(init))
  for i in range(n_games):
      done = False
      score = 0
      if sameInit:
        observation = env.reset()
        observation = copy.deepcopy(observationZero)
        env.map = copy.deepcopy(mapZero)
      else:
        observation = env.reset()
      #print("Estado inicial:\n")
      #for n in env.map:
       # print(n)
      c=0
      pastReward = 0
      proceso=[]
      infoH={}
      infoH["objetivo"]= copy.deepcopy(env.caracteristicas)
      while c<lim:
          action  = agent.choose_action(observation)                
          observation_, reward, done, info = env.step(action, pastReward) #Se calcula el siguiente estado, su recompensa, si ya se legó a un estado terminal, etc
          score+= reward    
          agent.remember(observation, action, reward, observation_, done)        
          observation = copy.copy(observation_)
          proceso.append(env.map)
          infoH[str(c)]= info
          pastReward = copy.copy(reward)
          #print("State modified...\n", observation)
          if c%(epocTrain)==0 and c>0:
            #print("Episodio: ",i+1,", Accion: ",c+1 ,", Accion elegida:", actions[action])
            #print("Ajustando red...")
            #print("Epsilon: ", agent.epsilon)    
            agent.learn()

          c+=1
          if c%(epocSave)==0 and c>0:
            
            print("\nGuardando progreso de entrenamiento")
            agent.save_model()
          if(c==lim):
            print("\nLímite de tiempo alcanzado")          

      endCiclo = time.time()
      print("Experimento:", i+1, "terminado en:", time.ctime(endCiclo))
      eps_history.append(agent.epsilon)
      scores.append(score)      
      avg_score = np.mean(scores[max(0, i-100):(i+1)])
      print('Episodio', i+1, 'recompensa final %.2f' % score, 'promedio de recompensa %2.f' % avg_score)
      env.expCounter+=1

      if not done: 
      #Se llego a un estado terminal al final del entrenamiento, donde env.maxRewad>= minReward            
        print("Se genero un nivel con una evaluacion de:", float(env.maxReward), "el minimo para guardar un nivel es de:", env.minReward)
        print("Guardando nivel...")
        n= {"dificultad":"facil","tiempo":100,"next_level":"bestlevelSalto_train6",
            "record": {"puntos":0, "dorados":[], "bonus":False, "tiempo":9999},"mapa":{}}

        plats, nPlats = ckAgnt.detectaObjetos([agent.plat_height, agent.plat_width],env.bestLevel)     
        levelFinal = ckAgnt.puleNivel(plats, env.bestLevel)
        n["mapa"] = {}
        for fila in range(filas):
          n["mapa"][str(fila)]={}
          for col in range(columnas):
            n["mapa"][str(fila)][str(col)]= levelFinal[fila][col]    
            cont = 0
        while cont<2:

          name= "bestlevel"+exp+"_train"+str(i)+"."+str(env.bestMove)
          f = open(drivePath+"/"+name+".json", "w+")
          nivel=json.dumps(n)
          f.write(nivel)
          f.close()
          name= "bestlevel"+exp+"_trainINFO"+str(i)+"."+str(env.bestMove)
          f2 = open(drivePath+"/"+name+".json", "w+")
          nivelI=json.dumps(infoH)
          f2.write(nivelI)
          f2.close()
          cont+=1

        with open(drivePath+'/'+"bestlevel"+exp+"_train"+str(i)+"."+str(env.bestMove)+".npy", 'wb') as f:
          np.save(f, np.array(proceso[:env.bestMove+1]), allow_pickle=True)

      #Se almacena el historico de mejores recompensas
      with open(drivePath+''+env.rewardsFile,'ab') as f:
        np.save(f, np.array([env.maxReward]))

      #Se almacena el historico de recompensas total  
      with open(drivePath+''+env.totalRFile,'ab') as f:
        np.save(f, np.array([score]))

      #Se almacena el historico de recompensas promedio  
      with open(drivePath+''+env.promRFile,'ab') as f:
        np.save(f, np.array([avg_score]))
      if i+1%2==0:
        print("Guardando progreso de entrenamiento")
        agent.save_model()

  end = time.time()
  print("Terminando en:", time.ctime(end))
  print("Epsilon: ", agent.epsilon)

  print("Se almacenara el mejor nivel producido durante el entrenamiento del agente...")
  print("Guardando nivel...")
  n= {"dificultad":"facil","tiempo":100,"next_level":"bestlevelSalto_train6",
      "record": {"puntos":0, "dorados":[], "bonus":False, "tiempo":9999},"mapa":{}}

 
  
  cont = 0
  while cont<2:
    plats, nPlats = ckAgnt.detectaObjetos([agent.plat_height, agent.plat_width],env.bestLevel)     
    levelFinal = ckAgnt.puleNivel(plats, env.bestLevel)
    n["mapa"] = {}
    for fila in range(filas):
      n["mapa"][str(fila)]={}
      for col in range(columnas):
        n["mapa"][str(fila)][str(col)]= levelFinal[fila][col]    
    name = "bestlevel"+exp+"_train"+str(i)+"."+str(env.bestMove)
    f = open(drivePath+"/"+name+".json", "w+")
    nivel=json.dumps(n)
    f.write(nivel)
    f.close()
    name= "bestlevel"+exp+"_trainINFO"+str(i)+"."+str(env.bestMove)
    f2 = open(drivePath+"/"+name+".json", "w+")
    nivelI=json.dumps(infoH)
    f2.write(nivelI)
    f2.close()
    cont+=1

  with open(drivePath+'/'+"bestlevel"+exp+"_train"+str(i)+"."+str(env.bestMove)+".npy", 'wb') as f:
    np.save(f, np.array(proceso[:env.bestMove+1]), allow_pickle=True)


def runModel(env, agent, actions, filas, columnas, n_games, lim, exp="Salto", sameInit=False):
  """
  Esta funcion ejecuta un agente entrenado basado en RL para la generación automática de niveles.
  Recibe:
  - env.- El ambiente, un objeto de la clase Environment. Debe estar inicializado de acuerdo al problema a resolver
  - agent.- El agente, un objeto de la clase Agent. Debe estar inicializado de acuerdo al problema a resolver
  - actions.- La lista de acciones que puede ejecutar el agente.
  - filas.- El número de filas del nivel.
  - columnas.- El número de columnas del nivel.
  - n_games.- El número de experimentos a realizar, cada experimento significa un nivel creado desde cero. 
  - lim.- El número de acciones a ejecutar en cada experimento.
  - exp="Salto".- La experiencia de juego que se intenta aprender.
  - sameInit.- Un indicador para saber si todos los experimentos se haran usando un mismo nivel inicial o no
  Entrega:
  No entrega nada, pero genera archivos de:
  - Proceso(s) de creacion de nivel(es) en archivo(s) *.npy
  - Información sobre evaluación de nivel(es) creado(s) en archivo(s) *.json
  - Nivel(es) creado(s) en archivo(s) *.json
  """
  
  agent.load_model()

  if sameInit:
    observationZero = env.reset()
    mapZero  = copy.deepcopy(env.map)
    print("Se almacenara el nivel inicial")
    print("Guardando nivel...")
    n= {"dificultad":"facil","tiempo":100,"next_level":"bestlevelSalto_train6",
        "record": {"puntos":0, "dorados":[], "bonus":False, "tiempo":9999},"mapa":{}}

    plats, nPlats = ckAgnt.detectaObjetos([agent.plat_height, agent.plat_width],mapZero)     
    levelFinal = ckAgnt.puleNivel(plats, mapZero)
    n["mapa"] = {}
    for fila in range(filas):
      n["mapa"][str(fila)]={}
      for col in range(columnas):
        n["mapa"][str(fila)][str(col)]= levelFinal[fila][col]    
        cont = 0
    while cont<2:
      name= "initiallevel"+exp
      f = open(drivePath+"/"+name+".json", "w+")
      nivel=json.dumps(n)
      f.write(nivel)
      f.close()      
      cont+=1
  levels = []
  procesos= []
  #infos = []
  scores = []
  init= time.time()
  print("Iniciando en:", time.ctime(init))
  for i in range(n_games):
      score = 0
      if sameInit:
        observation = env.reset()
        observation = copy.deepcopy(observationZero)
        env.map = copy.deepcopy(mapZero)
      else:
        observation = env.reset()
      #print("Estado inicial:\n")
      #for n in env.map:
       # print(n)
      c=0
      pastReward = 0
      proceso=[]
    #  infoH={}
     # infoH["objetivo"]= copy.deepcopy(env.caracteristicas)
      while c<lim:
          action  = agent.choose_action(observation)                
          observation_, reward, done ,info  = env.step(action, pastReward, need_reward=False) #Se calcula el siguiente estado, su recompensa, si ya se legó a un estado terminal, etc          
          observation = copy.copy(observation_)
          proceso.append(env.map)
      #    infoH[str(c)]= info
          c+=1
          if(c==lim):
            print("\nLímite de tiempo alcanzado")          

      #Se almacenan los niveles generados      
      print("El nivel se almacena como:")
      for l in observation:
        print(l)
      levels.append(observation)       
      procesos.append(proceso)
      #infos.append(infoH)
      endCiclo = time.time()
      print("Experimento:", i+1, "terminado en:", time.ctime(endCiclo))
      
      #scores.append(score)      
      #avg_score = np.mean(scores[max(0, i-100):(i+1)])
      #print('Episodio', i+1, 'recompensa final %.2f' % score, 'promedio de recompensa %2.f' % avg_score)
      env.expCounter+=1      
  

  end = time.time()
  print("Terminando en:", time.ctime(end))
  print("Se almacenaran los niveles generados...")
  contLevels = 0
  for level in levels:

    nivel = ckAgnt.traduceMap(level)
    escenario={}
    escenario["mapa"]=nivel
    #Aplicamos las metricas
    bloques = evlvl.detectaPlataformas(nivel,name)
    bloques = evlvl.refinaPlats(bloques,evlvl.pendUp, evlvl.pendDown, escenario) 
    evlvl.alcanzabilidad(bloques,escenario)
    evlvl.recalculaTrayectorias(bloques["objetos"])
    evlvl.insertaAtaques(bloques["objetos"])
    evlvl.riesgoTrans(bloques["objetos"])
    evlvl.riesgoPlat(bloques["objetos"])
    evlvl.calculaRecompensaPuntosPlat(bloques["objetos"])
    evlvl.calculaRecompensaPuntosTrans(bloques["objetos"])
    evlvl.calculaRecompensaNivelPlat(bloques["objetos"])
    evlvl.calculaRecompensaNivelTrans(bloques["objetos"])
    evlvl.calculaPrecision(bloques["objetos"], evlvl.pendUp, evlvl.pendDown, escenario)
    evlvl.calculaTiempo(bloques["objetos"])    
    evlvl.calculaMotivacionPuntos(bloques["objetos"])
    evlvl.calculaMotivacionNivel(bloques["objetos"])
    evlvl.calculaUtilidad(bloques["objetos"])
    
    #Se aplica el filtro de utilidad minima
    translate ={"piso":'i',"obstaculo":"f", "rebote":"b", "movil":['rh','rh1','rv','rv1'],
                "comida":['ws', 'ps', 'rf', 'bf'], "sub-mision":['d', 'p', 'l'],
                "enemigoHorizontal":['T', 'T1', 'O', 'O1'], "enemigoVertical":['A', 'A1'],
                "checkpoint":'c', "inicio":'S', "meta":'G'}
    for plat in bloques["objetos"]:
      if(plat["utilidad"] < env.utilidadMin) and plat["tipo"]!='ataque':
        #print("Removiendo plataformas por poca utilidad...")
        if type(translate[plat["tipo"]]) == list:
          for tipo in translate[plat["tipo"]]:
            plat["tipo"]= tipo
            level = ckAgnt.remuevePlat(plat, level)
        else:
          plat["tipo"] = translate[plat["tipo"]]
          level = ckAgnt.remuevePlat(plat, level)

    #Se calculan las rutas optimas
    initId, platInicio = rutas.encuentraInicio(bloques["objetos"])
    #print("La plataforma incial es: ", platInicio)
    meta = rutas.encuentraMeta(bloques["objetos"])
    #print("La plataforma meta es:", meta)
    rutasOptimas = rutas.bestRoutes(bloques["objetos"], [int(initId),int(platInicio)])
    caminos={}
    namesRoutes=[]
    #print("La rebanada tiene los bloques:")
    #for b in bloques['objetos']:
     # print(b["tipo"])
      #print(b["id"])
      #print(b["p_inicio"])
    for rute in rutasOptimas:
      caminos[rute]= rutas.get_route(rutasOptimas[rute],str(meta), int(initId))
      namesRoutes.append(rute)
    rewardCar = []
    rewardHistoric = []
    evalInfo = {}
    evalInfo["accion"]= action
    for c in env.caracteristicas:

      nFlucts, minVal, maxVal, castigo = rutas.evalRitmo(caminos[env.ruta_obj], bloques['objetos'], c)
      #Con la evaluacion de ritmo se define el reward
      reward = ckAgnt.reward(nFlucts, env.caracteristicas[c]['ritmo'], env.caracteristicas[c]['varRitmo'],
                             maxVal, minVal, env.caracteristicas[c]['limSup'], env.caracteristicas[c]['limInf'],
                             env.caracteristicas[c]['alpha'], env.caracteristicas[c]['beta'], castigo, env.pVal)
      evalInfo[c]={"nFlucts":int(nFlucts), "minVal":float(minVal), "maxVal":float(maxVal), "reward": float(reward)}
      rewardHistoric.append(reward)
      rewardCar.append(reward*env.caracteristicas[c]['ponderacion'])

    rewardCar=np.array(rewardCar)
    rewardFinal = rewardCar.sum()

    rewardHistoric.append(rewardFinal)
    #Se guarda el mejor nivel, asociado a la recompensa maxima de entrenamiento
    if rewardFinal > env.maxReward:
        env.maxReward = copy.copy(rewardFinal)
        env.bestLevel = copy.copy(env.map)
        env.bestMove = copy.copy(env.counter)
        env.bestExp = copy.copy(env.expCounter)

    evalInfo["Total"]= float(rewardFinal)


    cont = 0
    while cont<2:
      plats, nPlats = ckAgnt.detectaObjetos([agent.plat_height, agent.plat_width],level)     
      levelFinal = ckAgnt.puleNivel(plats, level)
      n["mapa"] = {}
      for fila in range(filas):
        n["mapa"][str(fila)]={}
        for col in range(columnas):
          n["mapa"][str(fila)][str(col)]= levelFinal[fila][col]    
      name = "level"+exp+str(contLevels)+"_run"+str(i)
      f = open(drivePath+"/"+name+".json", "w+")
      nivel=json.dumps(n)
      f.write(nivel)
      f.close()
      #name= "level"+exp+str(contLevels)+"_runINFO"+str(i)
      #f2 = open(drivePath+"/"+name+".json", "w+")
      #nivelI=json.dumps(infos[contLevels])
      #f2.write(nivelI)
      #f2.close()
      cont+=1
    
    with open(drivePath+'/'+"level"+exp+str(contLevels)+"_run"+".npy", 'wb') as f:
      np.save(f, np.array(procesos[contLevels]), allow_pickle=True)

    contLevels+=1



