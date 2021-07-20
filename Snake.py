#Snake game using pygame
import pygame
import numpy as np
import time 
import random

pygame.init()

block_size = 10
blocks_x = 40
blocks_y = 40

#FOOD = 3
#Head = 2
#Body = 1
#Nothing = 0    
#Wall = -1

game_state = np.zeros((blocks_x,blocks_y))

game_state[0] = np.full((1,blocks_x), -1)
game_state[blocks_y-1] = np.full((1,blocks_x), -1)

for i in game_state:
    i[0],i[blocks_y-1] = -1,-1

screen = pygame.display.set_mode([block_size * blocks_x, block_size * blocks_y])
running = True
eaten = False
clock = pygame.time.Clock()

#First position is head
body_list = [[11,10],[10,10],[9,10]]
food_list = []

snake_direction = [0,1]
while running:
    eaten = False
    if (len(food_list)) < 2:
        while 1:
            #Implement smarter food generation instead of random later
            rand_x,rand_y = [random.randint(0,39) for i in range(2)]
            if game_state[rand_x][rand_y] == 0:
                game_state[rand_x][rand_y] = 3
                food_list.append([rand_x,rand_y])
                break
    clock.tick(10)

    #Move snake
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and snake_direction != [1,0]:
                snake_direction = [-1,0]
            if event.key == pygame.K_RIGHT and snake_direction != [-1,0]:
                snake_direction = [1,0]
            if event.key == pygame.K_UP and snake_direction != [0,1]:
                snake_direction = [0,-1]
            if event.key == pygame.K_DOWN and snake_direction != [0,-1]:
                snake_direction = [0,1]
            break


    new_head = [body_list[0][0]+snake_direction[0],body_list[0][1]+snake_direction[1]]

    for i in body_list:
        if new_head == i:
            running = False
    if new_head[1] == 1 or new_head[1] == blocks_y-2:
        running = False
    if new_head[0] == 1 or new_head[0] == blocks_x-2:
        running = False   

    #Update Snake

    body_list.insert(0,new_head)

    for i in range(len(food_list)):
        if new_head == food_list[i-1]:
            eaten = True
            food_list.pop(i-1)
            
            
    if eaten == False:
        gone = body_list.pop()
        game_state[gone[0],gone[1]] = 0

    #Update Game
    for (i,pos) in enumerate(body_list):
        if (i == 0):
            game_state[pos[0]][pos[1]] = 2
        else:
            game_state[pos[0]][pos[1]] = 1

 
            
    #Render

    screen.fill((255,255,255))
    for row in range(len(game_state)):
        for column in range(len(game_state[row])):
            #Food
            if (game_state[row][column] == 3):
                pygame.draw.rect(screen, (255, 205, 168), (row*block_size,column*block_size,block_size,block_size))
            #Head
            if (game_state[row][column] == 2):
                pygame.draw.rect(screen, (90, 160, 168), (row*block_size,column*block_size,block_size,block_size))
            #Body
            if (game_state[row][column] == 1):
                pygame.draw.rect(screen, (132, 222, 194), (row*block_size,column*block_size,block_size,block_size))
            #Wall
            if (game_state[row][column] == -1):
                pygame.draw.rect(screen, (100, 100, 100), (row*block_size,column*block_size,block_size,block_size))


    pygame.display.flip()

time.sleep(3)
pygame.quit()