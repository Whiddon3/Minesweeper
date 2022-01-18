import pygame
from pygame.locals import *
import time
import random 
import sys, getopt

class Grid:
    def __init__(self, rows, cols, width, height, win, mine_count = 0):
        self.rows = rows
        self.cols = cols
        self.board = [[0 for i in range(cols)] for j in range(rows)]
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.win = win
        
        # (row, col)
        self.selected = None
        self.cells = [[Cell(i, j, width, height, self.board[i][j], rows) for j in range(cols)] for i in range(rows)]
        self.started = False
        self.completed = False
        if (self.mine_count == 0): self.mine_count = (self.rows * self.cols) // 6
        self.place_mines()

    def end_game(self, result):
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].GameOver = True 
        self.completed = True

    def start_game(self):
        row = self.selected[0]
        col = self.selected[1]
        count = 0
        if (self.cells[row][col].isMine == True):
            while count < 1:
                y = random.randint(0, self.rows-1)
                x = random.randint(0, self.cols-1)
                if (self.cells[y][x].isMine == False): 
                    self.cells[y][x].isMine = True
                    count += 1
            self.cells[row][col].isMine = False
        self.check_neighbors((0,0))
        self.dig_initial((row, col))
    
    def dig(self):
        r = self.selected[0]
        c = self.selected[1]
        self.cells[r][c].isHidden = False
        if not(self.cells[r][c].isMine):
            self.dig_neighbors((r,c))
        else:
            self.cells[r][c].isTriggered = True


    # Digs extra neighbors if they are not near a mine
    def dig_neighbors(self, pos):
        r = pos[0]
        c = pos[1]
        if (r < self.rows and c < self.cols and r >= 0 and c >= 0):
            if (self.cells[r][c].isMine == False and self.cells[r][c].isHidden == True):
                self.cells[r][c].isHidden = False
                if (self.cells[r][c].value == 0):
                    self.dig_neighbors((r+1, c))
                    self.dig_neighbors((r+1, c+1))
                    self.dig_neighbors((r, c+1))
                    self.dig_neighbors((r-1, c))
                    self.dig_neighbors((r-1, c-1))
                    self.dig_neighbors((r, c-1))
                    self.dig_neighbors((r-1, c+1))
                    self.dig_neighbors((r+1, c-1))


    def flag(self):
        r = self.selected[0]
        c = self.selected[1]
        if (self.cells[r][c].isHidden == True):
            self.cells[r][c].isFlagged = not(self.cells[r][c].isFlagged)
    
            

    def dig_initial(self, pos):
        r = pos[0]
        c = pos[1]
        if (r < self.rows and c < self.cols and r >= 0 and c >= 0):
            if (self.cells[r][c].isMine == False and self.cells[r][c].isHidden == True):
                self.cells[r][c].isHidden = False
                if (self.cells[r][c].value == 0 or self.started == False):
                    self.started = True
                    self.dig_initial((r+1, c))
                    self.dig_initial((r+1, c+1))
                    self.dig_initial((r, c+1))
                    self.dig_initial((r-1, c))
                    self.dig_initial((r-1, c-1))
                    self.dig_initial((r, c-1))
                    self.dig_initial((r-1, c+1))
                    self.dig_initial((r+1, c-1))

    def check_neighbors(self, pos):
        r = pos[0]
        c = pos[1]
        if (r < self.rows and c < self.cols):
            if r > 0 and self.cells[r-1][c].isMine == True:
                self.cells[r][c].value += 1
            # Check down    
            if r < self.rows-1  and self.cells[r+1][c].isMine == True:
                self.cells[r][c].value += 1
            # Check left
            if c > 0 and self.cells[r][c-1].isMine == True:
                self.cells[r][c].value += 1
            # Check right
            if c < self.cols-1 and self.cells[r][c+1].isMine == True:
                self.cells[r][c].value += 1
            # Check top-left    
            if r > 0 and c > 0 and self.cells[r-1][c-1].isMine == True:
                self.cells[r][c].value += 1
            # Check top-right
            if r > 0 and c < self.cols-1 and self.cells[r-1][c+1].isMine == True:
                self.cells[r][c].value += 1
            # Check below-left  
            if r < self.rows-1 and c > 0 and self.cells[r+1][c-1].isMine == True:
                self.cells[r][c].value += 1
            # Check below-right
            if r < self.rows-1 and c < self.cols-1 and self.cells[r+1][c+1].isMine == True:
                self.cells[r][c].value += 1
            if (c == self.cols-1): 
                r += 1
                c = 0
            else:
                c += 1
            self.check_neighbors((r, c))

    def place_mines(self):
        count = 0
        while count < self.mine_count:
            y = random.randint(0, self.rows-1)
            x = random.randint(0, self.cols-1)
            if (self.cells[y][x].isMine == 0): 
                self.cells[y][x].isMine = True
                count += 1

    def draw(self):
        # Draw Grid Lines
        gap = self.width / self.rows
        for i in range(self.rows+1):
            if i == 0 or i == self.rows:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(self.win, (0,0,0), (0, i*gap), (self.width, i*gap), thick)
            pygame.draw.line(self.win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)


        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].draw(self.win)

    def click(self, pos):
        if (pos[0] < self.width and pos[1] < self.height):
            gap = self.width / self.rows
            r = pos[0] // gap
            c = pos[1] // gap
            return (r, c)
        return None

    def select(self, col, row):
        # Reset all the other cells if they are selected
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].selected = False
        self.cells[row][col].selected = True
        self.selected = (row, col) 

    def is_won(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if (self.cells[i][j].isMine == False and self.cells[i][j].isHidden == True): return False
        return True

    def is_lost(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if (self.cells[i][j].isMine == True and self.cells[i][j].isHidden == False): return True
        return False

    def is_solved(self, pos):
        r = pos[0]
        c = pos[1]
        if self.cells[r+1][c].isHidden == True:
            return False
        if self.cells[r+1][c+1].isHidden == True:
            return False
        if self.cells[r][c+1].isHidden == True:
            return False
        if self.cells[r-1][c].isHidden == True:
            return False
        if self.cells[r-1][c-1].isHidden == True:
            return False
        if self.cells[r][c-1].isHidden == True:
            return False
        if self.cells[r-1][c+1].isHidden == True:
            return False        
        if self.cells[r+1][c-1].isHidden == True:
            return False              

    def is_valid(self, pos):
        r = pos[0]
        c = pos[1]
        if r < self.rows and c < self.cols and r >= 0 and c >= 0:
            return True
        return False
        



class Cell:
    def __init__(self, row, col, width, height, value, rows):
        self.row = row
        self.col = col
        self.width = width 
        self.height = height
        self.value = 0
        self.revealed = 0
        self.rows = rows
        self.isMine = False
        self.isHidden = True
        self.isFlagged = False
        self.isTriggered = False
        self.selected = False
        self.GameOver = False
        self.colors = {
            0 : (255,255,255),
            1 : (0,0,255),
            2 : (0,255,0),
            3 : (255,0,0),
            4 : (0,0,139),
            5 : (150,75,0),
            6 : (0,255,255),
            7 : (0,0,0),
            8 : (128,128,128)
        }

    def draw(self, win):
        fnt = pygame.font.SysFont("arial", 40)

        gap = self.width / self.rows
        x = self.col * gap
        y = self.row * gap


        color = self.colors[self.value]

        if self.isMine == 1 and self.isTriggered:
            mine = pygame.image.load('assets/triggered_mine.png')
            mine = pygame.transform.scale(mine, (gap, gap))
            #text = fnt.render(str("B"), 1,  color)
            win.blit(mine, (x, y))
        elif self.isMine == 1 and self.GameOver:
            mine = pygame.image.load('assets/mine.png')
            mine = pygame.transform.scale(mine, (gap, gap))
            #text = fnt.render(str("B"), 1,  color)
            win.blit(mine, (x, y))
        elif self.isFlagged == 1:
            flag = pygame.image.load('assets/flag.png')
            flag = pygame.transform.scale(flag, (gap-10, gap-10))
            win.blit(flag, (x+5, y+5))
        elif self.isHidden == False and self.value > 0:           
            text = fnt.render(str(self.value), 1, color)
            win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))
        elif self.isHidden == True:
            empty_block = pygame.image.load('assets/empty-block.png')
            empty_block = pygame.transform.scale(empty_block, (gap, gap))
            text = fnt.render(str(self.value), 1, color)
            win.blit(empty_block, (x, y))

        if (self.selected):
            color = (255,0,0)
            pygame.draw.rect(win, color, pygame.Rect(x, y, gap, gap),  2)


