import pygame
import sys
import random
import time
import os
pygame.init()
size = width, height = 800, 600
screen = pygame.display.set_mode(size)
#sound1 = pygame.mixer.Sound('step.mp3')
#sound1.play()
clock = pygame.time.Clock()


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


camera = Camera()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
    return image


tile_images = {'wall': [load_image('wall.png'), load_image('wall1.png')],
               'empty': [load_image('grass.png'), load_image('grass2.png')],
               'portal': [load_image('portal.png')]}
keys = 0
player_image = load_image('hero_down1.png')
animation_right = [load_image('hero_right1.png'), load_image('hero_right2.png'),
                   load_image('hero_right1.png'), load_image('hero_right3.png')]
animation_left = [load_image('hero_left1.png'), load_image('hero_left2.png'),
                  load_image('hero_left1.png'), load_image('hero_left3.png')]
animation_up = [load_image('hero_up1.png'), load_image('hero_up2.png'),
                load_image('hero_up1.png'), load_image('hero_up3.png')]
animation_down = [load_image('hero_down1.png'), load_image('hero_down2.png'),
                  load_image('hero_down1.png'), load_image('hero_down3.png')]
tile_width = tile_height = 80
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
keys_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()


def generate_level(level):
    paths = [['x+', 'x+', 'y-', 'y-', 'x-', 'x-', 'y+', 'y+'],
             ['x+', 'y-',  'y-', 'y-', 'y-', 'y+', 'y+', 'y+',
              'y+', 'x-'],
             ['y-', 'y-', 'y-', 'y-', 'y+', 'y+', 'y+', 'y+'],
             ['x+', 'x+', 'y-', 'x+', 'x+', 'y+', 'x+', 'x+',
              'x+', 'x-', 'x-', 'x-', 'y-', 'x-', 'x-', 'y+',
              'x-', 'x-']]
    new_player, new_enemy, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '!':
                Tile('empty', x, y)
                Enemy(x, y, paths[0])
                del paths[0]
            elif level[y][x] == 'K':
                Tile('empty', x, y)
                Key(x, y)
            elif level[y][x] == '*':
                Tile('empty', x, y)
                Tile('portal', x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = random.choice(tile_images[tile_type])
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y)
        self.x = pos_x
        self.y = pos_y

    def update(self):
        global keys
        if keys == 4 and level_map[self.y][self.x] == '*':
            print('next level')
            return False
        return True

    def move_right(self):
        self.x += 1
        self.rect.x += tile_width
        self.image = load_image('None.png')
        self.image = animation_right[0]
        animation_right.append(animation_right[0])
        del animation_right[0]

    def move_left(self):
        self.x -= 1
        self.rect.x -= tile_width
        self.image = load_image('None.png')
        self.image = animation_left[0]
        animation_left.append(animation_left[0])
        del animation_left[0]

    def move_up(self):
        self.y -= 1
        self.rect.y -= tile_height
        self.image = load_image('None.png')
        self.image = animation_up[0]
        animation_up.append(animation_up[0])
        del animation_up[0]

    def move_down(self):
        self.y += 1
        self.rect.y += tile_height
        self.image = load_image('None.png')
        self.image = animation_down[0]
        animation_down.append(animation_down[0])
        del animation_down[0]


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, path):
        super().__init__(enemies_group, all_sprites)
        self.image = random.choice((load_image('enemy2.png'), load_image('enemy3.png'),
                                    load_image('enemy1.png'), load_image('enemy4.png')))
        self.rect = self.image.get_rect().move(tile_width * pos_x + 5, tile_height * pos_y)
        self.x = pos_x
        self.y = pos_y
        self.path = []
        for direction in path:
            for _ in range(10):
                self.path.append(direction)

    def update(self):
        if self.path[0] == 'y+':
            self.rect.y += tile_height * 0.1
            self.y += 0.1
        elif self.path[0] == 'y-':
            self.rect.y -= tile_height * 0.1
            self.y -= 0.1
        elif self.path[0] == 'x-':
            self.rect.x -= tile_width * 0.1
            self.x -= 0.1
        elif self.path[0] == 'x+':
            self.rect.x += tile_height * 0.1
            self.x += 0.1
        self.path.append(self.path[0])
        del self.path[0]
        if player.x == round(self.x) and player.y == round(self.y):
            player.rect.x, player.rect.y = player.rect.x - (player.x - 2) * tile_width,\
                                           player.rect.y - (player.y - 1) * tile_height
            player.x, player.y = 2, 1
            player.image = load_image('hero_down1.png')


