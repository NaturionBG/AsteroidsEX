from pygame import *
import abc
from collections import defaultdict
import time as tm
import numpy as np
import scipy.stats as sc
from widgets import HealthBar, linear_coefficients


class Entity(abc.ABC):
  
  @abc.abstractmethod
  def collision():
    pass

  @abc.abstractmethod
  def logic():
    pass
  
  @abc.abstractmethod
  def draw():
    pass
  
  @abc.abstractmethod
  def get_state():
    pass
  
  @abc.abstractmethod
  def move():
    pass
  
  @abc.abstractmethod
  def strip_background():
    pass
  
class Shot(Entity):
  def __init__(self, w: int, h: int, parent, screen: Surface):
    self.__screen = screen
    self.__p = parent
    self.__w = w//30
    self.__h = h//20
    self.__speed = 10
    self.__dmg = 2
    self.__active = True
    self.__sprites = {
      1: transform.scale(image.load('./Sprites/Shot.png').convert(), (self.__w, self.__h)),
      2: transform.scale(image.load('./Sprites/ShotState2.png').convert(), (self.__w, self.__h)),
      3: transform.scale(image.load('./Sprites/ShotState3.png').convert(), (self.__w, self.__h)),
      4: transform.scale(image.load('./Sprites/ShotState4.png').convert(), (self.__w, self.__h))
    }
    self.strip_background()
    self.__x, self.__y = parent.rect.midtop
    self.rect = self.__sprites[1].get_rect(midbottom = (self.__x, self.__y))
    self.__hit = False
    self.__hit_timer = 0
    self.__add_shot()
    self.aff = 'good'
    self.__hitbox = Rect((self.__x + self.__w//1.5, self.__y + self.__h//8), (self.__w - self.__w//1.5, self.__h-self.__h//8))
  
  def get_hitbox(self) -> Rect:
    return self.__hitbox
  
  def __add_shot(self) -> None:
    self.__p.shotcount +=1
  def __take_shot(self) -> None:
    self.__p.shotcount -=1
  def strip_background(self):
    for i in self.__sprites.values():
      i.set_colorkey((0, 0, 0))
      
  def deal_dmg(self, other) -> None:
    other.take_dmg(self.__dmg)    
  
  def collision(self, other) -> None:
    if not self.__hit:
      if type(other.get_hitbox())!=list:
        if self.__hitbox.colliderect(other.get_hitbox()):
          self.deal_dmg(other)
          self.__hit = True
          other.trigger_hurt()
      elif type(other.get_hitbox())==list:
        for i in other.get_hitbox():
          if not self.__hit:
            if self.__hitbox.colliderect(i):
              self.deal_dmg(other)
              self.__hit = True
              other.trigger_hurt()

  def logic(self) -> None:
    if self.__hit:
      self.__hit_timer +=1
      if self.__hit_timer>9:
        self.__active = False
        
    if self.__y<-self.__h-5:
      self.__active = False

      
  
  def draw(self) -> None:
    if not self.__hit:
      self.__screen.blit(self.__sprites[1], (self.rect.topleft))
    else:
      if self.__hit_timer<=3:
        self.__screen.blit(self.__sprites[2], (self.rect.midtop))
      elif 3<self.__hit_timer<=6:
        self.__screen.blit(self.__sprites[3], (self.rect.midtop))
      elif 6<self.__hit_timer<=9:
        self.__screen.blit(self.__sprites[4], (self.rect.midtop))
    # draw.rect(self.__screen, (255, 255, 255), self.__hitbox, 2)

                           
  def get_state(self) -> bool:
    return self.__active
  
  def move(self) -> None:
    if not self.__hit:
      self.__y-=self.__speed
      self.rect.midbottom= (self.__x , self.__y)
      self.__hitbox.midbottom = (self.__x-2, self.__y)

  
  def __del__(self) -> None:
    self.__take_shot()
  
class Player(Entity):
  
  def __init__(self, w: int, h: int, parent, screen: Surface) -> None:
    self.__max_hp = 250
    self.__hp = 250
    self.__screen = screen
    self.__p = parent
    self.__shots = []
    self.__parent_w = w
    self.__parent_h = h
    self.__w = w//13
    self.__h = h//7
    self.__speed = 10
    self.__x = w//2
    self.__y = h - self.__h
    self.__sprites = {
      1: transform.scale(image.load('./Sprites/Base_Rocket.png').convert(), (self.__w, self.__h)),
      2: transform.scale(image.load('./Sprites/Base_Rocket_fire.png').convert(), (self.__w, self.__h)),
      3: transform.scale(image.load('./Sprites/Base_Rocket_shot.png').convert(), (self.__w, self.__h)),
      4: transform.scale(image.load('./Sprites/Base_Rocket_shot_fire.png').convert(), (self.__w, self.__h)),
    }
    self.__hurt_sprites = {
      1: self.hurt_sprite(self.__sprites[1]),
      2: self.hurt_sprite(self.__sprites[2]),
      3: self.hurt_sprite(self.__sprites[3]),
      4: self.hurt_sprite(self.__sprites[4]),
    }
    self.strip_background()
    self.rect = self.__sprites[1].get_rect(topleft = (self.__x, self.__y))
    self.__shot = False
    self.__last_shot = None
    self.__shot_CD = self.__p.fps//3
    self.__animation_CD = self.__p.fps//6
    self.__hurt_CD = self.__p.fps//12
    self.__hurt = False
    self.aff = 'good'
    self.shotcount = 0
    self.__alive = True
    self.__hitbox = Rect((self.__x + self.__w//1.65, self.__y + self.__h//4), (self.__w-self.__w//1.65, self.__h-self.__h//4))
    self.__sounds = {
      1: mixer.Sound('./Soundeffects/undertale-damage-taken.mp3'),
      2: mixer.Sound('./Soundeffects/capper_shoot.mp3')
    }
    self.__regulate_sounds()
    self.__healthbar= HealthBar(self.__w, self.__h//3, self.__screen, './Sprites/Red_heart.png', self.__h//3, self.__h//3)

  
  def get_hitbox(self) -> Rect:
    return self.__hitbox
  
  def __regulate_sounds(self) -> None:
    self.__sounds[1].set_volume(0.08)
    self.__sounds[2].set_volume(0.02)
  
  def hurt_sprite(self, original: Surface) -> Surface:
    sprite = original.copy()
    pixel_array = surfarray.pixels3d(sprite)    
    r, g, b = pixel_array[:,:,0], pixel_array[:,:,1], pixel_array[:,:,2]
    brightness = (r + g + b) / 3
    bright_mask = brightness > 50    
    pixel_array[bright_mask, 0] = np.minimum(r[bright_mask] * 1.5, 255) 
    pixel_array[bright_mask, 1] = g[bright_mask] * 0.5   
    pixel_array[bright_mask, 2] = b[bright_mask] * 0.5     
    return sprite
    
  
  def strip_background(self) -> None:
    for i in self.__sprites.values():
      i.set_colorkey((0, 0, 0))
    for i in self.__hurt_sprites.values():
      i.set_colorkey((0, 0, 0))
      
  def get_parent(self):
    return self.__p
  
  def shoot(self) -> None:
    if self.__last_shot is not None:
      if self.__shot_CD == 0:
        self.__shot = True
        self.__last_shot = self.__p.get_timer()
        self.__shot_CD = self.__p.fps//3
        self.__animation_CD = self.__p.fps//6
        self.__shots.append(Shot(self.__parent_w, self.__parent_h, self, self.__screen))
        self.__sounds[2].play()
    else:
      self.__shot = True
      self.__last_shot = self.__p.get_timer()
      self.__shot_CD = self.__p.fps//3
      self.__animation_CD = self.__p.fps//6
      self.__shots.append(Shot(self.__parent_w, self.__parent_h, self, self.__screen))
      self.__sounds[2].play()
  
  def get_shots(self) -> np.ndarray:
    return self.__shots
  
  def move(self, dir: int) -> None:
    self.__x += dir*self.__speed
    self.rect.center = (self.__x + self.__w//2, self.__y + self.__h//2)
    self.__hitbox.center = (self.__x + self.__w//2 - 3, self.__y + self.__h//2)

  def logic(self) -> None:
    if self.__hurt:
      if self.__hurt_CD >0:
        self.__hurt_CD-=1
      else:
        self.__hurt = False
        self.__hurt_CD = self.__p.fps//12
    
    if self.__animation_CD>0:
      self.__animation_CD-=1
    else:
      self.__animation_CD = 0
      
    if self.__shot_CD>0:
      self.__shot_CD-=1
    else:
      self.__shot_CD = 0
      
    if self.__x >= self.__parent_w - self.__w:
      self.__x = self.__parent_w - self.__w
    
    if self.__x <= 0:
      self.__x = 0
    
    if self.__last_shot is not None:  
      if self.__animation_CD == 0:
        self.__shot = False
        
    if self.shotcount > 0:
      self.__shots = [i for i in self.__shots if i.get_state()]
    
    if self.__hp<=0:
      self.__alive = False
      
  def draw(self) -> None:
    if not self.__hurt:
      offset_x = 0
      offset_y = 0
      if (self.__p.get_timer()//10)%2 == 0:
        if self.__shot is True:
          self.__screen.blit(self.__sprites[3], self.rect.topleft)
        else:
          self.__screen.blit(self.__sprites[1], self.rect.topleft)
      else:
        if self.__shot is True:
          self.__screen.blit(self.__sprites[4], self.rect.topleft)
        else:
          self.__screen.blit(self.__sprites[2], self.rect.topleft)
    else:
      offset_x = np.random.choice([-10, -9, -8] + [10, 9, 8])
      offset_y = np.random.choice([-10, -9, -8] + [10, 9, 8])
      if (self.__p.get_timer()//10)%2 == 0:
        if self.__shot is True:
          self.__screen.blit(self.__hurt_sprites[3], self.rect.topleft)
        else:
          self.__screen.blit(self.__hurt_sprites[1], self.rect.topleft)
      else:
        if self.__shot is True:
          self.__screen.blit(self.__hurt_sprites[4], self.rect.topleft)
        else:
          self.__screen.blit(self.__hurt_sprites[2], self.rect.topleft)
    self.__healthbar.draw(offset_x=offset_x, offset_y=offset_y)
    # draw.rect(self.__screen, (255, 255, 255), self.__hitbox, 2)
      
  def get_state(self) -> bool:
    return self.__alive
  
  def take_dmg(self, amt: int|float) -> None:
    self.__hp -= amt
    self.__healthbar.update(self.__hp/self.__max_hp)
  
  def trigger_hurt(self) -> None:
    self.__hurt = True
    self.__sounds[1].play()
  
  def check_hp(self) -> bool:
    return self.__hp == self.__max_hp
  
  def collision(self, other) -> None:
    '''Redundant for Player'''
    pass

class FallingStar(Entity):
  def __init__(self, w: int, h: int, parent, screen: Surface) -> None:
    self.__screen = screen
    self.__h = h//12
    self.__w = w//22
    self.__parent_h = h
    self.__parent_w = w
    self.__p = parent
    self.__origin = transform.scale(image.load('./Sprites/StarProjectile.png').convert(), (self.__w, self.__h)) 
    self.__hurt_star_origin = transform.scale(image.load('./RRS/StarProjectileHurt.png').convert(), (self.__w, self.__h))
    self.__sprite = self.__origin
    self.__hurt_star = self.__hurt_star_origin
    self.__dmg = 5
    self.__active = True
    self.__speed = 4
    self.__hp = 6 
    self.__x, self.__y = np.random.randint(0, w), np.random.randint(-self.__h-10, -self.__h)
    self.rect = self.__sprite.get_rect(topleft = (self.__x, self.__y))
    self.__hit = False
    self.__hurt = False
    self.__hurt_CD = self.__p.fps//12
    self.__spin_speed = 12
    self.__angle = 0
    self.aff = 'evil'
    self.__hitbox = Rect((self.__x + self.__w//3.5, self.__y + self.__h//4), (self.__w-self.__w//3.5, self.__w-self.__w//3.5))
    self.__sounds = {
      1: mixer.Sound('./Soundeffects/undertale-ding.mp3'),
    }
    self.__regulate_sounds()
    self.strip_background()
    self.__add_star()
  
  def get_hitbox(self) -> Rect:
    return self.__hitbox
  
  def __add_star(self) -> None:
    self.__p.current_stars +=1
    
  def __despawn_star(self) -> None:
    self.__p.current_stars -=1
  
  def __regulate_sounds(self) -> None:
    self.__sounds[1].set_volume(0.04)
  
  def deal_dmg(self, other: Player) -> None:
    other.take_dmg(self.__dmg)
  
  def collision(self, other: Player) -> None:
    if not self.__hit:
      if self.__hitbox.colliderect(other.get_hitbox()):
        self.deal_dmg(other)
        self.__hit = True
        other.trigger_hurt()

  def logic(self):
    if self.rect.topleft[1] > self.__parent_h:
      self.__active = False
    
    if self.__hp <=0:
      self.__active = False
      
    if self.__hurt:
      if self.__hurt_CD>0:
        self.__hurt_CD-=1
      else:
        self.__hurt = False
        self.__hurt_CD = self.__p.fps//12
        
    if self.__angle >=360:
      self.__angle = 0
  
  def draw(self):
    if not self.__hurt:
      self.__screen.blit(self.__sprite, (self.rect.topleft))
    else:
      self.__screen.blit(self.__hurt_star, (self.rect.topleft))
    # draw.rect(self.__screen, (255, 255, 255), self.__hitbox, 2)
    
  def get_state(self) -> bool:
    return self.__active
  
  def move(self):
    if self.__p.get_timer()%3 == 0:
      self.__angle = (self.__angle + self.__spin_speed)
      self.__sprite = transform.rotate(self.__origin, self.__angle)
      self.__hurt_star = transform.rotate(self.__hurt_star_origin, self.__angle)
      self.rect = self.__sprite.get_rect(center=self.rect.center)   
    self.__y += self.__speed
    self.rect.center = (self.__x, self.__y)
    self.__hitbox.center = (self.__x, self.__y)
  
  def strip_background(self) -> None:
    self.__origin.set_colorkey((0, 0, 0))
    self.__hurt_star_origin.set_colorkey((0, 0, 0))
  
  def take_dmg(self, amt: int) -> None:
    self.__hp-=amt
  
  def trigger_hurt(self) -> None:
    self.__hurt = True
    self.__sounds[1].play()

  def __del__(self) -> None:
    self.__despawn_star()
    
class ShootingStar(Entity):
  
  def __init__(self, w: int, h: int, parent, screen: Surface) -> None:
    self.__screen = screen
    self.__h = h//11
    self.__w = w//21
    self.__parent_h = h
    self.__parent_w = w
    self.__p = parent
    self.aff = 'evil'
    self.__origin = {
      1: transform.scale(image.load('./RRS/StarProjectileR1.png').convert(), (self.__w, self.__h)),
      2: transform.scale(image.load('./RRS/StarProjectileR2.png').convert(), (self.__w, self.__h)),
      3: transform.scale(image.load('./RRS/StarProjectileR3.png').convert(), (self.__w, self.__h)),
      4: transform.scale(image.load('./RRS/StarProjectileR4.png').convert(), (self.__w, self.__h)),
      5: transform.scale(image.load('./RRS/StarProjectileR5.png').convert(), (self.__w, self.__h)),
      6: transform.scale(image.load('./RRS/StarProjectileR6.png').convert(), (self.__w, self.__h)),
      7: transform.scale(image.load('./RRS/StarProjectileR7.png').convert(), (self.__w, self.__h)),
      8: transform.scale(image.load('./RRS/StarProjectileR8.png').convert(), (self.__w, self.__h)),
      9: transform.scale(image.load('./RRS/StarProjectileR9.png').convert(), (self.__w, self.__h)),
      10: transform.scale(image.load('./RRS/StarProjectileR10.png').convert(), (self.__w, self.__h)),
      11: transform.scale(image.load('./RRS/StarProjectileR11.png').convert(), (self.__w, self.__h)),
      12: transform.scale(image.load('./RRS/StarProjectileR12.png').convert(), (self.__w, self.__h)),
      13: transform.scale(image.load('./RRS/StarProjectileR13.png').convert(), (self.__w, self.__h)),
      14: transform.scale(image.load('./RRS/StarProjectileR14.png').convert(), (self.__w, self.__h)),
    }
    self.__origin_keys = list(self.__origin.keys())
    self.__original = self.__origin[np.random.choice(self.__origin_keys)]
    self.__sprite = self.__original
    self.__dmg = 10
    self.__active = True
    self.__hp = np.inf
    self.__x, self.__y = np.random.choice(np.arange(-self.__w - 30, -self.__w).tolist() + np.arange(self.__parent_w + self.__w, self.__parent_w + self.__w + 30).tolist()), np.random.randint(0, self.__parent_h//2)
    self.rect = self.__sprite.get_rect(topleft = (self.__x, self.__y))
    self.__hit = False
    self.__spin_speed = 19
    self.FRAMESKIP = 4
    self.__angle = 0
    self.__intercept, self.__slope = linear_coefficients(self.__p.get_player_coords(), self.rect.topleft)
    self.__hitbox = Rect((self.__x + self.__w//3.5, self.__y + self.__h//4), (self.__w-self.__w//3.5, self.__w-self.__w//3.5))
    self.__sounds = {
      1: mixer.Sound('./Soundeffects/squeak.mp3'),
      2: mixer.Sound('./Soundeffects/Mana_star.mp3')
    }
    self.__step = self.__step_setter()
    self.__tails = {
      1: 90,
      2: 60,
      3: 30,
    }
    self.__regulate_sounds()
    self.strip_background()
    self.__add_star()
  
  def get_hitbox(self) -> Rect:
    return self.__hitbox
  
  def __add_star(self) -> None:
    self.__p.current_stars +=1
    
  def __despawn_star(self) -> None:
    self.__p.current_stars -=1
  
  def __step_setter(self) -> int:
    if self.rect.centerx<self.__p.get_player_coords()[0]:
      return 6
    elif self.rect.centerx>self.__p.get_player_coords()[0]:
      return -6
    
  def __regulate_sounds(self) -> None:
    self.__sounds[1].set_volume(0.08)
    self.__sounds[2].set_volume(0.01)
  
  def __trail(self, original: Surface, alpha: int) -> Surface:
    sprite = original.copy()
    sprite.set_alpha(alpha)
    return sprite


  
  def __linear_function(self, x: int) -> None:
    return self.__intercept + self.__slope*x
  
  def collision(self, other) -> None:
    if not self.__hit:
      if self.__hitbox.colliderect(other.get_hitbox()):
        self.deal_dmg(other)
        self.__hit = True
        other.trigger_hurt()

  def logic(self) -> None:
    if self.rect.topleft[1] > self.__parent_h:
      self.__active = False

        
    if self.__angle >=360:
      self.__angle = 0
      
    if self.__p.get_timer()%(self.__p.fps//3) == 0:
      self.__sounds[2].play()
  
  
  def draw(self) -> None: 
    tx = self.rect.topleft[0]
    self.__screen.blit(self.__trail(self.__sprite, self.__tails[3]), (tx-self.__step*8.5, self.__linear_function(tx-self.__step*8.5)))
    self.__screen.blit(self.__trail(self.__sprite, self.__tails[2]), (tx-self.__step*5.5, self.__linear_function(tx-self.__step*5.5)))
    self.__screen.blit(self.__trail(self.__sprite, self.__tails[1]), (tx-self.__step*2.5, self.__linear_function(tx-self.__step*2.5)))
    self.__screen.blit(self.__sprite, self.rect.topleft)
    # draw.rect(self.__screen, (255, 255, 255), self.__hitbox, 2)
   
  def get_state(self) -> bool:
    return self.__active
  
  def move(self) -> None:
    if (self.__p.get_timer()%(self.__p.fps//15)) == 0:
      self.__original = self.__origin[(self.__p.get_timer()//(self.__p.fps//16))%14+1]
    if self.__p.get_timer()%self.FRAMESKIP == 0:
      self.__angle = (self.__angle + self.__spin_speed)
      self.__sprite = transform.rotate(self.__original, self.__angle)
      self.rect = self.__sprite.get_rect(center=self.rect.center)   
    self.__x += self.__step
    self.__y = self.__linear_function(self.__x)
    self.rect.topleft = (self.__x, self.__y)
    self.__hitbox.center = self.rect.center
  
  def strip_background(self) -> None:
    self.__sprite.set_colorkey((0, 0, 0))
    for val in self.__origin.values():
      val.set_colorkey((0, 0, 0))
  
  def deal_dmg(self, other: Player) -> None:
    other.take_dmg(self.__dmg)
    
  def take_dmg(self, amt: int) -> None:
    self.__hp-=amt
    
  def trigger_hurt(self) -> None:
    self.__sounds[1].play()
    
  def __del__(self) -> None:
    self.__despawn_star()

class ShockerBreaker(Entity):
  def __init__(self, w: int, h: int, parent, screen: Surface) -> None:
    self.__screen = screen
    self.__h = h
    self.__w = w//15
    self.__sound_played = False
    self.__p = parent
    self.__x = np.random.randint(0, w-self.__w)
    self.__y = 0
    self.__active = True
    self.__timer = 0
    self.aff = 'evil'
    self.__warning = transform.scale(image.load('./Sprites/Warning.png').convert(), (self.__w, self.__w))
    self.__sprite = {
      1:transform.scale(image.load('./ShockerBreaker/ShockerBreaker1.png').convert(), (self.__w, self.__h)),
      2:transform.scale(image.load('./ShockerBreaker/ShockerBreaker9.png').convert(), (self.__w, self.__h)),
      3:transform.scale(image.load('./ShockerBreaker/ShockerBreaker3.png').convert(), (self.__w, self.__h)),
      4:transform.scale(image.load('./ShockerBreaker/ShockerBreaker11.png').convert(), (self.__w, self.__h)),
      5:transform.scale(image.load('./ShockerBreaker/ShockerBreaker5.png').convert(), (self.__w, self.__h)),
      6:transform.scale(image.load('./ShockerBreaker/ShockerBreaker13.png').convert(), (self.__w, self.__h)),
      7:transform.scale(image.load('./ShockerBreaker/ShockerBreaker7.png').convert(), (self.__w, self.__h)),
      8:transform.scale(image.load('./ShockerBreaker/ShockerBreaker8.png').convert(), (self.__w, self.__h)),
      9:transform.scale(image.load('./ShockerBreaker/ShockerBreaker2.png').convert(), (self.__w, self.__h)),
      10:transform.scale(image.load('./ShockerBreaker/ShockerBreaker10.png').convert(), (self.__w, self.__h)),
      11:transform.scale(image.load('./ShockerBreaker/ShockerBreaker4.png').convert(), (self.__w, self.__h)),
      12:transform.scale(image.load('./ShockerBreaker/ShockerBreaker12.png').convert(), (self.__w, self.__h)),
      13:transform.scale(image.load('./ShockerBreaker/ShockerBreaker6.png').convert(), (self.__w, self.__h)),
      14:transform.scale(image.load('./ShockerBreaker/ShockerBreaker14.png').convert(), (self.__w, self.__h)),
    }
    self.__current = self.__sprite[np.random.choice(list(self.__sprite.keys()))]
    self.__sounds = {
      1: mixer.Sound('./Soundeffects/Shocker Breaker.mp3'),
    }
    self.rect = Rect((self.__x, self.__h - self.__w//4), (self.__w, 1))
    self.__truerect = self.__sprite[1].get_rect(topleft=(self.__x, self.__y))
    self.__warning_rect = self.__warning.get_rect(topleft = (self.__x, h-self.__w))
    self.__dmg = 35
    self.__hit = False
    self.__hitbox = Rect((self.__x + self.__w//11, self.__y + h*0.9), (self.__w-self.__w//9, h*0.05))
    self.strip_background()
    self.__regulate_sounds()
    self.__add_breaker()
  
  def get_hitbox(self) -> Rect:
    return self.__hitbox
  
  def __add_breaker(self) -> None:
    self.__p.current_ShockerBreakers +=1
    
  def __take_breaker(self) -> None:
    self.__p.current_ShockerBreakers -=1
  
  def __regulate_sounds(self) -> None:
    self.__sounds[1].set_volume(0.05)
    
  def collision(self, other: Player) -> None:
    if self.__timer> self.__p.fps and not self.__hit:
      if self.__hitbox.colliderect(other.get_hitbox()):
        self.deal_dmg(other)
        self.__hit = True
        other.trigger_hurt()

  def logic(self) -> None:
    self.__timer+=1
    if self.__timer>self.__p.fps:
      if self.__timer >= 1.12*self.__p.fps:
        self.__active = False
      if not self.__sound_played: 
        if self.__timer == self.__p.fps+1:
          self.__sounds[1].play()
          self.__sound_played = True
      if self.__timer%(self.__p.fps//15) == 0:
        self.__current = self.__sprite[(self.__p.get_timer()//self.__timer)%14+1]

  def draw(self) -> None:
    if self.__timer <= self.__p.fps:
      if self.__timer%(self.__p.fps//10) <= 1: 
        self.__screen.blit(self.__warning, self.__warning_rect.topleft)
    else:
      if self.__timer%2 == 0:
        self.__screen.blit(self.__current, self.__truerect.topleft)
    # draw.rect(self.__screen, (255, 255, 255), self.__hitbox, 2)
    
  def get_state(self) -> bool:
    return self.__active
  
  def move(self) -> None:
    '''Redundant for Shocker Breaker'''
    pass
  
  def deal_dmg(self, other: Player) -> None:
    other.take_dmg(self.__dmg)
  
  def strip_background(self) -> None:
    for sprite in self.__sprite.values():
      sprite.set_colorkey((0, 0, 0))
    self.__warning.set_colorkey((0, 0, 0))
      
  def __del__(self) -> None:
    self.__take_breaker()

class StarBomb(Entity):

  def __init__(self, w: int, h: int, parent, screen: Surface) -> None:
    self.__screen = screen
    self.__w = w//5
    self.__ph = h
    self.__h = w//5
    self.__p = parent
    self.__x, self.__y = np.random.choice([-self.__w, self.__w+w]), np.random.randint(0, h//2)
    self.__dest_x, self.__dest_y = np.random.randint(w//4, w*0.75), np.random.randint(h*0.75, h)
    self.__intercept, self.__slope = linear_coefficients((self.__dest_x, self.__dest_y), (self.__x, self.__y))
    self.__speed = self.__step_setter()
    self.__dmg = 75
    self.__timer = 0
    self.__active = True
    self.__origin = {
      1: transform.scale(image.load('./StarBombs/StarBomb1.png').convert(), (self.__w, self.__h)),
      2: transform.scale(image.load('./StarBombs/StarBomb2.png').convert(), (self.__w, self.__h)),
      3: transform.scale(image.load('./StarBombs/StarBomb3.png').convert(), (self.__w, self.__h)),
      4: transform.scale(image.load('./StarBombs/StarBomb4.png').convert(), (self.__w, self.__h)),
      5: transform.scale(image.load('./StarBombs/StarBomb5.png').convert(), (self.__w, self.__h)),
      6: transform.scale(image.load('./StarBombs/StarBomb6.png').convert(), (self.__w, self.__h)),
      7: transform.scale(image.load('./StarBombs/StarBomb7.png').convert(), (self.__w, self.__h)),
      8: transform.scale(image.load('./StarBombs/StarBomb8.png').convert(), (self.__w, self.__h)),
      9: transform.scale(image.load('./StarBombs/StarBomb9.png').convert(), (self.__w, self.__h)),
      10: transform.scale(image.load('./StarBombs/StarBomb10.png').convert(), (self.__w, self.__h)),
    }
    self.__sprite = self.__origin[1]
    self.rect = self.__sprite.get_rect(topleft=(self.__x, self.__y))
    self.__exp_center = self.rect.center
    self.__r = self.__w*1.5
    self.__r_draw = 0
    self.__r_step = self.__r / (self.__p.fps*0.25)
    self.__hit = False
    self.__sounds = {
      1: mixer.Sound('./Soundeffects/asriels-star-blazing-summon.mp3'),
      2: mixer.Sound('./Soundeffects/undertale-bomb-explosion.mp3')
    }
    self.__chaos_colors ={
      1:(79, 16, 9),
      2:(71, 12, 4),
      3:(135, 78, 7),
      4:(128, 81, 11),
      5:(143, 69, 4),
      6:(115, 41, 0),
      7:(125, 111, 27),
      8:(161, 132, 3),
      9:(120, 120, 43),
      10:(93, 105, 44),
      11:(57, 156, 0),
      12:(50, 105, 18),
      13: (28, 77, 1),
      14:(12, 125, 51),
      15:(78, 133, 111),
      16:(7, 131, 140),
      17:(0, 111, 153),
      18:(1, 10, 77),
      19:(25, 23, 77),
      20:(34, 13, 66),
      21:(102, 0, 96),
      22:(69, 9, 51),
      23:(71, 30, 55),
      24:(77, 1, 17),
      25:(107, 56, 1),
      26:(102, 96, 32),
      27:(0, 54, 28),
      28:(92, 4, 81),
      29:(4, 88, 92),
      30:(64, 0, 0)
    }
    self.__tails = {
      1: 135,
      2: 85,
      3: 55,
    }
    self.__cur_color = self.__chaos_colors[1]
    self.__add_bomb()
    self.strip_background()
    self.regulate_sounds()

  def __trail(self, original: Surface, alpha: int) -> Surface:
    sprite = original.copy()
    sprite.set_alpha(alpha)
    
    return sprite
  
  def __add_bomb(self) -> None:
    self.__p.current_bombs+=1

  def __take_bomb(self) -> None:
    self.__p.current_bombs-=1

  def __linear_function(self, x: int) -> int|float:
    return self.__intercept + self.__slope * x
  
  def __step_setter(self) -> int:
    if self.__x < self.__dest_x:
      return np.random.choice([4, 3, 5])
    else:
      return np.random.choice([-4, -3, -5])

  def deal_dmg(self, other: Player) -> None:
    other.take_dmg(self.__dmg)

  def collision(self, other: Player) -> None:
    if self.__p.fps*4 <= self.__timer <= self.__p.fps*4.25 and not self.__hit:
      px = other.rect.centerx
      py = other.rect.centery
      if (px - self.__exp_center[0])**2 + (py - self.__exp_center[1])**2 <= self.__r**2:
        self.deal_dmg(other)
        self.__hit = True
        other.trigger_hurt()

  def logic(self) -> None:
    
    if self.__timer > self.__p.fps*4.25:
      self.__active = False
    
    if self.__timer%(self.__p.fps*0.75)==0 and self.__p.fps*4 > self.__timer :
      self.__sounds[1].play()
    
    if self.__timer%(self.__p.fps//15) == 0:
      self.__cur_color = self.__chaos_colors[(self.__p.get_timer()//(self.__p.fps//16))%30+1]
    
    if self.__p.fps*4 <= self.__timer <= self.__p.fps*4.25:
      self.__r_draw+=self.__r_step
    if self.__timer == self.__p.fps*4:
      self.__sounds[2].play()
    
    self.__timer+=1
  
  def draw(self) -> None:
    if self.__timer < self.__p.fps*4:
      # tx = self.rect.topleft[0]     
      # self.__screen.blit(self.__trail(self.__sprite, self.__tails[3]), (tx-self.__speed*40.5, self.__linear_function(tx-self.__speed*40.5)))
      # self.__screen.blit(self.__trail(self.__sprite, self.__tails[2]), (tx-self.__speed*27, self.__linear_function(tx-self.__speed*27)))
      # self.__screen.blit(self.__trail(self.__sprite, self.__tails[1]), (tx-self.__speed*13.5, self.__linear_function(tx-self.__speed*13.5)))
      self.__screen.blit(self.__sprite, self.rect.topleft)
    elif self.__p.fps*4 <= self.__timer <= self.__p.fps*4.25:
      draw.circle(self.__screen, self.__cur_color, self.__exp_center, self.__r_draw)
    draw.circle(self.__screen, self.__cur_color, self.__exp_center, self.__r, 2)
  
  def get_state(self) -> bool:
    return self.__active

  def move(self) -> None:
    if (self.__p.get_timer()%(self.__p.fps//15)) == 0:
      self.__sprite = self.__origin[(self.__p.get_timer()//(self.__p.fps//16))%10+1]
    if self.__timer < self.__p.fps*4:
      self.__x += self.__speed
      self.__y = self.__linear_function(self.__x)
      self.rect.topleft = (self.__x, self.__y)
      self.__exp_center = self.rect.center
  
  def strip_background(self) -> None:
    for i in self.__origin.values():
      i.set_colorkey((0, 0, 0))
  
  def regulate_sounds(self) -> None:
    self.__sounds[1].set_volume(0.05)
    self.__sounds[2].set_volume(0.1)

  def __del__(self) -> None:
    self.__take_bomb()

class Boss(Entity):
  
  def __init__(self, w: int, h: int, parent, screen: Surface) -> None:
    self.__played1 = False
    self.__played2 = False
    self.__played3 = False
    self.__phase = 1
    self.__maxhp = 400
    self.__hp = 400
    self.__w = w//3
    self.__h = h//1.1
    self.__x = w//2
    self.__y = -80
    self.__winkCD = 18
    self.__hitCD = 10
    self.__winktimer = 0
    self.__hittimer = 0
    self.__wink = False
    self.__hit = False
    self.__p = parent
    self.__screen = screen
    self.__alive = True
    self.__dir = 1
    self.__curkey = 1
    self.__stage1_keys = [1, 2, 3, 4, 5, 6, 7, 8]
    self.__stage123sprites_nothit = {
      1: transform.scale(image.load('./Boss/Xeroc_bottomleft.png').convert_alpha(), (self.__w, self.__h)),
      2: transform.scale(image.load('./Boss/Xeroc_topright.png').convert_alpha(), (self.__w, self.__h)),
      3: transform.scale(image.load('./Boss/Xeroc_bottomright.png').convert_alpha(), (self.__w, self.__h)),
      4: transform.scale(image.load('./Boss/Xeroc_midbottom.png').convert_alpha(), (self.__w, self.__h)),
      5: transform.scale(image.load('./Boss/Xeroc_midleft.png').convert_alpha(), (self.__w, self.__h)),
      6: transform.scale(image.load('./Boss/Xeroc_midright.png').convert_alpha(), (self.__w, self.__h)),
      7: transform.scale(image.load('./Boss/Xeroc_midtop.png').convert_alpha(), (self.__w, self.__h)),
      8: transform.scale(image.load('./Boss/Xeroc_topleft.png').convert_alpha(), (self.__w, self.__h)),
    }
    self.__stage123sprites_hit = {
      1: transform.scale(image.load('./Boss/Xeroc_bottomleft_hit.png').convert_alpha(), (self.__w, self.__h)),
      2: transform.scale(image.load('./Boss/Xeroc_topright_hit.png').convert_alpha(), (self.__w, self.__h)),
      3: transform.scale(image.load('./Boss/Xeroc_bottomright_hit.png').convert_alpha(), (self.__w, self.__h)),
      4: transform.scale(image.load('./Boss/Xeroc_midbottom_hit.png').convert_alpha(), (self.__w, self.__h)),
      5: transform.scale(image.load('./Boss/Xeroc_midleft_hit.png').convert_alpha(), (self.__w, self.__h)),
      6: transform.scale(image.load('./Boss/Xeroc_midright_hit.png').convert_alpha(), (self.__w, self.__h)),
      7: transform.scale(image.load('./Boss/Xeroc_midtop_hit.png').convert_alpha(), (self.__w, self.__h)),
      8: transform.scale(image.load('./Boss/Xeroc_topleft_hit.png').convert_alpha(), (self.__w, self.__h)),
    }
    self.__stage4_nowink_nohit = {
      1: transform.scale(image.load('./Boss/Xeroc_mid_pulse1.png').convert_alpha(), (self.__w, self.__h)),
      2: transform.scale(image.load('./Boss/Xeroc_mid_pulse2.png').convert_alpha(), (self.__w, self.__h)),
    }
    self.__stage4pulse1_nowink_hit = {
      1: transform.scale(image.load('./Boss/Xeroc_mid_pulse1_hit.png').convert_alpha(), (self.__w, self.__h)),
    }
    self.__stage4pulse2_nowink_hit = {
      1: transform.scale(image.load('./Boss/Xeroc_mid_pulse2_hit.png').convert_alpha(), (self.__w, self.__h)),
    }
    self.__stage4_pulse1_wink_nohit = {
      1: transform.scale(image.load('./Boss/Xeroc_mid_pulse1_wink1.png').convert_alpha(), (self.__w, self.__h)),
      2: transform.scale(image.load('./Boss/Xeroc_mid_pulse1_wink2.png').convert_alpha(), (self.__w, self.__h)),
      3: transform.scale(image.load('./Boss/Xeroc_mid_pulse1_wink3.png').convert_alpha(), (self.__w, self.__h)),
    }
    self.__stage4_pulse2_wink_nohit = {
      1: transform.scale(image.load('./Boss/Xeroc_mid_pulse2_wink1.png').convert_alpha(), (self.__w, self.__h)),
      2: transform.scale(image.load('./Boss/Xeroc_mid_pulse2_wink2.png').convert_alpha(), (self.__w, self.__h)),
      3: transform.scale(image.load('./Boss/Xeroc_mid_pulse2_wink3.png').convert_alpha(), (self.__w, self.__h)),
    }
    self.__stage4_pulse1_wink_hit = {
      1: transform.scale(image.load('./Boss/Xeroc_mid_pulse1_hit_wink1.png').convert_alpha(), (self.__w, self.__h)),
      2: transform.scale(image.load('./Boss/Xeroc_mid_pulse1_hit_wink2.png').convert_alpha(), (self.__w, self.__h)),
      3: transform.scale(image.load('./Boss/Xeroc_mid_pulse1_hit_wink3.png').convert_alpha(), (self.__w, self.__h)),
    }
    self.__stage4_pulse2_wink_hit = {
      1: transform.scale(image.load('./Boss/Xeroc_mid_pulse2_hit_wink1.png').convert_alpha(), (self.__w, self.__h)),
      2: transform.scale(image.load('./Boss/Xeroc_mid_pulse2_hit_wink2.png').convert_alpha(), (self.__w, self.__h)),
      3: transform.scale(image.load('./Boss/Xeroc_mid_pulse2_hit_wink3.png').convert_alpha(), (self.__w, self.__h)),
    }
    self.__sounds = {
      1: mixer.Sound('./Soundeffects/undertale-ding.mp3'),
      2: mixer.Sound('./Soundeffects/EidolonWyrmRoar.mp3'),
      3: mixer.Sound('./Soundeffects/Terraria_boss_summon.mp3'),
      4: mixer.Sound('./Soundeffects/wall-of-flesh-terraria.mp3'),
    }
    self.__sprite = self.__stage123sprites_nothit[1]
    self.rect = self.__sprite.get_rect(midtop = (self.__x, self.__y))
    self.__hitbox = Rect((self.__x - self.__w//3.6, self.__y + self.__h//2.5), (self.__w-self.__w//2.4, 100))
    self.__hitbox1 = Rect((self.__x - self.__w//2.25, self.__y + self.__h//3.5), (self.__w-self.__w//11, 40))
    self.__hitbox2 = Rect((self.__hitbox.centerx-self.__w//26, self.__hitbox.midbottom[1]), (38, 190))
    self.__healthbar = HealthBar(self.__w//2, 80, self.__screen, './Boss/Xeroc_mid.png', 40, 80)
    self.strip_background()
    self.__regulate_sounds()

  def collision(self) -> None:
    '''Redundant for the Boss Class'''
    pass

  def get_hitbox(self) -> Rect:
    return [self.__hitbox, self.__hitbox1, self.__hitbox2]
  
  def logic(self) -> None:
    if self.__y == -80:
      self.__dir = 1
    elif self.__y == -40:
      self.__dir = -1
      
    if self.__p.bombspawned:
      self.__sounds[2].play()
      self.__wink = True
      
    if self.__phase == 4:
      
      if self.__wink and self.__hit:
        if self.__winktimer<self.__winkCD/3 and self.__p.get_timer()%10 < 5:
          self.__sprite = self.__stage4_pulse1_wink_hit[1]
        elif self.__winktimer<self.__winkCD*2/3 and self.__p.get_timer()%10 < 5:
          self.__sprite = self.__stage4_pulse1_wink_hit[2]
        elif self.__winktimer<self.__winkCD and self.__p.get_timer()%10 < 5:
          self.__sprite = self.__stage4_pulse1_wink_hit[3]
          
        if self.__winktimer<self.__winkCD/3 and self.__p.get_timer()%10 >= 5:
          self.__sprite = self.__stage4_pulse2_wink_hit[1]
        elif self.__winktimer<self.__winkCD*2/3 and self.__p.get_timer()%10 >= 5:
          self.__sprite = self.__stage4_pulse2_wink_hit[2]
        elif self.__winktimer<self.__winkCD and self.__p.get_timer()%10 >= 5:
          self.__sprite = self.__stage4_pulse2_wink_hit[3]
          
      elif self.__wink and not self.__hit:
        if self.__winktimer<self.__winkCD/3 and self.__p.get_timer()%10 < 5:
          self.__sprite = self.__stage4_pulse1_wink_nohit[1]
        elif self.__winktimer<self.__winkCD*2/3 and self.__p.get_timer()%10 < 5:
          self.__sprite = self.__stage4_pulse1_wink_nohit[2]
        elif self.__winktimer<self.__winkCD and self.__p.get_timer()%10 < 5:
          self.__sprite = self.__stage4_pulse1_wink_nohit[3]
          
        if self.__winktimer<self.__winkCD/3 and self.__p.get_timer()%10 >= 5:
          self.__sprite = self.__stage4_pulse2_wink_nohit[1]
        elif self.__winktimer<self.__winkCD*2/3 and self.__p.get_timer()%10 >= 5:
          self.__sprite = self.__stage4_pulse2_wink_nohit[2]
        elif self.__winktimer<self.__winkCD and self.__p.get_timer()%10 >= 5:
          self.__sprite = self.__stage4_pulse2_wink_nohit[3]
          
      elif not self.__wink and self.__hit:
        if self.__p.get_timer()%10 < 5:
          self.__sprite = self.__stage4pulse1_nowink_hit[1]
        else:
          self.__sprite = self.__stage4pulse2_nowink_hit[1]
      
      else:
        if self.__p.get_timer()%10 < 5:
          self.__sprite = self.__stage4_nowink_nohit[1]
        else:
          self.__sprite = self.__stage4_nowink_nohit[2] 
          
    elif self.__phase < 4:
      if self.__p.get_timer()%(3*self.__p.fps) == 0:
          self.__curkey = np.random.choice(self.__stage1_keys)
      if not self.__hit:
          self.__sprite = self.__stage123sprites_nothit[self.__curkey]
      else:
        self.__sprite = self.__stage123sprites_hit[self.__curkey]
 
    if self.__wink:
      self.__winktimer+=1
    
    if self.__hit:
      self.__hittimer+=1
      
    if self.__hittimer>= self.__hitCD:
      self.__hit = False
      self.__hittimer = 0
      
    if self.__winktimer >= self.__winkCD:
      self.__wink = False
      self.__winktimer = 0 
    
    if self.__hp == 300:
      if not self.__played1:
        self.__sounds[3].play()
        self.__played1=True
      self.__phase = 2
      self.__p.update_stage(1_000_000, 0, 10, 0.035, 0.01, 0)
      
    # update_stage(self, bombfreq: int, shockerbreaker: int, maxstars: int, 
    # starfalling: float, starshooting: float, breaker: float) -> None:
      
    if self.__hp == 200:
      if not self.__played2:
        self.__sounds[3].play()
        self.__played2=True
      self.__phase = 3
      self.__p.update_stage(1_000_000, 3, 12, 0.04, 0.03, 0.006)
      
    if self.__hp == 100:
      if not self.__played3:
        self.__sounds[4].play()
        self.__played3 = True
      self.__phase = 4
      self.__p.update_stage(10, 6, 14, 0.045, 0.04, 0.006)
    self.__healthbar.update(self.__hp/self.__maxhp)

    if self.__hp<=0:
      self.__alive = False

  def draw(self) -> None:
    offset_x = 0
    offset_y = 100
    self.__screen.blit(self.__sprite, self.rect.topleft)
    self.__healthbar.draw(offset_x=offset_x, offset_y=offset_y)
    # draw.rect(self.__screen, (255, 255, 255), self.__hitbox, 3)
    # draw.rect(self.__screen, (255, 255, 255), self.__hitbox1, 3)
    # draw.rect(self.__screen, (255, 255, 255), self.__hitbox2, 3)
  
  def get_state(self) -> bool:
    return self.__alive
  

  def move(self) -> None:
    self.__y+=self.__dir
    self.rect.midtop = (self.__x, self.__y)
    self.__hitbox.center = (self.__hitbox.centerx, self.__hitbox.centery+self.__dir)
    self.__hitbox1.center = (self.__hitbox1.centerx, self.__hitbox1.centery+self.__dir)
    self.__hitbox2.center = (self.__hitbox2.centerx, self.__hitbox2.centery+self.__dir)
  
  def take_dmg(self, dmg: int) -> None:
    self.__hp -=dmg
  
  def trigger_hurt(self) -> None:
    self.__hit = True
    self.__sounds[1].play()
  

  def strip_background(self) -> None:
    for i in self.__stage123sprites_nothit.values():
      i.set_colorkey((0, 0, 0))
    for i in self.__stage123sprites_hit.values():
      i.set_colorkey((0, 0, 0))
    for i in self.__stage4_nowink_nohit.values():
      i.set_colorkey((0, 0, 0))
    for i in self.__stage4pulse1_nowink_hit.values():
      i.set_colorkey((0, 0, 0))
    for i in self.__stage4pulse2_nowink_hit.values():
      i.set_colorkey((0, 0, 0))
    for i in self.__stage4_pulse1_wink_nohit.values():
      i.set_colorkey((0, 0, 0))
    for i in self.__stage4_pulse2_wink_nohit.values():
      i.set_colorkey((0, 0, 0))
    for i in self.__stage4_pulse1_wink_hit.values():
      i.set_colorkey((0, 0, 0))
    for i in self.__stage4_pulse2_wink_hit.values():
      i.set_colorkey((0, 0, 0))

  def __regulate_sounds(self) -> None:
    self.__sounds[1].set_volume(0.04)
    self.__sounds[2].set_volume(0.2)
    self.__sounds[3].set_volume(0.12)
    self.__sounds[4].set_volume(0.12)
# _______________________ THE END _________________________________#