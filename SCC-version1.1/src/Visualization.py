import pygame as pg
import numpy as np
import os



class DrawBackground():
    def __init__(self, screen, grid_size, grid_resolution, background_color):
        self.screen = screen
        self.grid_size = grid_size
        self.grid_resolution = grid_resolution
        self.cell_size = grid_resolution // grid_size
        self.background_color = background_color

        screen_width, screen_height = screen.get_size()
        self.grid_x = (screen_width - grid_resolution) // 2
        self.grid_y = (screen_height - grid_resolution) // 2


    def __call__(self):
        self.screen.fill((0, 0, 0))
        pg.draw.rect(self.screen, self.background_color, (self.grid_x, self.grid_y, self.grid_resolution, self.grid_resolution))

        for x in range(1, self.grid_size):
            pg.draw.line(self.screen, (0, 0, 0), (self.grid_x + x * self.cell_size, self.grid_y),
                         (self.grid_x + x * self.cell_size, self.grid_y + self.grid_resolution), 1)
            pg.draw.line(self.screen, (0, 0, 0), (self.grid_x, self.grid_y + x * self.cell_size),
                         (self.grid_x + self.grid_resolution, self.grid_y + x * self.cell_size), 1)
        return


class DrawNewState2P2G():
    def __init__(self, screen, drawBackground, targetColor, playerColor, player2Color,  targetRadius, playerRadius):
        self.screen = screen
        self.drawBackground = drawBackground
        self.targetColor = targetColor
        self.playerColor = playerColor
        self.player2Color = player2Color
        self.targetRadius = targetRadius
        self.playerRadius = playerRadius
        self.grid_x = drawBackground.grid_x
        self.grid_y = drawBackground.grid_y
        self.cell_size = drawBackground.cell_size


    def __call__(self, targetPositionA, targetPositionB, playerPosition, player2Position, ifnoisePlayer1, ifnoisePlayer2):

        self.drawBackground()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    exit()

        targets = [targetPositionA, targetPositionB]
        players = [playerPosition, player2Position]
        self.player_colors = [self.playerColor, self.player2Color]

        for idx, target_pos in enumerate(targets):
            # Use the color at the index of the current target
            target_grid_x, target_grid_y = target_pos
            target_x = self.grid_x + target_grid_x * self.cell_size
            target_y = self.grid_y + target_grid_y * self.cell_size
            target_width = self.cell_size - 20  # Subtract more to make it smaller
            target_height = self.cell_size - 20
            target_x_centered = target_x + (self.cell_size - target_width) // 2
            target_y_centered = target_y + (self.cell_size - target_height) // 2
            pg.draw.rect(self.screen, self.targetColor, (target_x_centered, target_y_centered, target_width, target_height))

        spaceOverlapping = 1/2*self.playerRadius


        if playerPosition == player2Position:

            for idx, player_pos in enumerate(players):
                color = self.player_colors[idx % len(self.player_colors)]
                player_grid_x, player_grid_y = player_pos
                player_center_x = self.grid_x + player_grid_x * self.cell_size + self.cell_size // 2
                player_center_y = self.grid_y + player_grid_y * self.cell_size + self.cell_size // 2

                if idx == 0:
                    pg.draw.circle(self.screen, color, (player_center_x - spaceOverlapping, player_center_y) , self.playerRadius)
                else:
                    pg.draw.circle(self.screen, color, (player_center_x + spaceOverlapping, player_center_y) , self.playerRadius)

        else:
            for idx, player_pos in enumerate(players):
                color = self.player_colors[idx % len(self.player_colors)]
                player_grid_x, player_grid_y = player_pos
                player_center_x = self.grid_x + player_grid_x * self.cell_size + self.cell_size // 2
                player_center_y = self.grid_y + player_grid_y * self.cell_size + self.cell_size // 2
                pg.draw.circle(self.screen, color, (player_center_x, player_center_y), self.playerRadius)


        pg.display.flip()
        return


class DrawNewState1P1G():
    def __init__(self, screen, drawBackground, targetColor, playerColor, targetRadius, playerRadius):
        self.screen = screen
        self.drawBackground = drawBackground
        self.targetColor = targetColor
        self.playerColor = playerColor
        self.targetRadius = targetRadius
        self.playerRadius = playerRadius
        self.grid_x = drawBackground.grid_x
        self.grid_y = drawBackground.grid_y
        self.cell_size = drawBackground.cell_size

    def __call__(self, targetPosition, playerPosition):

        self.drawBackground()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    exit()

        if targetPosition:
            target_grid_x, target_grid_y = targetPosition
            target_x = self.grid_x + target_grid_x * self.cell_size
            target_y = self.grid_y + target_grid_y * self.cell_size
            target_width = self.cell_size - 20  # Subtract more to make it smaller
            target_height = self.cell_size - 20
            target_x_centered = target_x + (self.cell_size - target_width) // 2
            target_y_centered = target_y + (self.cell_size - target_height) // 2
            pg.draw.rect(self.screen, self.targetColor, (target_x_centered, target_y_centered, target_width, target_height))

        player_grid_x, player_grid_y = playerPosition
        player_center_x = self.grid_x + player_grid_x * self.cell_size + self.cell_size // 2
        player_center_y = self.grid_y + player_grid_y * self.cell_size + self.cell_size // 2
        pg.draw.circle(self.screen, self.playerColor, (player_center_x, player_center_y), self.playerRadius)


        pg.display.flip()

        return

