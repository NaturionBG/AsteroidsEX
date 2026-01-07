from pygame import *
from widgets import Slider
import abc
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
from collections import defaultdict
import pygame_widgets
import time as tm
import json
import glob
from math import floor
import numpy as np
from pygame.font import *



def typewriter_text(screen: Surface, text: str, size: int, c: tuple[int], rc: Rect) -> None:
  font = Font('./fonts/DeterminationSansWebRegular.ttf', size=size)
  surf = font.render(text, True, c, (0, 0, 0))
  rec = surf.get_rect(center=rc.center)
  draw.rect(screen, (255, 255, 255), rc, 3, 6)
  screen.blit(surf, rec)

def typewriter_text_no_rect(screen: Surface, text: str, size: int, c: tuple[int], rc: Rect) -> None:
  font = Font('./fonts/DeterminationSansWebRegular.ttf', size=size)
  surf = font.render(text, True, c, (0, 0, 0))
  rec = surf.get_rect(center=rc.center)
  screen.blit(surf, rec)

class Background:
  def __init__(self, w: int, h: int, speed:int, filename: str):
    self.bg_speed = speed
    self.__bg = transform.scale(image.load(filename).convert(), (w, h))
    self.pos = 0
    self.h = h
    self.w = w
    
  def update(self):
    self.pos += self.bg_speed
        
    if self.pos >= self.h:
      self.pos = 0
  
  def get_bg(self) -> Surface:
    return self.__bg

  
class Cutscene(abc.ABC):
  @abc.abstractmethod
  def __init__(self) -> None:
    pass
  
  @abc.abstractmethod
  def update(self) -> None:
    pass
  
  @abc.abstractmethod
  def draw(self) -> None:
    pass

