import pygame
import random
import math
from PIL import Image, ImageFilter
pygame.init()

count = 0
boss = 'dead'
screenWidth = 1400
screenHeight = 1000
tileSize = 30
timeToHit = 0
currentWeaponIndex = 0
itemChance = False
screen = pygame.display.set_mode((screenWidth, screenHeight))
frameRate = pygame.time.Clock()
pygame.font.init()
mainCharacter = pygame.image.load('mainChar.png')
mainCharacter = pygame.transform.scale(mainCharacter, (30, 30))
wallImage = pygame.image.load('wall.png')
wallImage = pygame.transform.scale(wallImage, (30, 30))
doorImage = pygame.image.load('door.png')
doorImage = pygame.transform.scale(doorImage, (30, 90))
basicEnemyImage = pygame.image.load('basic_enemy.png')
basicEnemyImage = pygame.transform.scale(basicEnemyImage, (30, 30))
bossImage = pygame.transform.scale(basicEnemyImage, (50, 50))
effectPotionImage = pygame.image.load('effectPotion.png')
effectPotionImage = pygame.transform.scale(effectPotionImage, (30, 30))
gameOverFont = pygame.font.Font('medieval-sharp.bold.ttf', 64)    
font = pygame.font.Font('medieval-sharp.bold.ttf', 36)
heartIcon = pygame.image.load('Heart .png')
playerSpeed = 1
room = []
roomWidth = 0
roomHeight = 0
roomData = {}
roomNumber = 1
currentRow = 0
currentCol = 0
enemyPositions = {}
playerDoor = False
gameOver = False
currentRoomItems = []
commentaryMessages = []
commentaryFont = pygame.font.Font('medieval-sharp.bold.ttf', 15)
commentaryDisplayTime = 60

commentaryFrameCount = 0
maxMessages = 10
movementStack = []

class Character:
    def __init__(self,x, y, health):
        self.x = x
        self.y = y
        self.health = health

class Enemy(Character):
    def __init__(self, x, y,health):
        super().__init__(x,y,health)
        self.attackCooldown = 0
 
class Player(Character):
    def __init__(self, x, y,health):
        super().__init__(x,y,health)
        self.xp = 0
        self.level = 1
       
class Item:
    def __init__(self, itemType, x, y, effectType, effectValue, duration):
        self.itemType = itemType
        self.x = x
        self.y = y
        self.effectType = effectType
        self.effectValue = effectValue
        self.duration = duration

 class Weapon:
    def __init__(self, name, damage, range, attackSpeed):
        self.name = name
        self.damage = damage
        self.range = range
        self.attackSpeed = attackSpeed
    
    def calculateDamage(self, playerLevel):
        return self.damage * (1 + 0.02 * playerLevel) 
        