class DrawNewState1P2G():
    def __init__(self, screen, drawBackground, targetColor, playerColor, targetRadius, playerRadius):
        self.screen = screen
        self.drawBackground = drawBackground
        self.targetColor = targetColor
        self.playerColor = playerColor
        self.targetRadius = targetRadius
        self.playerRadius = playerRadius
        self.grid_x = drawBackground.grid_x
        self.grid_y = drawBackground.grid_y
        self.cell_size = drawBackground.cell_size

    def __call__(self, targetPositionA, targetPositionB, playerPosition):
        self.drawBackground()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    exit()

        targets = [targetPositionA, targetPositionB]
        players = [playerPosition]

        for idx, target_pos in enumerate(targets):
            target_grid_x, target_grid_y = target_pos
            target_x = self.grid_x + target_grid_x * self.cell_size
            target_y = self.grid_y + target_grid_y * self.cell_size
            target_width = self.cell_size - 20  # Subtract more to make it smaller
            target_height = self.cell_size - 20
            target_x_centered = target_x + (self.cell_size - target_width) // 2
            target_y_centered = target_y + (self.cell_size - target_height) // 2
            pg.draw.rect(self.screen, self.targetColor, (target_x_centered, target_y_centered, target_width, target_height))

        for idx, player_pos in enumerate(players):
            player_grid_x, player_grid_y = player_pos
            player_center_x = self.grid_x + player_grid_x * self.cell_size + self.cell_size // 2
            player_center_y = self.grid_y + player_grid_y * self.cell_size + self.cell_size // 2
            pg.draw.circle(self.screen, self.playerColor, (player_center_x, player_center_y), self.playerRadius)


        pg.display.flip()
        return self.screen


