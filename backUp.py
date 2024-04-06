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
level_items = ["Level 1", "Level 2", "Level 3"]
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

# Giao diện chọn level
def show_level_selection():
    current_level = 0
    while True:
        screen.fill(WHITE)
        for i, item in enumerate(level_items):
            text = font.render(item, True, RED if i == current_level else GRAY)
            text_rect = text.get_rect(center=(LENGTH // 2, WIDTH // 2 + i * 100 - 75))
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
                    return current_level, show_map_selection()
# Hàm chọn map sau khi chọn level
def show_map_selection():
    map_items = ["12x10", "20x20", "20x20", "50x50", "50x50"]
    current_map = 0
    while True:
        screen.fill(WHITE)
        for i, item in enumerate(map_items):
            text = font.render(item, True, RED if i == current_map else GRAY)
            text_rect = text.get_rect(center=(LENGTH // 2 + (i - 2) * 200, WIDTH // 2 - 50))
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
                    return current_map + 1

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
    #print("vị trí hider trong vision: ", hider.getPos())
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
        ##print (str(preX) + " " + str(preY) + " - " + str(frontier.getPos()))
        if (frontier.isCatch(hider) == True):
            #print("Đã tìm được đường đi từ Frontier -> hider = A*")
            path = []
            current = frontier
            while current.getPos() != seeker_2.getPos():
                path.append(current)
                current = parent[current]
            
            #print("Truy ngược đường đi từ currentPos -> hider = A*")
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


# NEW SOLVE
def newSolve(seeker, board, level):
    list_hider_pos = board.getHiderPos_list()
    count = len(list_hider_pos)
    index = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
    directions = [-1, 0, 1]
    memoryBoard = board    
    nextBestMove = seeker
    pointer = seeker
    previousMoves = deque() # lưu các ô đã đi qua
    board.draw_board(seeker, level)
    first = False
    
    #các biến dùng cho level 3:
    list_announce = []
    stepS = 0
    cnt = 0


    #loop while
    while len(list_hider_pos) > 0:
        step = 0
        checkHiderFound = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return
            
        frontier = nextBestMove
        if first == True:
            seeker.time_elapsed += 1
            seeker.score -= 1
        first = True

        # kiểm tra HIDER có trong VISION không
        print("Hider có trong Vision không? : ", frontier.hiderFound(list_hider_pos, memoryBoard)[0])
        if frontier.hiderFound(list_hider_pos, memoryBoard)[0]:
            checkHiderFound = True
            pointer = seeker
            seeker_2 = frontier
            hider = frontier.hiderFound(list_hider_pos, memoryBoard)[1]
            print("vị trí hider trong vision: ", hider.getPos())
            # Dùng A* để tìm HIDER
            step = 0
            queue = PriorityQueue()
            explored_set = []
            parent = {} # lưu node cha của nó
            parent[seeker_2] = None
            queue.put(seeker_2)
            explored_set.append(seeker_2.getPos())
            hiderX, hiderY = hider.getPos()
            preX, preY = seeker_2.getPos()
            
             #tìm vị trí announce trong list_hider:
            for i in range(len(list_hider_pos)):
                if list_hider_pos[i].getPos() == hider.getPos():
                    vitri = i
                    break
            print("TÌM Đường đi từ Frontier -> hider = A*")
            while not queue.empty():
                frontier = queue.get()
                #print (str(preX) + " " + str(preY) + " - " + str(frontier.getPos()))
                if (frontier.isCatch(list_hider_pos[vitri]) == True):
                    print("Đã tìm được đường đi từ Frontier -> hider = A*")
                    path = []
                    randomFound = False #tìm thấy ngẫu nhiên trong đường đi tới đích = False
                    current = frontier
                    while current.getPos() != seeker_2.getPos():
                        path.append(current)
                        current = parent[current]
                    path.append(current)
                    
                    print("Truy ngược đường đi từ currentPos -> hider = A*")
                    while path:
                        currentPos = path.pop()
                        memoryBoard = currentPos.updateMemoryBoard(memoryBoard)
                        previousMoves.append(currentPos)
                        currentPos.time_elapsed = pointer.time_elapsed + 1
                        currentPos.score = pointer.score - 1
                        memoryBoard.updatePos((preX, preY), currentPos, 3)
                        memoryBoard.draw_board(currentPos, level)
                        time.sleep(0.3)

                        if (level == 3):
                            print("Hider di chuyển ngẫu nhiên tỏng khi CurrentPos di chuyển đến hider")
                            for h in range(len(list_hider_pos)):
                                if (currentPos.getPos() == list_hider_pos[h].getPos()):
                                    randomFound = True
                                    print("currentPos tìm thấy hider ngẫu nhiên trong khi di chuyển đến")
                                    list_hider_pos = updateHiderFound(list_hider_pos, list_hider_pos[h])
                                    pointer.score += 20
                                    currentPos.score = pointer.score
                                    break
                    
                                hider_X, hider_Y = list_hider_pos[h].getPos()
                                dx = random.choice(directions)
                                dy = random.choice(directions)
                                while (hider_X + dx < 0) or (hider_X + dx >= memoryBoard.getInfo()[1]) or (hider_Y + dy < 0) or (hider_Y + dy >= memoryBoard.getInfo()[0]) or (memoryBoard.getMap()[hider_X + dx][hider_Y + dy] == 1):
                                    dx = random.choice(directions)
                                    dy = random.choice(directions)
                                list_hider_pos[h].setPosition(hider_X + dx, hider_Y + dy)
                                print(str(hider_X) + ", " + str(hider_Y) + " - " + str(list_hider_pos[h].getPos()))
                                memoryBoard.updatePos((hider_X, hider_Y), list_hider_pos[h], 2)

                            memoryBoard.draw_board(currentPos, level)
                            time.sleep(0.3)
                            if randomFound == True: break

                        preX, preY = currentPos.getPos()

                        # cnt += 1
                        # memoryBoard.drawBoard(cnt)

                    if randomFound == True:
                        break
                    elif (frontier.isCatch(list_hider_pos[vitri]) == True):
                        print("Frontier đã chạm được đến hider = A*")
                        memoryBoard.getMap()[frontier.getPos()[0]][frontier.getPos()[1]] = 4 #cập nhật lại sau khi tìm thấy 1 hider -> cho hider đó bằng ô trống đã đi qua
                        list_hider_pos = updateHiderFound(list_hider_pos, list_hider_pos[vitri])
                        pointer.score += 20
                        currentPos.score = pointer.score
                        break
                    else:
                        print("currentPos đã đi đến -> hider đi chỗ khác -> không bắt được")
                        # frontier = currentPos
                        break
                print("Tạo mới newState trong A*")
                for i in range(len(index)):
                    newState = frontier.update(board, index[i][0], index[i][1], list_hider_pos[vitri].getPos()[0], list_hider_pos[vitri].getPos()[1])
                    if (newState == None):
                        continue
                    try:
                        pos = explored_set.index(newState.getPos())
                    except ValueError: # newState chưa có trong explored set:
                        newState.setVision(memoryBoard)
                        queue.put(newState)
                        explored_set.append(newState.getPos())
                        parent[newState] = frontier
                        #print(explored_set)
                step += 1
            
                
        # tránh việc sau khi tìm hết nhưng game vẫn hoạt động thêm 1 step
        if (len(list_hider_pos) == 0): return
        seeker = pointer
        
        # if checkHiderFound == False:
        print("Tạo ra nextBestMove -> tìm kiếm map")
        # next nhận 2 biến là ô di chuyển kế tiếp với biến xác nhận có backTrack
        next = frontier.getNextBestMove(memoryBoard, previousMoves)
        nextBestMove = next[0]
        if nextBestMove == None: # không còn ô nào có thể đi nữa
            return
        nextBestMove.time_elapsed = seeker.time_elapsed + 1
        nextBestMove.score = seeker.score - 1
        
        if (level == 3): backTracked = next[1]
        else: backTracked = next[1]       

        print("Update MemoryBoard")
        memoryBoard = nextBestMove.updateMemoryBoard(memoryBoard)
        memoryBoard.draw_board(nextBestMove, level)
        time.sleep(0.3)

        # Nếu move tiếp theo không phải backTrack thì cho move hiện tại vào (để tránh bị lặp)
        if backTracked == 0:
            previousMoves.append(frontier)

        #tính năng cho level 3:
        if (level == 3):
            if checkHiderFound == False:
                print("CẬP NHẬT ANNOUNCE")
                list_announce = []
                for hider in list_hider_pos:
                    if (frontier.isCatch(hider) == True):
                        print("Frontier tìm thấy hider ngẫu nhiên trên đường đi")
                        list_hider_pos = updateHiderFound(list_hider_pos, hider)
                        memoryBoard.getMap()[hider.getPos()[0]][hider.getPos()[1]] = 4
                        seeker.score += 20
                        nextBestMove.score = seeker.score

                    hider_X, hider_Y = hider.getPos()
                    dx = random.choice(directions)
                    dy = random.choice(directions)
                    while (hider_X + dx < 0) or (hider_X + dx >= memoryBoard.getInfo()[1]) or (hider_Y + dy < 0) or (hider_Y + dy >= memoryBoard.getInfo()[0]) or (memoryBoard.getMap()[hider_X + dx][hider_Y + dy] == 1) or (memoryBoard.getMap()[hider_X + dx][hider_Y + dy] == 2):
                        dx = random.choice(directions)
                        dy = random.choice(directions)
                    hider.setPosition(hider_X + dx, hider_Y + dy)

                    print("HIDER DI CHUYỂN TRONG KHI PHÁT ANNOUNCE: " + str(hider_X) + ", " + str(hider_Y) + " - " + str(hider.getPos()))
                    memoryBoard.updatePos((hider_X, hider_Y), hider, 2)
                    nextBestMove.time_elapsed = seeker.time_elapsed + 1
                    nextBestMove.score = seeker.score - 1
                    memoryBoard.draw_board(nextBestMove, level)
                    if stepS % 5 == 0 and stepS != 0:
                        print("CÁC HIDER ANNOUNCE")
                        xH, yH = hider.announce(memoryBoard)

                        #cho vị trí announce trong bảng memoryBoard = 5
                        if memoryBoard.getMap()[xH][yH] != 1:
                            memoryBoard.getMap()[xH][yH] = 5
                        # if(xH <= xA + 3 and xH >= xA - 3 and xH >= 0 and xH < memoryBoard.getInfo()[1] and yH <= yA + 3 and yH >= 0 and yH >= 0 and yH < memoryBoard.getInfo()[0]):
                        list_announce.append(Hider("hider", xH, yH))
                    time.sleep(0.3)
                if list_announce:
                    print("LIST ANNOUNCE: ")
                    for a in list_announce:
                        print(a.getPos())
            stepS += 1
            #Cập nhật lại các ô announce = 5 -> = 0
            
            for announ in list_announce:
                if memoryBoard.getMap()[announ.getPos()[0]][announ.getPos()[1]] != 1:
                    memoryBoard.getMap()[announ.getPos()[0]][announ.getPos()[1]] = 0
        
        else:
            if checkHiderFound == False:
                if stepS %  5 == 0 and stepS != 0:
                    print("CẬP NHẬT ANNOUNCE")
                    list_announce = []
                    for hider in list_hider_pos:
                        print("CÁC HIDER ANNOUNCE")
                        xH, yH = hider.announce(memoryBoard)

                        #cho vị trí announce trong bảng memoryBoard = 5
                        if memoryBoard.getMap()[xH][yH] != 1:
                            memoryBoard.getMap()[xH][yH] = 5
                        # if(xH <= xA + 3 and xH >= xA - 3 and xH >= 0 and xH < memoryBoard.getInfo()[1] and yH <= yA + 3 and yH >= 0 and yH >= 0 and yH < memoryBoard.getInfo()[0]):
                        list_announce.append(Hider("hider", xH, yH))
                    time.sleep(0.3)

                    frontier.setVision(memoryBoard)
                    print("ANNOUNCE CO TRONG VISION? : ", frontier.announceFound(list_announce, memoryBoard)[0])
                    if frontier.announceFound(list_announce, memoryBoard)[0]:
                        print("ANNOUNCE")
                        pointer = seeker
                        seeker_2 = frontier
                        hiderA = frontier.announceFound(list_announce, memoryBoard)[1]
                        # Dùng A* để tìm Announce
                        step = 0
                        queue = PriorityQueue()
                        explored_set = []
                        parent = {} # lưu node cha của nó
                        parent[seeker_2] = None
                        queue.put(seeker_2)
                        explored_set.append(seeker_2.getPos())
                        hiderX, hiderY = hiderA.getPos()
                        preX, preY = seeker_2.getPos()
                        print (str(preX) + " " + str(preY) + " - " + str(frontier.getPos()))

                        #tìm vị trí announce trong list_announce:
                        for i in range(len(list_announce)):
                            if list_announce[i].getPos() == hiderA.getPos():
                                vitri = i
                                break
                        print("Tìm đường đi từ Frontier -> Announce = A*")
                        while not queue.empty():
                            
                            frontier = queue.get()

                            if (frontier.isCatch(hiderA) == True):
                                print("Đã tìm được đường đi từ Frontier -> Announce = A*")
                                path = []
                                # randomFound = False # trạng thái tìm ngẫu nhiên được trogn khi đang đi theo đường A*
                                current = frontier
                                while current.getPos() != seeker_2.getPos():
                                    path.append(current)
                                    current = parent[current]
                                path.append(current)
                                
                                print("Truy ngược đường đi từ CurrentPos -> Announce = A*")
                                while path:
                                    currentPos = path.pop()
                                    memoryBoard = currentPos.updateMemoryBoard(memoryBoard)
                                    previousMoves.append(currentPos)
                                    currentPos.time_elapsed = pointer.time_elapsed + 1
                                    currentPos.score = pointer.score - 1
                                    memoryBoard.updatePos((preX, preY), currentPos, 3)
                                    memoryBoard.draw_board(currentPos, level)
                                    time.sleep(0.3)

                                    preX, preY = currentPos.getPos()

                                memoryBoard.getMap()[frontier.getPos()[0]][frontier.getPos()[1]] = 4 #cập nhật lại sau khi tìm thấy 1 hider -> cho hider đó bằng ô trống đã đi qua

                                print("Frontier đã đi đến vị trí Announce")
                                nextBestMove = currentPos
                                break
                            print("Tạo mới newState trong A* cho Announce")
                            for i in range(len(index)):
                                newState = frontier.update(board, index[i][0], index[i][1], hiderX, hiderY)
                                if (newState == None):
                                    continue
                                try:
                                    pos = explored_set.index(newState.getPos())
                                except ValueError: # newState chưa có trong explored set:
                                    newState.setVision(memoryBoard)
                                    queue.put(newState)
                                    explored_set.append(newState.getPos())
                                    parent[newState] = frontier
            stepS += 1
            for announ in list_announce:
                if memoryBoard.getMap()[announ.getPos()[0]][announ.getPos()[1]] != 1:
                    memoryBoard.getMap()[announ.getPos()[0]][announ.getPos()[1]] = 0
            # cnt += 1
            # memoryBoard.drawBoard(cnt)

       

##########################################################################################################
##########################################################################################################


if __name__ == "__main__":
    choose_map = -1
    choose_level = -1
    
    while True:
        choose_level, choose_map = select_menu()
        draw_menu()
        if choose_level != -1 and choose_level != None and choose_map != -1 and choose_map != None:
            break
            
    
    map_text = "map" + str(choose_map) + ".txt"
    choose_level += 1
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

        #tham số cuối cùng là level : 1, 2, 3
        newSolve(seeker, board, choose_level)
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
        score_text = font.render(f"Score: {seeker.score}", True, (0, 0, 0))
        time_text = font.render(f"Time: {seeker.time_elapsed}", True, (0, 0, 0))
        board.screen.blit(score_text, (450, 235))
        board.screen.blit(time_text, (450, 320))
        pygame.display.flip()