import os
import pygame
import random

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init
pygame.font.init()
pygame.mixer.init()

CLOCK = pygame.time.Clock()

black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

WINDOW_SIZE = (800, 600)
main_screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('Pong in Pygame')

bounce_sound = pygame.mixer.Sound('pong bounce.wav')
score_sound = pygame.mixer.Sound('pong score.wav')
win_sound = pygame.mixer.Sound('pong win.wav')


p1score = 0
p2score = 0
PLAY_TO = 10
win_condition = 0
win_timer = 0

class Rectangles:
    def __init__(self, rect, color):
        self.rect = pygame.Rect(rect)
        self.color = color

    def BallIntersect(self, ball):
        #find closest point in rectange to the circle
        closest_x = Clamp(ball.x, self.rect.left, self.rect.right)
        closest_y = Clamp(ball.y, self.rect.top, self.rect.bottom)
        #find distance between this point and circle center
        dist_x = ball.x - closest_x
        dist_y = ball.y - closest_y
        #distance formula
        dist_hyp = dist_x**2 + dist_y**2
        return (dist_hyp < ball.radius**2, dist_x, dist_y)
        
class Bumper(Rectangles):
    def __init__(self, rect, speed, color):
        Rectangles.__init__(self, rect, color)
        self.speed = speed