class DrawFixation():
    def __init__(self, screen, drawBackground, fixation_length=20, fixation_color=(0, 0, 0)):
        self.screen = screen
        self.drawBackground = drawBackground
        self.fixation_length = fixation_length
        self.fixation_color = fixation_color
        self.grid_x = drawBackground.grid_x
        self.grid_y = drawBackground.grid_y
        self.grid_resolution = drawBackground.grid_resolution

    def __call__(self):
        self.drawBackground()

        screen_width, screen_height = self.screen.get_size()
        center_x = self.grid_x + self.grid_resolution // 2
        center_y = self.grid_y + self.grid_resolution // 2

        # Draw vertical line
        pg.draw.line(self.screen, self.fixation_color, (center_x, center_y - self.fixation_length // 2),
                     (center_x, center_y + self.fixation_length // 2), 4)

        # Draw horizontal line
        pg.draw.line(self.screen, self.fixation_color, (center_x - self.fixation_length // 2, center_y),
                     (center_x + self.fixation_length // 2, center_y), 4)

        pg.display.flip()

class DrawImage():
    def __init__(self, screen):
        self.screen = screen
        self.screenCenter = (self.screen.get_width() / 2, self.screen.get_height() / 2)

    def __call__(self, image):
        imageRect = image.get_rect()
        imageRect.center = self.screenCenter
        pause = True
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
        self.screen.fill((0, 0, 0))
        self.screen.blit(image, imageRect)
        pg.display.flip()
        while pause:
            pg.time.wait(10)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    pause = False
            pg.time.wait(10)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP, pg.QUIT])


class DrawLinkImage():
    def __init__(self, screen):
        self.screen = screen
        self.screenCenter = (self.screen.get_width() / 2, self.screen.get_height() / 2)

    def __call__(self, image, time):
        imageRect = image.get_rect()
        imageRect.center = self.screenCenter
        pause = True
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
        self.screen.fill((0, 0, 0))
        self.screen.blit(image, imageRect)
        pg.display.flip()
        pg.time.wait(time)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP, pg.QUIT])


class DrawText():
    def __init__(self, screen, drawBackground, size):
        self.screen = screen
        self.screenCenter = (self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.drawBackground = drawBackground
        self.leaveEdgeSpace = drawBackground.leaveEdgeSpace
        self.widthLineStepSpace = drawBackground.widthLineStepSpace
        self.heightLineStepSpace = drawBackground.heightLineStepSpace
        self.size = size

    def __call__(self, text, textColorTuple, textPositionTuple):
        self.drawBackground()
        font = pg.font.Font(None, self.size)
        textObj = font.render(text, 1, textColorTuple)
        self.screen.blit(textObj, [int((textPositionTuple[0] + self.leaveEdgeSpace + 0.2) * self.widthLineStepSpace),
                                   int((textPositionTuple[1] + self.leaveEdgeSpace - 0.1) * self.heightLineStepSpace)])
        pg.display.flip()
        return

# class DrawBackground():
#     def __init__(self, screen, gridSize, leaveEdgeSpace, backgroundColor, lineColor, lineWidth, textColorTuple):
#         self.screen = screen
#         self.gridSize = gridSize
#         self.leaveEdgeSpace = leaveEdgeSpace
#         self.widthLineStepSpace = int(screen.get_width() / (gridSize + 2 * self.leaveEdgeSpace))
#         self.heightLineStepSpace = int(screen.get_height() / (gridSize + 2 * self.leaveEdgeSpace))
#         self.backgroundColor = backgroundColor
#         self.lineColor = lineColor
#         self.lineWidth = lineWidth
#         self.textColorTuple = textColorTuple

#     def __call__(self):
#         self.screen.fill((0, 0, 0))
#         pg.draw.rect(self.screen, self.backgroundColor, pg.Rect(int(self.leaveEdgeSpace * self.widthLineStepSpace), int(self.leaveEdgeSpace * self.heightLineStepSpace),int(self.gridSize * self.widthLineStepSpace), int(self.gridSize * self.heightLineStepSpace)))
#         for i in range(self.gridSize + 1):
#             pg.draw.line(self.screen, self.lineColor, [int((i + self.leaveEdgeSpace) * self.widthLineStepSpace), int(self.leaveEdgeSpace * self.heightLineStepSpace)],
#                          [int((i + self.leaveEdgeSpace) * self.widthLineStepSpace), int((self.gridSize + self.leaveEdgeSpace) * self.heightLineStepSpace)], self.lineWidth)
#             pg.draw.line(self.screen, self.lineColor, [int(self.leaveEdgeSpace * self.widthLineStepSpace), int((i + self.leaveEdgeSpace) * self.heightLineStepSpace)],
#                          [int((self.gridSize + self.leaveEdgeSpace) * self.widthLineStepSpace), int((i + self.leaveEdgeSpace) * self.heightLineStepSpace)], self.lineWidth)
#         return


# class DrawNewState1P2G():
#     def __init__(self, screen, drawBackground, targetColor, playerColor, targetRadius, playerRadius):
#         self.screen = screen
#         self.drawBackground = drawBackground
#         self.targetColor = targetColor
#         self.playerColor = playerColor
#         self.targetRadius = targetRadius
#         self.playerRadius = playerRadius
#         self.leaveEdgeSpace = drawBackground.leaveEdgeSpace
#         self.widthLineStepSpace = drawBackground.widthLineStepSpace
#         self.heightLineStepSpace = drawBackground.heightLineStepSpace

#     def __call__(self, targetPositionA, targetPositionB, playerPosition):
#         self.drawBackground()
#         for event in pg.event.get():
#             if event.type == pg.QUIT:
#                 pg.quit()
#             if event.type == pg.KEYDOWN:
#                 if event.key == pg.K_ESCAPE:
#                     pg.quit()
#                     exit()
#         pg.draw.rect(self.screen, self.targetColor, [int((targetPositionA[0] + self.leaveEdgeSpace + 0.2) * self.widthLineStepSpace),
#                                                      int((targetPositionA[1] + self.leaveEdgeSpace + 0.2) * self.heightLineStepSpace), self.targetRadius * 2, self.targetRadius * 2])
#         pg.draw.rect(self.screen, self.targetColor, [int((targetPositionB[0] + self.leaveEdgeSpace + 0.2) * self.widthLineStepSpace),
#                                                      int((targetPositionB[1] + self.leaveEdgeSpace + 0.2) * self.heightLineStepSpace), self.targetRadius * 2, self.targetRadius * 2])
#         pg.draw.circle(self.screen, self.playerColor, [int((playerPosition[0] + self.leaveEdgeSpace + 0.5) * self.widthLineStepSpace),
#                                                        int((playerPosition[1] + self.leaveEdgeSpace + 0.5) * self.heightLineStepSpace)], self.playerRadius)
#         pg.display.flip()
#         return self.screen


# class DrawNewState2P2G():
#     def __init__(self, screen, drawBackground, targetColor, playerColor, player2Color,  targetRadius, playerRadius):
#         self.screen = screen
#         self.drawBackground = drawBackground
#         self.targetColor = targetColor
#         self.playerColor = playerColor
#         self.player2Color = player2Color
#         self.targetRadius = targetRadius
#         self.playerRadius = playerRadius
#         self.leaveEdgeSpace = drawBackground.leaveEdgeSpace
#         self.widthLineStepSpace = drawBackground.widthLineStepSpace
#         self.heightLineStepSpace = drawBackground.heightLineStepSpace

#     def __call__(self, targetPositionA, targetPositionB, playerPosition, player2Position, ifnoisePlayer1, ifnoisePlayer2):
#         self.drawBackground()
#         for event in pg.event.get():
#             if event.type == pg.QUIT:
#                 pg.quit()
#             if event.type == pg.KEYDOWN:
#                 if event.key == pg.K_ESCAPE:
#                     pg.quit()
#                     exit()

#         pg.draw.rect(self.screen, self.targetColor,
#                      [int((targetPositionA[0] + self.leaveEdgeSpace + 0.2) * self.widthLineStepSpace),
#                       int((targetPositionA[1] + self.leaveEdgeSpace + 0.2) * self.heightLineStepSpace),
#                       self.targetRadius * 2, self.targetRadius * 2])
#         pg.draw.rect(self.screen, self.targetColor,
#                      [int((targetPositionB[0] + self.leaveEdgeSpace + 0.2) * self.widthLineStepSpace),
#                       int((targetPositionB[1] + self.leaveEdgeSpace + 0.2) * self.heightLineStepSpace),
#                       self.targetRadius * 2, self.targetRadius * 2])

#         color1 = self.playerColor
#         color2 = self.player2Color
#         spaceOverlapping = 1/2*self.playerRadius
#         if playerPosition == player2Position:
#             pg.draw.circle(self.screen, color1, [int((playerPosition[0] + self.leaveEdgeSpace + 0.5) * self.widthLineStepSpace) - spaceOverlapping,
#                                                    int((playerPosition[1] + self.leaveEdgeSpace + 0.5) * self.heightLineStepSpace)], self.playerRadius)
#             pg.draw.circle(self.screen, color2, [int((player2Position[0] + self.leaveEdgeSpace + 0.5) * self.widthLineStepSpace) + spaceOverlapping,
#                                                            int((player2Position[1] + self.leaveEdgeSpace + 0.5) * self.heightLineStepSpace)], self.playerRadius)
#         else:
#             pg.draw.circle(self.screen, color1, [int((playerPosition[0] + self.leaveEdgeSpace + 0.5) * self.widthLineStepSpace),
#                                                    int((playerPosition[1] + self.leaveEdgeSpace + 0.5) * self.heightLineStepSpace)], self.playerRadius)
#             pg.draw.circle(self.screen, color2, [int((player2Position[0] + self.leaveEdgeSpace + 0.5) * self.widthLineStepSpace),
#                                                            int((player2Position[1] + self.leaveEdgeSpace + 0.5) * self.heightLineStepSpace)], self.playerRadius)

#         pg.display.flip()


#         return



# class DrawNewState1P1G():
#     def __init__(self, screen, drawBackground, targetColor, playerColor, targetRadius, playerRadius):
#         self.screen = screen
#         self.drawBackground = drawBackground
#         self.targetColor = targetColor
#         self.playerColor = playerColor
#         self.targetRadius = targetRadius
#         self.playerRadius = playerRadius
#         self.leaveEdgeSpace = drawBackground.leaveEdgeSpace
#         self.widthLineStepSpace = drawBackground.widthLineStepSpace
#         self.heightLineStepSpace = drawBackground.heightLineStepSpace

#     def __call__(self, targetPositionA, playerPosition):

#         self.drawBackground()
#         for event in pg.event.get():
#             if event.type == pg.QUIT:
#                 pg.quit()
#             if event.type == pg.KEYDOWN:
#                 if event.key == pg.K_ESCAPE:
#                     pg.quit()
#                     exit()

#         if targetPositionA:
#             pg.draw.rect(self.screen, self.targetColor,
#                          [int((targetPositionA[0] + self.leaveEdgeSpace + 0.2) * self.widthLineStepSpace),
#                           int((targetPositionA[1] + self.leaveEdgeSpace + 0.2) * self.heightLineStepSpace),
#                           self.targetRadius * 2, self.targetRadius * 2])

#         pg.draw.circle(self.screen, self.playerColor, [int((playerPosition[0] + self.leaveEdgeSpace + 0.5) * self.widthLineStepSpace),int((playerPosition[1] + self.leaveEdgeSpace + 0.5) * self.heightLineStepSpace)], self.playerRadius)

#         pg.display.flip()

#         return

