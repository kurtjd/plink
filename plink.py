#------------------------------------------------------------------------------
# Name:           Plink
# Version:        v1
#
# Author:         Kurtis Dinelle
#
# Created:        20/05/2013
# Last Updated:   24/07/2021
# Copyright:      (c) Dinelle 2013
# License:        MIT
#------------------------------------------------------------------------------

import pygame
import sys
import os
import pygame.locals as pygamevars

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Display constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
WINDOW_TITLE = 'Plink'
BG_COLOR = BLACK
FPSCOUNT_POS = {'x': 30, 'y': 23}
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
PADDLE_OFFSET = 25  # The space between the paddle and the side of the screen
PADDLE_BUFFER = 5  # THe space between the paddle and the barriers
PADDLE_Y = (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2)  # Centers the paddle
# Starting points for paddles
PADDLE1_POS = {'x': (SCREEN_WIDTH - PADDLE_WIDTH - PADDLE_OFFSET),
               'y': PADDLE_Y}
PADDLE2_POS = {'x': PADDLE_OFFSET, 'y': PADDLE_Y}
# Ball properties
BALL_SIZE = 20
BALL_POS = {'x': ((SCREEN_WIDTH / 2) - (BALL_SIZE / 2)),
            'y': ((SCREEN_HEIGHT / 2) - (BALL_SIZE / 2))}
BARRIER_WIDTH = SCREEN_WIDTH - 20
BARRIER_HEIGHT = 25
BARRIER_OFFSET = 10
BARRIER_X = 10
COURT_TOP = BARRIER_HEIGHT + BARRIER_OFFSET
COURT_BOTTOM = SCREEN_HEIGHT - BARRIER_HEIGHT - BARRIER_OFFSET
NET_SQUARE_SIZE = 23
NET_BUFFER = 16
NET_POS = {'x': float(SCREEN_WIDTH / 2) - float(NET_SQUARE_SIZE / 2),
           'y': COURT_TOP}
DIGIT_BLOCK_SIZE = 20
SCOREBOX_X_BUF = 100
SCOREBOX_Y_BUF = 20
P1_SCOREPOS = {'x': (SCREEN_WIDTH / 2) + SCOREBOX_X_BUF,
               'y': COURT_TOP + SCOREBOX_Y_BUF}
P2_SCOREPOS = {'x': (SCREEN_WIDTH / 2) - (DIGIT_BLOCK_SIZE * 3) -
                     SCOREBOX_X_BUF,
               'y': COURT_TOP + SCOREBOX_Y_BUF}
MENU_TITLE = 'PONG'
TITLE_BLOCK_SIZE = 20
LETTER_LENGTH = 4
LETTER_HEIGHT = 6
TITLE_POS = {'x': ((SCREEN_WIDTH / 2) - (TITLE_BLOCK_SIZE *
                  ((LETTER_LENGTH * 2) + 1))),
             'y': 100}
OPTIONS_BUFFER = 5
OPTIONS_BLOCK_SIZE = 3
OPTIONS_POS = {'x': (SCREEN_WIDTH / 2) - 50,
               'y': (TITLE_POS['y'] + 200)}
MENU_PNTR_SIZE = 7


# Game states
MENU = 1
TRANS = 1.5
PLAY = 2
PAUSED = 3
GAMEOVER = 4
WIN = 5


# System constants
FPS = 70


# Classes
class TextBox:
    """Simple class for creating and modifying text boxes."""
    def __init__(self, text_value, font_size, font_color,
                 position, font_type=None):
        """text_value: text to have in the text box
           font_size: the size of the text
           font_type: font to use; if none specified use default
           font_color: color of the text as a tuple
           positon is a tuple containing x and y coordinates"""
        self.font = pygame.font.Font(font_type, font_size)
        self.color = font_color
        self.position = position
        self.set_value(text_value)

    def set_value(self, text_value):
        """Set's the textbox's value, then displays it back on the screen."""
        text = self.font.render(text_value, True, self.color)
        self.text_rect = text.get_rect(center=self.position)
        screen.blit(text, self.text_rect)


