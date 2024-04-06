import math
import copy
import pygame


class Position:
    def __init__(self, x, y):
        self.x = x; #x là hàng
        self.y = y; #y là cột

    def getPosition(self):
        return self.x, self.y
    

class Seeker:
    def __init__(self, name, idx_X, idx_Y):
        self.name = name
        self.position = Position(idx_X, idx_Y)
        self.g = 0
        self.h = 0
        self.score = 0
        self.time_elapsed = 0

    def setPos(self, u, v):
        self.position = Position(u, v)
    
    def getPos(self):
        return self.position.getPosition()
    
    def move(self, newX, newY):   
        self.position = Position(newX, newY)
    def resetGH(self):
        self.g = 0
        self.h = 0
    
    def heuristicFunc(self, x, y):
        seekX, seekY = self.position.getPosition()

        return math.sqrt(abs(seekX - x)**2 + abs(seekY - y)**2) 
    
    def update(self, Board, idx, idy, hiderX, hiderY):
        newState = copy.deepcopy(self)
        
        x, y = self.position.getPosition()
        if (x + idx < 0 or x + idx >= Board.getInfo()[1]):
            return None
        elif (y + idy < 0 or y + idy >= Board.getInfo()[0]):
            return None
        elif Board.getMap()[x + idx][y + idy] == 1:
            return None
        
        newState.move(x + idx, y + idy)

        newState.h = newState.heuristicFunc(hiderX, hiderY)
        newState.g = newState.g + 1
        return newState

 
    def isCatch(self, Hider):
        x, y = self.position.getPosition()
        if x == Hider.getPosition()[0] and y == Hider.getPosition()[1]:
            return True
        return False
    
    def __lt__(self, other):
        return self.g + self.h < other.g + other.h
    

    def draw_score_and_time(self, screen, score, timing):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        time_text = font.render(f"Time: {timing}", True, (0, 0, 0))
        screen.blit(score_text, (20, 20))  # Vẽ điểm số ở vị trí (20, 20)
        screen.blit(time_text, (150, 20))   # Vẽ thời gian ở vị trí (100, 20)

    def setVision(self, memoryBoard):
        # Set bán kính nhìn được của SEEKER (3 ô)
        startX = self.position.getPosition()[0] - 3     #start là điểm trên-trái
        startY = self.position.getPosition()[1] - 3
        endX = self.position.getPosition()[0] + 3       #end là điểm dưới-phải
        endY = self.position.getPosition()[1] + 3

        #kiểm tra tính hợp lệ giới hạn tầm nhìn:
        if startX < 0: startX = 0
        if endX >= memoryBoard.getInfo()[1]: endX = memoryBoard.getInfo()[1] -1
        if startY < 0: startY = 0
        if endY >= memoryBoard.getInfo()[0]:endY = memoryBoard.getInfo()[0] -1

        self.vision = memoryBoard.copy(startX, startY, endX, endY)

        seekerInVisionX = 3
        seekerInVisionY = 3

        if startX == 0:
            seekerInVisionX = len(self.vision) - 1 - 3
        if startY == 0:
            seekerInVisionY = len(self.vision[0]) - 1 - 3

        self.vision[seekerInVisionX][seekerInVisionY] = 3

        self.vision = processVision(self.vision, seekerInVisionX, seekerInVisionY)
        

    def newHeuristic(self): # Hàm này chỉ dùng khi chưa thấy HIDER trong VISION
        heuristic = 0
        #Đọc các giá trị trong VISION
        for i in range(len(self.vision)):
            for j in range(len(self.vision[0])):
                if self.vision[i][j] == 0:
                    heuristic += 1  # Hàm heuristic tính bằng số lượng ô '0'

        return heuristic
        


    # Hàm kiểm tra trong bán kính VISION có HIDER không
    def announceFound(self, list_announce, memoryBoard):
        self.setVision(memoryBoard)
        announceInVision = [-1, -1]
        seekerInVision = [-1, -1]

        for i in range(len(self.vision)):
            for j in range(len(self.vision[i])):
                if (self.vision[i][j] == 5) and announceInVision == [-1, -1]:
                    announceInVision[0] = i
                    announceInVision[1] = j
                
                elif self.vision[i][j] == 3:
                    seekerInVision[0] = i
                    seekerInVision[1] = j

                if announceInVision != [-1, -1] and seekerInVision != [-1, -1]:
                    break

        rowDistance = seekerInVision[0] - announceInVision[0]
        colDistance = seekerInVision[1] - announceInVision[1]

        boardSeeker = self.position.getPosition()

        for hider in list_announce:
            currentHider = hider.getPosition()

            if currentHider[0] == boardSeeker[0] - rowDistance and currentHider[1] == boardSeeker[1] - colDistance:
                return True, hider
            
        return False, None
    def hiderFound(self, list_hider_pos, memoryBoard):

        hiderInVision = [-1, -1]
        seekerInVision = [-1, -1]

        for i in range(len(self.vision)):
            for j in range(len(self.vision[i])):
                if (self.vision[i][j] == 2) and hiderInVision == [-1, -1]:
                    hiderInVision[0] = i
                    hiderInVision[1] = j
                
                elif self.vision[i][j] == 3:
                    seekerInVision[0] = i
                    seekerInVision[1] = j

                if hiderInVision != [-1, -1] and seekerInVision != [-1, -1]:
                    break

        rowDistance = seekerInVision[0] - hiderInVision[0]
        colDistance = seekerInVision[1] - hiderInVision[1]

        boardSeeker = self.position.getPosition()

        for hider in list_hider_pos:
            currentHider = hider.getPosition()

            if currentHider[0] == boardSeeker[0] - rowDistance and currentHider[1] == boardSeeker[1] - colDistance:
                return True, hider
            
        return False, None
        
    def getvision(self):
        return self.vision

    def updateMemoryBoard(self, memoryBoard):
        startX = self.position.getPosition()[0] - 3
        startY = self.position.getPosition()[1] - 3

        width, length = memoryBoard.getInfo()

        if startX < 0:
            startX = 0
        elif startX >= length:
            startX = length - 1

        if startY < 0:
            startY = 0
        elif startY >= width:
            startY = width - 1

        for i in range(len(self.vision)):
            for j in range(len(self.vision[0])):
                if 0 <= startX + i < len(memoryBoard.getMap()) and 0 <= startY + j < len(memoryBoard.getMap()[0]):
                    if (memoryBoard.getMap()[startX + i][startY + j] == 5):
                        continue
                    if (memoryBoard.getMap()[startX + i][startY + j] == 0 and self.vision[i][j] == 0) or (memoryBoard.getMap()[startX + i][startY + j] == 3):   # Nếu ô trong memoryBoard chưa được thấy
                        memoryBoard.getMap()[startX + i][startY + j] = 4    # set giá trị ô đó = 4

        # update vị trí hiện tại của Seeker      
        memoryBoard.getMap()[self.position.getPosition()[0]][self.position.getPosition()[1]] = 3        
                          
        return memoryBoard

    def draw_vision(self, memoryBoard):
        self.visionOfSeeker = []
        self.setVision(memoryBoard)
        visionSeek = self.vision
        out = False
        
        i = 0
        for row in visionSeek:
            j = 0
            for column in range(len(row)):
                if row[column] == 3:
                    x = i
                    y = j
                    out = True
                    break
                j += 1
            if out:
                break
            i += 1
        xS, yS = self.getPos()
        
        i = 0
        for row in visionSeek:
            j = 0
            for column in range(len(row)):
                if (0 <= xS - (x-i) < memoryBoard.getInfo()[1]) and (0 <= yS - (y-j) < memoryBoard.getInfo()[0]):
                    if row[column] == 4 and memoryBoard.getMap()[xS - (x - i)][yS - (y - j)] != 1:
                        self.visionOfSeeker.append((xS - (x - i), yS - (y - j)))
                j += 1
            i += 1

        
        visionS = self.visionOfSeeker
        
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

        for x, y in visionS:
            pygame.draw.rect(memoryBoard.screen, (79, 138, 224), (marginL + (y + 1) * memoryBoard.tile_size, (x + 6) * memoryBoard.tile_size - marginT, memoryBoard.tile_size, memoryBoard.tile_size))
        xS, yS = self.getPos()
        pygame.draw.rect(memoryBoard.screen, (255, 0, 0), (marginL + (yS + 1) * memoryBoard.tile_size, (xS + 6) * memoryBoard.tile_size - marginT, memoryBoard.tile_size, memoryBoard.tile_size))
    
  
    def getNextBestMove(self, memoryBoard, previousMoves):
        x, y = self.position.getPosition()
        width, length = memoryBoard.getInfo()

        neighbors = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
        bestScore = 0
        backTracked = 0 # đánh dấu backTrack

        for i in neighbors:
            idx, idy = i[0], i[1]

            if x + idx < 0 or x + idx >= length:
                continue
            elif y + idy < 0 or y + idy >= width:
                continue
            elif memoryBoard.getMap()[x+idx][y+idy] == 1:
                continue

            newState = Seeker(self.name, self.position.getPosition()[0] + idx, self.position.getPosition()[1] + idy)
            newState.setVision(memoryBoard)

            stateScore = newState.newHeuristic()
            if stateScore > bestScore:
                nextBestMove = newState
                bestScore = stateScore


        # Nếu VISION của tất cả ô xung quanh không thấy được ô '0'
        if bestScore == 0:
            backTracked = 1 # đánh dấu có backTrack
            try:
                nextBestMove = previousMoves.pop()
            except:
                nextBestMove = None
        return nextBestMove, backTracked

