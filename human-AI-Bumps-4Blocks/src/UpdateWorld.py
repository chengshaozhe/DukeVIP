import numpy as np
from numpy import random
import copy
import random
from math import floor


class UpdateWorld1P2G():
    def __init__(self,direction,dimension):
        self.direction=direction
        self.dimension=dimension

    def __call__(self,bottom,height):
        direction=random.choice(self.direction)
        if direction==0:
            pacmanPosition=(floor(self.dimension/2),random.randint(height,self.dimension-1))
            bean1Position=(pacmanPosition[0]-floor(bottom/2),pacmanPosition[1]-height)
            bean2Position=(pacmanPosition[0]+floor(bottom/2),pacmanPosition[1]-height)
        elif direction==180:
            pacmanPosition = (floor(self.dimension / 2),random.randint(0, self.dimension - 1-height))
            bean1Position = (pacmanPosition[0] - floor(bottom / 2), pacmanPosition[1] + height)
            bean2Position = (pacmanPosition[0] + floor(bottom / 2), pacmanPosition[1] + height)
        elif direction==90:
            pacmanPosition = (random.randint(0, self.dimension - 1-height),floor(self.dimension / 2))
            bean1Position = (pacmanPosition[0] + height,pacmanPosition[1]- floor(bottom / 2) )
            bean2Position = (pacmanPosition[0] + height,pacmanPosition[1]+ floor(bottom / 2))
        else:
            pacmanPosition = (random.randint(height,self.dimension-1),floor(self.dimension / 2))
            bean1Position = (pacmanPosition[0] - height, pacmanPosition[1] - floor(bottom / 2))
            bean2Position = (pacmanPosition[0] - height, pacmanPosition[1] + floor(bottom / 2))
        return pacmanPosition,bean1Position,bean2Position,direction

class UpdateWorld():
    def __init__(self,direction,dimension):
        self.direction=direction
        self.dimension=dimension

    def __call__(self,bottom,height):
        direction=random.choice(self.direction)
        if direction==0:
            pacmanPosition=(floor(self.dimension/2),random.randint(2* height, self.dimension - 1))
            pacman2Position = (pacmanPosition[0],pacmanPosition[1] - 2 * height)
            bean1Position=(pacmanPosition[0]-floor(bottom/2),pacmanPosition[1]-height)
            bean2Position=(pacmanPosition[0]+floor(bottom/2),pacmanPosition[1]-height)
        elif direction==180:
            pacmanPosition = (floor(self.dimension / 2),random.randint(0, self.dimension - 2 * height - 1))
            pacman2Position = (pacmanPosition[0],pacmanPosition[1]+ 2 * height)
            bean1Position = (pacmanPosition[0] - floor(bottom / 2), pacmanPosition[1] + height)
            bean2Position = (pacmanPosition[0] + floor(bottom / 2), pacmanPosition[1] + height)
        elif direction==90:
            pacmanPosition = (random.randint(0, self.dimension - 2 * height - 1),floor(self.dimension / 2))
            pacman2Position = (pacmanPosition[0] + 2 * height,pacmanPosition[1] )
            bean1Position = (pacmanPosition[0] + height,pacmanPosition[1]- floor(bottom / 2) )
            bean2Position = (pacmanPosition[0] + height,pacmanPosition[1]+ floor(bottom / 2))
        else:

            pacmanPosition = (random.randint(2 * height, self.dimension - 1),floor(self.dimension / 2))
            pacman2Position = (pacmanPosition[0] - 2 * height,pacmanPosition[1] )
            bean1Position = (pacmanPosition[0] - height, pacmanPosition[1] - floor(bottom / 2))
            bean2Position = (pacmanPosition[0] - height, pacmanPosition[1] + floor(bottom / 2))
        if np.random.randint(0,2):
            return pacmanPosition,pacman2Position,bean1Position,bean2Position, direction
        else:
            return pacman2Position, pacmanPosition, bean1Position, bean2Position, direction

def createNoiseDesignValue(condition,blockNumber):
    noiseDesignValuesIndex=random.sample(list(range(len(condition))),blockNumber)
    noiseDesignValues=np.array(condition)[noiseDesignValuesIndex].flatten().tolist()
    random.shuffle(noiseDesignValues)
    noiseDesignValues.append('special')
    return noiseDesignValues

def createShapeDesignValue(bottom,height):
    shapeDesignValues = [[b, h] for b in bottom for h in height]
    random.shuffle(shapeDesignValues)
    shapeDesignValues.append([random.choice(bottom), random.choice(height)])
    return shapeDesignValues

def main():
    pass

if __name__=="__main__":
    main()
