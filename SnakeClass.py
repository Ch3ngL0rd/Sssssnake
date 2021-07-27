import random
from typing import Generic
import pygame
import math
from sklearn.preprocessing import MinMaxScaler
import numpy as np

#import keras

#Random agent
class Snake:
    def __init__(self,colour,position,id):
        self.colour = colour
        self.position = position
        self.direction = [i-j for i,j in zip(self.position[0],self.position[1])]
        self.move_choice = [[0,1],[1,0],[0,-1],[-1,0]]
        self.eaten = False
        self.id = id
        self.inputs = []
        self.memory = [0]
    
    def make_decision(self):
        new_direction = self.possible_direction()[random.randint(0,2)]
        self.direction = new_direction

    def possible_direction(self):
        if self.direction == ([0,1]):
            return  [[-1,0],[0,1],[1,0]]
        elif self.direction == ([0,-1]):
            return  [[1,0],[0,-1],[-1,0]]
        elif self.direction == ([1,0]):
            return  [[0,1],[1,0],[0,-1]]
        elif self.direction == ([-1,0]):
            return  [[0,-1],[-1,0],[0,1]]

    def update_inputs(self, game_state):
        pass
    
    def render(self,screen,block_size):
        for (x,y) in self.position: 
            pygame.draw.rect(screen, self.colour, (x*block_size,y*block_size,block_size,block_size))

    def move(self):
        self.position.insert(0,[self.position[0][0]+self.direction[0],self.position[0][1]+self.direction[1]])
        if (not self.eaten):
            self.position.pop()
        else:
            self.eaten = False  
    def return_position(self):
        return self.position

    def head(self):
        return self.position[0]

    def ateFood(self):
        self.eaten = True

#all classes have update_input and make_decision

#Goes straight until direction needs to be changed
class LoserAi(Snake):

    def make_decision(self):
        print(self.inputs)
        #If 1, direction is to be changed - removes current direction and chooses random left,right
        if self.inputs == [1]:
            possible = self.possible_direction()
            possible.remove(self.direction)
            self.direction = possible[random.randint(0,1)]
            

    def update_inputs(self, game_state):
        self.new_head = [self.position[0][0] + self.direction[0], self.position[0][1] + self.direction[1]]
        if game_state[self.new_head[0]][self.new_head[1]] != 0 or self.new_head[0] in (0,len(game_state[0]) - 1) or self.new_head[1] in (0,len(game_state) - 1):
            self.inputs = [1]
        else:
            self.inputs = [0]

class BasicAi(Snake):
    def make_decision(self):
        #Trapped
        potential = []
        for i,x in enumerate(self.possible_direction()):
            if self.inputs[i] == 0:
                potential.append(x)
        if len(potential) != 0:
            self.direction = potential[random.randint(0,len(potential)-1)]

    def update_inputs(self, game_state):
        self.inputs = [0,0,0]
        width = len(game_state[0])
        length = len(game_state)
        for i,(x,y) in enumerate(self.possible_direction()):
            if game_state[self.head()[0]+x][self.head()[1]+y] != 0 or (self.head()[0]+x) in (0,width-1) or (self.head()[1]+y) in (0,length-1):
                self.inputs[i] = 1

class EatFood(Snake):
    #DO MAX INPUT
    def make_decision(self):
        #Trapped
        potential = []
        small = min(self.inputs)
        for i,x in enumerate(self.possible_direction()):
            if self.inputs[i] == small:
                potential.append(x)

        if len(potential) != 0:
            self.direction = potential[random.randint(0,len(potential)-1)]

    #inputs
    #Returns distance from food
    #Returns 50 if no food detected
    #Returns 100 if there a wall
    def update_inputs(self, game_state):
        self.inputs = [50,50,50]
        width = len(game_state[0])
        length = len(game_state)
        for i,(x,y) in enumerate(self.possible_direction()):
            if game_state[self.head()[0]+x][self.head()[1]+y] == 1 or (self.head()[0]+x) in (0,width-1) or (self.head()[1]+y) in (0,length-1):
                self.inputs[i] = 100
            else:
                num = self.head().copy()
                original = self.head().copy()
                c = 0
                while 0 < num[0] < width-2 and 0 < num[1] < length-2:
                    if game_state[num[0],num[1]] == 2:
                        self.inputs[i] = max([abs(original[0]-num[0]),abs(original[1]-num[1])])
                        break
                    num[0],num[1] = num[0]+x,num[1]+y