class FPSCounter:
    """Creates a new FPS Counter."""
    GAP = 25

    def __init__(self, xpos, ypos):
        """xpos: x position on screen
           ypos: y position on screen"""
        self.fpslabel = TextBox('FPS: ', 16, BLACK, (xpos, ypos))
        # Text box that is constantly updated with the game's frame rate.
        # xpos + 25 puts the counter right next to the word 'FPS: '
        self.fps_counter = TextBox(None, 16, BLACK, (xpos + self.GAP, ypos))

    def update(self):
        """Updates the fps counter text field and redraws it."""
        #screen.fill(BLACK, self.fps_counter.text_rect)
        # Get clock fps, truncate decimals, then convert to string
        self.fps_counter.set_value(str(int(fps_clock.get_fps())))
        # Kina a nasty hack, I shouldn't have to set the value every frame.
        # Will add method that simply re-renders the text
        self.fpslabel.set_value('FPS: ')


class Paddle:
    """Class detailing how a pong paddle looks and functions."""
    def __init__(self, posx, posy, maxspeed=12):
        self.maxspeed = maxspeed
        # Simply invert movespeed to change direction
        self.movespeed = self.maxspeed
        self.moving = 0  # Decides if the paddle should move or not
        self.moveup = 0
        self.movedown = 0
        # Create the rect for the paddle then draw it to the screen
        self.paddle_rect = pygame.Rect(posx, posy, PADDLE_WIDTH, PADDLE_HEIGHT)

    def move(self):
        """Moves the paddle."""
        # Stop paddle from moving out of bounds
        if self.paddle_rect.y + self.movespeed <= COURT_TOP:
            self.paddle_rect.y = COURT_TOP + PADDLE_BUFFER
        elif (self.paddle_rect.y + self.movespeed +
              PADDLE_HEIGHT >= COURT_BOTTOM):
            self.paddle_rect.y = COURT_BOTTOM - PADDLE_HEIGHT - PADDLE_BUFFER
        else:
            self.paddle_rect.move_ip(0, self.movespeed)

    def update(self):
        """Draw the paddle."""
        if self.moving:
            self.move()
        screen.fill(WHITE, self.paddle_rect)


class Ball:
    """Class describing ball properties and behavior."""
    Y_SPEED = 5
    ACCELERATION = 1

    def __init__(self):
        self.origspeed = 15
        self.maxspeed = self.origspeed
        self.movex = -self.maxspeed
        self.movey = self.Y_SPEED
        self.ball_rect = pygame.Rect(BALL_POS['x'], BALL_POS['y'],
                                     BALL_SIZE, BALL_SIZE)

    def reset(self, side):
        """Put's the ball in center and resets speed.

            side is which side the ball should spawn on"""
        #self.ball_rect.x = BALL_POS['x']
        #self.ball_rect.y = BALL_POS['y']
        self.maxspeed = self.origspeed
        self.movex = self.maxspeed
        if side == 2:
            self.movex *= -1
            self.ball_rect.x = player2.paddle_rect.x + PADDLE_WIDTH
            self.ball_rect.y = player2.paddle_rect.y + (PADDLE_HEIGHT / 2)
        else:
            self.ball_rect.x = player1.paddle_rect.x - BALL_SIZE
            self.ball_rect.y = player1.paddle_rect.y + (PADDLE_HEIGHT / 2)
        self.movey = self.Y_SPEED

    def wall_collide_adjust(self, newy):
        """When the ball hits a wall, adjust it."""
        self.ball_rect.y = newy
        self.movey *= -1
        wallhit_sfx.play()

    def paddle_collide_adjust(self, newx, speed_modifier):
        """When the ball hits a paddle, adjust it."""
        self.ball_rect.x = newx
        self.movex *= -1
        self.movex += speed_modifier
        paddlehit_sfx.play()

    def ball_phased(self, player):
        """Check if ball 'phased' through the paddle."""
        if player is player1:
            return ((self.ball_rect.x + self.movex) >= player.paddle_rect.x and
                (self.ball_rect.y + BALL_SIZE) >= player.paddle_rect.y and
                 self.ball_rect.y <= (player.paddle_rect.y + PADDLE_HEIGHT))
        else:
            return ((self.ball_rect.x + self.movex) <= player.paddle_rect.x and
                (self.ball_rect.y + BALL_SIZE) >= player.paddle_rect.y and
                 self.ball_rect.y <= (player.paddle_rect.y + PADDLE_HEIGHT))

    def move(self):
        """Moves the ball then draws it to the screen."""
        # Bounces the ball off the walls
        if self.ball_rect.y + self.movey <= COURT_TOP:
            self.wall_collide_adjust(COURT_TOP)
        elif self.ball_rect.y + self.movey + BALL_SIZE >= COURT_BOTTOM:
            self.wall_collide_adjust(COURT_BOTTOM - BALL_SIZE)
        # Bounces the ball off paddles
        if ((self.ball_rect.colliderect(
                player1.paddle_rect.move(-self.movex, 0)) or
                self.ball_phased(player1)) and self.movex > 0):
            self.paddle_collide_adjust(player1.paddle_rect.x - BALL_SIZE,
                                       -self.ACCELERATION)
        elif ((self.ball_rect.colliderect(player2.paddle_rect.move(
                self.movex + PADDLE_WIDTH, 0)) or
                self.ball_phased(player2)) and self.movex < 0):
            self.paddle_collide_adjust(player2.paddle_rect.x + PADDLE_WIDTH,
                                       self.ACCELERATION)
        # Check for a score
        if self.ball_rect.x + self.movex <= 0:
            increase_score(player=1)
        elif self.ball_rect.x + self.movex + BALL_SIZE >= SCREEN_WIDTH:
            increase_score(player=2)
        # Finally move and draw the ball
        self.ball_rect.move_ip(self.movex, self.movey)
        screen.fill(WHITE, self.ball_rect)