def processVision(vision, seekerRow, seekerColumn):
    width = len(vision)
    length = len(vision[0])

    # Xử lý từng ô riêng lẻ
    for row in range(width):    
        for col in range(length):
            if vision[row][col] == 1:
                # Ô đang xét lệch theo chiều dọc nhiều so với Seeker
                if abs(row - seekerRow) > abs(col - seekerColumn): 
                    i = row
                    if row < seekerRow: # Ô ở phía trên Seeker
                        while i >= 0:
                            vision[i][col] = 1
                            i -= 1    

                        # Nếu ô ở ngay trên Seeker
                        if row > 0  and row == seekerRow - 1 and col == seekerColumn:
                            i = row - 1
                            while i >= 0:
                                if col > 0: vision[i][col-1] = 1
                                if col < length - 1: vision[i][col+1] = 1
                                i -= 1


                    elif row > seekerRow:   # Ô ở dưới Seeker
                        while i < width:
                            vision[i][col] = 1
                            i += 1

                        # Nếu ô ở ngay dưới Seeker
                        if row < width - 1 and row == seekerRow + 1 and col == seekerColumn:
                            i = row + 1
                            while i < width:
                                if col > 0: vision[i][col-1] = 1
                                if col < length - 1: vision[i][col+1] = 1
                                i += 1


                # Ô đang xét lệch theo chiều ngang nhiều so với Seeker
                elif abs(row - seekerRow) < abs(col - seekerColumn):
                    j = col
                    if col < seekerColumn:  # Ô bên trái Seeker
                        while j >= 0:
                            vision[row][j] = 1
                            j -= 1

                        # Nếu ô ngay trái Seeker
                        if col > 0 and col == seekerColumn - 1 and row == seekerRow:
                            j = col - 1
                            while j >= 0:
                                if row > 0: vision[row-1][j] = 1
                                if row < width - 1: vision[row+1][j] = 1
                                j -= 1


                    elif col > seekerColumn:  # Ô bên phải Seeker
                        while j < length:
                            vision[row][j] = 1
                            j += 1

                        # Nếu ô ngay phải Seeker
                        if col < length - 1 and col == seekerColumn + 1 and row == seekerRow:
                            j = col + 1
                            while j < length:
                                if row > 0: vision[row-1][j] = 1
                                if row < width - 1: vision[row+1][j] = 1
                                j += 1



                # Ô đang xét nằm trên đường chéo với Seeker
                else:
                    i, j = row, col
                    if row < seekerRow and col < seekerColumn:  # Đường chéo góc trên-trái
                        while i >= 0 and j >= 0:
                            vision[i][j] = 1

                            if i != row and i > 0: vision[i-1][j] = 1
                            if j != col and j > 0: vision[i][j-1] = 1

                            i -= 1
                            j -= 1

                    elif row < seekerRow and col > seekerColumn:  # Đường chéo góc trên-phải
                        while i >= 0 and j < length:
                            vision[i][j] = 1

                            if i != row and i > 0: vision[i-1][j] = 1
                            if j != col and j < length - 1: vision[i][j+1] = 1

                            i -= 1
                            j += 1

                    elif row > seekerRow and col > seekerColumn:   # Đường chéo góc dưới-phải
                        while i < width and j < length:
                            vision[i][j] = 1

                            if i != row and i < width - 1: vision[i+1][j] = 1
                            if j != col and j < length - 1: vision[i][j+1] = 1

                            i += 1
                            j += 1

                    elif row > seekerRow and col < seekerColumn:    # Đường chéo góc dưới-trái
                        while i < width and j >= 0:
                            vision[i][j] = 1

                            if i != row and i < width - 1: vision[i+1][j] = 1
                            if j != col and j > 0: vision[i][j-1] = 1

                            i += 1
                            j -= 1


    # Xử lý các ô bị che bởi 2 ô kề nhau
    for i in range(width//2):   # Loop để đảm bảo bao phủ toàn bộ Vision
        for row in range(width):
            for col in range(length):
                if vision[row][col] == 1:
                    if 0 < row < seekerRow: # 2 ô đang xét nằm trên Seeker
                        if col < seekerColumn and col < length-1:  # 2 ô nằm bên trái so với Seeker
                            if vision[row][col+1] == 1: # 2 ô đang xét nằm ngang
                                vision[row-1][col] = 1

                            if col > 0 and vision[row-1][col] == 1: # 2 ô đang xét nằm dọc
                                vision[row-1][col-1] = 1

                            if col > 0 and vision[row+1][col] == 1:
                                vision[row][col-1] = 1

                        if col > seekerColumn and col < length-1: # 2 ô nằm bên phải Seeker
                            if vision[row][col+1] == 1: # 2 ô nằm ngang
                                vision[row-1][col+1] = 1

                            if vision[row-1][col] == 1: # 2 ô nằm dọc
                                vision[row-1][col+1] = 1

                            if vision[row+1][col] == 1:
                                vision[row][col+1] = 1


                    elif row > seekerRow and row < width - 1:   # 2 ô đang xét nằm dưới Seeker, tương tự như trên
                        if col < seekerColumn and col < length-1:
                            if vision[row][col+1] == 1:
                                vision[row+1][col] = 1

                            if col > 0 and vision[row+1][col] == 1:
                                vision[row+1][col-1] = 1

                            if col > 0 and vision[row-1][col] == 1:
                                vision[row][col-1] = 1

                        elif col > seekerColumn and col < length-1:
                            if vision[row][col+1] == 1:
                                vision[row+1][col+1] = 1

                            if vision[row+1][col] == 1:
                                vision[row+1][col+1] = 1

                            if vision[row-1][col] == 1:
                                vision[row][col+1] = 1

    return vision