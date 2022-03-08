# ChunksCreator

## This is the hybrid intelligent agent proposed as an Exerience Driven PCG tool.

The Chunks creator in this repository, is based on IORand available in: \ref{}

The code is divided in parts as follows:

1. eval_level_V2 - This is the code were all levels evaluation functions (and the metrics) are programed. The main result or exit of this functions is the json file of the evaluated level, this file contains the levels features and overall description in a dictionary that relates the platforms and all its posible transitions.
2. encuentraRutas - This is the code were the functions for finding all the critical routes are. This code needs the graph structure calculated by the "eval_level_V2" functions which is stored in the evaluated level json file.
3. configPenguin - As this algorithm was originially used in "Pingu run!" this file serves as a general description of the agent's environment.
4. level8 - This example level also serves the agent as a source of information about the environment, and its used in the "eval_level_V2" functions
5. chunksAgent - This is the code were the main parts of the agent are. Here are dfined the semi-random content generators, but also other functions of the agent, like the reward function and the object detection fucntion.
6. chunksGeneratorV2 - This is the code for the IORand algorithm, here are defined the agent, the environment, the training algorithm and the functions for running the trained agent.
7. chunksGenerator_trainingGPU2 - This is an example code for the IORand agent implementation, the code is mainly composed by the inputs needed but also contains the functions for train or run the IORand agent
