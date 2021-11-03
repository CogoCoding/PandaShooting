import sys
import threading
from datetime import timedelta, datetime
from time import sleep
from itertools import cycle
import pygame
from pygame.locals import *
from gameRole import *
import random
import os
from threading import Timer

# ----------------------------------------------------------------------------

# 스크린 전체 크기 지정 및 스크린 객체 저장
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRAY = (150,150,150)

# 총알 판다옆 이동 위치 좌표 16개 : b_pos_list
b_pos_list =[[-10,-20],[0,-20],[10,-20],[20,-20],[30,-20],[30,0],[30,20],[30,40],[30,60],[20,60],[10,60],[0,60],[-10,60],[-10,40],[-10,20],[-10,10],[-10,0],[-10,-20]]

# 한글 벽 위치 좌표 20개 : hangeul_poses
# --리스트
hangeul_poses = []
# row1
y = 0
for i in range(0,6):
  x = 1
  x = x*i*100
  hangeul_poses.append([x,y])
# row2
x = 1
y = 500
for i in range(0,6):
   x = 1
   x = x*i*100
   hangeul_poses.append([x,y])
# row3
x = 0
for i in range(1,5):
   y = 1
   y = y*i*100
   hangeul_poses.append([x,y])
# row4
x = 500
for i in range(1,5):
   y = 1
   y = y*i*100
   hangeul_poses.append([x,y])

# -- 리스트 중 개별 위치 랜덤 수 20개: h_deck
h_deck = []
for j in range(0,20):
     h= random.randrange(0,19)
     while h in h_deck :
       h = random.randint(0,19)
     h_deck.append(h)

#한글 벽 이미지 20개 : hangeul_imgs
hangeul_imgs = []
for i in range(0,20):
    filename_hangeul = 'resources/image/h{}.png'.format(i)
    hangeul_img = pygame.image.load(filename_hangeul)
    hangeul_img = pygame.transform.scale(hangeul_img,(100,100))
    hangeul_imgs.append(hangeul_img)

# 중국어 이미지 5개 : zhong_imgs
zhong_imgs=[]
for i in range(1,6):
    filename_zhong = 'resources/image/z{}.png'.format(i)
    zhong_img = pygame.image.load(filename_zhong)
    zhong_img = pygame.transform.scale(zhong_img, (100, 100))
    zhong_imgs.append(zhong_img)

# -------------------------------------------------------------------------------------------------
HANGEULS = []
class Hangeulbox:  # 한글박스 그리기
    def load_hangeul(self):
        # 한글 이미지 할당
        self.image = hangeul_imgs[i]
        self.rect = self.image.get_rect()
        # 랜덤 poses 할당
        hangeul_pos = hangeul_poses[h_deck[i]]
        self.left = hangeul_pos[0]
        self.rect.top = hangeul_pos[1]

    def draw_hangeul(self):
        screen.blit(self.image, [self.rect.x,self.rect.y])

    def move_hangeul(self):
        try:
            hangeul_pos = hangeul_poses[h_deck[i + 1]]
            self.left = hangeul_pos[0]
            self.rect.top = hangeul_pos[1]
            self.draw_hangeul()
        except:
            hangeul_pos = hangeul_poses[h_deck[0]]
            self.left = hangeul_pos[0]
            self.rect.top = hangeul_pos[1]
            self.draw_hangeul()

       # sprite_group.update()

