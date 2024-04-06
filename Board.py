
from queue import PriorityQueue
from collections import deque
import pygame
from Hider import *
from Seeker import *

clock = pygame.time.Clock()

class Board:
    def __init__(self, filename, widthScreen, lengthScreen):
        pygame.init()
        self.filename = filename
        self.board = []
        self.obstacles = []
        self.width = 0
        self.length = 0
        self.widthScreen = widthScreen
        self.lengthScreen = lengthScreen
        self.screen = None
        self.tile_size = 30  # Kích thước của mỗi ô trên bảng

        self.colors = {
            0: (255, 255, 255),  # Ô trống
            1: (0, 0, 0),        # Tường
            2: (0, 255, 0),      # Hider
            3: (255, 0, 0),      # Seeker
        }

        pygame.display.set_caption("Hide and Seek Game") # Đặt tiêu đề cho cửa sổ khi chạy

    def updatePos(self, frontier, newState, value):
        newX, newY = newState.getPos()
        if (newX == frontier[0] and newY == frontier[1]):
            self.board[newX][newY] = 0

        if (self.board[frontier[0]][frontier[1]] == 2):
            self.board[frontier[0]][frontier[1]] = 0
        else: self.board[frontier[0]][frontier[1]] = 4 # cập nhật lại ô vừa đi qua về lại ô trắng - đường đi - đã đi qua rồi
        self.board[newX][newY] = value #cập nhật tọa độ mới cho newState

    def setScreen(self):
        self.screen = pygame.display.set_mode((self.widthScreen, self.lengthScreen))
    def getInfo(self):
        return self.width, self.length
    
    def getMap(self):
        return self.board
    
    def load_board(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            dimensions = lines[0].split()
            self.length = int(dimensions[0])
            self.width = int(dimensions[1])
            self.board = [[int(num) for num in line.split()] for line in lines[1:int(dimensions[0])+1]] # Mảng 2 chiều. Dimensions[0]+1 là dòng cuối của board.
            for line in lines[int(dimensions[0])+1:]:
                obstacles_info = line.split()
                obstacle = [int(obstacles_info[0]), int(obstacles_info[1]),
                            int(obstacles_info[2]), int(obstacles_info[3])]
                self.obstacles.append(obstacle)
            for obstacle in self.obstacles:
                top, left, bottom, right = obstacle
                for i in range(top, bottom+1):
                    for j in range(left, right+1):
                        self.board[i][j] = 1
    
    def getHiderPos_list(self):
        pos = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == 2:
                    h = Hider("hider", i, j)
                    pos.append(h)
        return pos

    def getSeekerPos(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == 3:
                    return i, j

    def copy(self, startX, startY, endX, endY):
        new_board = []
        for i in range(startX, endX + 1):
            row = []
            for j in range(startY, endY + 1):
                row.append(self.board[i][j])
            new_board.append(row)
        return new_board
    

    def drawBoard(self, cnt):
        with open(f"output{cnt}.txt", 'w') as fs:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    fs.write(str(self.board[i][j]) + ' ')

                fs.write('\n')

            fs.write("\n\n")
            
    def draw_board(self, seeker, level, score, timing):
        clock.tick(60)
        self.screen.fill((255, 253, 218))  # Màu nền vàng nhạt
        if self.length <= 10:
            self.tile_size = 40
            marginL = 150
            marginT = 50
        elif self.length <= 25:
            self.tile_size = 30
            marginL = 350
            marginT = 100
        else:
            self.tile_size = 13
            marginL = 350
            marginT = 50
        
        for y, row in enumerate(self.board):
            for x, tile in enumerate(row):
                color = self.colors.get(tile, (255, 255, 255)) # Trong trường hợp không tìm thấy tile thì trả về (255, 255, 255)
                pygame.draw.rect(self.screen, color, (marginL + (x+1)*self.tile_size, (y+6)*self.tile_size - marginT, self.tile_size, self.tile_size))
            
        seeker.draw_score_and_time(self.screen, score, timing)
        if (level == 3):
            listHider = self.getHiderPos_list()
            for hide in listHider:
                hide.drawVisionHider(self)
        seeker.draw_vision(self)

        # Vẽ đường kẻ giữa các ô
        for y, row in enumerate(self.board):
            for x, tile in enumerate(row):
                color = self.colors.get(tile, (255, 255, 255))
                pygame.draw.rect(self.screen, (0, 0, 0), (marginL + (x+1)*self.tile_size, (y+6)*self.tile_size - marginT, self.tile_size, self.tile_size), 1)

        # Vẽ đường kẻ giữa hàng và cột cuối cùng
        pygame.display.flip() # Cập nhật màn hình 