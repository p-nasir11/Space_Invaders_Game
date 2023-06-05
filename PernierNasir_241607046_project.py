import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

##set width and height
WIDTH, HEIGHT = 650, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) #windows #tuple
pygame.display.set_caption("Galaxy Attack")

WHITE = (255, 255, 255)
font = pygame.font.SysFont("candara", 30)

#loading images
##capital cuz constants - wont change
ALIEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","alien_spaceship.png"))
SECOND_SPACE_SHIP = pygame.image.load(os.path.join("assets","second_alien.png"))
THIRD_SPACE_SHIP = pygame.image.load(os.path.join("assets","third_enemy.png"))

##player ship
PINK_SPACE_SHIP = pygame.image.load(os.path.join("assets","pink_shooter.png"))

##BULLETS
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BACKGROUND = pygame.image.load(os.path.join("assets","gb_backp.png"))

#background sound
pygame.mixer.music.load(os.path.join("assets", "song.mpeg"))
pygame.mixer.music.set_volume(0.5)  # Set the volume level (0.0 to 1.0)
pygame.mixer.music.play(-1)  #loop

# asteroid
asteroid = pygame.image.load(os.path.join("assets","asteroid.png"))

class Laser:
    def __init__(self, x, y, img):
         self.x = x      ##set a direction for the laser to be independant and act on their own
         self.y = y      ##pass the image from the ship class
         self.img = img  ## with a new laser object, a new object will be created and added to its laser list
         self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y)) #window parameter represents the surface where the image will be drawn
                                                #blit function from graphics to draw an object

    ##to move it with a certain velocity command
    def move(self, vel):
        self.y += vel ##positive for upwards with a negative value

    def offf_screen(self, height): ##to know the laser isnt off target
        return not(self.y <= height and self.y >= 0) ##if the value is off screen or not

    def collision(self, obj): ##if laser collides with an obj, only returns the value of a collide function
        return collide(obj, self) ##function collide in enemy class handles collision logic

    ## ^indicates that method is comparing instance on which it is called
    # (self) with another object (obj) for collision detection rather the other way around