class IntroCutscene(Cutscene):
  def __init__(self, screen: Surface, w: int, h: int, fps: int) -> None:
    self.__step = 0
    self.__soul_speedup = 0.09 / fps
    self.__soulspeed = 0.005
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
    self.__chaos_choices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    self.__fps = fps
    self.__screen = screen
    self.__w = w
    self.__h = h
    self.__soul_w = self.__w//55
    self.__soul_h = self.__h//28
    self.__soundflag = False
    self.done = False
    self.__counter = 0
    self.__timer = 0
    self.__flowey_w = self.__w//6
    self.__flowey_h = self.__h//5
    self.__flowey_topleft_y = self.__h//2 - self.__flowey_h//2
    self.__flowey_topleft_x = self.__w//2 - self.__flowey_w//2
    self.__sfx = {
      'sonic': mixer.Sound('./Soundeffects/sonic-exe-laugh.mp3'),
      'omega laugh': mixer.Sound('./Soundeffects/Omega_flowey_laugh.mp3'),
      'flowey_typing_normal': mixer.Sound('./Soundeffects/Normal_flowey_talking.mp3'),
      'flowey_typing_evil': mixer.Sound('./Soundeffects/Evil_flowey_talking.mp3'),
      'flowey_one_letter':mixer.Sound('./Soundeffects/Flowey_one_letter.mp3'),
      'savepoint': mixer.Sound('./Soundeffects/savepoint.mp3'),
      'alarm': mixer.Sound('./Soundeffects/omega-flowey-alarm.mp3'),
      'hal1':mixer.Sound('./Soundeffects/hal1.mp3'),
      'chaos': mixer.Sound('./Soundeffects./Sound_of_chaos.mp3')
    }
    self.__set_sound()
    self.__sprites = {k:transform.scale(image.load(v).convert(), (self.__flowey_w, self.__flowey_h)) for k, v in zip([i[10:-4] for i in glob.glob('./Sprites/*.png')], glob.glob('./Sprites/*.png')) if 'soul' not in k}
    self.__souls = [transform.scale(image.load('./Sprites/teal_soul.png').convert_alpha(), (self.__w//55, self.__h//28)), 
                    transform.scale(image.load('./Sprites/Yellow_soul.png').convert_alpha(), (self.__w//55, self.__h//28)), 
                    transform.scale(image.load('./Sprites/Pink_soul.png').convert_alpha(), (self.__w//55, self.__h//28)),
                    transform.scale(image.load('./Sprites/Orange_soul.png').convert_alpha(), (self.__w//55, self.__h//28)),
                    transform.scale(image.load('./Sprites/Green_soul.png').convert_alpha(), (self.__w//55, self.__h//28)),
                    transform.scale(image.load('./Sprites/Blue_soul.png').convert_alpha(), (self.__w//55, self.__h//28))]
    self.__step_times = {
      0: 3*fps,
      1: 5.5*fps,
      2: 5*fps,
      3: 6.5*fps,
      4: 5*fps,
      5: 6.5*fps,
      6: 10*fps,
      7: 6*fps,
      8: 8*fps,
      9: 13*fps,
      10: 8*fps,
      11: 6.5*fps,
      12: 8*fps,
      13: 6*fps,
      14: 8.5*fps,
      15: 6*fps
      
    }
    self.__voicelines = {
      1: "Howdy! I am Flowey! And I am... A FLOWER!",
      2: "But you already know that, do you not? ;)",
      3: "Now, now, I know I gave you a beating last time we'd met",
      4: "...",
      5: "NOTHING IS STOPPING ME FROM DOING IT ALL OVER AGAIN, YOU KNOW?!",
      6: "That is right! Now that the barrier is broken, I have no SOUL left yet again!",
      7: "And that means... NO COMPASSION, MUAHAHA!",
      8: "What's better, I have all the PATHETIC human souls with me!",
      9: "HOW ABOUT... ",
      10: "... ThIs TiMe We PlAy A gAmE a TaD bIt DiFfErEnT fRoM tHe OnE wE'rE uSeD tO?",
      11: "I want to see how well you fare...",
      12: "... without your PATHETIC DETERMINATION! MUAHAAHAHAHA!!",
      15: "NOW BOW BEFORE THE GOD OF THIS WORLD"
    }
    self.__line_speeds ={
      1: 10/fps,
      2: 10/fps,
      3: 10/fps,
      4:1/fps,
      5:11/fps,
      6:11/fps,
      7:8/fps,
      8:9/fps,
      9:1/fps,
      10:11/fps,
      11:7.5/fps,
      12:8/fps,
      15: 8/fps
    }
    self.__textbox_w = self.__w//1.2
    self.__textbox = Rect((self.__w//2 -self.__textbox_w//2, self.__flowey_topleft_y+self.__flowey_h*1.5), (self.__textbox_w, self.__h//9))
    self.__sprite_update()
    
  def __set_sound(self) -> None:
    self.__sfx['flowey_typing_normal'].set_volume(0.2)
    self.__sfx['flowey_typing_evil'].set_volume(0.2)
    self.__sfx['flowey_one_letter'].set_volume(0.5)
    self.__sfx['savepoint'].set_volume(0.1)
    self.__sfx['omega laugh'].set_volume(0.1)
    self.__sfx['omega laugh'].set_volume(0.1)
    self.__sfx['chaos'].set_volume(0.7)
    
  def __chaos_intensify(self) -> None:
    self.__sfx['omega laugh'].set_volume(0.8)
  
  def __sprite_update(self) -> None:
    for sprite in self.__sprites.values():
      sprite.set_colorkey((0, 0, 0))
    for sprite in self.__souls:
      sprite.set_colorkey((0, 0, 0))
  
  def __play_hal1(self) -> None:
    mixer.music.load('./Soundeffects/Hal1.mp3')
    mixer.music.set_volume(0.5)
    mixer.music.play()
  
  def __step_14_chaos(self, x: int, y: int) -> None:
    center_offset_x = x
    center_offset_y = y
    center_x = self.__w//2 + center_offset_x 
    center_y = self.__h//2 + center_offset_y
    r = self.__w//12 + self.__h//12
    speed = 0.27
    rotation = self.__timer * speed
    for i in range(6):
      angle = rotation + i * (2*np.pi / 6)
      x = center_x + np.cos(angle) * r - self.__soul_w/2
      y = center_y + np.sin(angle) * r - self.__soul_h/2
      self.__screen.blit(self.__souls[i], (x, y))

    
  
  def homogenic_step(self, soundname: str) -> None:
    if not self.__soundflag:
      self.__sfx[soundname].play()
      self.__soundflag = True
    if floor(self.__counter) < len(self.__voicelines[self.__step]):
      self.__counter +=self.__line_speeds[self.__step]
    elif floor(self.__counter) >= len(self.__voicelines[self.__step]):
      self.__counter = len(self.__voicelines[self.__step])
      self.__sfx[soundname].stop()
    if self.__timer>self.__step_times[self.__step]:
      self.__step+=1
      self.__timer=0
      self.__soundflag = False
      self.__counter = 0
  
  def update(self) -> None:
    self.__timer+=1
    
    if self.__step == 0:
      if self.__timer==1:
        self.__sfx['sonic'].play()
      
      if self.__timer>self.__step_times[0]:
        self.__step+=1
        self.__timer=0
        
    if self.__step == 1:
      if not mixer.music.get_busy():
        self.__play_hal1()
      self.homogenic_step('flowey_typing_normal')
      
    if self.__step == 2:
      self.homogenic_step('flowey_typing_normal')
    
    if self.__step == 3:
      self.homogenic_step('flowey_typing_normal')
    
    if self.__step == 4:
      if self.__timer%self.__fps == 0 and self.__timer/self.__fps<=3 and self.__timer!=0:
        self.__sfx['flowey_one_letter'].play()
      if floor(self.__counter) < len(self.__voicelines[self.__step]):
        self.__counter +=self.__line_speeds[self.__step]
      elif floor(self.__counter) >= len(self.__voicelines[self.__step]):
        self.__counter = len(self.__voicelines[self.__step])
      if self.__timer>self.__step_times[self.__step]:
        self.__step+=1
        self.__timer=0
        self.__counter = 0
    
    if self.__step == 5:
      if mixer.music.get_busy():
        mixer.music.pause()
      self.homogenic_step('flowey_typing_evil')
    
    if self.__step == 6:
      if not mixer.music.get_busy():
        mixer.music.unpause()
      self.homogenic_step('flowey_typing_normal')
    
    if self.__step == 7:
      if mixer.music.get_busy():
        mixer.music.pause()
      self.homogenic_step('flowey_typing_evil')
      
    if self.__step == 8:
      self.homogenic_step('flowey_typing_evil')
    
    if self.__step == 9:
      if not mixer.music.get_busy():
        mixer.music.unpause()
      if self.__timer%self.__fps == 0 and self.__timer/self.__fps<=12 and self.__timer!=0:
        self.__sfx['flowey_one_letter'].play()
      if floor(self.__counter) < len(self.__voicelines[self.__step]):
        self.__counter +=self.__line_speeds[self.__step]
      elif floor(self.__counter) >= len(self.__voicelines[self.__step]):
        self.__counter = len(self.__voicelines[self.__step])
      if self.__timer>self.__step_times[self.__step]:
        self.__step+=1
        self.__timer=0
        self.__counter = 0
    
    if self.__step == 10:
      if mixer.music.get_busy():
        mixer.music.pause()
      self.homogenic_step('flowey_typing_evil')
    
    if self.__step == 11:
      if not mixer.music.get_busy():
        mixer.music.unpause()
      self.homogenic_step('flowey_typing_normal')
      
    if self.__step == 12:
      if mixer.music.get_busy():
        mixer.music.stop()
      self.homogenic_step('flowey_typing_evil')
    
    if self.__step == 13:
      if self.__timer%self.__fps == 0 and self.__timer/self.__fps<=6 and self.__timer!=0:
        self.__sfx['savepoint'].play()
      if self.__timer>self.__step_times[self.__step]:
        self.__step+=1
        self.__timer=0

    if self.__step == 14:
      if self.__timer == 1:
        self.__sfx['omega laugh'].play()
      if self.__timer == self.__fps:
        self.__sfx['alarm'].play()
      if self.__timer == self.__fps*5.7 + 1:
        self.__sfx['chaos'].play()
      if self.__timer>self.__step_times[self.__step]:
        self.__step+=1
        self.__timer=0
        
    if self.__step == 15:
      self.homogenic_step('flowey_typing_evil')
      
    if self.__step == 16:
      self.done = True
      

  def draw(self) -> None:
    if self.__step == 0:
      self.__screen.fill((0, 0, 0))
      
    if self.__step == 1:
      self.__screen.fill((0, 0, 0))
      self.__screen.blit(self.__sprites['Flowey_base_smile_2'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=self.__textbox)
    
    if self.__step == 2:
      self.__screen.fill((0, 0, 0))
      if self.__timer < self.__fps:
        self.__screen.blit(self.__sprites['Flowy_base_smile'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif self.__fps<=self.__timer <= 2.5*self.__fps:
        self.__screen.blit(self.__sprites['Flowey_wink'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else:
        self.__screen.blit(self.__sprites['Flowy_base_smile'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=self.__textbox)
    
    if self.__step == 3:
      self.__screen.fill((0, 0, 0))
      if self.__timer < self.__fps:
        self.__screen.blit(self.__sprites['Flowy_confused'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif self.__fps<=self.__timer < 2.5*self.__fps:
        self.__screen.blit(self.__sprites['Flowey_apologetic_left'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 2.5*self.__fps<=self.__timer < 3.2*self.__fps:
        self.__screen.blit(self.__sprites['Flowey_apologetic'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 3.2*self.__fps<=self.__timer <= 4.4*self.__fps:
        self.__screen.blit(self.__sprites['Flowey_apologetic_right'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 4.4*self.__fps<self.__timer <= 5.3*self.__fps:
        self.__screen.blit(self.__sprites['Flowey_apologetic'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else:
        self.__screen.blit(self.__sprites['Flowy_base_smile'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=self.__textbox)
      
    if self.__step == 4:
      self.__screen.fill((0, 0, 0))
      if self.__timer < self.__fps*1.8:
        self.__screen.blit(self.__sprites['Flowey_base_smile_2'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif self.__fps*1.8<=self.__timer < 2.9*self.__fps:
        self.__screen.blit(self.__sprites['Flowey_devious_0'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else: 
        self.__screen.blit(self.__sprites['Flowey_devious'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=self.__textbox)
      
    if self.__step == 5:
      self.__screen.fill((0, 0, 0))
      if self.__timer < self.__fps*3:
        self.__screen.blit(self.__sprites['Giant_monster_grin'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else: 
        self.__screen.blit(self.__sprites['Monster_grin_w_tongue'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      offset_x = 0
      offset_y = 0
      if (self.__timer//5)%2 == 0 and self.__timer<=6*self.__fps:
        offset_x = np.random.randint(-5, 5)
        offset_y = np.random.randint(-5, 5)
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=Rect((self.__w//2 -self.__textbox_w//2 + offset_x, self.__flowey_topleft_y+self.__flowey_h*1.5 + offset_y), (self.__textbox_w, self.__h//9)))
    
    if self.__step == 6:
      self.__screen.fill((0, 0, 0))
      if self.__timer < self.__fps*1.5:
        self.__screen.blit(self.__sprites['Flowey_happy_0'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 1.5*self.__fps<=self.__timer < self.__fps*3:
        self.__screen.blit(self.__sprites['Flowey_happy_1'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 3*self.__fps<=self.__timer < self.__fps*4.5:
        self.__screen.blit(self.__sprites['Flowey_faceless'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 4.5*self.__fps<=self.__timer < self.__fps*6:
        self.__screen.blit(self.__sprites['Skull_turning_0'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else: 
        self.__screen.blit(self.__sprites['Skull_turning_1'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=self.__textbox)
    
    if self.__step == 7:
      self.__screen.fill((0, 0, 0))
      if self.__timer < self.__fps*1.5:
        self.__screen.blit(self.__sprites['Skull_turning_2'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 1.5*self.__fps<=self.__timer < self.__fps*2.5:
        self.__screen.blit(self.__sprites['skull_turning_3'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 2.5*self.__fps<=self.__timer < self.__fps*3.5:
        self.__screen.blit(self.__sprites['Skull_turning_4'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else: 
        if (self.__timer//7) % 2 == 0 and self.__timer<=5.3*self.__fps:
          self.__screen.blit(self.__sprites['Skull_turning_4'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
        elif (self.__timer//7) % 2 == 1 and self.__timer<=5.3*self.__fps:
          self.__screen.blit(self.__sprites['Skull_turning_5'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
        else:
          self.__screen.blit(self.__sprites['Skull_turning_4'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      offset_x = 0
      offset_y = 0
      if (self.__timer//5)%2 == 0 and self.__timer<=5.3*self.__fps:
        offset_x = np.random.randint(-5, 5)
        offset_y = np.random.randint(-5, 5)
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=Rect((self.__w//2 -self.__textbox_w//2 + offset_x, self.__flowey_topleft_y+self.__flowey_h*1.5 + offset_y), (self.__textbox_w, self.__h//9)))
    
    if self.__step == 8:
      self.__screen.fill((0, 0, 0))
      if (self.__timer//7) % 2 == 0 and self.__timer<=6.8*self.__fps:
        self.__screen.blit(self.__sprites['Skull_turning_4'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif (self.__timer//7) % 2 == 1 and self.__timer<=6.8*self.__fps:
        self.__screen.blit(self.__sprites['Skull_turning_5'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else:
        self.__screen.blit(self.__sprites['Skull_turning_4'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      offset_x = 0
      offset_y = 0
      if (self.__timer//5)%2 == 0 and self.__timer<6.8*self.__fps:
        offset_x = np.random.randint(-5, 5)
        offset_y = np.random.randint(-5, 5)
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=Rect((self.__w//2 -self.__textbox_w//2 + offset_x, self.__flowey_topleft_y+self.__flowey_h*1.5 + offset_y), (self.__textbox_w, self.__h//9)))
      
    if self.__step == 9:
      self.__screen.fill((0, 0, 0))
      if self.__timer < self.__fps*3:
        self.__screen.blit(self.__sprites['Flowy_base_smile'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 3*self.__fps<=self.__timer < self.__fps*6:
        self.__screen.blit(self.__sprites['Flowey_base_looking_left'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 6*self.__fps<=self.__timer < self.__fps*9:
        self.__screen.blit(self.__sprites['Flowy_base_smile'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 9*self.__fps<=self.__timer < self.__fps*12:
        self.__screen.blit(self.__sprites['Flowey_base_looking_around'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else: 
        self.__screen.blit(self.__sprites['Flowy_base_smile'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=self.__textbox)

    if self.__step == 10:
      self.__screen.fill((0, 0, 0))
      if self.__timer < self.__fps*2:
        self.__screen.blit(self.__sprites['Red_smile_white'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 2*self.__fps<=self.__timer < self.__fps*4.5:
        self.__screen.blit(self.__sprites['Red_smile_red'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else: 
        if (self.__timer//7) % 2 == 0 and self.__timer<=6.8*self.__fps:
          self.__screen.blit(self.__sprites['Red_smile_white'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
        elif (self.__timer//7) % 2 == 1 and self.__timer<=6.8*self.__fps:
          self.__screen.blit(self.__sprites['Red_smile_red'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
        else:
          self.__screen.blit(self.__sprites['Red_smile_red'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      offset_x = 0
      offset_y = 0
      if (self.__timer//5)%2 == 0 and self.__timer<=7*self.__fps:
        offset_x = np.random.randint(-5, 5)
        offset_y = np.random.randint(-5, 5)
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=Rect((self.__w//2 -self.__textbox_w//2 + offset_x, self.__flowey_topleft_y+self.__flowey_h*1.5 + offset_y), (self.__textbox_w, self.__h//9)))
      
    if self.__step == 11:
      self.__screen.fill((0, 0, 0))
      if self.__timer < self.__fps:
        self.__screen.blit(self.__sprites['Flowey_faceless'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif  self.__fps<=self.__timer < self.__fps*2:
        self.__screen.blit(self.__sprites['pumpkin_turning_0'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 2*self.__fps<=self.__timer < self.__fps*3:
        self.__screen.blit(self.__sprites['pumpkin_turning_1'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 3*self.__fps<=self.__timer < self.__fps*4:
        self.__screen.blit(self.__sprites['pumpkin_turning_2'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else:
        self.__screen.blit(self.__sprites['pumpkin_turning_3'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=self.__textbox)
    
    if self.__step == 12:
      self.__screen.fill((0, 0, 0))
      if self.__timer < self.__fps*1.5:
        self.__screen.blit(self.__sprites['pumpkin_turning_4'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif  1.5*self.__fps<=self.__timer < self.__fps*3:
        self.__screen.blit(self.__sprites['pumpkin_turning_5'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 3*self.__fps<=self.__timer < self.__fps*4.5:
        self.__screen.blit(self.__sprites['Pumpkin_turning_6'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      elif 4.5*self.__fps<=self.__timer < self.__fps*6:
        self.__screen.blit(self.__sprites['pumpkin_turning_7'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else:
        self.__screen.blit(self.__sprites['pumpkin_turning_8'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      offset_x = 0
      offset_y = 0
      if (self.__timer//5)%2 == 0 and self.__timer<=7*self.__fps:
        offset_x = np.random.randint(-5, 5)
        offset_y = np.random.randint(-5, 5)
      typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=40, c=(255, 255, 255), rc=Rect((self.__w//2 -self.__textbox_w//2 + offset_x, self.__flowey_topleft_y+self.__flowey_h*1.5 + offset_y), (self.__textbox_w, self.__h//9)))
    
    if self.__step == 13:
      self.__screen.fill((0, 0, 0))
      center_x = self.__w//2
      center_y = self.__h//2
      r = self.__w//12 + self.__h//12
      souls = min(6, self.__timer//self.__fps)
      
      for i in range(souls):
        angle = i * (2*np.pi / 6)
        x = center_x + np.cos(angle) * r - self.__soul_w/2
        y = center_y + np.sin(angle) * r - self.__soul_h/2
        self.__screen.blit(self.__souls[i], (x, y))
      self.__screen.blit(self.__sprites['pumpkin_turning_8'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      
    if self.__step == 14:
      if self.__timer <=1.5*self.__fps:
        self.__screen.fill((0, 0, 0))
        center_x = self.__w//2
        center_y = self.__h//2
        r = self.__w//12 + self.__h//12
        self.__soulspeed+=self.__soul_speedup
        rotation = self.__timer * self.__soulspeed
        
        for i in range(6):
          angle = rotation + i * (2*np.pi / 6)
          x = center_x + np.cos(angle) * r - self.__soul_w/2
          y = center_y + np.sin(angle) * r - self.__soul_h/2
          self.__screen.blit(self.__souls[i], (x, y))
        if (self.__timer//7)%2 == 0 and self.__timer <= 6*self.__fps:
          self.__screen.blit(self.__sprites['pumpkin_turning_7'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
        elif (self.__timer//7)%2 == 1 and self.__timer <= 6*self.__fps:
          self.__screen.blit(self.__sprites['pumpkin_turning_8'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
        else:
          self.__screen.blit(self.__sprites['pumpkin_turning_8'], (self.__flowey_topleft_x, self.__flowey_topleft_y))
      else:
        if self.__timer == 2*self.__fps+1:
          self.__chaos_intensify()
        if self.__timer%10 == 0:
          self.__screen.fill(self.__chaos_colors[np.random.choice(self.__chaos_choices)])
        if (self.__timer//4)%2 == 0 and self.__timer <= 5.7*self.__fps:
          center_offset_x = np.random.randint(-12, 12)
          center_offset_y = np.random.randint(-12, 12)
          self.__step_14_chaos(center_offset_x, center_offset_y)
          self.__screen.blit(self.__sprites['pumpkin_turning_7'], (self.__flowey_topleft_x + center_offset_x , self.__flowey_topleft_y+center_offset_y))
        elif (self.__timer//4)%2 == 1 and self.__timer <= 5.7*self.__fps:
          center_offset_x = np.random.randint(-12, 12)
          center_offset_y = np.random.randint(-12, 12)
          self.__step_14_chaos(center_offset_x, center_offset_y)
          self.__screen.blit(self.__sprites['pumpkin_turning_8'], (self.__flowey_topleft_x+center_offset_x, self.__flowey_topleft_y+center_offset_y))
        elif self.__timer > self.__fps*5.7:
          if self.__timer <=6.6*self.__fps:
            self.__screen.fill((255, 255, 255))
          elif 6.6*self.__fps <self.__timer <=6.75*self.__fps:
            self.__screen.fill((185,185,185))
          elif 6.75*self.__fps <self.__timer <=6.9*self.__fps:
            self.__screen.fill((142,142,142))
          elif 6.9*self.__fps <self.__timer <= 7.05*self.__fps:
            self.__screen.fill((114,114,114))
          elif 7.05*self.__fps <self.__timer <= 7.2*self.__fps:
            self.__screen.fill((81,81,81))
          elif 7.2*self.__fps <self.__timer <= 7.35*self.__fps:
            self.__screen.fill((40,40,40))
          else:
            self.__screen.fill((0, 0, 0))
            
    if self.__step == 15:
      self.__screen.fill((0, 0, 0))
      if self.__timer <= self.__fps*5:
        center_offset_x = 0
        center_offset_y = 0
        if (self.__timer//5)%2 == 0:
          center_offset_x = np.random.randint(-8, 8)
          center_offset_y = np.random.randint(-8, 8)
        typewriter_text(self.__screen, self.__voicelines[self.__step][0:floor(self.__counter)], size=70, c=(255, 255, 255), rc=Rect((self.__w//2 -self.__textbox_w//2 + center_offset_x, self.__h//2 - self.__h//6 + center_offset_y), (self.__textbox_w, self.__h//3)))
    
  def __del__(self) -> None:
    pass

class LostCutscene(Cutscene):
  def __init__(self, screen: Surface, w: int, h: int, fps: int) -> None:
    self.__timer = 0
    self.__screen = screen
    self.__w = w
    self.__h = h
    self.__fps = fps
    self.__step = 0
    self.__textcounter = 0
    self.__button = Button(self.__screen, self.__w//2 - self.__w//6, self.__h*0.6, self.__w//3, self.__h//4, inactiveColour=(255, 255, 255), hoverColour=(155, 0, 0), shadowDistance = 0.5, pressedColour=(255, 0, 0), radius=10, textHAlign ='centre', textVAlign = 'centre', font=font.Font('fonts/DeterminationMonoWebRegular.ttf', 60), text='QUIT', margin=10)
    self.button_rect = Rect((self.__button.getX(), self.__button.getY()), (self.__button.getWidth(), self.__button.getHeight()))
    self.__button.hide()
    self.__x = w//2
    self.__y = h//2
    self.__rocket_x = w//2
    self.__rocket_y = h//2
    self.__angle = 0
    self.__spinspeed = 0.5
    self.__hover = False
    self.done = False
    self.maxstep = 3
    self.__sprites = {
      1: transform.scale(image.load('./Sprites/Base_Rocket.png').convert(), (self.__w//8, self.__h//4.5)),
      2: transform.scale(image.load('./Sprites/Red_Heart.png').convert(), (self.__w//10, self.__w//10)),
      3: transform.scale(image.load('./Sprites/Rocket_Defeat.png').convert(), (self.__w//10, self.__h//5)),
      4: transform.scale(image.load('./Sprites/Heart_Cracked.png').convert(), (self.__w//10, self.__w//10)),
      5: transform.scale(image.load('./Sprites/Cloud_forming.png').convert_alpha(), (self.__w//10, self.__w//10)),
      6: transform.scale(image.load('./Sprites/Cloud_formed.png').convert(), (self.__w//10, self.__w//10)),
      7: transform.scale(image.load('./Sprites/Cloud_formed1.png').convert(), (self.__w//10, self.__w//10)),
      8: transform.scale(image.load('./Sprites/Skull_Forming.png').convert(), (self.__w//10, self.__w//10)),
      9: transform.scale(image.load('./Sprites/Skull_Formed.png').convert(), (self.__w//10, self.__w//10)),
      10: transform.scale(image.load('./Sprites/Cloud_dissolving.png').convert(), (self.__w//10, self.__w//10)),
      11: transform.scale(image.load('./Sprites/Cloud_dissolved.png').convert(), (self.__w//10, self.__w//10)),
    }
    self.__sounds = {
      1: mixer.Sound('./Soundeffects/asgorevoice.mp3'),
      2: mixer.Sound('./Soundeffects/undertale-soul-shatter.mp3'),
      3: mixer.Sound('./Soundeffects/savepoint.mp3'),
      4: mixer.Sound('./Soundeffects/Hover_Quit.mp3'),
      5: mixer.Sound('./Soundeffects/Press.mp3'),
    }
    self.__lines = {
      'g': ' Game Over!',
      3: 'You cannot give up just yet... Stay DETERMINED!'
    }
    self.__linespeeds = {
      3: 10/self.__fps
    }
    self.__step_times = {
      0: 3*fps,
      1: 2.5*fps,
      2: 3.5*fps,
      3: 47*fps
    }
    self.__go_textbox = Rect((self.__w//2 - w//10, 0), (w//5, h//4))
    self.__asgore_textbox = Rect((self.__w//2 - w//6, h//2-h//6), (w//3, h//3))
    self.__set_sound()
    self.__strip_background()

  def __set_sound(self) -> None:
    self.__sounds[1].set_volume(0.2)
    self.__sounds[2].set_volume(0.4)
    self.__sounds[3].set_volume(0.3)
    self.__sounds[4].set_volume(0.05)
    self.__sounds[5].set_volume(0.1)

  def __strip_background(self) -> None:
    for i in self.__sprites.values():
      i.set_colorkey((0, 0, 0))
  
  def end(self) -> None:
    self.__sounds[5].play()
    tm.sleep(0.2)
    self.done = True
  
  def update(self) -> None:
    self.__timer+=1

    if self.__step == 0: 
      if self.__timer == 1:
        mixer.music.load('./Soundeffects/Game_Over.mp3')
        self.__sounds[3].play()
        self.__button.show()
      if self.__timer>self.__step_times[0]:
        self.__timer = 0
        self.__step+=1
        
    if self.__step == 1:
      self.__angle-=self.__spinspeed
      self.__rocket_x+=1
      self.__rocket_y+=8
      if self.__timer == 1:
        self.__sounds[3].play()
      if self.__timer>self.__step_times[1]:
        self.__timer = 0
        self.__step+=1
    
    if self.__step == 2:
      if self.__timer == 1:
        self.__sounds[2].play()
      if self.__timer>self.__step_times[2]:
        self.__timer = 0
        self.__step+=1
    
    if self.__step == 3:
      mouse_pos = mouse.get_pos()
      if self.button_rect.collidepoint(mouse_pos) and not self.__hover:
        self.__sounds[4].play()
        self.__hover = True
      elif not self.button_rect.collidepoint(mouse_pos):
        self.__hover = False
      if floor(self.__textcounter)<len(self.__lines[3]):
        self.__textcounter+=self.__linespeeds[3]
      else:
        self.__textcounter=len(self.__lines[3])
        self.__sounds[1].stop()
      if self.__timer == 1:
        self.__sounds[1].play()
        mixer.music.play()
      if self.__timer>self.__step_times[3]:
        self.done = True
      events = event.get()
      self.__button.listen(events)
      pygame_widgets.update(events)
    
      
  def draw(self) -> None:
    if self.__step == 0:
      self.__screen.fill((0, 0, 0))
      self.__screen.blit(self.__sprites[1], self.__sprites[1].get_rect(center=(self.__x, self.__y)).topleft)
    
    if self.__step == 1:
      self.__screen.fill((0, 0, 0))
      self.__screen.blit(self.__sprites[2], self.__sprites[2].get_rect(center=(self.__x, self.__y)).topleft)
      self.__screen.blit(transform.rotate(self.__sprites[3], self.__angle), transform.rotate(self.__sprites[3], self.__angle).get_rect(center=(self.__rocket_x, self.__rocket_y)).topleft)
    
    if self.__step == 2:
      self.__screen.fill((0, 0, 0))
      if self.__timer <= 1.4*self.__fps:
        self.__screen.blit(self.__sprites[4], self.__sprites[4].get_rect(center=(self.__x, self.__y)).topleft)
      elif 1.4*self.__fps < self.__timer <= 1.5*self.__fps:
        self.__screen.blit(self.__sprites[5], self.__sprites[5].get_rect(center=(self.__x, self.__y)).topleft)
      elif 1.5*self.__fps < self.__timer <= 1.6*self.__fps:
        self.__screen.blit(self.__sprites[6], self.__sprites[6].get_rect(center=(self.__x, self.__y)).topleft)
      elif 1.6*self.__fps < self.__timer <= 1.7*self.__fps:
        self.__screen.blit(self.__sprites[7], self.__sprites[7].get_rect(center=(self.__x, self.__y)).topleft)
      elif 1.7*self.__fps < self.__timer <= 1.8*self.__fps:
        self.__screen.blit(self.__sprites[8], self.__sprites[8].get_rect(center=(self.__x, self.__y)).topleft)
      elif 1.8*self.__fps < self.__timer <= 1.9*self.__fps:
        self.__screen.blit(self.__sprites[9], self.__sprites[9].get_rect(center=(self.__x, self.__y)).topleft)
      elif 1.9*self.__fps < self.__timer <= 2*self.__fps:
        self.__screen.blit(self.__sprites[10], self.__sprites[10].get_rect(center=(self.__x, self.__y)).topleft)
      elif 2*self.__fps < self.__timer <= 2.1*self.__fps:
        self.__screen.blit(self.__sprites[11], self.__sprites[11].get_rect(center=(self.__x, self.__y)).topleft)

    if self.__step == 3:
      self.__screen.fill((0, 0, 0))
      self.__button.draw()
      typewriter_text_no_rect(self.__screen, self.__lines['g'], 200, (255, 255, 255), self.__go_textbox)
      typewriter_text_no_rect(self.__screen, self.__lines[3][0:floor(self.__textcounter)], 60, (255, 255, 255), self.__asgore_textbox)
  
  def get_step(self) -> int:
    return self.__step
  
  def __del__(self) -> None:
    pass

class WonCutscene(Cutscene):

  def __init__(self, screen: Surface, w: int, h: int, fps: int, controller) -> None:
    self.__con = controller
    self.__secret = None
    self.__step = -1
    self.__screen = screen
    self.done = False
    self.__w = w
    self.__h = h
    self.__y = -80
    self.__x = w//2
    self.__dir = 1
    self.__fps = fps
    self.maxstep = None
    self.__timer = 0
    self.__soulspeed = 0.005
    self.__textcounter = 0
    self.__expanded = False
    self.__hover = False
    self.__soulR = self.__w//12 + self.__h//12
    self.__retract = 40
    self.__maxR = 0
    self.__expand = 0.1
    self.__last_expand = 0.5
    self.__soundflag = False
    self.__heartstep = 2
    self.__lightexpansion = 10
    self.__light = 0
    self.__bg = Background(self.__w, self.__h, 2, 'BG.jpg')
    self.__sky_after_rain = {
      1: 'All they wanted was to fly up through the sky',
      2: "But they're damned from the moment the spark faded from their eyes",
      3: "Restained by the harsh truth that in the end they're confined",
      4: "To a cage left in the dark of the night!",
      5: "Burned by their fate their mind a desolate land!",
      6: "Having lived a nightmare few could ever understand...",
      7: "And yet... clawing their way out of the cage they still shine!",
      8: "For in their HEART remains their guiding light!"
    }
    self.__reg_voicelines = {
      'g': 'Victory!',
      1: "Huh?",
      2: "Diligent as ever, I see...",
      3: "So, now what...?",
      4: "Do you TRULY believe that this is over?!",
      5: "Remember, you fool!",
      6: "With these souls I can-",
      7: "H-Huh?!",
      8: "W-What are you all doing?! Why do I sense so much hatred towards...",
      9: "...T-towards m-me?! I-i am your MASTER!",
      10: "B-Besides, what have I EVER done to you a-",
      11: "...Dis...loyal...",
      12: "...Trai...tors"
    }
    self.__secret_voicelines = {
      'g': 'Victory!',
      1: "Huh?",
      2: "Diligent as ever, I see...",
      3: "So, now what...?",
      4: "Do you TRULY believe that this is over?!",
      5: "Mark my word!",
      6: "I swear, It-",
      8: "Fascinating.",
      9: "Your reflexes and reaction. And your will.",
      10: "So unlike of a mere mortal.",
      11: "Truly...",
      12: "What a shame...",
      13: "Alas, you lack the ambition to grow more powerful than all else...",
      14: "...To subdue the weak...",
      15: "...Hence, I am afraid I will not be sharing my proposal with you.",
      16: "Though fret not, child.",
      17: "Perhaps...",
      18: "One day you will... reconsider your goals.",
      19: "If so comes to pass...",
      20: "I assure you, we shall meet again.",
      21: "I am certain that, should you reconsider...",
      22: "...You ought to have a chance to prove yourself worthy.",
      23: "But for now, I bid you farewell.",
      24: "Until next time."
    }
    self.__sfx = {
      "Fire": mixer.Sound("./Soundeffects/FireBall.mp3"),
      "GoodFlowey": mixer.Sound("./Soundeffects/Normal_flowey_talking.mp3"),
      "ExoSlash": mixer.Sound("./Soundeffects/ExobladeBeamSlash.mp3"),
      "Glasscrack": mixer.Sound("./Soundeffects/CryogenShieldBreak.mp3"),
      "Glassbreak": mixer.Sound("./Soundeffects/CryogenDeath.mp3"),
      "XerocSpawn": mixer.Sound("./Soundeffects/BossRushTerminusDeactivate.mp3"),
      "XerocDespawn": mixer.Sound("./Soundeffects/BossRushVictory.mp3"),
      "savepoint": mixer.Sound("./Soundeffects/savepoint.mp3"),
      'hover': mixer.Sound("./Soundeffects/Hover_Quit.mp3"),
      'press': mixer.Sound("./Soundeffects/Press.mp3"),
      'serenity': mixer.Sound('./Soundeffects/Serenity.mp3'),
      'asgore': mixer.Sound('./Soundeffects/asgorevoice.mp3'),
    }
    self.__sprites = {
      "XerocPulse1": transform.scale(image.load('./Boss/Xeroc_cutscene_pulse1.png').convert_alpha(), (self.__w//3, self.__h//1.1)),
      "XerocPulse2": transform.scale(image.load('./Boss/Xeroc_cutscene_pulse2.png').convert_alpha(), (self.__w//3, self.__h//1.1)),
      "Rocket": transform.scale(image.load('./Sprites/Base_Rocket.png').convert_alpha(), (self.__w//13, self.__h//7)),
      "XerocStep0Pulse1": transform.scale(image.load('./Boss/Xeroc_mid_pulse1.png').convert_alpha(), (self.__w//3, self.__h//1.1)),
      "XerocStep0Pulse2": transform.scale(image.load('./Boss/Xeroc_mid_pulse2.png').convert_alpha(), (self.__w//3, self.__h//1.1)),
      "BurnedSoul": transform.scale(image.load('./Sprites/burned_soul.png').convert_alpha(), (self.__w//55, self.__h//28)),
      "BurnedSoulD1": transform.scale(image.load('./Sprites/burned_soul_death1.png').convert_alpha(), (self.__w//55, self.__h//28)),
      "BurnedSoulD2": transform.scale(image.load('./Sprites/burned_soul_death2.png').convert_alpha(), (self.__w//55, self.__h//28)),
      "BurnedSoulD3": transform.scale(image.load('./Sprites/burned_soul_death3.png').convert_alpha(), (self.__w//55, self.__h//28)),
      "FloweyHappy1": transform.scale(image.load('./Sprites/Flowey_happy_0.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyHappy2": transform.scale(image.load('./Sprites/Flowey_happy_1.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyHappyR": transform.scale(image.load('./Sprites/Flowey_base_looking_around.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyHappyL": transform.scale(image.load('./Sprites/Flowey_base_looking_left.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyAfraid": transform.scale(image.load('./Sprites/Flowey_afraid.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyAfraidD1": transform.scale(image.load('./Sprites/Flowey_afraid_dying1.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyAfraidD2": transform.scale(image.load('./Sprites/Flowey_afraid_dying2.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyAfraidD3": transform.scale(image.load('./Sprites/Flowey_afraid_dying3.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyAfraidBurned": transform.scale(image.load('./Sprites/Flowey_afraid_burned.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyAfraidBurnedD1": transform.scale(image.load('./Sprites/Flowey_afraid_burned_dying1.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyAfraidBurnedD2": transform.scale(image.load('./Sprites/Flowey_afraid_burned_dying2.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "FloweyAfraidBurnedD3": transform.scale(image.load('./Sprites/Flowey_afraid_burned_dying3.png').convert_alpha(), (self.__w//6, self.__h//5)),
      "Crack1": transform.scale(image.load('./Sprites/ScreenCrack1.png').convert_alpha(), (self.__w, self.__h)),
      "Crack2": transform.scale(image.load('./Sprites/ScreenCrack2.png').convert_alpha(), (self.__w, self.__h)),
      "Crack3": transform.scale(image.load('./Sprites/ScreenCrack3.png').convert_alpha(), (self.__w, self.__h)),
      "Crack4": transform.scale(image.load('./Sprites/ScreenCrack4.png').convert_alpha(), (self.__w, self.__h)),
      "RedHeart": transform.scale(image.load('./Sprites/Red_heart.png').convert_alpha(), (self.__w//12, self.__w//12)),
    }
    self.__souls = [transform.scale(image.load('./Sprites/teal_soul.png').convert_alpha(), (self.__w//55, self.__h//28)), 
                    transform.scale(image.load('./Sprites/Yellow_soul.png').convert_alpha(), (self.__w//55, self.__h//28)), 
                    transform.scale(image.load('./Sprites/Pink_soul.png').convert_alpha(), (self.__w//55, self.__h//28)),
                    transform.scale(image.load('./Sprites/Orange_soul.png').convert_alpha(), (self.__w//55, self.__h//28)),
                    transform.scale(image.load('./Sprites/Green_soul.png').convert_alpha(), (self.__w//55, self.__h//28)),
                    transform.scale(image.load('./Sprites/Blue_soul.png').convert_alpha(), (self.__w//55, self.__h//28))]
    self.__reglinespeed = 8/self.__fps
    self.__secretlinespeed = 8/self.__fps
    self.__spincounter = 0
    self.__flowey_textbox = Rect((self.__w//2 - self.__w//3, self.__h//2 + self.__h//5 + 20), (self.__w//1.5, self.__h//8))
    self.__hearty = self.__sprites['RedHeart'].get_rect(midbottom=(self.__w//2, self.__h)).centery
    self.__reg_steptimes = {
      0: 5*fps,
      1: 3*fps,
      2: 5*fps,
      3: 5*fps,
      4: 6.5*fps,
      5: 3.5*fps,
      6: 3.2*fps,
      7: 3*fps,
      8: 10*fps,
      9: 5.5*fps,
      10: 6.5*fps,
      11: 4*fps,
      12: 17*fps,
    }
    self.__secret_steptimes = {
      1: 3*fps,
      2: 5*fps,
      3: 5*fps,
      4: 6.5*fps,
      5: 3*fps,
      6: 9.5*fps,
      7: 10*fps,
      8: 3*fps,
      9: 7*fps,
      10: 5*fps,
      11: 3*fps,
      12: 4*fps,
      13: 10*fps,
      14: 4*fps,
      15: 9*fps,
      16: 4*fps,
      17: 3*fps,
      18: 8*fps,
      19: 5*fps,
      20: 6*fps,
      21: 8*fps,
      22: 8*fps,
      23: 5*fps,
      24: 7.5*fps,
      
    }
    self.__go_textbox = Rect((self.__w//2 - w//10, 0), (w//5, h//4))
    self.__button = Button(self.__screen, self.__w//2 - self.__w//6, self.__h*0.6, self.__w//3, self.__h//4, inactiveColour=(255, 255, 255), hoverColour=(155, 0, 0), shadowDistance = 0.5, pressedColour=(255, 0, 0), radius=10, textHAlign ='centre', textVAlign = 'centre', font=font.Font('fonts/DeterminationMonoWebRegular.ttf', 60), text='QUIT', margin=10)
    self.button_rect = Rect((self.__button.getX(), self.__button.getY()), (self.__button.getWidth(), self.__button.getHeight()))
    self.__button.hide()
    self.__lyricstextbox = Rect((self.__w//2 - w//8, h//4), (w//4, h//4))
    self.__strip_background()
    self.__regulate_sound()
  
  def __homogenic_step(self, soundname: str, lines: dict, steps: dict, spd: int) -> None:
    if self.__timer == 1:
      self.__sfx[soundname].play()
    if floor(self.__textcounter) < len(lines[self.__step]):
      self.__textcounter += spd
    elif floor(self.__textcounter) >= len(lines[self.__step]):
      self.__textcounter = len(lines[self.__step])
      self.__sfx[soundname].stop()
    if self.__timer>steps[self.__step]:
      self.__step+=1
      self.__timer=0
      self.__textcounter = 0
  
  def end(self) -> None:
    self.__sfx['press'].play()
    tm.sleep(0.2)
    self.done = True
  
  def update(self) -> None:
    self.__timer +=1
    if self.__spincounter*self.__soulspeed == 360:
      self.__spincounter = 0
    if self.__step == -1:
      self.__button.show()
      self.__secret = (self.__con._player_hp == 'full')
      if not self.__secret:
        self.maxstep = 13
      else:
        self.maxstep = 25
      self.__step +=1
      self.__timer = 0

    if self.__step == 0:
      if self.__y == -80:
        self.__dir = 1
      elif self.__y == -20:
        self.__dir = -1
        
      if self.__timer == self.__fps + 1 or self.__timer == 2*self.__fps+1 or self.__timer == 3*self.__fps+1 or self.__timer == 4*self.__fps+1:
        self.__sfx['Glasscrack'].play()
      elif self.__timer == self.__reg_steptimes[0]:
        self.__sfx['Glassbreak'].play()
      if self.__timer > self.__reg_steptimes[0]:
        self.__timer = 0
        self.__step += 1
      self.__bg.update()
      self.__y += self.__dir
      

    if not self.__secret:
      if 1 <= self.__step <= 6:
        self.__spincounter+=1
        self.__homogenic_step('GoodFlowey', self.__reg_voicelines, self.__reg_steptimes, self.__reglinespeed)
      if 7 <= self.__step <= 8:
        self.__soulR+=self.__expand
        self.__homogenic_step('GoodFlowey', self.__reg_voicelines, self.__reg_steptimes, self.__reglinespeed)
      if self.__step == 9:
        self.__spincounter+=1
        self.__soulR+=self.__expand
        self.__maxR = self.__soulR
        self.__homogenic_step('GoodFlowey', self.__reg_voicelines, self.__reg_steptimes, self.__reglinespeed)
      if self.__step == 10:
        self.__spincounter+=1
        if self.__soulR > 0 and self.__timer > (len(self.__reg_voicelines[self.__step])/8)*self.__fps:
          self.__soulR-=self.__retract
          if self.__soulR < 0:
            self.__soulR = 0
        if self.__timer == (len(self.__reg_voicelines[self.__step])/8)*self.__fps + self.__maxR//self.__retract:
          self.__sfx['ExoSlash'].play()
        self.__homogenic_step('GoodFlowey', self.__reg_voicelines, self.__reg_steptimes, self.__reglinespeed)
        
      if self.__step == 11:
        self.__homogenic_step('GoodFlowey', self.__reg_voicelines, self.__reg_steptimes, self.__reglinespeed)
      
      if self.__step == 12:
        if self.__timer > self.__fps*3:
          if self.__timer == self.__fps*3 + 1:
            self.__sfx['savepoint'].play()
            self.__sfx['serenity'].play() 
          if self.__soulR <= 150 and not self.__expanded:
            self.__soulR+=self.__last_expand
          else:
            self.__soulR-=self.__last_expand
            self.__expanded = True
          self.__spincounter+=1
          if self.__hearty > self.__h//2 - 100:
            self.__hearty -=self.__heartstep
          else:
            self.__hearty = self.__h//2 - 100
          if self.__soulR <= 0:
            self.__soulR = 0
            if not self.__soundflag:
              self.__sfx['XerocSpawn'].play()
              self.__soundflag = True
            self.__light += self.__lightexpansion
        self.__homogenic_step('GoodFlowey', self.__reg_voicelines, self.__reg_steptimes, self.__reglinespeed)
      
      if self.__step == 13:
        mouse_pos = mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos) and not self.__hover:
          self.__sfx['hover'].play()
          self.__hover = True
        elif not self.button_rect.collidepoint(mouse_pos):
          self.__hover = False
        if self.__timer == 1:
          mixer.music.load('./Soundeffects/Sky After Rain.mp3')
          mixer.music.set_volume(0.2)
          mixer.music.play()
        if self.__timer > (60*2 + 14)*self.__fps + 10:
          self.done = True
        events = event.get()
        self.__button.listen(events)
        pygame_widgets.update(events)
    else:
      '''SECRET CUTSCENE LOGIC FROM HERE'''
      if 1 <= self.__step <= 5:
        self.__spincounter+=1
        self.__homogenic_step('GoodFlowey', self.__secret_voicelines, self.__secret_steptimes, self.__secretlinespeed)
      
      if self.__step == 6:
        if self.__timer <= (len(self.__secret_voicelines[self.__step])/8)*self.__fps + 1:
          self.__spincounter+=1
          self.__homogenic_step('GoodFlowey', self.__secret_voicelines, self.__secret_steptimes, self.__secretlinespeed)
        if self.__timer == (len(self.__secret_voicelines[self.__step])/8)*self.__fps - 10:
          self.__sfx['Fire'].play()
        if self.__timer > self.__secret_steptimes[6]:
          self.__step+=1
          self.__timer = 0
          self.__textcounter = 0
          
      if self.__step == 7:
        if self.__timer == 0:
          self.__sfx['Fire'].play()
        elif self.__timer >= 5*self.__fps:
          if self.__timer == 5*self.__fps:
            self.__sfx['XerocSpawn'].play()
          if self.__timer < 6*self.__fps:
            self.__light += self.__lightexpansion
          else:
            if self.__light > 0:
              self.__light -=self.__lightexpansion
              if self.__light <= 0:
                self.__light = 0
          if self.__y == -80:
            self.__dir = 1
          elif self.__y == -40:
            self.__dir = -1
          self.__y += self.__dir
        if self.__timer > self.__secret_steptimes[6]:
          self.__step+=1
          self.__timer = 0
          self.__textcounter = 0
      
      if 8 <= self.__step <= 24:
        if self.__y == -80:
          self.__dir = 1
        elif self.__y == -40:
          self.__dir = -1
        self.__y += self.__dir
        if self.__step == 8 and self.__timer == 1:
          mixer.music.load("./Soundeffects/Siren's Call.mp3")
          mixer.music.play()
        if self.__step == 24 and self.__timer ==  (len(self.__secret_voicelines[self.__step])/8)*self.__fps + 1:
          mixer.music.stop()
          mixer.music.unload()
          self.__sfx['XerocDespawn'].play()
        if self.__step == 24:
          if self.__timer > (len(self.__secret_voicelines[self.__step])/8)*self.__fps:
            if self.__timer <= self.__fps*5:
              self.__light += self.__lightexpansion
        self.__homogenic_step('asgore', self.__secret_voicelines, self.__secret_steptimes, self.__secretlinespeed)
      
      if self.__step == 25:
        mouse_pos = mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos) and not self.__hover:
          self.__sfx['hover'].play()
          self.__hover = True
        elif not self.button_rect.collidepoint(mouse_pos):
          self.__hover = False
        if self.__timer == 1:
          mixer.music.load('./Soundeffects/Sky After Rain.mp3')
          mixer.music.set_volume(0.2)
          mixer.music.play()
        if self.__timer > (60*2 + 14)*self.__fps + 10:
          self.done = True
        events = event.get()
        self.__button.listen(events)
        pygame_widgets.update(events)
  
  def __homogenic_draw(self, lines: dict) -> None:
      if self.__timer%10 <5 and self.__timer < (len(lines[self.__step])/8)*self.__fps:
        self.__screen.blit(self.__sprites['FloweyHappy1'], self.__sprites['FloweyHappy1'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
      elif self.__timer%10 >= 5 and self.__timer < (len(lines[self.__step])/8)*self.__fps:
        self.__screen.blit(self.__sprites['FloweyHappy2'], self.__sprites['FloweyHappy2'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
      else:
        self.__screen.blit(self.__sprites['FloweyHappy1'], self.__sprites['FloweyHappy1'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
      center_x = self.__w//2 
      center_y = self.__h//2 - 100
      r = self.__w//12 + self.__h//12
      rotation = self.__spincounter* self.__soulspeed
      for i in range(6):
        angle = rotation + i * (2*np.pi / 6)
        x = center_x + np.cos(angle) * r - (self.__w//55)/2
        y = center_y + np.sin(angle) * r - (self.__h//28)/2
        self.__screen.blit(self.__souls[i], (x, y))
      typewriter_text(self.__screen, lines[self.__step][:floor(self.__textcounter)], 40, (255, 255, 255), self.__flowey_textbox)
  
  def __homogenic_draw_Xeroc(self, lines: dict) -> None:
      if self.__timer%10 < 5:
        self.__screen.blit(self.__sprites['XerocPulse1'], self.__sprites['XerocPulse1'].get_rect(midtop = (self.__x, self.__y)))
      else:
        self.__screen.blit(self.__sprites['XerocPulse2'], self.__sprites['XerocPulse2'].get_rect(midtop = (self.__x, self.__y)))
      typewriter_text(self.__screen, lines[self.__step][:floor(self.__textcounter)], 40, (255, 255, 255), self.__flowey_textbox)
  
  def draw(self) -> None:
    if self.__step == 0:
      self.__screen.blit(self.__bg.get_bg(), (0, self.__bg.pos))
      self.__screen.blit(self.__bg.get_bg(), (0, self.__bg.pos-self.__h))
      if self.__timer%10 < 5:
        self.__screen.blit(self.__sprites['XerocStep0Pulse1'], self.__sprites['XerocStep0Pulse1'].get_rect(midtop = (self.__x, self.__y)))
      else:
        self.__screen.blit(self.__sprites['XerocStep0Pulse2'], self.__sprites['XerocStep0Pulse2'].get_rect(midtop = (self.__x, self.__y)))
      self.__screen.blit(self.__sprites['Rocket'], self.__sprites['Rocket'].get_rect(midbottom = (self.__x, self.__h)))
      
      if self.__fps <= self.__timer < 2*self.__fps:
        self.__screen.blit(self.__sprites['Crack1'], (0, 0))
      elif 2*self.__fps <= self.__timer  < 3*self.__fps:
        self.__screen.blit(self.__sprites['Crack2'], (0, 0))
      elif 3*self.__fps <= self.__timer  < 4*self.__fps:
        self.__screen.blit(self.__sprites['Crack3'], (0, 0))
      elif 4*self.__fps <= self.__timer < 5*self.__fps:
        self.__screen.blit(self.__sprites['Crack4'], (0, 0))
      elif self.__timer >= 5*self.__fps:
        self.__screen.fill((0, 0, 0))
      
    if not self.__secret:
      if 0 < self.__step < 12:
        self.__screen.fill((0, 0, 0))
        self.__screen.blit(self.__sprites['RedHeart'], self.__sprites['RedHeart'].get_rect(midbottom=(self.__w//2, self.__h)).topleft)
      
      if 1 <=self.__step <= 6:
        self.__homogenic_draw(self.__reg_voicelines)
        
      if self.__step == 7 or self.__step == 8:
        if self.__timer%60 <30:
          self.__screen.blit(self.__sprites['FloweyHappyL'], self.__sprites['FloweyHappyL'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        else:
          self.__screen.blit(self.__sprites['FloweyHappyR'], self.__sprites['FloweyHappyR'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        center_x = self.__w//2 
        center_y = self.__h//2 - 100
        rotation = self.__spincounter* self.__soulspeed
        for i in range(6):
          angle = rotation + i * (2*np.pi / 6)
          x = center_x + np.cos(angle) * self.__soulR - (self.__w//55)/2
          y = center_y + np.sin(angle) * self.__soulR - (self.__h//28)/2
          self.__screen.blit(self.__souls[i], (x, y))
        typewriter_text(self.__screen, self.__reg_voicelines[self.__step][:floor(self.__textcounter)], 40, (255, 255, 255), self.__flowey_textbox)
      
      if self.__step == 9:
        if self.__timer%10 <5 and self.__timer < (len(self.__reg_voicelines[self.__step])/8)*self.__fps:
          self.__screen.blit(self.__sprites['FloweyHappy1'], self.__sprites['FloweyHappy1'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        elif self.__timer%10 >= 5 and self.__timer < (len(self.__reg_voicelines[self.__step])/8)*self.__fps:
          self.__screen.blit(self.__sprites['FloweyHappy2'], self.__sprites['FloweyHappy2'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        else:
          self.__screen.blit(self.__sprites['FloweyHappy1'], self.__sprites['FloweyHappy1'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        center_x = self.__w//2 
        center_y = self.__h//2 - 100
        rotation = self.__spincounter* self.__soulspeed
        for i in range(6):
          angle = rotation + i * (2*np.pi / 6)
          x = center_x + np.cos(angle) * self.__soulR - (self.__w//55)/2
          y = center_y + np.sin(angle) * self.__soulR - (self.__h//28)/2
          self.__screen.blit(self.__souls[i], (x, y))
        typewriter_text(self.__screen, self.__reg_voicelines[self.__step][:floor(self.__textcounter)], 40, (255, 255, 255), self.__flowey_textbox)
    
      if self.__step == 10:
        if self.__timer%10 <5 and self.__timer < (len(self.__reg_voicelines[self.__step])/8)*self.__fps:
          self.__screen.blit(self.__sprites['FloweyHappy1'], self.__sprites['FloweyHappy1'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        elif self.__timer%10 >= 5 and self.__timer < (len(self.__reg_voicelines[self.__step])/8)*self.__fps:
          self.__screen.blit(self.__sprites['FloweyHappy2'], self.__sprites['FloweyHappy2'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        else:
          self.__screen.blit(self.__sprites['FloweyAfraid'], self.__sprites['FloweyAfraid'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        if self.__soulR > 0:
          center_x = self.__w//2 
          center_y = self.__h//2 - 100
          rotation = self.__spincounter* self.__soulspeed
          for i in range(6):
            angle = rotation + i * (2*np.pi / 6)
            x = center_x + np.cos(angle) * self.__soulR - (self.__w//55)/2
            y = center_y + np.sin(angle) * self.__soulR - (self.__h//28)/2
            self.__screen.blit(self.__souls[i], (x, y))
        typewriter_text(self.__screen, self.__reg_voicelines[self.__step][:floor(self.__textcounter)], 40, (255, 255, 255), self.__flowey_textbox)
      
      if self.__step == 11:
        self.__screen.blit(self.__sprites['FloweyAfraid'], self.__sprites['FloweyAfraid'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        typewriter_text(self.__screen, self.__reg_voicelines[self.__step][:floor(self.__textcounter)], 40, (255, 255, 255), self.__flowey_textbox)
      
      if self.__step == 12:
        self.__screen.fill((0, 0, 0))
        if self.__timer <= self.__fps:
          self.__screen.blit(self.__sprites['FloweyAfraidD1'], self.__sprites['FloweyAfraidD1'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
          self.__screen.blit(self.__sprites['RedHeart'], self.__sprites['RedHeart'].get_rect(midbottom=(self.__w//2, self.__h)).topleft)
          typewriter_text(self.__screen, self.__reg_voicelines[self.__step][:floor(self.__textcounter)], 40, (255, 255, 255), self.__flowey_textbox)
        elif self.__fps < self.__timer <= self.__fps*2:
          self.__screen.blit(self.__sprites['FloweyAfraidD2'], self.__sprites['FloweyAfraidD2'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
          self.__screen.blit(self.__sprites['RedHeart'], self.__sprites['RedHeart'].get_rect(midbottom=(self.__w//2, self.__h)).topleft)
          typewriter_text(self.__screen, self.__reg_voicelines[self.__step][:floor(self.__textcounter)], 40, (255, 255, 255), self.__flowey_textbox)
        elif self.__fps*2 < self.__timer <= self.__fps*3:
          self.__screen.blit(self.__sprites['FloweyAfraidD3'], self.__sprites['FloweyAfraidD3'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
          self.__screen.blit(self.__sprites['RedHeart'], self.__sprites['RedHeart'].get_rect(midbottom=(self.__w//2, self.__h)).topleft)
          typewriter_text(self.__screen, self.__reg_voicelines[self.__step][:floor(self.__textcounter)], 40, (255, 255, 255), self.__flowey_textbox)
        elif self.__fps*3 < self.__timer <= self.__fps*15:
          if self.__soulR > 0:
            center_x = self.__w//2 
            center_y = self.__h//2 - 100
            rotation = self.__spincounter* self.__soulspeed
            for i in range(6):
              angle = rotation + i * (2*np.pi / 6)
              x = center_x + np.cos(angle) * self.__soulR - (self.__w//55)/2
              y = center_y + np.sin(angle) * self.__soulR - (self.__h//28)/2
              self.__screen.blit(self.__souls[i], (x, y))
          self.__screen.blit(self.__sprites['RedHeart'], self.__sprites['RedHeart'].get_rect(center=(self.__w//2, self.__hearty)).topleft)
          if self.__soundflag:
            draw.circle(self.__screen, (255, 255, 255), (self.__w//2, self.__h//2 - 100), self.__light)
        else:
          if self.__timer <=15.6*self.__fps:
            self.__screen.fill((255, 255, 255))
          elif 15.6*self.__fps <self.__timer <=15.75*self.__fps:
            self.__screen.fill((185,185,185))
          elif 15.75*self.__fps <self.__timer <=15.9*self.__fps:
            self.__screen.fill((142,142,142))
          elif 15.9*self.__fps <self.__timer <= 16.05*self.__fps:
            self.__screen.fill((114,114,114))
          elif 16.05*self.__fps <self.__timer <= 16.2*self.__fps:
            self.__screen.fill((81,81,81))
          elif 16.2*self.__fps <self.__timer <= 16.35*self.__fps:
            self.__screen.fill((40,40,40))
          else:
            self.__screen.fill((0, 0, 0))
            
      if self.__step == 13:
        self.__screen.fill((0, 0, 0))
        self.__button.draw()
        typewriter_text_no_rect(self.__screen, self.__reg_voicelines['g'], 200, (255, 255, 255), self.__go_textbox)
        if 60*(self.__fps + 7) <= self.__timer <= 60*(self.__fps + 15):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[1], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 15) < self.__timer <= 60*(self.__fps + 23):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[2], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 23) < self.__timer <= 60*(self.__fps + 32):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[3], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 32) < self.__timer <= 60*(self.__fps + 40):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[4], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 40) < self.__timer <= 60*(self.__fps + 47):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[5], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 47) < self.__timer <= 60*(self.__fps + 56):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[6], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 56) < self.__timer <= 120*self.__fps + 60*5:
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[7], 40, (255, 255, 255), self.__lyricstextbox)
        elif self.__timer > 120*self.__fps + 60*5:
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[8], 40, (255, 255, 255), self.__lyricstextbox)
    else:
      '''SECRET CUTSCENE LOGIC FROM HERE'''
      if 0 < self.__step <= 24:
        self.__screen.fill((0, 0, 0))
        self.__screen.blit(self.__sprites['RedHeart'], self.__sprites['RedHeart'].get_rect(midbottom=(self.__w//2, self.__h)).topleft)
      
      if 1 <=self.__step <= 5:
        self.__homogenic_draw(self.__secret_voicelines)
        
      if self.__step == 6:
        if self.__timer <= (len(self.__secret_voicelines[self.__step])/8)*self.__fps + 1:
          self.__homogenic_draw(self.__secret_voicelines)
        else:
          if self.__timer < self.__fps*5 + 15:
            if self.__timer%60 <30:
              self.__screen.blit(self.__sprites['FloweyHappyL'], self.__sprites['FloweyHappyL'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
            else:
              self.__screen.blit(self.__sprites['FloweyHappyR'], self.__sprites['FloweyHappyR'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
            center_x = self.__w//2 
            center_y = self.__h//2 - 100
            rotation = self.__spincounter* self.__soulspeed
            for i in range(6):
              angle = rotation + i * (2*np.pi / 6)
              x = center_x + np.cos(angle) * self.__soulR - (self.__w//55)/2
              y = center_y + np.sin(angle) * self.__soulR - (self.__h//28)/2
              self.__screen.blit(self.__sprites['BurnedSoul'], (x, y))
          else:
            self.__screen.blit(self.__sprites['FloweyAfraid'], self.__sprites['FloweyAfraid'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
            if self.__timer < self.__fps*6:
              center_x = self.__w//2 
              center_y = self.__h//2 - 100
              rotation = self.__spincounter* self.__soulspeed
              for i in range(6):
                angle = rotation + i * (2*np.pi / 6)
                x = center_x + np.cos(angle) * self.__soulR - (self.__w//55)/2
                y = center_y + np.sin(angle) * self.__soulR - (self.__h//28)/2
                self.__screen.blit(self.__sprites['BurnedSoulD1'], (x, y))
            elif self.__timer < 7*self.__fps:
              center_x = self.__w//2 
              center_y = self.__h//2 - 100
              rotation = self.__spincounter* self.__soulspeed
              for i in range(6):
                angle = rotation + i * (2*np.pi / 6)
                x = center_x + np.cos(angle) * self.__soulR - (self.__w//55)/2
                y = center_y + np.sin(angle) * self.__soulR - (self.__h//28)/2
                self.__screen.blit(self.__sprites['BurnedSoulD2'], (x, y))
            elif self.__timer < 8*self.__fps:
              center_x = self.__w//2 
              center_y = self.__h//2 - 100
              rotation = self.__spincounter* self.__soulspeed
              for i in range(6):
                angle = rotation + i * (2*np.pi / 6)
                x = center_x + np.cos(angle) * self.__soulR - (self.__w//55)/2
                y = center_y + np.sin(angle) * self.__soulR - (self.__h//28)/2
                self.__screen.blit(self.__sprites['BurnedSoulD3'], (x, y))
                
      if self.__step == 7:
        if self.__timer < 12:
          self.__screen.blit(self.__sprites['FloweyAfraid'], self.__sprites['FloweyAfraid'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        elif 15 <= self.__timer < 2*self.__fps :
          self.__screen.blit(self.__sprites['FloweyAfraidBurned'], self.__sprites['FloweyAfraidBurned'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        elif 2*self.__fps <= self.__timer < 3*self.__fps:
          self.__screen.blit(self.__sprites['FloweyAfraidBurnedD1'], self.__sprites['FloweyAfraidBurnedD1'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        elif 3*self.__fps <= self.__timer < 4*self.__fps:
          self.__screen.blit(self.__sprites['FloweyAfraidBurnedD2'], self.__sprites['FloweyAfraidBurnedD2'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)     
        elif 4*self.__fps <= self.__timer < 5*self.__fps:
          self.__screen.blit(self.__sprites['FloweyAfraidBurnedD3'], self.__sprites['FloweyAfraidBurnedD3'].get_rect(center=(self.__w//2, self.__h//2 - 100)).topleft)
        else:
          if self.__timer >= self.__fps*6 :
            if self.__timer%10 < 5:
              self.__screen.blit(self.__sprites['XerocPulse1'], self.__sprites['XerocPulse1'].get_rect(midtop = (self.__x, self.__y)))
            else:
              self.__screen.blit(self.__sprites['XerocPulse2'], self.__sprites['XerocPulse2'].get_rect(midtop = (self.__x, self.__y)))
          if self.__timer <= 7.5*self.__fps:
            draw.circle(self.__screen, (255, 255, 255), (self.__w//2, self.__h//2 - 100), self.__light)
      
      if 8 <= self.__step <= 24:
        if self.__step < 24:
          self.__homogenic_draw_Xeroc(self.__secret_voicelines)
        elif self.__step == 24:
          if self.__timer <= (len(self.__secret_voicelines[self.__step])/8)*self.__fps:
            self.__homogenic_draw_Xeroc(self.__secret_voicelines)
          else:
            if self.__timer <= self.__fps*5:
              if self.__timer%10 < 5:
                self.__screen.blit(self.__sprites['XerocPulse1'], self.__sprites['XerocPulse1'].get_rect(midtop = (self.__x, self.__y)))
              else:
                self.__screen.blit(self.__sprites['XerocPulse2'], self.__sprites['XerocPulse2'].get_rect(midtop = (self.__x, self.__y)))
              draw.circle(self.__screen, (255, 255, 255), (self.__w//2, self.__h//2 - 100), self.__light)
            else:
              if self.__timer <=5.6*self.__fps:
                self.__screen.fill((255, 255, 255))
              elif 5.6*self.__fps <self.__timer <=5.75*self.__fps:
                self.__screen.fill((185,185,185))
              elif 5.75*self.__fps <self.__timer <=5.9*self.__fps:
                self.__screen.fill((142,142,142))
              elif 5.9*self.__fps <self.__timer <= 6.05*self.__fps:
                self.__screen.fill((114,114,114))
              elif 6.05*self.__fps <self.__timer <= 6.2*self.__fps:
                self.__screen.fill((81,81,81))
              elif 6.2*self.__fps <self.__timer <= 6.35*self.__fps:
                self.__screen.fill((40,40,40))
              else:
                self.__screen.fill((0, 0, 0))
               
      if self.__step == 25:
        self.__screen.fill((0, 0, 0))
        self.__button.draw()
        typewriter_text_no_rect(self.__screen, self.__reg_voicelines['g'], 200, (255, 255, 255), self.__go_textbox)
        if 60*(self.__fps + 7) <= self.__timer <= 60*(self.__fps + 15):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[1], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 15) < self.__timer <= 60*(self.__fps + 23):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[2], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 23) < self.__timer <= 60*(self.__fps + 32):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[3], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 32) < self.__timer <= 60*(self.__fps + 40):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[4], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 40) < self.__timer <= 60*(self.__fps + 47):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[5], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 47) < self.__timer <= 60*(self.__fps + 56):
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[6], 40, (255, 255, 255), self.__lyricstextbox)
        elif 60*(self.__fps + 56) < self.__timer <= 120*self.__fps + 60*5:
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[7], 40, (255, 255, 255), self.__lyricstextbox)
        elif self.__timer > 120*self.__fps + 60*5:
          typewriter_text_no_rect(self.__screen, self.__sky_after_rain[8], 40, (255, 255, 255), self.__lyricstextbox)          
          
  def __strip_background(self) -> None:
    for i in self.__sprites.values():
      i.set_colorkey((0, 0, 0))
    for i in self.__souls:
      i.set_colorkey((0, 0, 0))
      
  def get_step(self) -> int:
    return self.__step
  
  def __regulate_sound(self) -> None:
    for i in self.__sfx.values():
      i.set_volume(0.2)
    self.__sfx['hover'].set_volume(0.05)
    self.__sfx['press'].set_volume(0.1)
    self.__sfx['serenity'].set_volume(0.4)
    self.__sfx['ExoSlash'].set_volume(0.4)
    self.__sfx['Fire'].set_volume(0.5)
