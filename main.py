import random
import math
import time

WIDTH = 380
HEIGHT = 680

backgrounds = []
backgrounds.append(Actor("warplanes_background", topleft=(0, 0)))
backgrounds.append(Actor("warplanes_background", bottomleft=(0, 0)))

hero = Actor("warplanes_hero1", midbottom=(WIDTH//2, HEIGHT-500))
hero.speed = 5
hero.animcount = 0
hero.power = False # 是否有超级火力道具
hero.score = 0 # 游戏积分
hero.live = 5 # 战机生命
hero.unattack = False # 战机是否无敌
hero.ukcount = 0 # 无敌倒计时，为0时退出无敌状态

bullets = []
powers = []

# 敌机的移动方式
tweens = ["linear", "accelerate", "decelerate", "accel_decel", \
        #"in_elastic", "out_elastic", "in_out_elastic", \
        #"bounce_end", "bounce_start_end",
          "bounce_start"]
enemies = []

gameover = False

music.play("warplanes")

def spawn_enemy():
    origin_x = random.randint(50, WIDTH)
    target_x = random.randint(50, WIDTH)
    tn = random.choice(tweens)
    dn = random.randint(4, 6)
    enemy = Actor("warplanes_enemy1", bottomright=(origin_x, 0))
    if random.randint(1, 100) < 20:
        enemy.image = "warplanes_enemy2"
    enemies.append(enemy)
    animate(enemy, tween=tn, duration=dn, topright=(target_x, HEIGHT))
    #print("tween=", tn, " duration=", dn)
clock.schedule_interval(spawn_enemy, 2.0)

def update_enemy():
    global gameover
    for e in enemies:
        if e.top >= HEIGHT:
            enemies.remove(e)
            continue
        # 判断是否与子弹相撞
        n = e.collidelist(bullets)
        if n != -1:
            enemies.remove(e)
            bullets.remove(bullets[n])
            sounds.shooted.play()
            hero.score += 200 if e.image == "warplanes_enemy2" else 100

        # 判断是否与战机相撞
        if e.colliderect(hero) and not hero.unattack:
            hero.live -= 1
            if hero.live > 0:
                hero.unattack = True
                hero.ukcount = 100
                enemies.remove(e)
                sounds.shooted.play()
            else:
                sounds.gameover.play()
                gameover = True
                music.stop()
                time.sleep(0.5)

def update_powerup():
    if random.randint(1, 1000) < 3:
        powers.append(Actor("warplanes_powerup", bottomright=(random.randint(50, WIDTH), 0)))

    for p in powers:
        p.y += 2
        if p.top > HEIGHT:
            powers.remove(p)
        elif p.colliderect(hero):
            powers.remove(p)
            hero.power = True
            clock.schedule(powerdown, 5.0)

def powerdown():
    hero.power = False

def shoot():
    sounds.bullet.play()
    bullets.append(Actor("warplanes_bullet", midbottom=(hero.x, hero.top)))
    if hero.power:
        left = Actor("warplanes_bullet", midbottom=(hero.x, hero.top))
        left.angle = 15
        bullets.append(left)
        right = Actor("warplanes_bullet", midbottom=(hero.x, hero.top))
        right.angle = -15
        bullets.append(right)

def update_bullets():
    for b in bullets:
        theta = math.radians(b.angle + 90)
        b.x += 10 * math.cos(theta)
        b.y -= 10 * math.sin(theta)
        if b.bottom < 0:
            bullets.remove(b)

def update_hero():
    move_hero()
    hero.animcount = (hero.animcount+1)%20
    if hero.animcount == 0:
        hero.image = "warplanes_hero1"
    elif hero.animcount == 10:
        hero.image = "warplanes_hero2"
    if hero.unattack:
        hero.ukcount -= 1
        if hero.ukcount <= 0:
            hero.unattack = False
            hero.ukcount = 100

def draw_hero():
    if hero.unattack:
        if hero.ukcount % 5 == 0:
            return
    hero.draw()

def draw_hud():
    for i in range(hero.live):
        screen.blit("warplanes_live", (i*35, HEIGHT-35))
    screen.draw.text(str(hero.score), topleft=(20, 20), fontname="marker_felt", fontsize=25)

def move_hero():
    if keyboard.right:
        hero.x += hero.speed
    elif keyboard.left:
        hero.x -= hero.speed
    elif keyboard.down:
        hero.y += hero.speed
    elif keyboard.up:
        hero.y -= hero.speed
    if hero.left < 0:
        hero.left = 0
    elif hero.right > WIDTH:
        hero.right = WIDTH
    if hero.top < 0:
        hero.top = 0
    elif hero.bottom > HEIGHT:
        hero.bottom = HEIGHT

    # 检查是否射击
    if keyboard.space:
        clock.schedule_unique(shoot, 0.1)

def update_backgrounds():
    for b in backgrounds:
        b.y += 2
        if b.top > HEIGHT:
            b.bottom = 0

def draw():
    if gameover:
        screen.blit("warplanes_gameover", (0, 0))
        return
    for b in backgrounds:
        b.draw()
    for b in bullets:
        b.draw()
    for p in powers:
        p.draw()
    for e in enemies:
        e.draw()
    draw_hero()
    draw_hud()

def update():
    if gameover:
        clock.unschedule(spawn_enemy)
        return
    update_backgrounds()
    update_hero()
    update_bullets()
    update_powerup()
    update_enemy()
