# IMPORTS
import pygame
import os
import time
import random
pygame.font.init()

# PYGAME WINDOW
WIDTH, HEIGHT = 750, 750 # DEFINING WIDTH AND HIGHT FOR DISPLAY
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Avoid Ticket") # NAME OF THE WINDOW

# LOADING IMAGE ASSETS INTO SCRIPTS SO WE CAN USE THEM AND DISPLAY THEM ON THE SCREEN
# CODE EXPLANATION

# VARIABLES ALL CAPITAL BECAUSE THEY ARE CONSTANT.
# FOR enemies ( one, two, three ) FROM pygame MODULE USE image.load METHOD AND INSIDE OF PARETESIS WE ARE LOADING IMAGES WHICH IS LOCATED AT os.path.join IN FOLDER NAMED assets AND NAME OF THE FILE one.png

# SAME FOR player, ticket, and background.

ONE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "one.png")), (200, 100))
TWO = pygame.transform.scale(pygame.image.load(os.path.join("assets", "two.png")), (200, 100))
THREE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "three.png")), (200, 100))

# PLAYER
BUGATTI = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bugatti.png")), (100, 200))

# TICKET
FOUR = pygame.transform.scale(pygame.image.load(os.path.join("assets", "four.png")), (10, 20))
FIVE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "five.png")), (10, 20))
SIX = pygame.transform.scale(pygame.image.load(os.path.join("assets", "six.png")), (10, 20))
SEVEN = pygame.transform.scale(pygame.image.load(os.path.join("assets", "seven.png")), (10, 20))

# BACKGROUND
# SCALING width AND height OF THE background TO FILL THE SCREEN BASE ON width AND height THAT WE DEFINED ABOVE
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "road.png")), (WIDTH, HEIGHT))

# TICKET - PUBLIC
class Ticket:
    def __init__(self, x, y, img): # REPRESENTS 1 ticket OBJECT

        # SETTING UP atributes FOR THE CLASS
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img) # TAKING THE surface OF car image AND MAKING A mask OF IT ( mask TELLS US WHERE PX LOCATION)
    
    #DRAW
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # IF WE WANT TO GO down - IF WE WANT TO GO UP +
    def move(self, vel):
        self.y += vel

    # IF ticket IS off THE screen
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    # IF collide WITH AN object
    def collision(self, obj):
        return collide(self, obj) # self GIVING ACCESS TO SPECIFIC instance / ticket

# CAR - PUBLIC
class Car: # CREATING ABSTRACT CLASS TO INHERIT FROM IT
    COOLDOWN = 30

    def __init__(self, x, y, health=100): # PROPERTIES OF CARS ( starting position and health )

        # SETTING UP atributes FOR THE CLASS
        self.x = x
        self.y = y
        self.health = health
        self.car_img = None
        self.ticket_img = None
        self.tickets = []
        self.cool_down_counter = 0

    # DEFINING METHODS
    def draw(self, window): # TELLING WHERE TO DRAW
        window.blit(self.car_img, (self.x, self.y)) # REFERENCING atrubites THAT SPECIFIC TO THIS car THAT BEEING DRAWN
        for ticket in self.tickets:
            ticket.draw(window) # THAT WILL DRAW ALL tickets

    # MOVE TICKETS
    def move_tickets(self, vel, obj): 
        self.cooldown()
        for ticket in self.tickets:
            ticket.move(vel)
            if ticket.off_screen(HEIGHT):
                self.tickets.remove(ticket)
            elif ticket.collision(obj):
                obj.health -= 10 # IF collided - 10
                self.tickets.remove(ticket)
    # COOL DOWN
    def cooldown(self): # HENDLING COOL DOWN COUNTER
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0 # IF COOL DOWN IS 0 WE ARE CREATING NEW ticket
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    # SHOOT
    def shoot(self):
        if self.cool_down_counter == 0: # HOW LONG TO THE NEXT shot
            ticket = Ticket(self.x, self.y, self.ticket_img) # TICKET
            self.tickets.append(ticket)
            self.cool_down_counter = 1 # STARTING COOL DOWN COUNTER

    # MAKING SURE THAT car IS STAYS INSIDE OF THE SCREEN
    def get_width(self):
        return self.car_img.get_width()

    def get_height(self):
        return self.car_img.get_height()

