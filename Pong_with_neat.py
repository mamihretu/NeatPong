
# import modules

import turtle
import os
import neat
import numpy as np



#create window and set parameters

wn = turtle.Screen()
wn.title("Pong")
wn.bgcolor("black")
wn.setup(width=800, height=600)
wn.tracer(0)

# get root canvas to properly close the window
canvas = wn.getcanvas()  # or, equivalently: turtle.getcanvas()
root = canvas.winfo_toplevel()

def on_close():
    global running
    running = False




#initialize generations 
gen = 0


#custom paddle class to create pong paddles
class Paddle():

    def __init__(self, goto_x, goto_y, speed = 0, shape = "square", color = None, wid_stretch = 2, len_stretch = 1):
        self.paddle = turtle.Turtle()
        self.paddle.speed(speed)
        self.paddle.shape(shape)
        self.paddle.color(color)
        self.paddle.shapesize(stretch_wid = wid_stretch , stretch_len = len_stretch)
        self.paddle.penup()
        self.paddle.goto(goto_x, goto_y)


    def move_up(self):
        y = self.paddle.ycor()
        y += 20
        self.paddle.sety(y)

    def move_down(self):
        y = self.paddle.ycor()
        y -= 20
        self.paddle.sety(y)

    def clear(self):
        self.paddle.clear()

    def xcor(self):
        return self.paddle.xcor()  

    def ycor(self):
        return self.paddle.ycor() 


  
#custom ball class to create ball
class Ball():
    def __init__(self, goto_x, goto_y, speed = 0, shape = "circle", color = "yellow"):
        self.ball = turtle.Turtle()
        self.ball.speed(speed)
        self.ball.shape(shape)
        self.ball.color(color)
        self.ball.penup()
        self.ball.goto(goto_x, goto_y)



    def up(self):
        y = self.ball.ycor()
        y += 20
        self.ball.sety(y)

    def down(self):
        y = self.ball.ycor()
        y -= 20
        self.ball.sety(y)

    def setx(self, new_X):
        self.ball.setx(new_X)
    
    def sety(self, new_Y):
        self.ball.sety(new_Y)  
    
    def goto(self, goto_x, goto_y):
        self.ball.goto(goto_x, goto_y)


    def xcor(self):
        return self.ball.xcor()  

    def ycor(self):
        return self.ball.ycor() 

    def clear(self):
        self.ball.clear()



#custom pen class to create pen
class Pen():
    def __init__(self, goto_x = 0, goto_y = 260, speed = 0, shape = "square", color = "white"):
        self.pen = turtle.Turtle()
        self.pen.speed(speed)
        self.pen.shape(shape)
        self.pen.color(color)
        self.pen.penup()
        self.pen.goto(goto_x, goto_y)
        self.pen.hideturtle()



    def write(self, text):
        self.pen.write(text, align="center", font=("Courier", 24, "normal"))

    def clear(self):
        self.pen.clear()



#fitness function for each paddle
def fitness_func(genomes, config):
    """
    runs the simulation of the current population of
    paddles and sets their fitness how long they last in the game
    """
    global wn
    best_score = 0
    game_score = 0
    global gen
    gen += 1 
    ball = Ball(0, 0)
    X_vel = 2
    Y_vel = 1.5
    pen = Pen()
    pen.write("Gen: {}   best_score: {}  game_score: {}".format(gen-1, best_score, game_score))

    """
    start by creating lists holding the genome itself, the
    neural network associated with the genome and the
    paddle object that uses that network to play and 
    finally populate them
    """

    nets = []
    paddles = []
    ge = []


    #population size = 50
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        color_list = ["blue", "yellow", "red","white", "orange"]
        c = np.random.randint(4)
        paddles.append(Paddle(-350,np.random.randint(-20,20), color=color_list[c]))
        ge.append(genome)



    #main game loop
    while len(paddles) > 0 and running == True:
        
        
        # Move the ball
        ball.setx(int(ball.xcor() + X_vel))
        ball.sety(int(ball.ycor() + Y_vel))

        # create a wall on the right side
        if ball.xcor() > 350: 
            X_vel *= -1 


        # Top and bottom bounce
        if ball.ycor() > 290:
            ball.sety(290)
            Y_vel *= -1
   
        
        elif ball.ycor() < -290:
            ball.sety(-290)
            Y_vel *= -1
            

        """pass the position of the ball, velocity of the ball, 
           and position of each paddle as a parameter for the network 
           controling the paddle 
        """ 
        for x, paddle in enumerate(paddles):  

            # give each paddle a fitness of survival time for each loop it stays alive
            ge[x].fitness += 0.05 

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[paddles.index(paddle)].activate((paddle.ycor(), ball.ycor(), ball.xcor(), X_vel, Y_vel))

            # use output to make decision
            if output[0] > 0.5:
                paddle.move_up()

            else:
                paddle.move_down()


        
        for paddle in paddles:

            # kill paddles that go off screan    
            if abs(paddle.ycor())  > 350 :
                ge[paddles.index(paddle)].fitness -= 5
                nets.pop(paddles.index(paddle))
                ge.pop(paddles.index(paddle))
                paddles.pop(paddles.index(paddle))
                paddle.clear()

            # reward the paddles that hit the ball    
            if ball.xcor() <= -340 and paddle.ycor() + 50 > ball.ycor() > paddle.ycor() - 50:
                print(len(paddles))
                ge[paddles.index(paddle)].fitness += 5
                X_vel*= -1
                best_score+= 5
                pen.clear()
                pen.write("Gen: {}   best_score: {}  game_score: {}".format(gen-1, best_score, game_score))

            # kill paddles which miss the ball
            if ball.xcor() == -340 and abs(ball.ycor()) > abs(paddle.ycor()) + 50: 
            
                print("length was:", len(paddles))

                ge[paddles.index(paddle)].fitness -= 5
                nets.pop(paddles.index(paddle))
                ge.pop(paddles.index(paddle))
                paddles.pop(paddles.index(paddle))
                print("length became:", len(paddles))
                paddle.clear()
            
        #kill all paddles if system scores
        if ball.xcor() < -340 :
            game_score += 1
            pen.clear()
            pen.write("Gen: {}   best_score: {}  game_score: {}".format(gen-1, best_score, game_score))
            ball.goto(0, 0)
            X_vel *= -1
            for paddle in paddles:
                paddle.clear()
                print("length was:", len(ge))
                ge[paddles.index(paddle)].fitness -= 5
                nets.pop(paddles.index(paddle))
                ge.pop(paddles.index(paddle))
                paddles.pop(paddles.index(paddle))
                print("length became:", len(ge))
                


        wn.update()
    wn.clear()
    wn = turtle.Screen()
    wn.title("Pong")
    wn.bgcolor("black")
    wn.setup(width=800, height=600)
    wn.tracer(0)



def runner(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)


    

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))

    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations.
    winner = p.run(fitness_func, 50)



    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.



    root.protocol("WM_DELETE_WINDOW", on_close)
    running = True  
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    runner(config_path)