# -------------------------------------------------------------------------------------------------
# 판다 클래스 [ init/ load / draw/ move_x /move_y / checkscreen/ shoot ]
class Panda:
    def __init__(self,x=0,y=0,dx=0,dy=0):
        self.image = ""
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.rect = ""

    #판다 이미지 불러오기
    def load_panda(self):
        # 판다 이미지 경로
        filename = 'resources/image/panda.png'
        #1) 이미지를 불러온다.
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, (30, 60))
        #2) 이미지의 정보를 rect에 저장한다.
        self.rect = self.image.get_rect()
        #3) 판다 초기 생성 위치를 정한다.
        self.rect.x = WINDOW_WIDTH / 2
        self.rect.y = WINDOW_HEIGHT / 2

    #판다 이미지 그리기 제어 + # 스크린 밖으로 나가지 못하게 하기
    def draw_panda(self):
        screen.blit(self.image,[self.rect.x,self.rect.y])

    def move_x(self):
        self.rect.x += self.dx

    def move_y(self):
        self.rect.y += self.dy

    def pos_panda(self):
        pos = [self.rect.x, self.rect.y]
        print("p pos : ",pos)

    def pos_panda_x(self):
        return self.rect.x

    def pos_panda_y(self):
        return self.rect.y

    def shoot(self, all_sprites,bullets):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def check_screen(self):
        # 화면 밖으로 못 나가게 방지
        if self.rect.x < 100:
            self.rect.x =100
        if self.rect.right > 500 :
            self.rect.right = 500
        if self.rect.bottom > WINDOW_HEIGHT-100 :
            self.rect.bottom = WINDOW_HEIGHT-100
        if self.rect.y-100 < 0 :
            self.rect.y = 100


# -------------------------------------------------------------------------------------------------

# 대나무 클래스
class Bullet: # 판다 클래스 [ init/ load / draw/ move_x /move_y / checkscreen ]
    def __init__(self,x=0,y=0,dx=0,dy=0,cx=10,cy=30):
        self.image = ""
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.cx = cx
        self.cy = cy
        self.rect = ""

    # 대나무 이미지 불러오기
    def load_bullet(self,panda): # Panda 클래스 / panda 객체
        # 대나무 이미지 경로
        filename = 'resources/image/bullet.PNG'
        bul_img = pygame.image.load(filename)
        bul_img = pygame.transform.scale(bul_img, (10, 20))
        # 1) 이미지를 불러온다.
        self.image = bul_img
        # 2) 이미지의 정보를 rect에 저장한다.
        self.rect = self.image.get_rect()
        # 3) 대나무 초기 생성 위치를 판다 옆으로 정한다.
        px, py = Panda.pos_panda_x(panda),Panda.pos_panda_y(panda)
        self.rect.x= px
        self.rect.y = py
        # print("load px,py :", px, py)

    def draw_bullet(self):
        screen.blit(self.image, [self.rect.x, self.rect.y])

    def move_x(self):
        self.rect.x += self.dx

    def move_y(self):
        self.rect.y += self.dy

    def circle_x(self,panda):
        px = Panda.pos_panda_x(panda)
        self.rect.x = px + self.cx

    def circle_y(self,panda):
        py = Panda.pos_panda_y(panda)
        self.rect.y = py + self.cy

    def pos_bullet(self):
        pos = [self.rect.x, self.rect.y]
        print("b pos : ", pos)

    def check_screen(self):
        # 화면 밖으로 못 나가게 방지
        if self.rect.x < 100:
            self.rect.x = 100
        if self.rect.right > 500:
            self.rect.right = 500
        if self.rect.bottom > WINDOW_HEIGHT - 100:
            self.rect.bottom = WINDOW_HEIGHT - 100
        if self.rect.y - 100 < 0:
            self.rect.y = 100


# -------------------------------------------------------------------------------------------------