class Key(pygame.sprite.Sprite):
    key_image = load_image('key.png')

    def __init__(self, pos_x, pos_y):
        super().__init__(keys_group, all_sprites)
        self.image = self.key_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y + 30)
        self.x = pos_x
        self.y = pos_y
        self.exist = True

    def update(self):
        global keys
        if self.x == player.x and self.y == player.y and self.exist is True:
            self.exist = False
            self.image = load_image('None.png')
            keys += 1


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(intro_text, picture='fon.jpg'):
    fon = pygame.transform.scale(load_image(picture), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 29)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, (34, 255, 0))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(50)

def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


level_map = load_level("map.txt")
player, level_x, level_y = generate_level(level_map)
running = True
start_screen(['', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Лабиринт и знаки', '',
                  'Не касайтесь знаков, соберите все ключи и найдите портал!',
                  'Управление персонажем осуществляется WASD или стрелками клавиатуры'])
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or not player.update():
            terminate()
        if event.type != pygame.KEYDOWN:
            continue
        button = pygame.key.get_pressed()
        if sum(button) > 1:
            continue
        elif button[pygame.K_DOWN] or button[pygame.K_s]:
            if level_map[player.y + 1][player.x] != '#':
                player.move_down()
        elif button[pygame.K_UP] or button[pygame.K_w]:
            if level_map[player.y - 1][player.x] != '#':
                player.move_up()
        elif button[pygame.K_RIGHT] or button[pygame.K_d]:
            if level_map[player.y][player.x + 1] != '#':
                player.move_right()
        elif button[pygame.K_LEFT] or button[pygame.K_a]:
            if level_map[player.y][player.x - 1] != '#':
                player.move_left()
                running = False
    screen.fill((0, 255, 255))
    all_sprites.draw(screen)
    player_group.draw(screen)
    enemies_group.draw(screen)
    # изменяем ракурс камеры
    camera.update(player)
    for el in all_sprites:
        el.update()
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)
    pygame.display.flip()
    clock.tick(60)