class PixelChar:
    """Converts a character into 'pixels' on the screen.
       Each character is represented by a matrix"""
    CHARS = {  0:
                [[1, 1, 1],
                 [1, 0, 1],
                 [1, 0, 1],
                 [1, 0, 1],
                 [1, 1, 1]],
                1:
                [[0, 1, 0],
                 [1, 1, 0],
                 [0, 1, 0],
                 [0, 1, 0],
                 [0, 1, 0]],
                2:
                [[1, 1, 1],
                 [0, 0, 1],
                 [1, 1, 1],
                 [1, 0, 0],
                 [1, 1, 1]],
                3:
                [[1, 1, 1],
                 [0, 0, 1],
                 [1, 1, 1],
                 [0, 0, 1],
                 [1, 1, 1]],
                4:
                [[1, 0, 1],
                 [1, 0, 1],
                 [1, 1, 1],
                 [0, 0, 1],
                 [0, 0, 1]],
                5:
                [[1, 1, 1],
                 [1, 0, 0],
                 [1, 1, 1],
                 [0, 0, 1],
                 [1, 1, 1]],
                6:
                [[1, 1, 1],
                 [1, 0, 0],
                 [1, 1, 1],
                 [1, 0, 1],
                 [1, 1, 1]],
                7:
                [[1, 1, 1],
                 [0, 0, 1],
                 [0, 0, 1],
                 [0, 0, 1],
                 [0, 0, 1]],
                8:
                [[1, 1, 1],
                 [1, 0, 1],
                 [1, 1, 1],
                 [1, 0, 1],
                 [1, 1, 1]],
                9:
                [[1, 1, 1],
                 [1, 0, 1],
                 [1, 1, 1],
                 [0, 0, 1],
                 [0, 0, 1]],
                'P':
                [[1, 1, 1, 0],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 1, 1, 0],
                 [1, 0, 0, 0],
                 [1, 0, 0, 0]],
                'O':
                [[0, 1, 1, 0],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [0, 1, 1, 0]],
                'N':
                [[1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 1, 0, 1],
                 [1, 0, 1, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1]],
                'G':
                [[0, 1, 1, 0],
                 [1, 0, 0, 1],
                 [1, 0, 0, 0],
                 [1, 0, 1, 0],
                 [1, 0, 0, 1],
                 [0, 1, 1, 0]],
                'L':
                [[1, 0, 0, 0],
                 [1, 0, 0, 0],
                 [1, 0, 0, 0],
                 [1, 0, 0, 0],
                 [1, 0, 0, 0],
                 [1, 1, 1, 1]],
                'A':
                [[0, 1, 1, 0],
                 [1, 0, 0, 1],
                 [1, 1, 1, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1]],
                'Y':
                [[1, 0, 1, 0],
                 [1, 0, 1, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0]],
                'E':
                [[1, 1, 1, 1],
                 [1, 0, 0, 0],
                 [1, 1, 1, 0],
                 [1, 0, 0, 0],
                 [1, 0, 0, 0],
                 [1, 1, 1, 1]],
                'R':
                [[1, 1, 1, 0],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 1, 1, 0],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1]],
                'D':
                [[1, 1, 1, 0],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 1, 1, 0]],
                'S':
                [[0, 1, 1, 0],
                 [1, 0, 0, 1],
                 [0, 1, 0, 0],
                 [0, 0, 1, 0],
                 [1, 0, 0, 1],
                 [0, 1, 1, 0]],
                'M':
                [[1, 0, 0, 1],
                 [1, 1, 1, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1]],
                'U':
                [[1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [0, 1, 1, 0]],
                'C':
                [[0, 1, 1, 1],
                 [1, 0, 0, 0],
                 [1, 0, 0, 0],
                 [1, 0, 0, 0],
                 [1, 0, 0, 0],
                 [0, 1, 1, 1]],
                'W':
                [[1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 1, 1, 1],
                 [1, 0, 0, 1]],
                'I':
                [[1, 1, 1, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0],
                 [1, 1, 1, 0]],
                'T':
                [[1, 1, 1, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0]],
                'K':
                [[1, 0, 0, 1],
                 [1, 0, 1, 0],
                 [1, 1, 0, 0],
                 [1, 1, 0, 0],
                 [1, 0, 1, 0],
                 [1, 0, 0, 1]],
                'B':
                [[1, 1, 1, 0],
                 [1, 0, 0, 1],
                 [1, 1, 1, 0],
                 [1, 0, 0, 1],
                 [1, 0, 0, 1],
                 [1, 1, 1, 0]],
                ' ':
                [[0, 0, 0, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]],
                '>':
                [[1, 0, 0, 0],
                 [1, 1, 0, 0],
                 [1, 1, 1, 0],
                 [1, 1, 1, 0],
                 [1, 1, 0, 0],
                 [1, 0, 0, 0]],
                '-':
                [[0, 0, 0, 0],
                 [0, 0, 0, 0],
                 [1, 1, 1, 1],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]]
            }

    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos

    def draw_character(self, char, block_size):
        """Draws the character.
            char is a matrix containing data on a character"""
        if char == 10:
            char = '-'
        for y, row in enumerate(self.CHARS[char]):
            for x, block_on in enumerate(row):
                if block_on:
                    blockrect = pygame.Rect(self.xpos + (block_size * x),
                                            self.ypos + (block_size * y),
                                            block_size, block_size)
                    screen.fill(WHITE, blockrect)