class Ship: ##multiple instances , base class

    COOL_DOWN = 30 ##defining variable
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None #draw ship
        self.laser_img = None #draw lasers 
        self.lasers = [] 
        self.cool_down_counter = 0

    def draw(self, window):
    #use the draw module in pygame to draw a window before importing an image
        window.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window) ##draws all the lasers, correlates with the draw method in our laser class

    def move_laser(self, vel, obj): ##implements velocity and when lasers move we check for collision with these objs ##check if each laser hits target
        self.cool_down()##implement cool down counter, ##used for player and enemy both ## call it based on commands defined in cool down function
        for laser in self.lasers: ##loop through lasers in list
            laser.move(vel)
            if laser.offf_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj): #obj is the player
                obj.health -= 5
                self.lasers.remove(laser)

    def cool_down(self):
        if self.cool_down_counter >= self.COOL_DOWN:
            self.cool_down_counter = 0 ##nothing implements
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1##if it is greater than zero and within FPS time frame, increment by one


    def shoot(self):##function in this class to shoot because both classes will use this
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img) ##we make a laser and add it to the list
            self.lasers.append(laser)
            self.cool_down_counter = 1 ##at 0 for cool down counter, if it is, create new laser, add it to list, and set the counter


    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x, y, health) #ships initialization method
        self.ship_img = PINK_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health 

        ##take the image and make pixels of it
        # inherits from ship, ship has a draw method

    def move_laser(self, vel, obj_p): ##overwrites the parent class one so polymorphism is happening
        self.cool_down()
        for laser in self.lasers: ##for each laser that the player has, move the laser
            laser.move(vel)
            if laser.offf_screen(HEIGHT): ##remove if offscreen
                self.lasers.remove(laser)
            else:
                for obj in obj_p:
                    if laser.collision(obj): ##remove laser and obj when they collide
                        obj_p.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar( ) ##draw method from the parent class


    def health_bar(self):
        pygame.draw.rect(WIN, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(WIN, (0, 255, 0),(self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Asteroid(Ship):
    def __init__(self, x, y,health=100):
        super().__init__(x, y, health)
        self.ship_img = asteroid
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y += vel

class Enemy(Ship):
    COLOUR_MAP = {
        "red": (ALIEN_SPACE_SHIP, RED_LASER),
        "green": (SECOND_SPACE_SHIP, GREEN_LASER),
        "blue": (THIRD_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOUR_MAP[color] ##pass the color parameter to the map and the image we want t use will be displayed
        self.mask = pygame.mask.from_surface(self.ship_img)


    ##method to move the ship
    ##to make the ship move downwards
    def move(self, vel):
        self.y += vel

    def shoot(self):##function in this class to shoot because both classes will use this
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img) ##we make a laser and add it to the list
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2): ##maask lets you ask pygame that when even 0.1% pixels collide, we declare it as a hit
    offset_x = obj2.x - obj1.x ##calculates the coordinates by subtraction
    offset_y = obj2.y - obj1.y #offset lets you know whether they collide or not, by returning a portion of the mask where the two objects overlap
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None #returns tuple of x and y if collide


def main_menu():
    score = 0

    def draw_score():
        score_text = font.render("Score: " + str(score), 1, WHITE)
        WIN.blit(score_text, (10, 10))

    run = True

    while run:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


##main loop
##handle commands
def main():
    run = True #set to TRUE for loop to function
    FPS = 55  ##time allocated for the game to run in whole time
    level = -1
    lives = 3
    main_font = pygame.font.SysFont("candara", 48)
    lost_font = pygame.font.SysFont("comicsans", 30)
    score = 0

    enemies = [] ##store enemies in a list
    asteroids = []
    wave_length = 5 ##wave length different for each level
    enemy_vel = 1
    asteroid_vel = 1

    player_velocity = 5 ##helps move 5 pixels in evert direction
    laser_velocity = 5

    player = Player(350,600)
    
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0
    


    def redraww_window():
        WIN.blit(BACKGROUND,(0,0))

        ##bring text to the surface
        lives_label = main_font.render(f"Lives: {lives}", 1, (0,255,0))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        ##screen display of text
        WIN.blit(lives_label, (WIDTH - lives_label.get_width() - 10, 10))
        WIN.blit(level_label, (10,10))


        for enemy in enemies:
            enemy.draw(WIN) ##for each enemy we draw it on the screen to make it simpler
            ##before the player so it falls behind it instead of the player behind it
        for asteroid in asteroids:
            asteroid.draw(WIN)


        player.draw(WIN) #draw method draws the rectangle for us so calling the method

        if lost: ##can be accessed as set to False, display for a certain amount of time
            lost_label = lost_font.render("You have Lost!!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 340)) ##display Lost

        ##will help later draw it to the location mentioned
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraww_window()

        if lives <= 0 or player.health <= 0: ##no negative lives
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 4: ##frames per second
                run = False #quit the game when past our timer and if looping it continues
            else:
                continue
        if len(asteroids) == 0:
            level += 1
            wave_length += 3
            for i in range(wave_length):
                asteroid1 = Asteroid(random.randrange(50, WIDTH-100),random.randrange(-1200, -100))
                asteroids.append(asteroid1)


        if len(enemies)  == 0:
            level += 1 ##level increases as soon as all enemies are dead so going to next level
            wave_length += 3 ##adding newer enemies
            for i in range(wave_length): ##append new enemies to a list and pick positions to avoid crowding so we pick a negative position
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1200, -100), random.choice(["red", "green", "blue"])) ##to create a different layout & random call picks random color from the list
                enemies.append(enemy)

        ##check all possible events to see if occured so any sort of action
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                ##if screen quit action takes place, stop the game


    ##modify the way you can move the player around
    ##outside the loop because player only moves in one direction

        keys = pygame.key.get_pressed() #returns a dictionary of all the keys and tells you whether they're pressed or not at the current time
        if keys[pygame.K_LEFT] and player.x - player_velocity: #left    and now extractx value from players
            player.x -= player_velocity #subtract from x value of the player so you move on pixel to left
        if keys[pygame.K_RIGHT] and player.x + player_velocity < WIDTH: #right
            player.x += player_velocity
        if keys[pygame.K_DOWN] and player.y + player_velocity < HEIGHT: #down #if i add this value to current value of y , dont move off screen
            player.y += player_velocity
        if keys[pygame.K_UP] and player.y - player_velocity > 0: #up
            player.y -= player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot() ##call a method to create new laser

        for asteroid in asteroids[:]: ##iterate over each list item
            asteroid.move(asteroid_vel) ##update position of the asteroid based on its velocity in each level

            if collide(asteroid,player):
                player.health -= 10 ##decrement in health
                asteroids.remove(asteroid)
            elif asteroid.y + asteroid.get_height() > HEIGHT:
                lives -= 1 #reducing the lives once out of screen
                asteroids.remove(asteroid)


        ##to move these enemies down by velocity as they're in negative dimensions
        for enemy in enemies[:]: ##helps not modify the original list
            enemy.move(enemy_vel)
            enemy.move_laser(laser_velocity, player)

            if random.randrange(0, 150) == 1: ##fix the speed of the laser
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1 #end life
                enemies.remove(enemy) ##removes the enemy from the list once life ends


        player.move_laser(-laser_velocity,  enemies) ##checks if laser has collided with any of the enemies
        player.move_laser(-laser_velocity,  asteroids)

    draw_score()
    pygame.quit()
main()