class CircleClass:
    def __init__(self, x, y, radius, x_speed, y_speed, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.color = color

    def Reset(self):
        self.x = WINDOW_SIZE[0]/2
        self.y = WINDOW_SIZE[1]/2
        new_x_speed = random.randint(3,9)
        new_y_speed = random.randint(3,9)
        if random.randint(0,1) == 1:
            new_y_speed = new_y_speed * -1
        if random.randint(0,1) == 1:
            new_x_speed = new_x_speed * -1
        #now new_x_speed and new_y_speed will be in between -5, 5 but != 0
        #probably a much better way of doing this...
        self.x_speed = new_x_speed
        self.y_speed = new_y_speed

def PrintText(text, color, size):
    font1 = pygame.font.Font('freesansbold.ttf', size)
    printed_text = font1.render(text, 1, color)
    return printed_text

def Clamp(value, min, max):
	if value < min:
		return min
	if value > max:
		return max
	else:
		return value

def PrepareWinText(winning_player):
    if winning_player == 1:
        player_won = 'Player 1'
    if winning_player == 2:
        player_won = 'Player 2'
    winning_text = '%s wins!' % player_won
    printable_text = PrintText(winning_text, white, 40)
    #center the text
    text_rect = printable_text.get_rect()
    text_rect.center = main_screen.get_rect().center
    return (printable_text, text_rect)

bumpers = {'p1bumper': Bumper((100, 275, 10, 50), 0, white),
           'p2bumper': Bumper((700, 275, 10, 50), 0, white),
           }

walls = {'topboundary': Rectangles((10, 10, 780, 10), white),
         'bottomboundary': Rectangles((10, 580, 780, 10), white),
         }

ball = CircleClass(0, 0, 10, 0, 0, white)

ball.Reset()
#main loop
game_loop = 1
while game_loop == 1:
    #Input
    for event in pygame.event.get():
        #hit x button
        if event.type == pygame.QUIT:
            game_loop = 0
        #Key pressed down
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_loop = 0
            if event.key == pygame.K_w:
                #p1bumper_speed = -7
                bumpers['p1bumper'].speed = -7
            if event.key == pygame.K_s:
                bumpers['p1bumper'].speed = 7
            if event.key == pygame.K_UP:
                bumpers['p2bumper'].speed = -7
            if event.key == pygame.K_DOWN:
                bumpers['p2bumper'].speed = 7
        #Key released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                bumpers['p1bumper'].speed = 0
            if event.key == pygame.K_s:
                bumpers['p1bumper'].speed = 0
            if event.key == pygame.K_UP:
                bumpers['p2bumper'].speed = 0
            if event.key == pygame.K_DOWN:
                bumpers['p2bumper'].speed = 0
                
    #Game Logic
    
    #bumpers don't go offscreen, probably could do this part better
    for a in bumpers:
        if walls['topboundary'].rect.bottom < bumpers[a].rect.top + bumpers[a].speed:
            if bumpers[a].rect.bottom + bumpers[a].speed < walls['bottomboundary'].rect.top:
                bumpers[a].rect.move_ip(0, bumpers[a].speed)
        if walls['topboundary'].rect.bottom >= bumpers[a].rect.top + bumpers[a].speed:
            bumpers[a].rect.top = walls['topboundary'].rect.bottom
        if walls['bottomboundary'].rect.top <= bumpers[a].rect.bottom + bumpers[a].speed: 
            bumpers[a].rect.bottom = walls['bottomboundary'].rect.top
    #make dict with bumpers and walls
    rect_dict = {}
    rect_dict.update(bumpers)
    rect_dict.update(walls)
    #Ball collision with bumpers and walls using our new dictionary
    for entry in rect_dict:
        rect_collision = rect_dict[entry].BallIntersect(ball)
        collision_occur, c_closest_x, c_closest_y = rect_collision
        if collision_occur == True and c_closest_x != 0 and c_closest_y == 0:
            ball.x_speed = ball.x_speed * -1
            bounce_sound.play()
        if collision_occur == True and c_closest_y != 0 and c_closest_x == 0:
            ball.y_speed = ball.y_speed * -1
            bounce_sound.play()
        if collision_occur == True and c_closest_x != 0 and c_closest_y != 0:
            ball.y_speed = ball.y_speed * -1
            ball.x_speed = ball.x_speed * -1
            bounce_sound.play()
    #move the ball
    ball.x += ball.x_speed
    ball.y += ball.y_speed
    #scoring
    if ball.x + ball.radius > WINDOW_SIZE[0]:
        ball.Reset()
        p1score += 1
        #if p1score = PLAY_TO that means the win sound will play
        #and we don't want both the normal score sound and the win sound to play at once
        if p1score != PLAY_TO:
            score_sound.play()
    if ball.x - ball.radius < 0:
        ball.Reset()
        p2score += 1
        if p2score != PLAY_TO:
            score_sound.play()

    text_to_print = {'p1score_text': (PrintText(str(p1score), white, 25), (200, 40)),
                     'p2score_text': (PrintText(str(p2score), white, 25), (600, 40)),
                     }
    #winning
    if p1score >= PLAY_TO:
        win_condition = 1
        text_ready, text_center_pos = PrepareWinText(1) 
        #have to do text_center_pos[0] and [1] because the text_center_pos is a Rect
        #so that means its a tuple with 4 entries
        text_to_print['win_text'] = (text_ready, (text_center_pos[0], text_center_pos[1]))
    if p2score >= PLAY_TO:
        win_condition = 1
        text_ready, text_center_pos = PrepareWinText(2) 
        text_to_print['win_text'] = (text_ready, (text_center_pos[0], text_center_pos[1]))
    if win_condition == 1:
        if win_timer == 0:
            win_sound.play()
        #act as timer, maybe a better way to do this?
        win_timer += 1
        if win_timer >= 80:
            ball.Reset()
            del text_to_print['win_text']
            p1score = 0
            p2score = 0
            win_timer = 0
            win_condition = 0
            for entry in bumpers:
                bumpers[entry].rect.y = 275
    #Draw
    main_screen.fill(black)
    for entry in rect_dict:
        pygame.draw.rect(main_screen, rect_dict[entry].color, rect_dict[entry].rect)
    for entry in text_to_print:
        text_ready, text_pos = text_to_print[entry]
        main_screen.blit(text_ready, text_pos)
    pygame.draw.circle(main_screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)
    pygame.display.flip()
    CLOCK.tick(30)