def main():
    global screen,WINDOW_WIDTH,WINDOW_HEIGHT
    # 게임 시작 초기화
    pygame.init()

    print(b_pos_list)
    print(len(b_pos_list))
    nb = 0

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT),
                                     pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    # 상단바 아이콘 및 문구
    windowicon = pygame.image.load('resources/image/panda.png')
    windowicon = pygame.transform.scale(windowicon, (32, 32))
    pygame.display.set_caption('CHINESE WORD GAME')
    pygame.display.set_icon(windowicon)

    # fps위한 clock
    clock = pygame.time.Clock()

    # 객체 생성 및 그리기 ( 한글박스 )
    for i in range(0, 20):
        hangeul = Hangeulbox()
        hangeul.load_hangeul()
        HANGEULS.append(hangeul)

    # 객체 생성 및 그리기 ( 판다, 대나무)
    panda = Panda() #초기위치 (x,y,dx,dy)로 지정해줘도 됌
    panda.load_panda()
    bullet = Bullet()
    bullet.load_bullet(panda)

    playing = True
    while playing:

        # 배경사진
        background = pygame.image.load('resources/image/back2.png')
        background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        # 배경 그리기
        screen.blit(background, (0, 0))

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
                pygame.quit()
                sys.exit()

            #  판다 움직이기 조작
        # 화살표 키를 이용해서 panda 움직임 거리를 조정해준다.
        # 키를 떼면 움직임 거리를 0으로 한다.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    panda.dx = 5
                    bullet.dx = 5

                elif event.key == pygame.K_LEFT:
                    panda.dx = -5
                    bullet.dx = -5

                elif event.key == pygame.K_DOWN:
                    panda.dy = 5
                    bullet.dy = 5

                elif event.key == pygame.K_UP:
                    panda.dy = -5
                    bullet.dy = -5

                elif event.key == pygame.K_UP:
                    panda.dy = -5
                    bullet.dy = -5

                elif event.key == pygame.K_SPACE:
                    panda.pos_panda()
                    bullet.pos_bullet()
                    bullet.draw_bullet()
                    bullet = Bullet()
                    bullet.fly_bullet()

                elif event.key == pygame.K_x:
                    nb = nb + 1
                    if nb > 15:
                        nb = 0
                    bullet.cx = b_pos_list[nb][0]
                    bullet.cy = b_pos_list[nb][1]
                    # print("k_z_nb", b_pos_list[nb][0], b_pos_list[nb][1])
                    print("k_z", bullet.cx, bullet.cy)

                elif event.key == pygame.K_z:
                    nb = nb - 1
                    if nb < 0:
                        nb = 15
                    bullet.cx = b_pos_list[nb][0]
                    bullet.cy = b_pos_list[nb][1]
                    # print("k_x_nb", b_pos_list[nb][0], b_pos_list[nb][1])
                    print("k_x", bullet.cx, bullet.cy)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    panda.dx = 0
                    bullet.dx = 0

                elif event.key == pygame.K_LEFT:
                    panda.dx = 0
                    bullet.dx = 0

                elif event.key == pygame.K_DOWN:
                    panda.dy = 0
                    bullet.dy = 0

                elif event.key == pygame.K_UP:
                    panda.dy = 0
                    bullet.dy = 0

        panda.check_screen()
        panda.draw_panda()
        bullet.draw_bullet()
        panda.move_x()
        bullet.move_x()
        panda.move_y()
        bullet.move_y()
        bullet.circle_x(panda)
        bullet.circle_y(panda)

    # 한글 박스 그리기
        HANGEULS[i].draw_hangeul()
    # 한글 박스 움직이기
        global last_moved_time
        last_moved_time = datetime.now()
        if timedelta(seconds=1.0) <= datetime.now() - last_moved_time:
                HANGEULS[i].move_hangeul()
                HANGEULS[i].draw_hangeul()
        # threading.Timer(3,HANGEULS[i].move_hangeul()).start()
        #
        # hangeul.move_hangeul()
        # panda.check_screen()
        # hangeul.draw_hangeul()

        # 1. 랜덤 수로 poses 꺼내와서 img랑 배치
        for i in range(0, 20):
            # 랜덤 poses 할당
            hangeul_pos = hangeul_poses[h_deck[i]]
            # 한글 이미지 할당
            hangeul = hangeul_imgs[i]
            # 한글 rect 할당
            hangeul_rect = hangeul.get_rect()
            hangeul_rect.left = hangeul_pos[0]
            hangeul_rect.top = hangeul_pos[1]
            screen.blit(hangeul, hangeul_rect)

        pygame.display.flip()

        clock.tick(60)

if __name__ == '__main__':
    main()