from pygame import *
from widgets import Slider
import abc
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
from collections import defaultdict
import pygame_widgets
import time as tm
from cutscenes import *
import sys
from entities import *
import scipy.stats as sc

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

class Engine:
  @abc.abstractmethod
  def __init__(w: int, h: int, c: tuple[int], fps: int, screen: Surface, parent) -> None:
    '''Base Constructor'''
    pass
  @abc.abstractmethod
  def run() -> None:
    '''Base Run Method'''
    pass
  @abc.abstractmethod
  def __check_event() -> None:
    '''Base event checker'''
    pass
  @abc.abstractmethod
  def __draw() -> None:
    '''Base Drawer Method'''
    pass
  @abc.abstractmethod
  def __status_update() -> str:
    '''Base Status update method'''
    pass
  
class GameEngine(Engine):
  def __init__(self, w: int, h: int, c: tuple[int], fps: int, screen: Surface, parent) ->None :
    self.c = c
    self.__w = w
    self.__h = h
    self.__screen = screen
    self.fps = fps
    self.__clock = time.Clock()
    self.__bg = Background(self.__w, self.__h, 2, 'BG.jpg')
    self.__lost = False
    self.__won = False
    self.__interrupted = False
    self.p = parent
    self.__player = Player(self.__w, self.__h, self, self.__screen)
    self.__boss = Boss(self.__w, self.__h, self, self.__screen)
    self.__player_shots = self.__player.get_shots()
    self.__enemy_shots = []
    self.__shocker_breakers = []
    self.__hover = mixer.Sound('./Soundeffects/Hover_Quit.mp3')
    self.__press = mixer.Sound('./Soundeffects/Press.mp3')
    self.__hover.set_volume(0.05)
    self.__press.set_volume(0.1)
    self.__pause_music = mixer.Sound('./Soundeffects/Their Fabricator.mp3')
    self.__pause_music.set_volume(0.2)
    self.__hovered_quit = False
    self.__hovered_resume = False
    self.__timer = 0
    self.__paused = False
    self.__quit = Button(self.__screen, self.__w//2 - self.__w//6, self.__h*0.25, self.__w//3, self.__h*0.2, inactiveColour=(255, 255, 255), hoverColour=(155, 0, 0), shadowDistance = 0.5, pressedColour=(255, 0, 0), radius=10, textHAlign ='centre', textVAlign = 'centre', font=font.Font('fonts/DeterminationMonoWebRegular.ttf', 60), text='QUIT', margin=10)
    self.__resume = Button(self.__screen, self.__w//2 - self.__w//6, self.__h*0.55, self.__w//3, self.__h*0.2, inactiveColour=(255, 255, 255), hoverColour=(0, 155, 0), shadowDistance = 0.5, pressedColour=(0, 255, 0), radius=10, textHAlign ='centre', textVAlign = 'centre', font=font.Font('fonts/DeterminationMonoWebRegular.ttf', 60), text='RESUME', margin=10)
    self.__quit.hide()
    self.__resume.hide()
    self.__quitrect = Rect((self.__quit.getX(), self.__quit.getY()), (self.__quit.getWidth(), self.__quit.getHeight()))
    self.__resrect = Rect((self.__resume.getX(), self.__resume.getY()), (self.__resume.getWidth(), self.__resume.getHeight()))
    self.__music = [
      './Soundeffects/Hopes&Dreams.mp3',
      './Soundeffects/SAVEtheWorld.mp3',
      './Soundeffects/Finale.mp3',
      './Soundeffects/LastGoodbye.mp3',
    ]
    self.__current_theme = 0
    self.__theme_started = False
    self.__player_dir = 0
    self.__star_falling_freq = 0.04
    self.__star_shooting_freq = 0
    self.__breaker_freq = 0
    self.__bomb_freq = 1_000_000*self.fps
    self.__cell_size = 100
    self.__regular_star_limit = 8
    self.__Shocker_Breaker_limit = 3
    self.__bomb = None
    self.FRAMESKIP = fps//10 
    self.current_stars = 0
    self.current_ShockerBreakers = 0
    self.current_bombs = 0
    self.bombspawned = False
    

  def pause(self) -> None:
    self.__paused = True
  
  def end(self) -> None:
    self.__press.play()
    tm.sleep(0.2)
    self.__interrupted = True
  
  def unpause(self) -> None:
    self.__pause_music.stop()
    mixer.music.unpause()
    self.__quit.hide()
    self.__resume.hide()
    self.__paused = False
  
  def get_player_coords(self) -> tuple[int]|list[int]:
    return self.__player.rect.topleft
    
  def __start_themes(self) -> None:
    if not self.__theme_started:
      self.__current_theme = 0
      self.__play_theme()
      self.__theme_started = True
  
  
  def __play_theme(self) -> None:
    if self.__current_theme < len(self.__music):
      mixer.music.load(self.__music[self.__current_theme])
      mixer.music.set_volume(self.p._menu_engine.music_val)
      mixer.music.play()
  
  def __transition(self) -> None:
    if not self.__paused:
      if not mixer.music.get_busy() and self.__theme_started:
        self.__current_theme+=1
        if self.__current_theme >= len(self.__music):
          self.__current_theme = 0
        self.__play_theme()
    
  def __update_shots(self) -> None:
    self.__player_shots = self.__player.get_shots()
    
  def __del__(self) -> None:
    pass
  
  def get_timer(self) -> int:
    return self.__timer
  
  def run(self) -> None:
    self.__start_themes()
    while not self.__lost and not self.__won and not self.__interrupted:
      self.__check_event()
      self.__logic()
      self.__move()
      self.__draw()
      self.__transition()
      self.__status_update()



  def __build_collision_grid(self):
    grid = defaultdict(list)
    
    for shot in self.__player_shots:
        cell_x = shot.rect.centerx // self.__cell_size
        cell_y = shot.rect.centery // self.__cell_size
        grid[(cell_x, cell_y)].append(shot)
    
    for enemy_shot in self.__enemy_shots:
        cell_x = enemy_shot.rect.centerx // self.__cell_size
        cell_y = enemy_shot.rect.centery // self.__cell_size
        grid[(cell_x, cell_y)].append(enemy_shot)
    return grid
  
  def __check_collisions_with_grid(self):
    grid = self.__build_collision_grid()
    
    for (cell_x, cell_y), objects in grid.items():
      nearby_good = []
      nearby_evil = []
      for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
          for obj in grid.get((cell_x + dx, cell_y + dy), []):
            if obj.aff == 'good':
              nearby_good.append(obj)
            else:
              nearby_evil.append(obj)
      
      for obj in objects:
        if obj.aff == 'good':
          for enemy in nearby_evil:
            obj.collision(enemy)
          obj.collision(self.__boss)
        else:  
          obj.collision(self.__player)
          
  def __check_event(self) -> None:
    if not self.__paused:
      keys = key.get_pressed()
      for ev in event.get():
        if ev.type == QUIT:
          self.__interrupted = True
        if ev.type == KEYDOWN and ev.key == K_SPACE:
          self.__player.shoot()
        elif ev.type == KEYDOWN and ev.key == K_ESCAPE:
          mixer.music.pause()
          self.__pause_music.play(-1)
          self.__quit.show()
          self.__resume.show()
          self.pause()
          
      if self.__timer%self.FRAMESKIP == 0:    
        self.__check_collisions_with_grid()
        for i in self.__shocker_breakers:
          i.collision(self.__player)
        if not self.__bomb is None:
          self.__bomb.collision(self.__player)
        
      if keys[K_a]:
        self.__player_dir = -1
      if keys[K_d]:
        self.__player_dir = 1
      if not (keys[K_a] or keys[K_d]):
        self.__player_dir = 0
      
      if not self.__player.get_state():
        self.__lost = True
      if not self.__boss.get_state():
        self.__won = True
    else:
      mouse_pos = mouse.get_pos()
      events = event.get()
      self.__quit.listen(events)
      self.__resume.listen(events)
      pygame_widgets.update(events)
      if self.__quitrect.collidepoint(mouse_pos) and not self.__hovered_quit:
        self.__hovered_quit = True
        self.__hover.play()
      elif not self.__quitrect.collidepoint(mouse_pos):
        self.__hovered_quit = False
      if self.__resrect.collidepoint(mouse_pos) and not self.__hovered_resume:
        self.__hovered_resume = True
        self.__hover.play()
      elif not self.__resrect.collidepoint(mouse_pos):
        self.__hovered_resume = False
      for ev in events:
        if ev.type == KEYDOWN and ev.key == K_ESCAPE:
          self.unpause()
        elif ev.type == MOUSEBUTTONDOWN and ev.button == 1:
          if self.__quitrect.collidepoint(mouse_pos):
            self.end()
          elif self.__resrect.collidepoint(mouse_pos):
            self.unpause()
        if ev.type == QUIT:
          self.__interrupted = True

  def __move(self) -> None:
    if not self.__paused:
      self.__bg.update()
      self.__boss.move()
      self.__player.move(self.__player_dir)
      if self.__player.shotcount > 0:
        for shot in self.__player_shots:
          shot.move()
      if self.current_stars > 0:
        for enemy in self.__enemy_shots:
          enemy.move()
      if not self.__bomb is None:
        self.__bomb.move()
  
  def __logic(self) -> None:
    if not self.__paused:
      if self.bombspawned:
        self.bombspawned = False
        
      self.__timer +=1
      if self.__timer >=10_000:
        self.__timer = 0
      if self.__player.shotcount > 0:
        for shot in self.__player_shots:
          shot.logic()
      if self.current_stars > 0:
        for enemy in self.__enemy_shots:
          enemy.logic()
      if self.current_ShockerBreakers>0:
        for i in self.__shocker_breakers:
            i.logic()
      if not self.__bomb is None:
        self.__bomb.logic()
        
      if (self.__timer//(self.fps//15))% 2 == 0:
        val = np.random.random()
        if self.current_stars<self.__regular_star_limit:
          if self.__star_falling_freq >= val:
            self.__enemy_shots.append(FallingStar(self.__w, self.__h, self, self.__screen))
          if self.__star_shooting_freq >= val:
            self.__enemy_shots.append(ShootingStar(self.__w, self.__h, self, self.__screen))
        if self.current_ShockerBreakers<self.__Shocker_Breaker_limit:
          if self.__breaker_freq >= val:
            for i in range(self.__Shocker_Breaker_limit):
              self.__shocker_breakers.append(ShockerBreaker(self.__w, self.__h, self, self.__screen))
        if self.__bomb is None and self.__timer%self.__bomb_freq == 0 and self.__timer != 0:
          self.bombspawned = True
          self.__bomb = StarBomb(self.__w, self.__h, self, self.__screen)
          
      self.__boss.logic()
      self.__player.logic()
      self.__update_shots()
      if self.current_stars > 0:
        self.__enemy_shots = [i for i in self.__enemy_shots if i.get_state()]
      if self.current_ShockerBreakers > 0:
        self.__shocker_breakers = [i for i in self.__shocker_breakers if i.get_state()]
      if not self.__bomb is None:
        if not self.__bomb.get_state():
          self.__bomb = None
    
  
  def __draw(self) -> None:
    if not self.__paused:
      self.__screen.blit(self.__bg.get_bg(), (0, self.__bg.pos))
      self.__screen.blit(self.__bg.get_bg(), (0, self.__bg.pos-self.__h))
      self.__boss.draw()
      if self.current_stars > 0:
        for i in self.__enemy_shots:
          i.draw()
      if self.__player.shotcount > 0:
        for i in self.__player_shots:
          i.draw()
      if self.current_ShockerBreakers>0:
        for i in self.__shocker_breakers:
            i.draw()
      if not self.__bomb is None:
        self.__bomb.draw()
      self.__player.draw()
    else:
      self.__screen.fill((0, 0, 0))
      self.__quit.draw()
      self.__resume.draw()
    display.flip()
    self.__clock.tick(self.fps)
    
  def __status_update(self) -> str:
    if self.__lost:
      mixer.music.stop()
      mixer.music.unload()
      self.p.state = 'cutscene_lost'
      self.p.execute()
    elif self.__won:
      mixer.music.stop()
      mixer.music.unload()
      self.p.state = 'cutscene_won'
      if self.__player.check_hp(): 
        self.p._player_hp = 'full'
      else:
        self.p._player_hp = 'spent'
      self.p.execute()
    elif self.__interrupted:
      mixer.music.stop()
      mixer.music.unload()
      self.p.state = 'over'
      self.p.execute()
      
  def update_stage(self, bombfreq: int, shockerbreaker: int, maxstars: int, starfalling: float, starshooting: float, breaker: float) -> None:
    self.__Shocker_Breaker_limit = shockerbreaker
    self.__regular_star_limit = maxstars
    self.__star_falling_freq = starfalling
    self.__star_shooting_freq = starshooting
    self.__breaker_freq = breaker
    self.__bomb_freq = bombfreq*self.fps
      
class CutsceneEngine(Engine):
    def __init__(self, w: int, h: int, c: tuple[int], fps: int, screen: Surface, parent) -> None :
      self.c = c
      self.__w = w
      self.__h = h
      self.__screen = screen
      self.fps = fps
      self.__clock = time.Clock()
      self.__won = WonCutscene(self.__screen, self.__w, self.__h, self.fps, parent)
      self.__lost = LostCutscene(self.__screen, self.__w, self.__h, self.fps)
      self.__intro = IntroCutscene(self.__screen, self.__w, self.__h, self.fps)
      self.p = parent
      self.__scene = None
      self.__interrupted = False
      self.__current_cutscene = None
      
    def run(self, command: str) -> None:
      self.__run_cutscene(command=command)
      while not self.__interrupted and not self.__current_cutscene.done:
        self.__check_event()
        self.__logic()
        self.__draw()
        self.__status_update()
    
    def __logic(self) -> None:
      self.__current_cutscene.update()
    
    def __check_event(self) -> None:
      for ev in event.get():
        if ev.type == QUIT:
          self.__interrupted = True
        if hasattr(self.__current_cutscene, 'button_rect'):
          mouse_pos = mouse.get_pos()
          if ev.type == MOUSEBUTTONDOWN and self.__current_cutscene.button_rect.collidepoint(mouse_pos) and ev.button == 1 and self.__current_cutscene.maxstep == self.__current_cutscene.get_step():
            self.__current_cutscene.end()
    
    def __run_cutscene(self, command: str) -> None:
      if command == 'cutscene_intro':
        self.__scene = 'intro'
        self.__current_cutscene = self.__intro
      elif command == 'cutscene_lost':
        self.__scene = 'lost'
        self.__current_cutscene = self.__lost
      elif command == 'cutscene_won':
        self.__scene = 'won'
        self.__current_cutscene = self.__won
        
    def __draw(self) -> None:
      self.__current_cutscene.draw()
      
      display.flip()
      self.__clock.tick(self.fps)
    
    def __status_update(self) -> str:
      if self.__interrupted:
        self.p.state = 'over'
        self.p.execute()
      if self.__current_cutscene.done and self.__scene == 'intro':
        self.p.state = 'game'
        self.p.execute()
      if self.__current_cutscene.done and (self.__scene == 'won' or self.__scene == 'won'):
        self.p.state = 'over'
        self.p.execute()

class MenuEngine(Engine):
  def __init__(self, w: int, h: int, c: tuple[int], fps: int, screen: Surface, parent) ->None :
    self.c = c
    self.music_val = 0.05
    self.__hover_quit = mixer.Sound('./Soundeffects/Hover_Quit.mp3')
    self.__hover_quit.set_volume(0.05)
    self.__hover = mixer.Sound('./Soundeffects/Hover.mp3')
    self.__hover.set_volume(0.08)
    self.__press = mixer.Sound('./Soundeffects/Press.mp3')
    self.__press.set_volume(0.1)
    self.__w = w
    self.__h = h
    self.__screen = screen
    self.fps = fps
    self.__clock = time.Clock()
    self.__bg = Background(self.__w, self.__h, 1, 'BG.jpg')
    self.__cutscene = False
    self.__game = False
    self.__interrupted = False
    self.p = parent
    self.__hover_states = defaultdict(None)
    self.__buttons = [
      Button(self.__screen, w//2-w//5, h//2-h//2.5, 2*w//5, 2*h//8, inactiveColour=(255, 255, 255), hoverColour=(0, 155, 0), shadowDistance = 0.5, pressedColour=(0, 255, 0), radius=10, textHAlign ='centre', textVAlign = 'centre', font=font.Font('fonts/DeterminationMonoWebRegular.ttf', 40), text='Begin Cutscene', margin=10, onClick = self.cutscene),
      Button(self.__screen, w//2-w//5, h//2-h//2.5 + 30 + 2*h//8, 2*w//5, 2*h//8, inactiveColour=(255, 255, 255), hoverColour=(0, 155, 0), shadowDistance = 0.5, pressedColour=(0, 255, 0), radius=10, textHAlign ='centre', textVAlign = 'centre', font=font.Font('fonts/DeterminationMonoWebRegular.ttf', 40), text='Begin', margin=10, onClick = self.game),
      Button(self.__screen, w//2-w//5, h//2-h//2.5 + 60 + 4*h//8, 2*w//5, 2*h//8, inactiveColour=(255, 255, 255), hoverColour=(155, 0, 0), shadowDistance = 0.5, pressedColour=(255, 0, 0), radius=10, textHAlign ='centre', textVAlign = 'centre', font=font.Font('fonts/DeterminationMonoWebRegular.ttf', 40), text='QUIT', margin=10, onClick = self.quit)
      ]
    self.__button_rects = [Rect(button.getX(), button.getY(), button.getWidth(), button.getHeight()) for button in self.__buttons]
    self.__volume_slider = Slider(self.__w//9, h//2-h//2.5 + 30 + 2*h//8 +h//8, self.__w//6, self.__h//34, self.__screen, (50, 50, 50), (150, 0, 150), (0, 100, 167), (90, 0, 90), 2)
    self.__music_icon = transform.scale(image.load('./Icon/Music Icon.png').convert(), (self.__w//12, 2*self.__h//25))  
    self.__slider_rect = self.__volume_slider.get_rect()
    self.__start_music()
    
  def __del__(self) -> None:
    pass
   
  def __start_music(self) -> None: 
    mixer.music.load('./Soundeffects/DeepAbyss.mp3')
    mixer.music.set_volume(self.music_val)
    mixer.music.play(-1)
    
  def __regulate_volume(self, volval: float) -> None:
    mixer.music.set_volume(volval)
    self.music_val = volval
    
  def cutscene(self) -> None:
    self.__press.play()
    mixer.music.stop()
    self.__cutscene=True
  
  def game(self) -> None:
    self.__press.play()
    mixer.music.stop()
    self.__game=True
    
  def quit(self) -> None:
    self.__press.play()
    mixer.music.stop()
    tm.sleep(0.2)
    self.__interrupted=True
  
  def __move(self) -> None:
    self.__bg.update()    
    
  def run(self) -> None:
    while not self.__cutscene and not self.__interrupted and not self.__game:
      self.__check_event()
      self.__move()
      self.__draw()
      self.__status_update()
      
  def __check_event(self) -> None:
    events = event.get()
    pressed_LMB = mouse.get_pressed()[0]
    for ev in events:
      if ev.type == QUIT:
        self.__interrupted = True
      
      if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
        if self.__slider_rect.collidepoint(ev.pos):
          self.__volume_slider.move(ev.pos[0])
          self.__regulate_volume(self.__volume_slider.get_slider_value()/100)
    mouse_pos = mouse.get_pos()      
    if pressed_LMB and self.__slider_rect.collidepoint(mouse_pos):
      self.__volume_slider.move(mouse_pos[0])
      self.__regulate_volume(self.__volume_slider.get_slider_value()/100)

    mouse_pos = mouse.get_pos()
    for i, button_rect in enumerate(self.__button_rects):
      if i not in self.__hover_states.keys():
        self.__hover_states[i] = None       
      if button_rect.collidepoint(mouse_pos):
        if not self.__hover_states[i]:
            if i == 2:  
              self.__hover_quit.play()
            else:
              self.__hover.play()
            self.__hover_states[i] = True
      else:
        self.__hover_states[i] = False
        
    for c, button in enumerate(self.__buttons):
      button.listen(events)
    pygame_widgets.update(events)
      
  def __draw(self) -> None:
    self.__screen.blit(self.__bg.get_bg(), (0, self.__bg.pos))
    self.__screen.blit(self.__bg.get_bg(), (0, self.__bg.pos-self.__h))
    self.__screen.blit(self.__music_icon, (self.__w//9 - self.__w//9, self.__h//2-self.__h//2.5 + 30 + 2*self.__h//8 +self.__h//8 -self.__h//25))
    for button in self.__buttons:
      button.draw()
    self.__volume_slider.draw()
    display.flip()
    self.__clock.tick(self.fps)
  
  def __status_update(self) -> str:
    if self.__interrupted:
      self.p.state = 'over'
      self.p.execute()
    elif self.__cutscene:
      self.p.state = 'cutscene_intro'
      for i in self.__buttons:
        i.hide()
      self.p.execute()
    elif self.__game:
      self.p.state = 'game'
      for i in self.__buttons:
        i.hide()
      self.p.execute()

class ControllerEngine:
  def __init__(self, w: int, h: int, c: tuple[int], fps: int) ->None :
    init()
    self.__screen = display.set_mode((w, h), FULLSCREEN | SCALED)
    self.__game_engine = GameEngine(w, h, c, fps, self.__screen, self)
    self._menu_engine = MenuEngine(w, h, c, fps, self.__screen, self)
    self.__cutscene_engine= CutsceneEngine(w, h, c, fps, self.__screen, self)
    mixer.set_num_channels(100)
    self._player_hp = 'TBD'
    self.state = 'menu'
    
    
  
  def execute(self) -> None:
    if self.state=='game':
      self.__game_engine.run()
    elif self.state == 'menu':
      self._menu_engine.run()
    elif self.state == 'cutscene_intro':
      self.__cutscene_engine.run('cutscene_intro')
    elif self.state == 'cutscene_lost':
      self.__cutscene_engine.run('cutscene_lost')
    elif self.state == 'cutscene_won':
      self.__cutscene_engine.run('cutscene_won')
    elif self.state == 'over':
      quit()
      sys.exit()
 
     
Game = ControllerEngine(1920, 1080, (0, 0, 0), 60)
Game.execute()