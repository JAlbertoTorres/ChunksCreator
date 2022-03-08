# ChunksCreator

## This is the hybrid intelligent agent proposed as an Experience Driven PCG tool.

The Chunks creator in this repository, is based on IORand available in: \ref{}

The code is divided in parts as follows:

1. eval_level_V2 - This is the code were all levels evaluation functions (and the metrics) are programed. The main result or exit of this functions is the json file of the evaluated level, this file contains the levels features and overall description in a dictionary that relates the platforms and all its posible transitions.
2. encuentraRutas - This is the code were the functions for finding all the critical routes are. This code needs the graph structure calculated by the "eval_level_V2" functions which is stored in the evaluated level json file.
3. configPenguin - As this algorithm was originially used in "Pingu run!" this file serves as a general description of the agent's environment.
4. level8 - This example level also serves the agent as a source of information about the environment, and its used in the "eval_level_V2" functions
5. chunksAgent - This is the code were the main parts of the agent are. Here are dfined the semi-random content generators, but also other functions of the agent, like the reward function and the object detection fucntion.
6. chunksGeneratorV2 - This is the code for the IORand algorithm, here are defined the agent, the environment, the training algorithm and the functions for running the trained agent.
7. chunksGenerator_trainingGPU2 - This is an example code for the IORand agent implementation, the code is mainly composed by the inputs needed but also contains the functions for train or run the IORand agent


## How to use it?

### Before running IORand

This code requires some packages and libraries to run, some of them are part of python, but there are others that doesn't.
To properly run this code, you need to insltall:
1. Tensorflow (CPU or GPU versions are valid, but its highly recommended to use the GPU version)
2. Keras, the final deployment of the DNN is programed in Keras
3. json, most of the data used in the code is used in this format
4. pickle, for writing and loading part of the used data

Please, check for official Tensorflow documentation for more details at: https://www.tensorflow.org/install/

### Running the IORand agent

To run the EDPCG agent  open the "chunksGenerator_trainingGPU2" file.
There are some inputs of the algorithm that needs to be defined. 

1. limPlats: This is the dictionary that holds the maximun number of each block to be added. It contains a set of labels, related to each game level block, and the maximum number to be placed of it in the level chunk.
2. actions: These are the allowed actions to be performed by the agent, each one is in the form "action_gameBlock"
3. caracteristicas: This is the dictionary with the description of the reward function, it states which features will be evaluated and its own behavior, by defining a rythm and a range of values, as well as the ponderations of each one of them and the feature in general for the reward calculation.
4. env: This is the definition of the encironment, it iis related to each game experience and the specific case study to solve. In this repository, the case study is "Pingu run"
5. agent: This is the definition of the agent, it also needs some specifications about the environment, such as the input_dims, which are the dimensions of the chunk to create and also the dimensions of each platform.

Once this data is defined, you may use the functions to run the algorithm.
There are two forms of running the algorithm:
1. Training - use chunksGenerator.trainModel, feeding it with the definitions of the inputs described above. 
2. Creating chunks - use chunksGenerator.runModel, feeding it with the definitions of the inputs described above. 