def format_time(secs):
    sec = secs % 60
    minute = secs // 60
    hour = minute // 60
    time_string = " " + str(minute) + ":" + str(sec).zfill(2)
    return time_string

def redraw_window(win, board, time):
    win.fill((128,128,128))
    # Draw time
    fnt = pygame.font.SysFont("arial", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
    win.blit(text, (10, 550))
    # Draw grid and board
    if board.is_lost():
        text = fnt.render("You Lost!", 1, (255,0,0))
        win.blit(text, (350, 550))
    elif board.is_won():
        text = fnt.render("You Won!", 1, (0,255,0))
        win.blit(text, (350, 550))
    board.draw()


def main(argv):
    if (len(sys.argv) != 3): sys.exit("Program needs two arguments: (num rows) (num cols)")
    if not(sys.argv[1].isdigit and sys.argv[2].isdigit): sys.exit("Program needs two arguments: (num rows) (num cols)")
    rows = int(sys.argv[1])
    cols = int(sys.argv[2])
    pygame.init()
    win = pygame.display.set_mode((540,600))
    board = Grid(rows, cols, 540, 540, win)
    pygame.display.set_caption = 'Minesweeper'
    key = None
    run = True
    end = False
    start_time = time.time()
    while (run):
        round_time = round(time.time() - start_time)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                selected_cell = board.click(pos)
                if selected_cell:
                    board.select(int(selected_cell[0]), int(selected_cell[1]))
                    key = None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if board.selected:
                    board.flag()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not(board.started) and board.selected:
                    board.start_game()
                elif board.selected:
                    board.dig()

        if (board.is_lost()):
            board.end_game(0)
        elif (board.is_won()):
            board.end_game(1)
        if not(end):
            redraw_window(win, board, round_time)
            pygame.display.update()
        if (board.completed):
            end = True


if __name__ == "__main__":
    main(sys.argv[1:])
    pygame.quit()

