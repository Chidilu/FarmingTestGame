import pygame
import sys
import random

#constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 50
ROWS = SCREEN_HEIGHT // GRID_SIZE
COLS = int(SCREEN_WIDTH-(SCREEN_WIDTH/6)) // GRID_SIZE
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (100, 75, 50)
GRASS = (106, 164, 102)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
SEED_COST = -2
WATER_COST = -1
TOTAL_PLANTS = 2

#initialize variables
money = 10
plantSelection = 0
plantType = {
    0: "Mushroom",
    1: "Truffel"
}

#pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Farming Prototype")
clock = pygame.time.Clock()

#Classes
    #superclass
class Tile:
    def __init__(self, row, col, type=None, stage=None):
        self.row = row
        self.col = col
        self.x = col * GRID_SIZE
        self.y = row * GRID_SIZE
        self.color = WHITE
        self.type = type
        self.stage = stage
        self.watered = False
        self.growth_timer = 0
    
    def draw(self):
        surface = pygame.Surface((GRID_SIZE, GRID_SIZE))
        surface.fill(self.getColour())
        screen.blit(surface, (self.x, self.y))
        pygame.draw.rect(screen, self.color, (self.x, self.y, GRID_SIZE, GRID_SIZE), 1)
    
    def update(self):
        self.draw()
        if self.watered == True:
            self.stage = "Watered"
            self.draw()
            self.growth_timer -= 1
            if self.growth_timer <= 0:
                self.stage = "Crop"
                self.watered = False
                self.growth_timer = 0
                self.draw()
    
    def getColour(self):
        return GRASS
    
    def harvest(self):
        return 0


class Mushroom(Tile):
    try:
        seed_image = pygame.image.load("FarmPics/mushroom_seed.png")
        seed_image = pygame.transform.scale(seed_image, (GRID_SIZE/2, GRID_SIZE/2))
        crop_image = pygame.image.load("FarmPics/mushroom_crop.png")
        crop_image = pygame.transform.scale(crop_image, (GRID_SIZE, GRID_SIZE))
    except:
        raise ImportError("Images could not be found for: Mushroom")
    
    def __init__(self, row, col, type="Mushroom", stage="Seed"):
        super().__init__(row, col, type, stage)
        self.image = self.getImage()
        self.growth_timer = 100
    
    def draw(self):
        if self.image == None: return
        self.checkWatered()
        self.image = self.getImage()
        seed_x = self.x + (GRID_SIZE - self.image.get_width()) // 2
        seed_y = self.y + (GRID_SIZE - self.image.get_height()) // 2
        screen.blit(self.image, (seed_x, seed_y))
    
    def checkWatered(self):
        surface = pygame.Surface((GRID_SIZE, GRID_SIZE))
        if self.watered:
            surface.fill(BLUE)
        else:
            surface.fill(self.getColour())
        screen.blit(surface, (self.x, self.y))

    def getImage(self):
        if self.stage == "Seed" or self.stage == "Watered":
            temp_image = self.seed_image
        elif self.stage == "Crop":
            temp_image = self.crop_image
        else:
            return None
        return temp_image

    def getColour(self):
        return BROWN
    
    def harvest(self):
        return 4
                
class Truffle(Tile): #TODO
    try:
        truffle_image = pygame.image.load("FarmPics/truffle_crop.png")
        truffle_image = pygame.transform.scale(truffle_image, (GRID_SIZE, GRID_SIZE))
    except:
        raise ImportError("Images could not be found for: Truffle")

    def __init__(self, row, col, type="Truffle", stage="Crop"):
        super().__init__(row, col, type, stage)
        self.image = self.getImage()
    
    def getImage(self):
        return self.truffle_image
    
    def draw(self):
        if self.image == None: return
        surface = pygame.Surface((GRID_SIZE, GRID_SIZE))
        surface.fill(self.getColour())
        screen.blit(surface, (self.x, self.y))
        self.image = self.getImage()
        seed_x = self.x + (GRID_SIZE - self.image.get_width()) // 2
        seed_y = self.y + (GRID_SIZE - self.image.get_height()) // 2
        screen.blit(self.image, (seed_x, seed_y))
    
    def getColour(self):
        return BROWN
    
    def harvest(self):
        return 10
    


