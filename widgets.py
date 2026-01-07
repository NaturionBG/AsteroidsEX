from pygame import *
import numpy as np

def linear_coefficients(player_coords: tuple[int]|list[int], object_coords:tuple[int]|list[int]) -> np.ndarray:
  A = np.array([[1, player_coords[0]], [1, object_coords[0]]])
  b = np.array([player_coords[1], object_coords[1]])
  return np.linalg.solve(A, b)


class Slider:
  def __init__(self, startx: int, starty: int, w:int, h:int, screen: Surface, bgc: tuple[int], handleColor: tuple[int], handleBorder: tuple[int], barBorder: tuple[int], borderThickness: int, initial: int =5) -> None:
    self.x = startx
    self.y = starty
    self.w = w
    self.h = h
    self.__screen = screen
    self.bg = bgc
    self.handle = np.array(handleColor)
    self.handleBorder = handleBorder
    self.borderThickness = borderThickness
    self.barBorder = barBorder
    self.__bar = Rect((self.x+self.borderThickness, self.y+self.borderThickness), (self.w-self.borderThickness, self.h-self.borderThickness))
    self.__borderRect = Rect((self.x, self.y), (self.w+self.borderThickness, self.h+self.borderThickness))
    self.__handlepos = (self.x + initial, (2*self.y + self.h)/2)
    self.__handleRad = self.h
    self.mn = self.x
    self.mx = self.x + self.w
    
  def move(self, x_value: int|float) -> None:
    if self.__handlepos[0]!= x_value and self.x<=x_value<=self.x + self.w:
      self.__handlepos = (x_value, self.__handlepos[1])
    elif self.__handlepos[0]!= x_value and self.x>x_value:
      self.__handlepos = (self.x, self.__handlepos[1])
    elif self.__handlepos[0]!= x_value and self.x+self.w<x_value:
      self.__handlepos = (self.x+self.w, self.__handlepos[1])
      
  def get_slider_value(self) -> int|float:
    scaled = (self.__handlepos[0] - self.mn) / (self.mx - self.mn)
    if scaled<0.05:
      scaled = 0
    if scaled>0.98:
      scaled = 1
    return scaled * 100
  
  def get_rect(self) -> Rect:
    return self.__bar
  
  def draw(self) -> None:
    draw.rect(self.__screen, self.barBorder, self.__borderRect, self.borderThickness, 8)
    draw.rect(self.__screen, self.bg, self.__bar, border_radius=7)
    draw.rect(self.__screen, (0, 155, 255), Rect((self.x+self.borderThickness, self.y+self.borderThickness), (self.__handlepos[0]-self.x, self.h-self.borderThickness)), border_radius=7)
    draw.circle(self.__screen, self.handleBorder, self.__handlepos, self.__handleRad, self.borderThickness)
    draw.circle(self.__screen, self.handle, self.__handlepos, self.__handleRad-self.borderThickness)
    draw.circle(self.__screen, np.where(self.handle>0, self.handle-50, self.handle), self.__handlepos, self.__handleRad-self.borderThickness-5)
  
  
class HealthBar:
  def __init__(self, w: int, h: int, screen: Surface, icon: str, iconw: int, iconh: int):
    self.__screen = screen
    self.__w = w
    self.__h = h
    self.__current_green_left_border = self.__w
    self.__icon_w = iconw
    self.__icon_h = iconh
    self.__icon = transform.scale(image.load(icon).convert_alpha(), (self.__icon_w, self.__icon_h))
    self.__icon.set_colorkey((0, 0, 0))
    
  def update(self, percent: float) -> None:
    if percent<0:
      percent = 0
    self.__current_green_left_border = self.__w*percent
  
  def draw(self, offset_x: int, offset_y: int) -> None:
    icon_rect = self.__icon.get_rect(topleft = (0+10+offset_x, 0+10+offset_y))
    
    self.__screen.blit(self.__icon, icon_rect.topleft)
    draw.rect(self.__screen, (255, 255, 255), icon_rect, 2, 5)
    if self.__current_green_left_border == self.__w:
      draw.rect(self.__screen, (0, 128, 0), Rect((0+10+self.__icon_w+offset_x, 0+10+offset_y), (self.__current_green_left_border, self.__h)), border_radius=5)
    elif self.__current_green_left_border<self.__w:
      draw.rect(self.__screen, (0, 128, 0), Rect((0+10+self.__icon_w+offset_x, 0+10+offset_y), (self.__current_green_left_border, self.__h)), border_bottom_left_radius=5, border_top_left_radius=5)
      draw.rect(self.__screen, (64, 0, 0), Rect((0+10+self.__icon_w+self.__current_green_left_border+offset_x, 0+10+offset_y), (self.__w-self.__current_green_left_border, self.__h)), border_top_right_radius=5, border_bottom_right_radius=5)
    draw.rect(self.__screen, (255, 255, 255), Rect((0+10+self.__icon_w+offset_x, 0+10+offset_y), (self.__w, self.__h)), width=2, border_radius=5)
  
  
