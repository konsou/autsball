# level1
level = {10: '   W   WW      W',
         11: ' W W W W  WW    ',
         12: ' W W W  W  W W  ',
         13: '     W    W  WW ',
         14: '  W  WWWWW      ',
         15: 'W  W   W WWWW  W',
         16: '  W          W  ',
         17: '  W  W   P  W   ',
         18: '     W    W W W ',
         19: 'WWW  W  WWWWW W ',
         20: '  W  WWW W    W ',
         21: 'W  W   WW  WW W ',
         22: ' W   W   W   WW ',
         23: '  WW W WW     W ',
         24: ' W   W W   W W  ',
         25: '   W W  W  WXW  '}



# add wall to wallObjs

def addWalls(self, level):
    downCoord = 0
    for i in range(10, 26, 1):
        rightCoord = 0
        for j in range(0, 16, 1):
            if level[i][j] == 'W':
                wallObjs.append(wallObject.drawWalls(self, rightCoord, downCoord))
                self.wall['x'] = rightCoord
                self.wall['y'] = downCoord
            rightCoord += 50
        downCoord += 50

def loopDraw(self):
    # return self.data
    for wObj in wallObjs:
        wObj['rect'] = pygame.Rect((wObj['x'],
                                    wObj['y'],
                                    wObj['width'],
                                    wObj['height']))
        DispSurf.blit(wObj['surface'], wObj['rect'])

def drawWalls(self, x, y):
    self.wall = {}
    self.wall['width'] = 50
    self.wall['height'] = 50
    self.wall['x'], self.wall['y'] = (x, y)
    self.wall['rect'] = pygame.Rect((self.wall['x'], self.wall['y'], self.wall['width'], self.wall['height']))
    self.wall['left'] = self.wall['rect'].left
    self.wall['right'] = self.wall['rect'].right
    self.wall['top'] = self.wall['rect'].top
    self.wall['bottom'] = self.wall['rect'].bottom
    self.wall['surface'] = pygame.transform.scale(self.image, (self.wall['width'], self.wall['height']))