class SmartFood(EatFood):
    #inputs
    #Returns distance from food
    #Returns 50 if no food detected
    #Returns 100 if there a wall
    def update_inputs(self, game_state):
        self.inputs = [50,50,50]
        width = len(game_state)
        length = len(game_state[0])
        for i,(x,y) in enumerate(self.possible_direction()):
            if [x,y] == self.direction:
                self.inputs[i] = 49
            if game_state[self.head()[0]+x][self.head()[1]+y] == 1 or (self.head()[0]+x) in (0,width-1) or (self.head()[1]+y) in (0,length-1):
                self.inputs[i] = 100

            else:
                num = self.head().copy()
                original = self.head().copy()
                c = 0
                while 0 < num[0] < width-2 and 0 < num[1] < length-2:
                    if game_state[num[0],num[1]] == 2:
                        self.inputs[i] = max([abs(original[0]-num[0]),abs(original[1]-num[1])])
                        break
                    num[0],num[1] = num[0]+x,num[1]+y

#Feed-Forward Generic Snake
#Inputs will 
class GenericSnake(Snake):
    def __init__(self,colour,position,id,n_hidden,n_output):
        super().__init__(colour,position,id)
        self.vision = [[1,1],[-1,-1],[1,-1],[-1,1],[0,1],[0,-1],[1,0],[-1,0]]
        self.output = []
        self.inputs = [0 for i in range(len(self.vision)*2)]
        self.n_hidden = n_hidden
        self.n_output = n_output
        self.network = self.initialise_network()
        self.scaler = MinMaxScaler()
        self.history = []

        #Evaluation fitness
        self.steps = 0
        self.initLength = len(self.position)
        self.turn = 0

        #highest food per step

    def move(self):
        self.position.insert(0,[self.position[0][0]+self.direction[0],self.position[0][1]+self.direction[1]])
        self.history.append(self.position[0])
        self.steps += 1
        if (not self.eaten):
            self.position.pop()
        else:
            self.eaten = False  

    def make_decision(self):
        index = self.output.index(max(self.output))
        new_direction = self.possible_direction()[index]
        if (self.direction != new_direction):
            self.turn += 1
        self.direction = new_direction
        
    def update_inputs(self, game_state):
        self.inputs = [0 for i in range(len(self.vision)*2)]
        #Returns inputs in 8 directions - x2 (food, wall)
        #update inputs based on distance to food
        width = len(game_state)
        length = len(game_state[0])

        #Distance to food, else 0
        #Distance to other snake else to wall
        for i,direction in enumerate(self.vision):
            distance = 1
            headPos = self.head().copy()
            foundSnake = False
            foodDistance = 0
            otherDistance = 0
            '''
            while 0 < direction[0]*distance + headPos[0] < width-1 and 0 < direction[1]*distance + headPos[1] < length-1:
                distance += 1
                if game_state[direction[0]*distance + headPos[0]][direction[1]*distance + headPos[1]] == 2:
                    foodDistance = distance
                if game_state[direction[0]*distance + headPos[0]][direction[1]*distance + headPos[1]] == 1 :
                    otherDistance = distance
                    foundSnake = True
            
            if foundSnake == False:
                otherDistance = distance
            '''
            if game_state[direction[0]*distance + headPos[0]][direction[1]*distance + headPos[1]] == 2:
                foodDistance = 1
            if game_state[direction[0]*distance + headPos[0]][direction[1]*distance + headPos[1]] == 1 :
                otherDistance = 1
            self.inputs[i] = foodDistance
            self.inputs[i+len(self.vision)] = otherDistance
        #self.scaler.fit(np.array(self.inputs).reshape(-1,1))
        #self.inputs = self.scaler.transform(np.array(self.inputs).reshape(-1,1))
        self.forward_propagate()
    #takes in inputs and changes outputs
    #called in make_decision
    def forward_propagate(self):
        inputs = self.inputs.copy()
        for layer in self.network:
            new_inputs = []
            for neuron in layer:
                activation = self.activate(neuron['weights'], inputs)
                neuron['output'] = self.transfer(activation)
                new_inputs.append(neuron['output'])
            inputs = new_inputs
        self.output = inputs

    def initialise_network(self):
        network = list()
        hidden_layer = [{'weights':[random.random()*2-1 for i in range(len(self.inputs) + 1)]} for i in range(self.n_hidden)]
        network.append(hidden_layer)
        output_layer = [{'weights':[random.random()*2-1 for i in range(self.n_hidden + 1)]} for i in range(self.n_output)]
        network.append(output_layer)
        return network

    def activate(self, weights, inputs):
        activation = weights[-1]
        for i in range(len(weights)-1):
            activation += weights[i] * inputs[i]
        return activation

    def transfer(self, activation):
	    return 1.0 / (1.0 + math.e**(-activation))

    def fitness(self):
        #find new steps - create set -> not intersect
        uniqueNum = len(list(set(tuple(i) for i in self.history)))
        return (len(self.position) - self.initLength)*100 + uniqueNum

    def returnWeights(self):
        return self.network

    def changeWeights(self, weights):
        self.network = weights

print("Snake Class Init.")