class Player:
    def __init__(self):
        self.row = 0
        self.col = 0
    
    def move(self, dr, dc):
        new_row = self.row + dr
        new_col = self.col + dc
        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
            self.row = new_row
            self.col = new_col
    
    def isCrop(self, grid):
        tile = grid[self.row][self.col]
        return tile.stage
    
    def plant_crop(self, grid, selection): #TODO
        if selection == 0:
            grid[self.row][self.col] = Mushroom(self.row, self.col)
        elif selection == 1:
            grid[self.row][self.col] = Truffle(self.row, self.col)
    
    def water_crop(self, grid):
        grid[self.row][self.col].watered = True
    
    def harvest_crop(self, grid):
        tile = grid[self.row][self.col]
        money_earned = tile.harvest()
        grid[self.row][self.col] = Tile(self.row, self.col)
        return money_earned

class Pig:
    try:
        pig_image = pygame.image.load("FarmPics/pig.png")
    except:
        raise ImportError("Images could not be found for: Pig")
    
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.image = None
        self.radius = radius  # Adjust the size of the object as needed

    def draw(self):
        self.image = self.getImage()
        screen.blit(self.image, (self.x - self.radius, self.y - self.radius))

    @staticmethod
    def resize_image(image, width, height):
        return pygame.transform.scale(image, (width, height))

    def getImage(self):
        return self.resize_image(self.pig_image, self.radius * 2, self.radius * 2)

    def check_collision(self, grid):
    # Define the collision area based on the radius
        collision_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    # Check for collision with tiles in the grid
        for row in grid:
            for tile in row:
                tile_rect = pygame.Rect(tile.x, tile.y, GRID_SIZE, GRID_SIZE)
                if collision_rect.colliderect(tile_rect):
                # Perform actions based on the type of tile
                    if isinstance(tile, Mushroom):
                        print("Collided with Mushroom!")
                    elif isinstance(tile, Truffle):
                        print("Collided with Truffle!")
                # You can extend this with more tile types and actions as needed


#functions
def draw_grid(player):
    for row in grid:
        for tile in row:
            tile.draw()
            if tile.row == player.row and tile.col == player.col:
                pygame.draw.rect(screen, GREEN, (tile.x, tile.y, GRID_SIZE, GRID_SIZE), 3)

def draw_sidebar(money, selection):
    sidebar_surface = pygame.Surface(((SCREEN_WIDTH/5), SCREEN_HEIGHT))
    sidebar_surface.fill(WHITE)
    font = pygame.font.Font(None, 24)
    font2 = pygame.font.Font(None, 20)
    text = font.render(f"Money: {money}", True, BLACK)
    text_rect = text.get_rect(center=(75, 50))
    sidebar_surface.blit(text, text_rect)
    text2 = font.render(f"Selection: ", True, BLACK)
    textSelection = font2.render((" -> " + selection), True, BLACK)
    text_rect2 = text.get_rect(center=(75, 75))
    text_rectSelection = text.get_rect(center=(75, 90))
    sidebar_surface.blit(text2, text_rect2)
    sidebar_surface.blit(textSelection, text_rectSelection)
    screen.blit(sidebar_surface, (SCREEN_WIDTH - (SCREEN_WIDTH/5), 0))

def handle_events(player, money):
    global plantSelection
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.move(-1, 0)
            elif event.key == pygame.K_DOWN:
                player.move(1, 0)
            elif event.key == pygame.K_LEFT:
                player.move(0, -1)
            elif event.key == pygame.K_RIGHT:
                player.move(0, 1)
            elif event.key == pygame.K_a:
                plantSelection += 1
                if plantSelection >= TOTAL_PLANTS:
                    plantSelection = 0
            elif event.key == pygame.K_SPACE:
                if (player.isCrop(grid) == None) and money >= 2:
                    player.plant_crop(grid, plantSelection)
                    return SEED_COST
                elif (player.isCrop(grid) == "Seed") and money >= 1:
                    player.water_crop(grid)
                    return WATER_COST
                elif (player.isCrop(grid) == "Crop"):
                    return player.harvest_crop(grid)
    return 0

player = Player()
grid = [[Tile(row, col) for col in range(COLS)] for row in range(ROWS)]
money_timer = 0
money_exponential = 300
PIGRADIUS = 100
piggy = Pig(100, 100, PIGRADIUS)
while True:
    money += handle_events(player, money)
    for row in grid:
        for tile in row:
            tile.update()
    draw_grid(player)
    draw_sidebar(money, plantType[plantSelection])
    #piggy.draw()
    #piggy.check_collision(grid)
    pygame.display.flip()
    clock.tick(30)
    money_timer += 1
    if money >= 100: money_exponential = 30000
    if money_timer >= money_exponential and money < 100:
        money += 1
        money_timer = 0
        if money_exponential < 30000: money_exponential += 30