# Functions
def set_icon(icon_file):
    """Set's the window icon."""
    # If there is no icon to load, don't worry about it
    try:
        pygame.display.set_icon(pygame.image.load(icon_file))
    except:
        print('Icon could not be loaded!')


def load_sound(soundfile):
    """Loads a sound file and returns a sound object."""
    fullpath = os.path.join('Sounds', soundfile)  # For cross compatibility
    try:
        sound = pygame.mixer.Sound(fullpath)
    except:
        print('Sound file could not be loaded!')
        # Make a dummy class so we don't need to do future error checking
        class NoSound:
            def play(self):
                pass
        sound = NoSound()
    return sound


def play_music(musicfile):
    """Load and begin playing background music."""
    if pygame.mixer.music.get_busy():
        return
    fullpath = os.path.join('Sounds', musicfile)  # For cross compatibility
    try:
        pygame.mixer.music.load(fullpath)
    except:
        print('Can not load music!')
        return
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)


def create_window(width, height, title, icon=None):
    """Creates a new pygame window."""
    # Lower the buffer size to remove sound lag
    pygame.mixer.pre_init(buffer=512)
    pygame.init()
    set_icon(icon)
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    return screen


def quit_game():
    """Quits the game gracefully."""
    pygame.quit()
    sys.exit()


