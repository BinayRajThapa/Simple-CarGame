import pygame
from pygame.locals import *
import random

pygame.init()

# create the window
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car Game')

# colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# road and marker sizes
road_width = 300
marker_width = 10
marker_height = 50

# lane coordinates
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# road and edge markers
road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
player_x = 250
player_y = 400

# frame settings
clock = pygame.time.Clock()
fps = 120

# game settings
gameover = False
speed = 2
score = 0
health = 3

# high score
try:
    with open('high_score.txt', 'r') as file:
        high_score = int(file.read())
except FileNotFoundError:
    high_score = 0

# load images
player_image = pygame.image.load('images/car.png')
coin_image = pygame.image.load('images/coin.png')
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()
heart_image = pygame.image.load('images/heart.png')  # Load heart image for health

# scale heart image
heart_image = pygame.transform.scale(heart_image, (30, 30))

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        super().__init__(player_image, x, y)

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(coin_image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# load the vehicle images
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('images/' + image_filename)
    vehicle_images.append(image)

# game loop
running = True
background_y = 0

while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # move the player's car using the left/right arrow keys
        if event.type == KEYDOWN:
            if event.key == K_LEFT and player.rect.center[0] > left_lane:
                player.rect.x -= 100
            elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                player.rect.x += 100

            # check for side swipe collision after changing lanes
            for vehicle in vehicle_group:
                if pygame.sprite.collide_rect(player, vehicle):
                    health -= 1
                    if health <= 0:
                        gameover = True
                        crash_rect.center = [player.rect.center[0], player.rect.top]

    # draw the scrolling background
    background_y += speed / 2
    if background_y >= height:
        background_y = 0

    # draw the road
    pygame.draw.rect(screen, gray, road)

    # draw the edge markers
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)

    # draw the lane markers
    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

    # draw the player's car
    player_group.draw(screen)

    # add a vehicle
    if len(vehicle_group) < 2:
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False

        if add_vehicle:
            lane = random.choice(lanes)
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)

    # make the vehicles move
    for vehicle in vehicle_group:
        vehicle.rect.y += speed

        # remove vehicle once it goes off screen
        if vehicle.rect.top >= height:
            vehicle.kill()
            score += 1

            # speed up the game after passing 5 vehicles
            if score > 0 and score % 5 == 0:
                speed += 1

    # draw the vehicles
    vehicle_group.draw(screen)

    # add coins
    if len(coin_group) < 1 and random.randint(0, 100) < 2:
        lane = random.choice(lanes)
        coin = Coin(lane, height / -2)
        coin_group.add(coin)

    # make coins move
    for coin in coin_group:
        coin.rect.y += speed
        if coin.rect.top >= height:
            coin.kill()

    # check for coin collection
    if pygame.sprite.spritecollide(player, coin_group, True):
        score += 5

    # draw coins
    coin_group.draw(screen)

    # display the score
    font = pygame.font.Font(pygame.font.get_default_font(), 30)  # Larger font for score
    text = font.render(f'Score: {score}', True, white)
    text_rect = text.get_rect()
    text_rect.center = (width // 2, 50)  # Position score at the top center
    screen.blit(text, text_rect)

    # display hearts (health)
    for i in range(health):
        screen.blit(heart_image, (10 + i * 35, 10))  # Display hearts at top left

    # check for head-on collision
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        health -= 1
        if health <= 0:
            gameover = True
            crash_rect.center = [player.rect.center[0], player.rect.top]

    # display game over
    if gameover:
        screen.blit(crash, crash_rect)
        pygame.draw.rect(screen, red, (0, 50, width, 100))
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Game over. Play again? (Enter Y or N)', True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 100)
        screen.blit(text, text_rect)

        # display high score
        if score > high_score:
            high_score = score
            with open('high_score.txt', 'w') as file:
                file.write(str(high_score))

        high_score_text = font.render(f'High Score: {high_score}', True, white)
        high_score_rect = high_score_text.get_rect()
        high_score_rect.center = (width / 2, 150)
        screen.blit(high_score_text, high_score_rect)

    pygame.display.update()

    # wait for user's input to play again or exit
    while gameover:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False
            if event.type == KEYDOWN:
                if event.key == K_y:
                    # reset the game
                    gameover = False
                    speed = 2
                    score = 0
                    health = 3
                    vehicle_group.empty()
                    coin_group.empty()
                    player.rect.center = [player_x, player_y]
                elif event.key == K_n:
                    # exit the loops
                    gameover = False
                    running = False

pygame.quit()