class Boss(Character):
    def __init__(self, x, y, health, damage, ability):
        super().__init__(x, y, health)
        self.max_health = health
        self.damage = damage
        self.ability = ability
        self.attackCooldown = 0
    def heuristicCostEstimate(self, start, goal):
        return abs(goal[0] - start[0]) + abs(goal[1] - start[1])

    def canBossMove(self, nextTile):
        return 0 <= nextTile[0] < roomWidth and 0 <= nextTile[1] < roomHeight and ro
    def remakePath(self, cameFrom, current):
        path = [current]
        while current in cameFrom:
            current = cameFrom[current]
            path.insert(0, current)
        return path
    def findPath(self, start, goal):
        openSet = set([start])
        cameFrom = {}
        gScore = {start: 0}
        while openSet:
            current = min(openSet, key=lambda node: gScore[node] + self.heuristicCos
            if current == goal:
                return self.remakePath(cameFrom, current)
            openSet.remove(current)
            for nextTile in [(current[0] + dx, current[1] + dy) for dx, dy in [(-1, 
                if not self.canBossMove(nextTile):
                    continue
                temporary_gScore = gScore[current] + 1
                if nextTile not in gScore or temporary_gScore < gScore[nextTile]:
                    cameFrom[nextTile] = current
                    gScore[nextTile] = temporary_gScore
                    openSet.add(nextTile)
        return [] 
    def move(self):
        global player
        if self.attackCooldown == 0:
            distanceFromBoss = calculateDistance(self.x, player.x, self.y, player.y)
            if distanceFromBoss <= 3:
                path = self.findPath((self.x, self.y), (player.x, player.y))
                if path and len(path) > 1:
                    nextPosition = path[1]
                    self.x, self.y = nextPosition
                    room[self.y][self.x] = 'B'
            else:
                new_x = self.x + random.choice([-1, 0, 1])
                new_y = self.y + random.choice([-1, 0, 1])
                if canMove(new_y, new_x):
                    room[self.y][self.x] = ' '
                    self.x, self.y = new_x, new_y
                    room[self.y][self.x] = 'B'
        elif self.attackCooldown > 0:
            self.attackCooldown -= 1
    def meleeAttack(self):
        global player
        distanceFromBoss = calculateDistance(self.x, player.x, self.y, player.y)
        if distanceFromBoss <= 1:
            player.health -= self.damage
    
class BossHealthBar:
    def __init__(self, boss, width, height, colour):
        self.boss = boss
        self.width = width
        self.height = height
        self.colour = colour    
    def draw(self,screen):
        pygame.draw.rect(screen, (255, 255, 255), (screenWidth - self.width - 20, sc
        pygame.draw.rect(screen, self.colour, (screenWidth - self.width - 15, screen
        pygame.draw.rect(screen, (255, 255, 255), (screenWidth - self.width - 15, sc
 player = Player(currentCol, currentRow, 100)
 playerInventory = [Weapon("Sword", 20, 1, 1.5), Weapon("Spear", 30, 1, 1.0), Weapon(
 currentWeaponIndex = 0
 currentWeapon = playerInventory[currentWeaponIndex]
 
itemImages = {
    "Sword": pygame.transform.scale(pygame.image.load('Sword.png'), (60, 60)),
    "Spear": pygame.transform.scale(pygame.image.load('Spear.png'), (60, 60)),
    "Staff": pygame.transform.scale(pygame.image.load('Staff.png'), (60, 60)),
    "Dagger": pygame.transform.scale(pygame.image.load('Dagger.png'), (60, 60))
 }
 
def calculateDistance(x1,x2,y1,y2):
    return math.sqrt(((x2 - x1)**2) + ((y2 - y1) ** 2))
 
def currentLocation(character):
    global currentCol, currentRow, playerDoor
    for j in range(roomHeight):
        for i in range(roomWidth):
            if room[j][i] == character:
                currentCol = j
                currentRow = i
                playerDoor = True
            elif room[j][i] == ' ':
                playerDoor = False
   
def canMove(newCol, newRow):
    return (0 <= newCol < roomHeight and 0 <= newRow < roomWidth and (room[newCol][n
def updateRoom(newCol, newRow):
    global currentCol, currentRow
    room[currentCol][currentRow] = ' '
    room[newCol][newRow] = mainCharacter
def enemyGen(roomRow, roomCol):
    global enemy
    xEnemy = random.randint(0,roomCol - 1)
    yEnemy = random.randint(0,roomRow - 1)
    if room[yEnemy][xEnemy] == ' ':
        enemy = Enemy(xEnemy, yEnemy,100)
        if roomNumber not in enemyPositions:
            enemyPositions[roomNumber] = []
        enemyPositions[roomNumber].append(enemy)
    else:
        enemyGen(roomRow, roomCol)
 def itemGeneration(x,y):
    itemTypes = ["Health Potion", "Damage Potion"]
    itemEffect = {
        "Health Potion": "health",
        "Damage Potion": "damage"
    }
    if room[y][x] == ' ':
        itemType = random.choice(itemTypes)
        effectType = itemEffect[itemType]
        
        effectValue = random.randint(10,30)
        duration = 3
        return (Item(itemType, x, y, effectType, effectValue, duration))
    
    else:
        return itemGeneration(random.randint(0, roomWidth - 1), random.randint(0, ro
    
def applyItem(item):
    global player, damageBoost
    if item.effectType == "health":
        player.health += item.effectValue
    if item.effectType == "damage":
        damageBoost = 1.05
        
    
def dungeonGen(roomNumber):
    global room, roomWidth, roomHeight, currentCol, currentRow, itemChance
    itemChance = False
    if roomNumber not in roomData:
        roomWidth = random.randint(10, 30)
        roomHeight = random.randint(10, 30)
        room = [['-' for i in range(roomWidth)] for j in range(roomHeight)]
       
        wallCount = (roomHeight * roomWidth) // 2.3
        xPos = (roomWidth - 1) // 2
        yPos = (roomHeight - 1) // 2
        while wallCount >= 0:
            if room[yPos][xPos] == '-':
                room[yPos][xPos] = ' '
                wallCount -= 1
            randMove = random.randint(1, 4)
            if randMove == 1 and yPos > 2:
                yPos -= 1
            if randMove == 2 and yPos < roomHeight - 3:
                yPos += 1
            if randMove == 3 and xPos > 2:
                xPos -= 1
            if randMove == 4 and xPos < roomWidth - 3:
                xPos += 1
       
        room[roomHeight//2][roomWidth//2] = mainCharacter
       
        if len(roomData) >= 1:
            for i in range(3):
                room[(roomHeight // 2) - 1 + i][0] = 'd'
                enemyGen(roomHeight, roomWidth)
            for i in range(roomWidth//2):
                room[(roomHeight)//2][i] = ' '
             
        roomData[roomNumber] = room
        if roomNumber % 5 == 0:
            bossRoom()
    else:
        room = roomData[roomNumber]
        roomHeight = len(room)
        roomWidth = len(room[0])
        currentCol, currentRow = roomHeight // 2, roomWidth - 2

def bossRoom():
    global boss, bossHealthBar
    bossRoomText = gameOverFont.render("WARNING: BOSS ROOM", True, (255,0,0))
    screen.blit(bossRoomText,bossRoomText.get_rect(center = screen.get_rect().center
    pygame.display.update()
    pygame.time.wait(250)
    
    xPos = (roomHeight - 1) // 2
    yPos = (roomWidth - 1) // 2
    if room[xPos][yPos] == ' ':
        if roomNumber % 10 == 0:
            boss = Boss(xPos, yPos, 200, 30, "not yet")
        else:
            boss = Boss(xPos,yPos,100,20, "not yet")
        bossHealthBar = BossHealthBar(boss, 200, 20, (255, 0, 0))
        if roomNumber not in enemyPositions:
            enemyPositions[roomNumber] = []
        enemyPositions[roomNumber].append(boss)

def doorInteraction():
    global roomData, roomNumber, room, currentCol, currentRow, roomWidth, roomHeight
    if currentCol in range(roomHeight // 2 - 1, roomHeight // 2 + 2) and currentRow in range(roomWidth // 2 - 1, roomWidth // 2 + 2):
        roomNumber -= 1
        if roomNumber >= 1:
            room = roomData[roomNumber]
            roomHeight = len(room)
            roomWidth = len(room[0])
            currentCol, currentRow = roomHeight // 2, roomWidth - 2
    if currentCol in range(roomHeight // 2 - 1, roomHeight // 2 + 2) and currentRow in range(roomWidth // 2 - 1, roomWidth // 2 + 2):
        roomNumber += 1
        dungeonGen(roomNumber)

def handleMovement(event):
    global currentRow, currentCol, movementStack
    currentLocation(mainCharacter)
    newCol, newRow = currentCol, currentRow
    if gameOver == False:
        if event.key == pygame.K_a:
            newRow -= playerSpeed
        if event.key == pygame.K_w:
            newCol -= playerSpeed
        if event.key == pygame.K_s:
            newCol += playerSpeed
        if event.key == pygame.K_d:
            newRow += playerSpeed
        if event.key == pygame.K_e:
            doorInteraction()
        if event.key == pygame.K_f:
            playerInteraction()
        
        if canMove(newCol, newRow):
            updateRoom(newCol, newRow)
        if event.key == pygame.K_u and movementStack:
                newRow,newCol = movementStack.pop()
                updateRoom(newCol, newRow)
                
        movementStack.append((currentRow, currentCol))

def roomClear():
    global count, mainCharacter
    if count < roomNumber:
        count += 1
        for i in range(3):
            room[(roomHeight//2) - 1 + i][roomWidth-2] = ' '
            room[(roomHeight//2) - 1 + i][roomWidth - 3] = ' '
            room[(roomHeight//2) - 1 + i][roomWidth - 1] = 'd'
        for i in range(roomWidth//2):
            room[(roomHeight)//2][roomWidth - 2 - i] = ' '
        if count > 1:
            room[roomHeight//2][0] = mainCharacter
        if roomNumber in enemyPositions:
            for enemy in enemyPositions[roomNumber]:
                room[enemy.y][enemy.x] = 'x'
                screen.blit(basicEnemyImage, (enemy.x * 30, enemy.y * 30))

def enemyBehaviour(enemy):
    global player
    if enemy.attackCooldown == 0:
        if enemyDistance <= 1:
            player.health -= 10
            enemy.attackCooldown = 60
        if enemy.attackCooldown > 0:
            enemy.attackCooldown -= 1
    if enemy.health <= 0:
        enemyPositions[roomNumber].remove(enemy)
        room[enemy.x][enemy.y] = ' '

def displayGameOver():
    game_over_text = gameOverFont.render("Game Over", True, (255,0,0))
    centre = screen.get_rect().center    
    pygame.image.save(screen, 'screenshot.png')
    background_image = Image.open('screenshot.png')
    blurredImage = background_image.filter(ImageFilter.BLUR)
    blurredBackground = pygame.image.fromstring(blurredImage.tobytes(), blurredImage
    screen.fill((0,0,0))
    screen.blit(blurredBackground,(0,0))
    screen.blit(game_over_text,game_over_text.get_rect(center = centre))
 
dungeonGen(1)

def checkLevelUp():
    global player, xpForLevelUp
    xpForLevelUp = 10 * (2 ** (player.level - 1))
    if player.xp >= xpForLevelUp:
        player.health = 100
        player.level += 1
        
def playerInteraction():
    global currentWeapon, enemyPositions, roomNumber
    enemiesToRemove = []
    for enemy in enemyPositions.get(roomNumber, []):
        enemyDistance = calculateDistance(enemy.x, currentRow,enemy.y, currentCol)
        if enemyDistance <= currentWeapon.range:
            enemy.health -= currentWeapon.calculateDamage(player.level)
            displayCommentary(f"Dealt {round(currentWeapon.calculateDamage(player.level))} damage to the {enemy}!")
        if enemy.health <= 0:
            enemiesToRemove.append(enemy)
            player.xp += 10
    itemsToRemove = []
    for item in currentRoomItems:
        if item.x == player.x and item.y == player.y:
            itemsToRemove.append(item)
            applyItem(item)
    for item in itemsToRemove:
        print(itemsToRemove)
        currentRoomItems.remove(item)
        displayCommentary(f"Consumed {item.itemType}")
    
    for enemy in enemiesToRemove:
        enemyPositions[roomNumber].remove(enemy)
        room[enemy.y][enemy.x] = ' '
        displayCommentary("Enemy killed!")
    checkLevelUp()

def switchWeapon(index):
    global currentWeapon, currentWeaponIndex
    if index >= 0 and index < len(playerInventory):
        currentWeaponIndex = index
        currentWeapon = playerInventory[currentWeaponIndex]

def drawXPBar():
    xpForLevelUp = 10 * (2 ** (player.level - 1))
    xpPercentage = (player.xp % xpForLevelUp) / xpForLevelUp
    x = screenWidth - 210
    y = 50
    pygame.draw.rect(screen, (100, 100, 100), (x, y, 200, 10))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, int(200 * xpPercentage), 10))

def drawInventory():
    pygame.draw.rect(screen, (50, 50, 50), (10, screenHeight - 70, len(playerInventory) * 60, 60))
    inventoryX = 10
    inventoryY = screenHeight - 70
    for index, item in enumerate(playerInventory):
        itemImage = itemImages.get(item.name)
        itemX = inventoryX + index * 60
        itemY = inventoryY
        if index == currentWeaponIndex:
            pygame.draw.rect(screen, (255, 0, 0), (itemX, itemY, 60, 60), 2)
        if itemImage:
            screen.blit(itemImage, (itemX, itemY))

def displayCommentary(message):
    global commentaryMessages, commentaryFrameCount
    commentaryMessages.append(message)
    commentaryFrameCount = commentaryDisplayTime
    while len(commentaryMessages) > maxMessages:
        commentaryMessages.pop(0)

def roomTest(room1, room2):
    if len(room1) != len(room2) or len(room1[0]) != len(room2[0]):
        return True
    
    for row in range(len(room1)):
        for col in range(len(room1[0])):
            if room1[row][col] != room2[row][col]:
                return True
    return False

while True:
    player.x, player.y = currentRow, currentCol
    currentLocation(mainCharacter)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            handleMovement(event)
            if event.key == pygame.K_1:
                switchWeapon(0)
            elif event.key == pygame.K_2:
                switchWeapon(1)
            elif event.key == pygame.K_3:
                switchWeapon(2)
    screen.fill((0, 0, 0))
    
    for row in range(len(room)):
        for col in range(len(room[0])):
            if room[row][col] == '-':
                screen.blit(wallImage, (col * tileSize, row * tileSize))
            elif room[row][col] == 'x':
                screen.blit(basicEnemyImage, (col * tileSize, row * tileSize))
    screen.blit(mainCharacter, (currentRow * tileSize, currentCol * tileSize))

    if not gameOver:
        for enemy in enemyPositions.get(roomNumber, []):
            enemyDistance = calculateDistance(enemy.x, currentRow, enemy.y, currentCol)
            enemyBehaviour(enemy)
            if enemyDistance < 2 and playerDoor == False:
                newX, newY = enemy.x, enemy.y
                if enemy.x < currentRow:
                    newX += 1
                elif enemy.x > currentRow:
                    newX -= 1
                if enemy.y < currentCol:
                    newY += 1
                elif enemy.y > currentCol:
                    newY -= 1
                
                if canMove(newY, newX):  
                    room[enemy.y][enemy.x] = ' '
                    enemy.x, enemy.y = newX, newY
           
            room[enemy.y][enemy.x] = 'x'
            screen.blit(basicEnemyImage, (enemy.x * 30, enemy.y * 30))

    if roomNumber > 1:
        screen.blit(doorImage, (0, ((roomHeight-2) // 2 * 30)))
        print("Is room different:", roomTest(roomData[roomNumber - 1], roomData[roomNumber]))
    if player.health <= 0:
        gameOver = True
        displayGameOver()
   
    room_number_text = font.render(f"Room {roomNumber}", True, (255, 255, 255))
    text_rect = room_number_text.get_rect()
    text_rect.center = (screenWidth // 2, screenHeight - 30)
    screen.blit(room_number_text, text_rect)
   
    fullHearts = player.health // 10
    remainingHealth = player.health % 10

    for i in range(fullHearts):
        screen.blit(heartIcon, (10 + i * 30, 10))
    if remainingHealth > 0:
        screen.blit(heartIcon, (10 + fullHearts * 30, 10))
    level_text = font.render(f"Level {player.level}", True, (255, 255, 255))
    screen.blit(level_text, (screenWidth - 160, 10))
    drawXPBar()
    inventoryX = 10
    inventoryY = screenHeight - 70
    drawInventory()

    if len(currentRoomItems) != 0:
        screen.blit(effectPotionImage, (currentRoomItems[0].x * 30, currentRoomItems[0].y * 30))

    if len(currentRoomItems) == 0 and random.random() < 0.25 and itemChance == False:
        item = itemGeneration(random.randint(0, roomWidth - 1), random.randint(0, roomHeight - 1))
        currentRoomItems.append(item)
        itemChance = True

    if roomNumber % 5 == 0:
        bossHealthBar.draw(screen)
        if boss.health > 0:
            screen.blit(bossImage, (boss.x * tileSize, boss.y * tileSize))
            if boss.attackCooldown == 0:
                boss.meleeAttack()
                boss.attackCooldown = 60
            elif boss.attackCooldown > 0:
                boss.attackCooldown -= 1
            boss.move()
        else:
            if boss in enemyPositions[roomNumber]:
                enemyPositions[roomNumber].remove(boss)
    if roomNumber > 1:
        allEnemiesDead = all(enemy.health <= 0 for enemy in enemyPositions.get(roomNumber, []))
        if allEnemiesDead:
            roomClear()
    else:
        roomClear()

    if commentaryFrameCount > 0:
        commentaryFrameCount -= 1
        yOffset = screenHeight - 100
        for i, message in enumerate(commentaryMessages):
            text = commentaryFont.render(message, True, (100, 100, 100))
            screen.blit(text, (screenWidth - 300, yOffset - i * 30))

    pygame.display.update()
    frameRate.tick(60)