def increase_score(player):
    """Increases a player's score and resets the ball."""
    # Probably a better solution than globals here.
    global player1_score
    global player2_score
    if player1_score >= 9 and player == 1:
        win_go()
    elif player2_score >= 9 and player == 2:
        game_over_go()
    if player == 1:
        player1_score += 1
        playerscore_sfx.play()
    elif player == 2:
        player2_score += 1
        aiscore_sfx.play()
    ball.reset(player)


def draw_barriers():
    """Draws upper and lower barriers."""
    barrierup = pygame.Rect(BARRIER_X, BARRIER_OFFSET, BARRIER_WIDTH,
                            BARRIER_HEIGHT)
    barrierdown = pygame.Rect(BARRIER_X, SCREEN_HEIGHT - BARRIER_HEIGHT -
                              BARRIER_OFFSET, BARRIER_WIDTH, BARRIER_HEIGHT)
    screen.fill(WHITE, barrierup)
    screen.fill(WHITE, barrierdown)


def draw_net():
    """Draws the tennis net down the center of the screen."""
    for y in range(NET_POS['y'], COURT_BOTTOM, NET_SQUARE_SIZE + NET_BUFFER):
        netsquare = (pygame.Rect(NET_POS['x'], y,
                     NET_SQUARE_SIZE, NET_SQUARE_SIZE))
        screen.fill(WHITE, netsquare)


def handle_player_movement(event, player):
    """Handles all player movement."""
    if player is player1:
        upkey = pygamevars.K_UP
        downkey = pygamevars.K_DOWN
    else:
        upkey = pygamevars.K_a
        downkey = pygamevars.K_z
    if event.type == pygamevars.KEYDOWN:
        if event.key == downkey:
            player.movedown = 1
            player.moving = 1
            player.movespeed = player.maxspeed
        elif event.key == upkey:
            player.moveup = 1
            player.moving = 1
            player.movespeed = -player.maxspeed
    elif event.type == pygamevars.KEYUP:
        # Extra logic to stop the paddle from freezing when a key is pressed
        # while another key is pressed
        if event.key == downkey:
            player.movedown = 0
            if player.moveup:
                player.movespeed = -player.maxspeed
        elif event.key == upkey:
            player.moveup = 0
            if player.movedown:
                player.movespeed = player.maxspeed
        if not player.movedown and not player.moveup:
            player.moving = 0


def handle_AI():
    """Handles paddle AI."""
    # Have the paddle only move when ball is moving towards it
    if ball.movex < 0:
        player2.moving = 1
    else:
        player2.moving = 0
    if ball.ball_rect.y > (player2.paddle_rect.y + PADDLE_HEIGHT +
                           player2.movespeed):
        player2.movespeed = player2.maxspeed
    elif ball.ball_rect.y < (player2.paddle_rect.y - player2.movespeed):
        player2.movespeed = -player2.maxspeed


def pause_game():
    """Pauses the game."""
    global game_state
    game_state = PAUSED
    pygame.mixer.music.pause()
    pause_sfx.play()


def unpause_game():
    """Unpauses the game."""
    global game_state
    game_state = PLAY
    pygame.mixer.music.unpause()
    unpause_sfx.play()


def game_over_go():
    """Handles the transition to the game over state."""
    global game_state
    criticalerr_sfx.play()
    #pygame.mixer.music.fadeout(1000)
    game_state = GAMEOVER


def win_go():
    """Handles the transition to the game win state."""
    global game_state
    victory_sfx.play()
    #pygame.mixer.music.fadeout(1000)
    game_state = WIN


def draw_word(word, xpos, ypos, blocksize, charlen):
    """Converts a word into pixelated format."""
    for x, char in enumerate(word):
        if char.isdigit():
            char = int(char)
        if char == 10:
            char = '-'
        pixelchar = PixelChar(xpos + (x * (blocksize *
                             (charlen + 1))),
                              ypos)
        pixelchar.draw_character(char, blocksize)


