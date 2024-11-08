import pygame, simpleGE, random

class TransparentCatcher(simpleGE.Sprite):
    
    def __init__(self,scene):
        super().__init__(scene)
        self.setImage("catcher.png")
        self.setSize(1, 480)
        self.position = (0, 240)

class Pitcher(simpleGE.Sprite):
    
    def __init__(self,scene):
        super().__init__(scene)
        self.setImage("pitcher.png")
        self.setSize(50, 70)
        self.position = (520, 240)

class Ball(simpleGE.Sprite):
    
    def __init__(self, scene):
        super().__init__(scene)   
        self.setImage("ball.png")
        self.setSize(25, 25)
        self.minSpeed = -15
        self.maxSpeed = -1
        self.screenWidth = 520  
        self.screenHeight = 480
        self.reset()

    def reset(self):
        self.x = self.screenWidth
        self.y = random.randint(150, self.screenHeight)
        self.dx = random.randint(self.minSpeed, self.maxSpeed)

class Batter(simpleGE.Sprite):
    
    def __init__(self, scene):
        super().__init__(scene)
        self.originalImage = "batter.png"
        self.setImage(self.originalImage)
        self.setSize(50, 70)
        self.position = (120, 240)
        self.contactImage = "homerun.png"
        self.contactDuration = 500
        self.contactTimer = 0

    def process(self):
        keysDown = pygame.key.get_pressed()
        if keysDown[pygame.K_UP]:
            self.y -= 7
        if keysDown[pygame.K_DOWN]:
            self.y += 7
        if self.contactTimer > 0:
            self.contactTimer -= 1000 / 30
            if self.contactTimer <= 0:
                self.setImage(self.originalImage)
                
    def hit(self):
        self.setImage(self.contactImage)  
        self.setSize(50, 70)  
        self.contactTimer = self.contactDuration

class Game(simpleGE.Scene):
    def __init__(self, hits=0, innings=0, outs=0, strikes=0):
        super().__init__()
        pygame.font.init()  
        self.setImage("field.jpg")

        pygame.mixer.init()
        self.sndHits = pygame.mixer.Sound("hits.wav")
        self.sndStrikes = pygame.mixer.Sound("strikes.wav")
        self.sndOuts = pygame.mixer.Sound("outs.wav")
        self.sndInnings = pygame.mixer.Sound("innings.wav")

        self.hits = hits
        self.innings = innings
        self.outs = outs
        self.strikes = strikes
        
        self.batter = Batter(self)
        self.pitcher = Pitcher(self)
        self.transparentCatcher = TransparentCatcher(self)
        self.numBall = 10
        self.ball = [Ball(self) for i in range(self.numBall)]
            
        self.sprites = [self.batter, *self.ball, self.pitcher, self.transparentCatcher]

        self.lblInnings = simpleGE.Label()
        self.lblOuts = simpleGE.Label()
        self.lblStrikes = simpleGE.Label()
        self.lblHits = simpleGE.Label()
        
        labelX1 = 550
        labelX2 = 350
        font_size = 12 
        bgColor = (0, 100, 0)  
        
        for lbl in [self.lblInnings, self.lblOuts, self.lblStrikes, self.lblHits]:
            lbl.fontSize = font_size
            lbl.bgColor = bgColor
            
        self.lblInnings.center = (labelX1, 20)
        self.lblOuts.center = (labelX1, 80)
        self.lblStrikes.center = (labelX1, 50)
        self.lblHits.center = (labelX2, 50)

        self.sprites.extend([self.lblInnings, self.lblOuts, self.lblStrikes, self.lblHits])
        
        self.updateLabels()

    def updateLabels(self):
        self.lblInnings.text = f"Innings: {self.innings}"
        self.lblOuts.text = f"Outs: {self.outs}"
        self.lblStrikes.text = f"Strikes: {self.strikes}"
        self.lblHits.text = f"Hits: {self.hits}"
        
    def process(self):

        for ball in self.ball:
            if self.batter.collidesWith(ball):
                self.hits += 1
                self.sndHits.play()
                ball.reset()
                self.batter.hit()
                self.updateLabels()

        for ball in self.ball:
            if self.transparentCatcher.collidesWith(ball):
                self.strikes += 1
                self.sndStrikes.play()
                ball.reset()
                if self.strikes == 3:
                    self.outs += 1
                    self.sndOuts.play()
                    self.strikes = 0
                    if self.outs == 3:
                        self.innings += 1
                        self.sndInnings.play()
                        self.outs = 0

                    
                self.updateLabels()
                
                
        if self.innings >= 10:
            self.stop()
            return False
        return True

                                
class Instructions(simpleGE.Scene):
    def __init__(self, hits=0, innings=0):
        super().__init__()
        self.setImage("field.jpg")
        
        self.response = "Play"
        
        self.instructions = simpleGE.MultiLabel()
        self.instructions.textLines = [
            "You are Shohei Ohtani.",
            "Move with the up and down arrow keys",
            "and hit as many ball as possible before the 9th inning ends.",
            "The ball will come from the right side,",
            "and it is a strike if the ball touches",
            "the left boundary without you hitting.",
            "3 strikes = 1 out, and 3 outs = 1 inning",
            "",
            "Good Luck!"
        ]
        
        self.instructions.center = (320, 200)
        self.instructions.size = (600, 350)
        
        self.prevHits = hits
        self.lblHits = simpleGE.Label()
        self.lblHits.text = (f"Last score: {self.prevHits} hits")
        self.lblHits.center = (320, 400)
        self.lblHits.size = (300, 40)
        self.lblHits.fontSize = 12  
        
        self.btnPlay = simpleGE.Button()
        self.btnPlay.text = "Play (right)"
        self.btnPlay.center = (575, 400)
        self.btnPlay.size = (100, 30)

        self.btnQuit = simpleGE.Button()
        self.btnQuit.text = "Quit (left)"
        self.btnQuit.center = (75, 400)
        self.btnQuit.size = (100, 30)
        
        self.sprites = [self.instructions, self.lblHits, self.btnQuit, self.btnPlay]
        
    def process(self):
        if self.btnQuit.clicked:
            self.response = "Quit"
            self.stop()
        if self.btnPlay.clicked:
            self.response = "Play"
            self.stop()

        if self.isKeyPressed(pygame.K_RIGHT):
            self.response = "Play"
            self.stop()
        if self.isKeyPressed(pygame.K_LEFT):
            self.response = "Quit"
            self.stop()

def main():
    keepGoing = True
    hits = 0
    innings = 0
    
    while keepGoing:
        instructions = Instructions(hits, innings)
        instructions.start()  
                
        if instructions.response == "Play":
            hits = 0
            innings = 0
            
            game = Game(hits, innings) 
            game.start()
            
            while game.process():  
                pass
            
            hits = game.hits
            innings = game.innings

        else:
            keepGoing = False  


if __name__ == "__main__":
    main()
