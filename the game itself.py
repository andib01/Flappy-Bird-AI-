import pygame
import neat
import os
import random

pygame.font.init()

WIN_WIDTH = 550
WIN_HEIGHT = 800

# loading images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("pics", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("pics", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("pics", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("pics", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("pics", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("pics", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


# Bird class
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    # constants for the bird class

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    # setting up the jump command
    def jump(self):
        self.vel = -10
        self.tick_count = 0  # keeps track of when we last jumped
        self.height = self.y  # keeps track of where the bird jumped from

    def move(self):
        self.tick_count += 1  # this is for keeping track how many times we moved since the last jump

        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2  # d = how many pixels the bird is moving up or down during this frame

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2  # this tells us if we are moving updwards, lets move a bit more

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:  # every time we jump ,we keep track where we jump from
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:  # this allows us to rotate the bird 90 deg since we dont want complete rotation
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # This is for showing each image depending on the animation used at that moment

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # this is to stop the bird from flapping its wings while it is tilted downards

        if self.tilt <= 80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # rotating an imagine around its center (pygame)

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # this is used for collision with objects

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


# pipe class

class Pipe:
    GAP = 200  # how much space is between the pipes
    VEL = 5  # how fast is the pipe moving

    def __init__(self, x):  # the reason we only include x is because the height(y) will be randomised
        self.x = x
        self.height = 0

        # variables that keep track of where the bottom/top pipe are drawn, how tall they are
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    # moving the pipes
    def move(self):
        self.x -= self.VEL

    # drawing the pipes
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # collision function
    def collide(self, bird, ):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # checking the distance between two masks
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # figuring out if the masks collide
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # check if either of these points exist
        if t_point or b_point:  # if they are not none
            return True

        return False


# constants for class base
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        # the if statements are causing a circular motion where the image furthest to the left comes back after leaving the screen
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # drawing the two base images
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


# drawing the window for the game

def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    # rendering font that tells us the score

    text = STAT_FONT.render("Score " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    for bird in birds:
        bird.draw(win)
    pygame.display.update()


# game loop

def main(genomes, config):
    nets = []  # keeping track of the birds in the neural networks
    ge = []  # keeping track of the genomes
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    # birds = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(550)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False  # if there are no birds left we quit the game
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()


        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1  # every time a bird hits the pipe it loses 1 fitness score
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # checking if the pipe is off the screen
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(700))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:  # this is for checking if the bird hit the ground
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "AI.txt")
    run(config_path)