def draw_menu_pointer():
    """Draws the menu option pointer."""
    # Code for flashing is inelegant and doesn't really work for any number
    # besides 5. But it gets the job done.
    global pntrflash
    if game_state == TRANS:
        if (pygame.time.get_ticks() % 5) == 0:
            if pntrflash:
                pntrflash = 0
            else:
                pntrflash = 1
        if pntrflash:
            return
    xpos = OPTIONS_POS['x'] - 30
    ypos = (OPTIONS_POS['y'] + ((LETTER_HEIGHT + OPTIONS_BUFFER) *
            menu_pointer * OPTIONS_BLOCK_SIZE))
    pointer = PixelChar(xpos, ypos)
    pointer.draw_character('>', OPTIONS_BLOCK_SIZE)


def show_menu_options():
    """Draws menu options on the menu."""
    for y, option in enumerate(menu_options):
        draw_word(option, OPTIONS_POS['x'], OPTIONS_POS['y'] +
                ((LETTER_HEIGHT + OPTIONS_BUFFER) * y * OPTIONS_BLOCK_SIZE),
                  OPTIONS_BLOCK_SIZE, LETTER_LENGTH)

def play_game():
    """Determines which gameplay mode to start."""
    global menu_pointer
    global numplayers
    global game_state
    menuselect_sfx.play()
    if menu_pointer == 0:
        numplayers = 1
    elif menu_pointer == 1:
        numplayers = 2
    game_state = TRANS


def game_state_play():
    """What to do when game_state = PLAY"""
    play_music('music.ogg')
    screen.fill(BG_COLOR)
    draw_barriers()
    draw_net()
    if numplayers == 1:
        handle_AI()
    player1.update()
    ball.move()
    p1_scorebox.draw_character(player1_score, DIGIT_BLOCK_SIZE)
    player2.update()
    p2_scorebox.draw_character(player2_score, DIGIT_BLOCK_SIZE)
    #fps_counter.update()  # Uncomment this if you want an FPS counter
    pygame.display.flip()


def draw_gameover():
    """Gameover message."""
    draw_word('YOU LOSE', 485, 200, 10, LETTER_LENGTH)
    draw_word('PRESS SPACE', 520, 280, 6, LETTER_LENGTH)


def draw_win():
    """Win message."""
    draw_word('YOU WIN', 485, 200, 10, LETTER_LENGTH)
    draw_word('PRESS SPACE', 520, 280, 6, LETTER_LENGTH)


def game_state_gameover():
    """Gameover state."""
    screen.fill(BG_COLOR)
    draw_barriers()
    draw_net()
    player1.update()
    player2.update()
    p1_scorebox.draw_character(player1_score, DIGIT_BLOCK_SIZE)
    p2_scorebox.draw_character(player2_score, DIGIT_BLOCK_SIZE)
    draw_gameover()
    pygame.display.flip()


def game_state_win():
    """Gameover state."""
    screen.fill(BG_COLOR)
    draw_barriers()
    draw_net()
    player1.update()
    player2.update()
    p1_scorebox.draw_character(player1_score, DIGIT_BLOCK_SIZE)
    p2_scorebox.draw_character(player2_score, DIGIT_BLOCK_SIZE)
    draw_win()
    pygame.display.flip()


def draw_title_line():
    """Draws the line under the menu title."""
    global titleline_width
    # Magic numbers... I know. My lack of forethought is biting me in the ass
    underline = pygame.Rect((TITLE_POS['x'] + 190) - (titleline_width / 2),
                             TITLE_POS['y'] + 140, titleline_width, 5)
    screen.fill(WHITE, underline)
    if titleline_width < 420:
        titleline_width += 10


def draw_credits():
    """Draws my credits."""
    draw_word('MADE BY KURT', 10, SCREEN_HEIGHT - 30, 3, LETTER_LENGTH)


def draw_menu():
    """Draws the entire menu screen."""
    screen.fill(BG_COLOR)
    draw_word(MENU_TITLE, TITLE_POS['x'], TITLE_POS['y'],
              TITLE_BLOCK_SIZE, LETTER_LENGTH)
    draw_title_line()
    show_menu_options()
    draw_menu_pointer()
    draw_credits()
    pygame.display.flip()


def go_to_menu():
    """Returns to the menu."""
    global game_state
    pygame.mixer.music.stop()
    game_state = MENU


def game_state_menu():
    """What to do when game_state = MENU"""
    play_music('mainmenu.ogg')
    draw_menu()