# PLAYER - PUBLIC
class Player(Car): # INHERETING FROM car
    def __init__(self, x, y, health=100): # PROPERTIES OF CARS ( starting position and health )

         # SETTING UP atributes FOR THE CLASS
        super().__init__(x, y, health)
        self.car_img = BUGATTI # RERERENCING TO IMAGES
        self.ticket_img = SEVEN # RERERENCING TO IMAGES
        self.mask = pygame.mask.from_surface(self.car_img) # TAKING THE surface OF car image AND MAKING A mask OF IT ( mask TELLS US WHERE PX LOCATION)
        self.max_health = health # SETTING maximum health

    # MOVE TICKETS
    def move_tickets(self, vel, objs):
        self.cooldown() # CHECKS IF WE CAN shot ANOTHER ticket OR NOT
        for ticket in self.tickets:
            ticket.move(vel) # MOVE BY velosiry
            if ticket.off_screen(HEIGHT):
                self.tickets.remove(ticket)

            # IF ticket collides
            else:
                for obj in objs:
                    if ticket.collision(obj):
                        objs.remove(obj)
                        if ticket in self.tickets:
                            self.tickets.remove(ticket)

    # OVERRIDING METHOD FROM PARENT CLASS
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    # pygame USES draw MODULE AND rect (rectangle ) IN window WITH RBG red in #1 and #2 BELLOW
    def healthbar(self, window): # HEALTH BAR HALF RED HALF GREEN
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.car_img.get_height() + 10, self.car_img.get_width(), 10)) #1 HEALTH BAR RED BELLOW PLAYER
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.car_img.get_height() + 10, self.car_img.get_width() * (self.health/self.max_health), 10)) #2 # HEALTH BAR GREEN BELLOW PLAYER

# ENEMY - PUBLIC
class Enemy(Car): # INHERETING FROM car
    COLOR_MAP = {
                "red": (ONE, FOUR),
                "green": (TWO, FIVE),
                "blue": (THREE, SIX)
                } # ASSIGNING color OF THE car TO THE color OF THE ticket IN THE dictionary

    def __init__(self, x, y, color, health=100): # PROPERTIES OF CARS ( starting position color, and health )
    # THIS TIME WE ADDED COLOR BECAUSE cars WILL START WITH DIFFERENT colors

         # SETTING UP atributes FOR THE CLASS
        super().__init__(x, y, health)
        self.car_img, self.ticket_img = self.COLOR_MAP[color] # PASSING THE color
        self.mask = pygame.mask.from_surface(self.car_img) # TAKING THE surface OF car image AND MAKING A mask OF IT ( mask TELLS US WHERE PX LOCATION)

    # IMPLOMATING THE method THAT ALLOWES US TO MOVE THE car
    def move(self, vel):
        self.y += vel # enemy car MOVES ONLY down THE SCREEN # vel STANDS FOR velosity

    # SHOOT
    def shoot(self):
        if self.cool_down_counter == 0:
            ticket = Ticket(self.x-20, self.y, self.ticket_img) # CENTERING tickets
            self.tickets.append(ticket)
            self.cool_down_counter = 1

# collision OF AN objects
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x # DISTANCE BETWEEN object 1 AND object 2
    offset_y = obj2.y - obj1.y # DISTANCE BETWEEN object 1 AND object 2
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None # MAKING SURE THAT objects ACTUALLY collided

