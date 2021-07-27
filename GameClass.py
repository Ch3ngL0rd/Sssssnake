from hashlib import new
import numpy as np
import random

from numpy.core.numeric import cross
from SnakeClass import Snake, LoserAi, BasicAi, EatFood, SmartFood, GenericSnake
from FoodClass import Food
import pygame
import time

#0 - EMPTY
#1 - SNAKE
#2 - FOOD

np.set_printoptions(threshold=np.inf)

class Game:
    def __init__(self,block_size,blocks_x,blocks_y,num_snake,snake_len,num_food,FPS, seed = 41):
        self.block_size = block_size
        self.blocks_x = blocks_x
        self.blocks_y = blocks_y
        self.num_snake = num_snake
        self.snake_len = snake_len
        self.num_food = num_food
        self.seed = seed
        self.FPS = FPS
        self.generation = 1000
        self.generationNum = 0
        random.seed(seed)

        x_game_state = []
        x_game_state.append([1 for i in range(blocks_y)])
        for l in range(blocks_x-2):
            x_game_state.append([1] + [0 for i in range(blocks_y-2)] + [1])
        x_game_state.append([1 for i in range(blocks_y)])

        self.gameBoard = x_game_state

        self.game_state = self.gameBoard
        self.snake_list = []
        self.dead_snakes = []
        self.food_list = []
        self.running = True

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode([self.block_size * self.blocks_x, self.block_size * self.blocks_y])

        self.mutation_percept = 50
        self.nextSnakes = []
        self.steps = 0

    def generate_game(self):
        #Create snakes - horizontal of length snake_len
        if self.generationNum != 0:
            new_snakes = self.select_snakes(self.num_snake)
        for create in range(self.num_snake):
            #Walls are 1 length around
            #Attempt to place random snake
            created = True
            '''
            orientation = random.randint(0,1)

            if orientation == 1: 
                random_x = random.randint(3,self.blocks_x-3-self.snake_len)
                random_y = random.randint(3,self.blocks_y-3)
                for i in range(self.snake_len):
                    if self.game_state[random_x+i][random_y] != 0:
                        created = False
            else:
                random_x = random.randint(3,self.blocks_x-3)
                random_y = random.randint(3,self.blocks_y-3-self.snake_len)
                for i in range(self.snake_len):
                    if self.game_state[random_x][random_y+i] != 0:
                        created = False
            '''
            #Creation is messed - this works
            random_x = create*13%self.blocks_x
            random_y = (create*17)*13%self.blocks_y

            orientation = 0
            #Add snake to game_state
            if created:
                for i in range(self.snake_len):
                    if orientation:
                        self.game_state[random_x+i][random_y] = 1
                    else:
                        self.game_state[random_x][random_y+1] = 1
                if orientation:
                    snake_pos = [[random_x+i,random_y] for i in range(self.snake_len)]
                else:
                    snake_pos = [[random_x,random_y+i] for i in range(self.snake_len)]
                
                #FIRST GENERATION - RANDOM
                self.snake_list.append(GenericSnake([random.randint(0,255) for i in range(3)],snake_pos,create,6,3))
                if self.generationNum != 0:
                    self.snake_list[len(self.snake_list)-1].changeWeights(new_snakes[create])
        self.dead_snakes = []

        for create in range(self.num_food):
            self.addFood()

    def addFood(self):
            random_x = random.randint(3,self.blocks_x-3-self.snake_len)
            random_y = random.randint(3,self.blocks_y-3)
            if self.game_state[random_x][random_y] == 0:
                self.food_list.append(Food((123,255,1),[random_x,random_y]))
                self.game_state[random_x][random_y] = 2
    
    def update(self):   
        self.game_state = self.gameBoard
        for snake in self.snake_list:
            for (x,y) in snake.return_position():
                self.game_state[x][y] = 1

        for food in self.food_list:
            x,y = food.return_position()
            self.game_state[x][y] = 2

        for snake in self.snake_list:
            snake.update_inputs(self.game_state)
            snake.make_decision()
            snake.move()

        self.killSnakes()
        self.killFood()
        self.createFood()

    def createFood(self):
        if len(self.food_list) <= self.num_food:
            self.addFood()

    def killSnakes(self):
        toKill = []
        for num,snake in enumerate(self.snake_list):
            for otherSnake in self.snake_list:
                if snake.id != otherSnake.id:
                    if snake.head() in otherSnake.return_position():    
                        toKill.append(num)
            if snake.head() in snake.return_position()[1:] or snake.head()[0] in (0,self.blocks_x-1) or snake.head()[1] in (0,self.blocks_y-1):
                toKill.append(num)
        for num,i in enumerate(toKill):
            #must minus num from i for every snake moved
            try:
                self.dead_snakes.append(self.snake_list.pop(i-num))
            except IndexError:
                print(self.snake_list)

    def killFood(self):
        #Check snake head == food pos
        toKill = []
        for num,food in enumerate(self.food_list):
            for snake in self.snake_list:
                if food.return_position() == snake.head():
                    snake.ateFood()
                    toKill.append(num)
        for num,i in enumerate(toKill):
            #must minus num from i for every snake moved
            self.food_list.pop(i-num)

    def render(self):
        for snake in self.snake_list:
            snake.render(self.screen,self.block_size)
        for food in self.food_list:
            food.render(self.screen,self.block_size)

    def run(self):
        while self.running:
            self.clock.tick(self.FPS)
            self.steps += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
            if len(self.snake_list) == 0:
                self.running = False
            if self.steps == 300:
                for i in self.snake_list:
                    self.dead_snakes.append(i)
                self.running = False
            self.screen.fill((255,255,255))
            self.render()
            self.update()
            pygame.display.flip()

    def run_simulation(self):
        self.generate_game()
        self.run()
        self.restart()
        
        for i in range(self.generation):
            self.generationNum += 1
            self.generate_game()
            self.run()
            self.restart()

            if (self.generationNum % 50 == 0):
                self.FPS = 20
            else:
                self.FPS = 1000
        
    def restart(self):
        self.game_state = self.gameBoard
        self.snake_list = []    
        self.food_list = []
        self.running = True
        self.steps = 0

    #returns num bred snakes
    def select_snakes(self, num):
        sorted_fitness = [(snake.fitness(),snake) for snake in self.dead_snakes] 
        sorted_fitness.sort(key = lambda x: x[0], reverse = True)

        #SELECT 4 BEST SNAKES AND BREED
        best_snakes = [i[1] for i in sorted_fitness[:4]]
        x = 0
        new_snakes = []
        #possible for it to be the same snake
        while x <= num:
            rand1,rand2 = random.randint(0,3), random.randint(0,3)
            new_snakes.append(self.crossover(best_snakes[rand1],best_snakes[rand2]))
            x += 1
        return new_snakes

    #Not sure if it should be += or =?
    def mutate(self, layer: list):
        length = len(layer)
        newLayer = layer.copy()
        for i in range(len(layer)):
            if random.randint(0,100) < self.mutation_percept:
                newLayer[i] = random.random() * 2 - 1
        return newLayer

    def crossover(self, snake1 : GenericSnake, snake2 : GenericSnake):
        network_a = snake1.returnWeights()
        network_b = snake2.returnWeights()
        network = []
        for (i,j) in zip(network_a,network_b):
            layer = []
            for (layer1,layer2) in zip(i,j):
                split = random.randint(0,len(layer1['weights'])-1)
                weight = {'weights' : self.mutate(layer1['weights'][:split] + layer2['weights'][split:])}
                layer.append(weight)
            network.append(layer)
        network = [network[0]]+[network[1]]
        return network
pygame.init()
testGame = Game(10,110,60,10,10,10,50)
testGame.run_simulation()