def level_2():
    start_screen(['', '', '', '', '', '', '', '', '', '', '', '', 'Игра обманов', '',
                  'Ход должен быть сделан так, чтобы непрерывный ряд фишек соперника', 'оказался «закрыт»'
                  ' фишками игрока с двух сторон. Выигрывает тот,', 'у кого к концу игры больше фишек.',
                                                                    'Желтыми полями подсвечены возможные ходы.'])


    class Board:
        # создание поля
        def __init__(self, width, height):
            self.width = width
            self.height = height
            self.board = [[' '] * width for _ in range(height)]
            self.cell_size = 100

        def render(self):
            for y in range(self.height):
                for x in range(self.width):
                    color = pygame.Color('black')
                    if self.board[y][x] == "X":
                        pygame.draw.circle(screen, (41, 49, 51), (x * self.cell_size + self.cell_size // 2 + 1,
                                                                           y * self.cell_size + self.cell_size // 2 + 1),
                                           self.cell_size // 2 - 2, 0)
                    elif self.board[y][x] == 'O':
                        pygame.draw.circle(screen, (214, 206, 204), (x * self.cell_size + self.cell_size // 2 + 1,
                                                                           y * self.cell_size + self.cell_size // 2 + 1),
                                           self.cell_size // 2 - 2, 0)
                    elif self.board[y][x] == '!' and not game.computer_turn:
                        color = pygame.Color('yellow')
                    pygame.draw.rect(screen, color,
                                     (x * self.cell_size + 2,
                                      y * self.cell_size + 2,
                                    self.cell_size - 2, self.cell_size - 2), 1)
            pygame.draw.rect(screen, (6, 139, 54), (0, 0, 801, 801), 5)

        def get_cell(self, xy):
            x, y = xy[0], xy[1]
            cell_x = x // self.cell_size
            cell_y = y // self.cell_size
            return cell_x, cell_y


    class Othello(Board):
        def __init__(self, width, height):
            super().__init__(width, height)
            self.width, self.height = width, height
            tiles = ['X', 'O']
            random.shuffle(tiles)
            self.player_tile, self.computer_tile = tiles
            self.showHints = False
            self.computer_turn = self.computer_tile is "X"
            self.board[3][4] = "O"
            self.board[3][3] = "X"
            self.board[4][4] = "X"
            self.board[4][3] = "O"

        def isOnBoard(self, x, y):
            return 0 <= x <= 7 and 0 <= y <= 7

        def isOnCorner(self, x, y):
            return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)

        def isValidMove(self, tile, xstart, ystart):
            if not self.isOnBoard(xstart, ystart):
                return False
            if self.board[xstart][ystart] not in [' ', '!']:
                return False
            self.board[xstart][ystart] = tile
            if tile == 'X':
                otherTile = 'O'
            else:
                otherTile = 'X'
            tilesToFlip = []
            for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
                x, y = xstart, ystart
                x += xdirection
                y += ydirection
                if self.isOnBoard(x, y) and self.board[x][y] == otherTile:
                    x += xdirection
                    y += ydirection
                    if not self.isOnBoard(x, y):
                        continue
                    while self.board[x][y] == otherTile:
                        x += xdirection
                        y += ydirection
                        if not self.isOnBoard(x, y):
                            break
                    if not self.isOnBoard(x, y):
                        continue
                    if self.board[x][y] == tile:
                        while True:
                            x -= xdirection
                            y -= ydirection
                            if x == xstart and y == ystart:
                                break
                            tilesToFlip.append([x, y])
            self.board[xstart][ystart] = ' '
            if len(tilesToFlip) == 0:
                return False
            return tilesToFlip

        def getBoardWithValidMoves(self):
            hints_board = self.board.copy()
            for x, y in self.getValidMoves(self.player_tile):
                hints_board[x][y] = '!'
            return hints_board

        def getValidMoves(self, tile):
            validMoves = []
            for x in range(8):
                for y in range(8):
                    if self.isValidMove(tile, x, y):
                        validMoves.append([x, y])
            return validMoves

        def play_again(self):
            global game
            game = Othello(self.width, self.height)

        def getScoreOfBoard(self, board):
            score_list = self.linear(board)
            return score_list.count(self.computer_tile), score_list.count(self.player_tile)

        def linear(self, some_list):
            if type(some_list) != list:
                return [some_list]
            if not some_list:
                return []
            else:
                return self.linear(some_list[:-1]) + self.linear(some_list[-1])

        def plan_move(self, plan_board, tile, xstart, ystart):
            tilesToFlip = self.isValidMove(tile, xstart, ystart)
            if tilesToFlip == False:
                return False
            plan_board[xstart][ystart] = tile
            for x, y in tilesToFlip:
                plan_board[x][y] = tile
            return plan_board

        def getComputerMove(self):
            bestMove = False
            possibleMoves = self.getValidMoves(self.computer_tile)
            random.shuffle(possibleMoves)
            for x, y in possibleMoves:
                if self.isOnCorner(x, y):
                    self.computer_turn = False
                    self.board = self.plan_move(self.board, self.computer_tile, x, y)
                    return True
            bestScore = -1
            for x, y in possibleMoves:
                plan_board = self.copy_board()
                self.plan_move(plan_board, self.computer_tile, x, y)
                score = self.getScoreOfBoard(plan_board)[0]
                if score > bestScore:
                    bestMove = [x, y]
                    bestScore = score
            self.computer_turn = False
            if 0 in self.getScoreOfBoard(game.board) or self.linear(self.board).count(' ') +\
                    self.linear(self.board).count('!') == 0:
                return False
            if bestMove is False:
                return True
            self.board = self.plan_move(self.board, self.computer_tile, bestMove[0], bestMove[1])
            return True

        def copy_board(self):
            some_list = []
            for i in self.board:
                other_list = []
                for j in i:
                    other_list.append(j)
                some_list.append(other_list)
            return some_list

        def on_click(self, cell):
            if self.plan_move(self.copy_board(), self.player_tile, cell[1], cell[0]) is False:
                return
            self.board = self.plan_move(self.copy_board(), self.player_tile, cell[1], cell[0])
            self.render()
            self.computer_turn = True

        def get_click(self, mouse_pos):
            cell = self.get_cell(mouse_pos)
            self.on_click(cell)

    size = 801, 801
    screen = pygame.display.set_mode(size)
    game = Othello(8, 8)
    if game.computer_turn:
        game.getComputerMove()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game.computer_turn:
                    if 0 in game.getScoreOfBoard(game.board) or game.linear(game.board).count(' ')\
                            + game.linear(game.board).count('!') == 0:
                        running = False
                        break
                    game.get_click(event.pos)
        screen.fill((6, 139, 54))
        computer_board = game.copy_board()
        game.board = game.getBoardWithValidMoves()
        if game.linear(game.board).count('!') == 0:
            game.computer_turn = True
        if game.computer_turn:
            game.board = computer_board
        game.render()
        pygame.display.flip()
        if game.computer_turn:
            time.sleep(0.5)
            running = game.getComputerMove()
    pygame.quit()
    player_score = game.getScoreOfBoard(game.board)[1]
    computer_score = game.getScoreOfBoard(game.board)[0]
    if computer_score > player_score:
        start_screen([('Победа компьютера на', str(computer_score - player_score), 'очка')], 'end.jpg')
        level_2()
    elif computer_score < player_score:
        start_screen([('Победа игрока на',  str(player_score - computer_score), 'очка')], 'end.jpg')
        terminate()
    else:
        start_screen(['Ничья'], 'end.jpg')
        level_2()


level_2()