# PYGAME MAIN LOOP
def main():
    run = True # RUN WILL DECIDE IF while WILL RUN OR NOT
    FPS = 60 # FPS STANDS FOR FRAMES PER SECOND IT IS SET TO STANDART 60 FPS
    level = 0 # STARTING LEVEL
    lives = 5 # STARTING LIVES
    main_font = pygame.font.SysFont("comicsans", 50) # DEFINING font STYLE AND SIZE
    lost_font = pygame.font.SysFont("comicsans", 60) # DEFINING font STYLE AND SIZE

    enemies = [] # CREATING A list TO STORE ALL enemies
    wave_length = 5 # STARTING WITH 5
    enemy_vel = 1 # enemy velosity 1

    player_vel = 5 # EVERY TIME THE KEY IS PRESSED YOU CAN MOVE 5 PX
    ticket_vel = 5 # SPEED OF ticket

    player = Player(300, 630) # MAKING player CAR AND DEFINING starting position AND INHERITING FROM car class

    clock = pygame.time.Clock() # WE WILL tick THIS CLOCK BASED ON FPS ( 60 ) TO MAKE SURE THAT pygame IS COSISTANT

    lost = False
    lost_count = 0

    # FUNCTION DEFINED INSIDE OF THE FUNCTION BECAUSE WE WILL CALL IT ONLY WHEN WE NEED TO USE IT
    # WE CAN CALL IT ONLY WHEN WE ARE IN THIS FUNCTION
    def redraw_window():
        WIN.blit(BG, (0,0)) # LOCATION OF DRAWING OF OBJECT ( FROM TOP LEFT )

        # DRAW TEXT
        lives_label = main_font.render(f"LIVES: {lives}", 1, (255,255,255)) # TAKES value OF lives AND WE ARE SETTING UP RBG TO WHITE
        level_label = main_font.render(f"LEVELS: {level}", 1, (255,255,255)) # TAKES value OF level AND WE ARE SETTING UP RBG TO WHITE

        WIN.blit(lives_label, (10, 10)) # POSITION OF lifes LABEL ( TOP LEFT CORNER )
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10)) # POSITION OF levels LABEL ( TOP RIGHT CORNER )

        # inheriting FROM car
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN) # CALLING ON draw METHOD

        # GAME OVER
        if lost:
            lost_label = lost_font.render("GAME OVER", 1, (255,255,255)) # MESSAGE AND RBG COLOR
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350)) # CENTERING THE MESSAGE

        pygame.display.update() # WILL REFRESH THE DISPLAY

    while run:
        clock.tick(FPS)
        redraw_window()

        # MAKING SURE THAT GAME WILL end AT THIS POINT
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        # IF LOST WHEN TO QUIT THE GAME
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1 # LEVEL
            wave_length += 5 # AMOUNT OF enemies

            # RENDOMLY CHOOSING color AND position FOR enemie spawn
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy) # appending TO enemies list

        for event in pygame.event.get(): # CHECKS IF USER QUIT THE WINDOW
            if event.type == pygame.QUIT: # WILL STOP RUNNING pygame
                quit()

        #player.x - player_vel > 0: # LEFT MAKES SURE TAHT CAR IS INSEDE OF DISPLAY ( IN CODE BELLOW )
        # player.x + player_vel + player.get_width() < WIDTH: MAKES SURE TAHT CAR IS INSEDE OF DISPLAY ( IN CODE BELLOW )
        # player.y - player_vel > 0: # UP MAKES SURE TAHT CAR IS INSEDE OF DISPLAY ( IN CODE BELLOW )
        # player.y + player_vel + player.get_height() + 15 < HEIGHT: MAKES SURE TAHT CAR IS INSEDE OF DISPLAY ( IN CODE BELLOW )

        keys = pygame.key.get_pressed() # RETURNS A disctionary OF ALL OF THE keys AND CHECKS IF THE KEY IS PRESSED OR NOT
        if keys[pygame.K_a] and player.x - player_vel > 0: # LEFT
            player.x -= player_vel # EVERY TIME TO MOVE WE ARE SUBTRACTING -1 TO MOVE 1 PX TO THE left
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # RIGHT
            player.x += player_vel # EVERY TIME TO MOVE WE ARE SUBTRACTING -1 TO MOVE 1 PX TO THE left
        if keys[pygame.K_w] and player.y - player_vel > 0: # UP
            player.y -= player_vel # EVERY TIME TO MOVE WE ARE SUBTRACTING -1 TO MOVE 1 PX up
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # DOWN
            player.y += player_vel # EVERY TIME TO MOVE WE ARE ADDING +1 TO MOVE 1 PX down
        if keys[pygame.K_SPACE]: #SHOOT
            player.shoot()

        # MOVING DOWN THE enemies BY velosety
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_tickets(ticket_vel, player) # CHECK IF HITS THE player

            # enemies SHOOTING WITH probability of 50% every second
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            # SUBTRACTING lives IF enemies HIT THE CHECK POINT and REMOVING AN object
            if collide(enemy, player): # MAKING SURE WHEN collide WE ARE SUBTRACTING health
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT: 
                lives -= 1 # SUBTRACTING health
                enemies.remove(enemy)

        player.move_tickets(-ticket_vel, enemies) # CHECK IF ticket collide WITH enemies

#MAIN MENU
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70) # FONT SIZE AND STYLE
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("PRESS MOUSE TO BEGIN", 1, (255,255,255)) # START MESSAGE AND RBG COLOR WHITE
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350)) # CENTERING THE MESSAGE
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()

# ALISHER BEGMATOV