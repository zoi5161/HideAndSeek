import random
import pygame
from Seeker import processVision

class Position:
    def __init__(self, x, y):
        self.x = x; #x là hàng
        self.y = y; #y là cột

    def getPosition(self):
        return self.x, self.y

class Hider:
    def __init__(self, name, idx_X, idx_Y):
        self.name = name
        self.position = Position(idx_X, idx_Y)
        self.isCaught = False

    def getPos(self):
        return self.position.getPosition()

    def announce(self, memoryBoard): #width vs length là chiều dài, rộng của bảng trò chơi cho trước.
        #Không gian mẫu các tham số ngẫu nhiên để thay đổi vị trí:
        directions = [-3, -2, -1, 1, 2, 3]

        dx = random.choice(directions)
        dy = random.choice(directions)

        x, y = self.position.getPosition()
        #kiểm tra xem vị trí mới có nằm ngoài bảng trò chơi hay không:
        while (x + dx < 0) or (x + dx >= memoryBoard.getInfo()[1]) or (y + dy < 0) or (y + dy >= memoryBoard.getInfo()[0]):
            dx = random.choice(directions)
            dy = random.choice(directions)
            
        width, length = memoryBoard.getInfo()
        if length <= 10:
            marginL = 150
            marginT = 50
        elif length <= 25:
            marginL = 350
            marginT = 100
        else:
            marginL = 350  
            marginT = 50
        pygame.draw.rect(memoryBoard.screen, (236, 103, 172), (marginL + (y + dy + 1) * memoryBoard.tile_size, (x + dx + 6) * memoryBoard.tile_size - marginT, memoryBoard.tile_size, memoryBoard.tile_size))
        pygame.display.flip() # Cập nhật màn hình 
        return x + dx, y + dy
    def getPosition(self):
        return self.position.getPosition()
    def setPosition(self, newX, newY):
        self.position = Position(newX, newY)

    def setVision(self, memoryBoard):
        # Set bán kính nhìn được của HIDER (2 ô)
        startX = self.position.getPosition()[0] - 2     #start là điểm trên-trái
        startY = self.position.getPosition()[1] - 2
        endX = self.position.getPosition()[0] + 2       #end là điểm dưới-phải
        endY = self.position.getPosition()[1] + 2

        #kiểm tra tính hợp lệ giới hạn tầm nhìn:
        if startX < 0: startX = 0
        if endX >= memoryBoard.getInfo()[1]: endX = memoryBoard.getInfo()[1] -1
        if startY < 0: startY = 0
        if endY >= memoryBoard.getInfo()[0]:endY = memoryBoard.getInfo()[0] -1

        self.vision = memoryBoard.copy(startX, startY, endX, endY)

        hiderInVisionX = 2
        hiderInVisionY = 2

        if startX == 0:
            hiderInVisionX = len(self.vision) - 1 - 2
        if startY == 0:
            hiderInVisionY = len(self.vision[0]) - 1 - 2

        self.vision[hiderInVisionX][hiderInVisionY] = 2

        self.vision = processVision(self.vision, hiderInVisionX, hiderInVisionY)

    def drawVisionHider(self, memoryBoard):
        self.visionOfHider = []
        self.setVision(memoryBoard)
        visionHide = self.vision
        out = False
        
        i = 0
        for row in visionHide:
            j = 0
            for column in range(len(row)):
                if row[column] == 2:
                    x = i
                    y = j
                    out = True
                    break
                j += 1
            if out:
                break
            i += 1
        xH, yH = self.getPos()
        
        i = 0
        for row in visionHide:
            j = 0
            for column in range(len(row)):
                if (0 <= xH - (x-i) < memoryBoard.getInfo()[1]) and (0 <= yH - (y-j) < memoryBoard.getInfo()[0]):
                    if (row[column] == 0 or row[column] == 4) and memoryBoard.getMap()[xH - (x - i)][yH - (y - j)] != 1:
                        self.visionOfHider.append((xH - (x - i), yH - (y - j)))
                j += 1
            i += 1

        visionH = self.visionOfHider
        
        width, length = memoryBoard.getInfo()

        if length <= 10:
            marginL = 150
            marginT = 50
        elif length <= 25:
            marginL = 350
            marginT = 100
        else:
            marginL = 350  
            marginT = 50
        for x, y in visionH:
            pygame.draw.rect(memoryBoard.screen, (167, 137, 194), (marginL + (y + 1) * memoryBoard.tile_size, (x + 6) * memoryBoard.tile_size - marginT, memoryBoard.tile_size, memoryBoard.tile_size))
        xH, yH = self.getPos()
        pygame.draw.rect(memoryBoard.screen, (0, 255, 0), (marginL + (yH + 1) * memoryBoard.tile_size, (xH + 6) * memoryBoard.tile_size - marginT, memoryBoard.tile_size, memoryBoard.tile_size))