def game_state_transition():
    """Transition between the menu and the game."""
    global game_state
    pygame.mixer.music.fadeout(2000)
    if not pygame.mixer.music.get_busy():
        reset_game(numplayers)
        game_state = PLAY
    draw_menu()


def game_loop():
    """The game loop."""
    handle_input()
    if game_state == MENU:
        game_state_menu()
    elif game_state == TRANS:
        game_state_transition()
    elif game_state == PLAY:
        game_state_play()
    elif game_state == GAMEOVER:
        game_state_gameover()
    elif game_state == WIN:
        game_state_win()
    fps_clock.tick(FPS)


def reset_game(playersnum=1):
    """Resets all variables for the game."""
    # Yeah, I know. I blame feature creep and lack of understanding how
    # quickly organization would become a problem.
    global menu_options, game_state, menu_pointer, player1_score
    global player2_score, numplayers, player1, player2, ball
    global p1_scorebox, p2_scorebox, pntrflash, titleline_width
    menu_options = ['1 PLAYER', '2 PLAYER']
    game_state = MENU
    menu_pointer = 0
    player1_score = 0
    player2_score = 0
    numplayers = playersnum
    player1 = Paddle(PADDLE1_POS['x'], PADDLE1_POS['y'])
    if numplayers == 1:
        player2 = Paddle(PADDLE2_POS['x'], PADDLE2_POS['y'], maxspeed=8)
    else:
        player2 = Paddle(PADDLE2_POS['x'], PADDLE2_POS['y'])
    ball = Ball()
    p1_scorebox = PixelChar(P1_SCOREPOS['x'], P1_SCOREPOS['y'])
    p2_scorebox = PixelChar(P2_SCOREPOS['x'], P2_SCOREPOS['y'])
    pntrflash = 1
    titleline_width = 5


def handle_input():
    """Handles all user input."""
    global menu_pointer
    global game_state
    for event in pygame.event.get():
        if event.type == pygamevars.QUIT:
            quit_game()
        elif event.type == pygamevars.KEYDOWN:
            if event.key == pygamevars.K_ESCAPE:
                go_to_menu()
        if game_state == PLAY or game_state == PAUSED:
            if event.type == pygamevars.KEYDOWN:
                if (event.key == pygamevars.K_p or
                        event.key == pygamevars.K_SPACE):
                    if game_state != PAUSED:
                        pause_game()
                    else:
                        unpause_game()
            handle_player_movement(event, player1)
            if numplayers == 2:
                handle_player_movement(event, player2)
        elif game_state == MENU:
            if event.type == pygamevars.KEYDOWN:
                if event.key == pygamevars.K_DOWN:
                    menu_pointer += 1
                    if menu_pointer > (len(menu_options) - 1):
                        menu_pointer = 0
                    menumove_sfx.play()
                elif event.key == pygamevars.K_UP:
                    menu_pointer -= 1
                    if menu_pointer < 0:
                        menu_pointer = (len(menu_options) - 1)
                    menumove_sfx.play()
                elif event.key == pygamevars.K_SPACE:
                    play_game()
        elif game_state == GAMEOVER or game_state == WIN:
            if event.type == pygamevars.KEYDOWN:
                if event.key == pygamevars.K_SPACE:
                    reset_game(numplayers)
                    game_state = PLAY


# Initialize display and FPS clock
screen = create_window(SCREEN_WIDTH, SCREEN_HEIGHT,
                       WINDOW_TITLE, 'pong_icon.png')
fps_clock = pygame.time.Clock()
fps_counter = FPSCounter(FPSCOUNT_POS['x'], FPSCOUNT_POS['y'])

#Load sounds
paddlehit_sfx = load_sound('paddlehit.wav')
wallhit_sfx = load_sound('wallhit.wav')
aiscore_sfx = load_sound('aiscore.wav')
playerscore_sfx = load_sound('playerscore.wav')
pause_sfx = load_sound('pause.wav')
unpause_sfx = load_sound('unpause.wav')
menumove_sfx = load_sound('menumove.wav')
menuselect_sfx = load_sound('menuselect.wav')
criticalerr_sfx = load_sound('criticalerror.wav')  # Just for fun
victory_sfx = load_sound('victory.wav')  # Just for fun


# Set everything up
reset_game()

# Main Loop
while 1:
    game_loop()
