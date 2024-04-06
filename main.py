import random
import sys
from queue import PriorityQueue
from collections import deque
import pygame
import time
from Board import *
from Hider import *
from Seeker import *


WIDTH = 700
LENGTH = 1400

pygame.init()
screen = pygame.display.set_mode((LENGTH, WIDTH))
pygame.display.set_caption("Game Menu")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# Font
font = pygame.font.Font(None, 36)

# Trạng thái menu
menu_items = ["Play", "Exit"]
level_items = ["Level 1", "Level 2", "Level 3", "Back"]
current_item = 0

# Vẽ menu
def draw_menu():
    screen.fill(WHITE)
    for i, item in enumerate(menu_items):
        text = font.render(item, True, RED if i == current_item else GRAY)
        text_rect = text.get_rect(center=(LENGTH // 2, WIDTH // 2 + i * 100 - 75))
        screen.blit(text, text_rect)
    pygame.display.flip()

# Hàm chọn menu
def select_menu():
    global current_item
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                current_item = (current_item - 1) % len(menu_items)
            elif event.key == pygame.K_DOWN:
                current_item = (current_item + 1) % len(menu_items)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if current_item == 0:
                    return show_level_selection() #hiển thị giao diện chọn level
                elif current_item == 1:
                    pygame.quit()
                    sys.exit()
    return None, None

# Hàm chọn level
def show_level_selection():
    current_level = 0
    while True:
        screen.fill(WHITE)
        for i, item in enumerate(level_items):
            text = font.render(item, True, RED if i == current_level else GRAY)
            text_rect = text.get_rect(center=(LENGTH // 2, WIDTH // 2 + i * 100 - 150))
            screen.blit(text, text_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_level = (current_level - 1) % len(level_items)
                elif event.key == pygame.K_DOWN:
                    current_level = (current_level + 1) % len(level_items)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if current_level == len(level_items) - 1:
                        return None, None  # Trả về None nếu chọn "Back"
                    return current_level, show_map_selection()

# Hàm chọn map sau khi chọn level
def show_map_selection():
    map_items = ["10x25", "25x25", "25x25", "50x50", "50x50", "Back"]
    current_map = 0
    while True:
        screen.fill(WHITE)
        for i, item in enumerate(map_items):
            text = font.render(item, True, RED if i == current_map else GRAY)
            text_rect = text.get_rect(center=(LENGTH // 2 + (i - 3) * 200 + 100, WIDTH // 2 - 50))
            screen.blit(text, text_rect)

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_map = (current_map - 1) % len(map_items)
                elif event.key == pygame.K_RIGHT:
                    current_map = (current_map + 1) % len(map_items)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if current_map == len(map_items) - 1:
                        return None  # Trả về None nếu chọn "Back"
                    return current_map

def updateHiderFound(list_hider_pos, hider):
    for h in list_hider_pos:
        if h.getPos() == hider.getPos():
            list_hider_pos.remove(h)
            return list_hider_pos
    #không có hider cần tìm trong list_hider_pos
    return list_hider_pos

def aStarSearch(seeker, hider, memoryBoard):
    index = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
    seeker_2 = seeker
    # Dùng A* để tìm HIDER
    step = 0
    queue = PriorityQueue()
    explored_set = []
    parent = {} # lưu node cha của nó
    parent[seeker_2] = None
    queue.put(seeker_2)
    explored_set.append(seeker_2.getPos())


    while not queue.empty():
        frontier = queue.get()
        if (frontier.isCatch(hider) == True):
            path = []
            current = frontier
            while current.getPos() != seeker_2.getPos():
                path.append(current)
                current = parent[current]
            
            return path.pop()

            
        for i in range(len(index)):
            newState = frontier.update(board, index[i][0], index[i][1], hider.getPos()[0], hider.getPos()[1])
            if (newState == None):
                continue
            try:
                pos = explored_set.index(newState.getPos())
            except ValueError: # newState chưa có trong explored set:
                newState.setVision(memoryBoard)
                queue.put(newState)
                explored_set.append(newState.getPos())
                parent[newState] = frontier


    return None

def newSolve(seeker, board, level):
    step = 0
    score = 0
    timing = 0

    list_hider_pos = board.getHiderPos_list()
    memoryBoard = board    
    nextBestMove = seeker
    previousMoves = deque()
    board.draw_board(seeker, level, score, timing)
    first = False

    nextBestMove.setVision(memoryBoard)
    memoryBoard = nextBestMove.updateMemoryBoard(memoryBoard)
    memoryBoard.draw_board(nextBestMove, level, score, timing)
    time.sleep(0.3)

    while len(list_hider_pos) > 0:
        step += 1
        score -= 1
        timing += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, timing
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return score, timing
            
        frontier = nextBestMove
    

        hiderExist = frontier.hiderFound(list_hider_pos, memoryBoard)
        if hiderExist[0]:
            rowDist = frontier.getPos()[0] - hiderExist[1].getPos()[0]
            colDist = frontier.getPos()[1] - hiderExist[1].getPos()[1]
            if abs(rowDist) <= 1 and abs(colDist) <= 1:
                nextBestMove = Seeker('Seeker', hiderExist[1].getPos()[0], hiderExist[1].getPos()[1])
            else:
                nextBestMove = aStarSearch(frontier, hiderExist[1], memoryBoard)
            
        else:       

            #Announce:
            if step % 5 == 0 and step != 0:
                list_announce = []
                for hider in list_hider_pos:
                    aX, aY = hider.announce(memoryBoard)
                    list_announce.append(Hider("Hider", aX, aY))
                    
                    #cập nhật giá trị trong memoryBoard:
                    if memoryBoard.getMap()[aX][aY] != 1:
                        memoryBoard.getMap()[aX][aY] = 5
                time.sleep(0.3)

                frontier.setVision(memoryBoard)
                announExist = frontier.announceFound(list_announce, memoryBoard)
                if announExist[0]:
                    rowDist = frontier.getPos()[0] - announExist[1].getPos()[0]
                    colDist = frontier.getPos()[1] - announExist[1].getPos()[1]
                    if abs(rowDist) <= 1 and abs(colDist) <= 1:
                        nextBestMove = Seeker("Seeker", announExist[1].getPos()[0], announExist[1].getPos()[1])
                    else:
                        #lấy bước đi đầu tiên trong đường đi từ frontier -> announce
                        nextBestMove = aStarSearch(frontier, announExist[1], memoryBoard)

                else:
                    next = frontier.getNextBestMove(memoryBoard, previousMoves)
                    nextBestMove = next[0]
                    if nextBestMove == None: # không còn ô nào có thể đi nữa
                        return score, timing
                #cập nhật lại các ô = 5 của announce về lại = 0
                for an in list_announce:
                    if memoryBoard.getMap()[an.getPos()[0]][an.getPos()[1]] == 5:
                        memoryBoard.getMap()[an.getPos()[0]][an.getPos()[1]] = 0
            
            else:
                next = frontier.getNextBestMove(memoryBoard, previousMoves)
                nextBestMove = next[0]
                if nextBestMove == None: # không còn ô nào có thể đi nữa
                    return score, timing
        
        

        if not next[1]:
            previousMoves.append(frontier)

        
        for hider in list_hider_pos:
            if (nextBestMove.isCatch(hider)):
                score += 20
                memoryBoard.getMap()[nextBestMove.getPos()[0]][nextBestMove.getPos()[1]] = 4 #cập nhật lại sau khi tìm thấy 1 hider -> cho hider đó bằng ô trống đã đi qua
                list_hider_pos = updateHiderFound(list_hider_pos, hider)

        nextBestMove.setVision(memoryBoard)
        memoryBoard = nextBestMove.updateMemoryBoard(memoryBoard)
        memoryBoard.draw_board(nextBestMove, level, score, timing)
        time.sleep(0.3)



        if level == 3:
            directions = [-1, 0, 1]
            for h in range(len(list_hider_pos)):
                if h >= len(list_hider_pos): h -= 1

                hider_X, hider_Y = list_hider_pos[h].getPos()
                dx = random.choice(directions)
                dy = random.choice(directions)
                while (hider_X + dx < 0) or (hider_X + dx >= memoryBoard.getInfo()[1]) or (hider_Y + dy < 0) or (hider_Y + dy >= memoryBoard.getInfo()[0]) or (memoryBoard.getMap()[hider_X + dx][hider_Y + dy] == 1):
                    dx = random.choice(directions)
                    dy = random.choice(directions)
                list_hider_pos[h].setPosition(hider_X + dx, hider_Y + dy)

                memoryBoard.updatePos((hider_X, hider_Y), list_hider_pos[h], 2)

                if (nextBestMove.isCatch(list_hider_pos[h])):
                    score += 20
                    memoryBoard.getMap()[nextBestMove.getPos()[0]][frontier.getPos()[1]] = 4 #cập nhật lại sau khi tìm thấy 1 hider -> cho hider đó bằng ô trống đã đi qua
                    list_hider_pos = updateHiderFound(list_hider_pos, list_hider_pos[h])          


            nextBestMove.setVision(memoryBoard)
            memoryBoard = nextBestMove.updateMemoryBoard(memoryBoard)
            memoryBoard.draw_board(nextBestMove, level, score, timing)
            time.sleep(0.3)
    
    return score, timing
       
##########################################################################################################
##########################################################################################################


if __name__ == "__main__":
    choose_map = -1
    choose_level = -1
    
    while True:
        while True:
            choose_level, choose_map = select_menu()
            draw_menu()
            if choose_level != -1 and choose_level != None and choose_map != -1 and choose_map != None:
                break
                
        
        choose_level += 1
        map_text = "map" + str(choose_map)
        if choose_level == 1:
            map_text += "_Lv1.txt"
        else:
            map_text += ".txt"
        
        board = Board(map_text, LENGTH, WIDTH)
        board.load_board()
        board.setScreen()
        board.screen.fill((255, 253, 218))
        pygame.display.flip()
        seeker = Seeker("seeker", board.getSeekerPos()[0], board.getSeekerPos()[1])
        seeker.setVision(board)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = False

            score, timing = newSolve(seeker, board, choose_level)
            running = False

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        running = False
            board.screen.fill((255, 253, 218))  # Màu nền vàng nhạt
            pygame.draw.rect(board.screen, (130, 161, 222), (400, 200, 600, 200))
            font = pygame.font.Font(None, 48)
            score_text = font.render(f"Score: {score}", True, (0, 0, 0))
            time_text = font.render(f"Time: {timing}", True, (0, 0, 0))
            board.screen.blit(score_text, (450, 235))
            board.screen.blit(time_text, (450, 320))
            pygame.display.flip()