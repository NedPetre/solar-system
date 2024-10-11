import pygame
import math
from datetime import datetime, timedelta

pygame.init()

width, height = 1920, 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Solar System")

bgCOLOUR = (30, 30, 40)

font = pygame.font.SysFont("comicsans", 16)

# Global variables
AU = 149.6e9  # Corrected AU value
G = 6.67428e-11
scale = 250 / AU  # 100px to 1 AU
scaleFactor = 1
Timestep = 3600 * 24  # 1 day


class Planet:
    def __init__(self, x, y, radius, colour, mass):
        self.x = x
        self.y = y
        self.r = radius
        self.colour = colour
        self.m = mass

        self.IS_SUN = False
        self.orbitalPath = []
        self.D_sol = 0
        self.ON_SCREEN = None

        self.Vx = 0
        self.Vy = 0

    def draw(self, win):
        x = self.x * scale + width / 2
        y = self.y * scale + height / 2  # Corrected height
        pygame.draw.circle(win, self.colour, (int(x), int(y)), self.r)

        if len(self.orbitalPath) > 2:
            updated_points = []
            for point in self.orbitalPath:
                x, y = point
                x = x * scale + width / 2
                y = y * scale + height / 2
                updated_points.append((x, y))
            pygame.draw.lines(screen, self.colour, False, updated_points, 2)

    def force(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        self.D_sol = distance

        if distance == 0:
            return 0, 0  # Avoid division by zero

        F = G * self.m * other.m / distance ** 2
        theta = math.atan2(dy, dx)
        Fx = F * math.cos(theta)
        Fy = F * math.sin(theta)

        return Fx, Fy

    def updatePos(self, bodies):
        TFx = TFy = 0
        for body in bodies:
            if self == body:
                continue

            fx, fy = self.force(body)
            TFx += fx
            TFy += fy

        self.Vx += TFx / self.m * Timestep  # Accumulate velocity
        self.Vy += TFy / self.m * Timestep

        self.x += self.Vx * Timestep
        self.y += self.Vy * Timestep

        self.orbitalPath.append((self.x, self.y))
        

            

class Date:
    def __init__(self, startDate):
        self.start = startDate

    def calculate_new_date(self):
        global Timestep  # Declare Timestep as global to access the variable

        # Convert the start date string to a datetime object
        start_date = datetime.strptime(self.start, "%Y-%m-%d %H:%M:%S")

        # Create a timedelta object for the time step
        time_step = timedelta(seconds=Timestep)  # Use the global Timestep variable

        # Calculate the new date
        new_date = start_date + time_step

        self.start = new_date.strftime("%Y-%m-%d %H:%M:%S")

        return new_date

    def render(self):
        new_date = self.calculate_new_date()
        text = font.render(new_date.strftime("%Y-%m-%d"), True, (255, 255, 255))
        tw = text.get_width()
        screen.blit(text, (width/2-tw/2, int(height*0.05)))

def calculate_angle_earth_mars_sun(earth, mars):
    D_earth = earth.D_sol  # Distance from Earth to Sun
    D_mars = mars.D_sol    # Distance from Mars to Sun
    Dx = earth.x - mars.x  # Difference in x-coordinates
    Dy = earth.y - mars.y  # Difference in y-coordinates
    D_EM = math.sqrt(Dx ** 2 + Dy ** 2)  # Distance between Earth and Mars

    # Using the law of cosines to calculate the angle at the Sun
    cos_angle = (D_earth ** 2 + D_mars ** 2 - D_EM ** 2) / (2 * D_earth * D_mars)

    # Clamp the cosine value to the range [-1, 1] to avoid math domain error
    cos_angle = max(-1, min(1, cos_angle))

    angle_radians = math.acos(cos_angle)

    # Convert the angle from radians to degrees
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees

def draw_text(position, string):
    screen.blit(pygame.font.SysFont('comicsans', 16).render(string, True, (255, 255, 255)), position)

def draw_lines_to_sun(planet_1, planet_2):
    earth_x = planet_1.x * scale + width / 2
    earth_y = planet_1.y * scale + height / 2
    sun_x = planet_2.x * scale + width / 2
    sun_y = planet_2.y * scale + height / 2
    pygame.draw.line(screen, 'white', (earth_x, earth_y), (sun_x, sun_y), 1)

def draw_planets(planets, focused_planet=None):
    for planet in planets:
        # Calculate the position based on whether we have a focused planet
        if focused_planet:
            # Center the view on the focused planet
            x = (planet.x - focused_planet.x) * scale + width / 2
            y = (planet.y - focused_planet.y) * scale + height / 2
        else:
            # Default view
            x = planet.x * scale + width / 2
            y = planet.y * scale + height / 2

        # Draw the planet
        pygame.draw.circle(screen, planet.colour, (int(x), int(y)), planet.r)

        # Draw the orbital path if it has more than 2 points
        if len(planet.orbitalPath) > 2:
            updated_points = []
            for point in planet.orbitalPath:
                px = (point[0] - (focused_planet.x if focused_planet else 0)) * scale + width / 2
                py = (point[1] - (focused_planet.y if focused_planet else 0)) * scale + height / 2
                updated_points.append((px, py))
            pygame.draw.lines(screen, planet.colour, False, updated_points, 2)
    
    if focused_planet:  # Display information about the focused planet
        orbital_radius = math.sqrt(focused_planet.x**2 + focused_planet.y**2)/1000  # Distance from the Sun
        velocity = math.sqrt(focused_planet.Vx**2 + focused_planet.Vy**2)  # Calculate speed
        
        orbital_radius_meters = orbital_radius * 1000
        period = 2 * math.pi * math.sqrt((orbital_radius_meters**3) / (G * 1.98892e30))
        period_years = period / (60 * 60 * 24 * 365.25)#sec to year
        
        # Draw the text for velocity and orbital radius
        velocity_text = font.render(f"Velocity: {velocity:} m/s", True, "white")
        radius_text = font.render(f"Orbital Radius: {orbital_radius:} km", True, "white")
        period_text = font.render(f"Orbital period: {round(period_years,2)} years", True, "white")

        screen.blit(velocity_text, (width/2+focused_planet.r+10/2, height/2+focused_planet.r))  
        screen.blit(radius_text, (width/2+focused_planet.r+10, height/2+focused_planet.r+15)) 
        screen.blit(period_text, (width/2+focused_planet.r+10, height/2+focused_planet.r+30)) 


def main():
    global Timestep, scale, scaleFactor
    # Initialize
    run = True
    ANGLE = False
    PAUSE = False
    clock = pygame.time.Clock()
    focused_planet = None

    # Create planets
    sun = Planet(0, 0, 50, 'yellow', 1.98892e30)
    sun.IS_SUN = True

    mercury = Planet(-0.387 * AU, 0, 6, 'darkgrey', 3.3e23)
    mercury.Vy = 47400
    venus = Planet(-0.723 * AU, 0, 15, 'khaki', 4.8685e24)
    venus.Vy = 35020
    earth = Planet(-AU, 0, 16, 'lightblue', 5.9742e24)
    earth.Vy = 29783
    mars = Planet(-1.524 * AU, 0, 9, 'firebrick', 6.39e23)
    mars.Vy = 24077
    jupiter = Planet(-5.204 * AU, 0, 45, 'orange', 1.898e27)
    jupiter.Vy = 13070
    saturn = Planet(-9.582 * AU, 0, 38, 'gold', 5.683e26)  # Saturn's color
    saturn.Vy = 9680
    uranus = Planet(-19.191 * AU, 0, 28, 'lightblue', 8.681e25)  # Uranus' color
    uranus.Vy = 6800
    neptune = Planet(-30.047 * AU, 0, 28, 'blue', 1.024e26)  # Neptune's color
    neptune.Vy = 5430

    Planets = [sun, earth, mars, mercury, venus, jupiter, saturn, uranus, neptune]

    date = Date('2021-8-13 00:00:00')

    # Update loop
    # =======================================================================================================================================================================================
    while run:
        # Frame initialization
        clock.tick(60)
        screen.fill(bgCOLOUR)

        # Update positions of planets before drawing
        for planet in Planets:
            planet.updatePos(Planets)

        # Draw planets with the current focus
        draw_planets(Planets, focused_planet)
        #draw soi
        # pygame.draw.circle(screen, "white", xy_to_screen(sun.x,sun.y), 28_509_000*scaleFactor, 100)
        
        # UI draw and other elements
        date.render()

        draw_text((50,50),f"<W/S>      Time step: {round(Timestep/60/24)} days/sec")
        draw_text((50,70), "<r>            reset orbital tracks")
        draw_text((50,90), "<t>            debug mode")
        if ANGLE:   
            draw_text((300,90),f"|angle: {round(calculate_angle_earth_mars_sun(earth,mars),3)}")
            draw_lines_to_sun(earth,sun)
            draw_lines_to_sun(mars,sun)
            _,orbital_eq=xy_to_screen(0,sun.y)
            print(f"Planets on screen: {[f'Planet {i}' for i, planet in enumerate(Planets) if planet.ON_SCREEN]}")
            pygame.draw.line(screen,"white",(0,orbital_eq),(xy_to_screen(sun.x,sun.y)),1)
            draw_text((300,110),f"fps: {clock.get_fps():.1f}")

        draw_text((50,110),f"<-/+>         scale: {round(scaleFactor,3)}")
        draw_text((50,130), "<space>       pause")
        draw_text((50,150), "<lmb>         focus view")
        draw_text((50,170), "<f>           reset view")
        
        draw_text((1761,1050), "Made by: Ned Petre")    

        pygame.display.update()

        # pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            # Check for mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for planet in Planets:
                    planet_x = planet.x * scale + width / 2
                    planet_y = planet.y * scale + height / 2
                    if (planet_x - planet.r <= mouse_x <= planet_x + planet.r*2) and (planet_y - planet.r <= mouse_y <= planet_y + planet.r*2):
                        focused_planet = planet  # Set the clicked planet as focused
                        break
            # Look for keystroke
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    Timestep *= 0.9
                elif event.key == pygame.K_w:
                    Timestep *= 1.1
                elif event.key == pygame.K_r:
                    for planet in Planets:
                        planet.orbitalPath = []
                elif event.key == pygame.K_t:
                    ANGLE = not ANGLE  # Toggle angle display
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    run = False
                elif event.key == pygame.K_SPACE:
                    PAUSE = not PAUSE
                    if PAUSE:
                        store = Timestep
                        Timestep=0
                    else:
                        Timestep=store
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS) :
                    zoom_out(Planets)
                elif event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
                    zoom_in(Planets)
                elif event.key == pygame.K_f:
                    focused_planet = None  # Reset focus
            elif event.type == pygame.MOUSEWHEEL:
                if event.y < 0:
                    zoom_out(Planets)
                if event.y > 0:
                    zoom_in(Planets)
                    
        #cleanup for perfomance
        if clock.get_fps() < 45:
            for i in Planets:
                i.orbitalPath = []
                
        



def zoom_in(Planets):
    global scale, scaleFactor
    scale *= 1.1
    scaleFactor *= 1.1
    for planet in Planets:
        planet.r *= 1.1

def zoom_out(Planets):
    global scale, scaleFactor
    scale *= 0.9
    scaleFactor *= 0.9
    for planet in Planets:
        planet.r *= 0.9
        
def xy_to_screen(x,y):
    y = y * scale + height / 2
    x = x * scale + width / 2
    return (x,y)

if __name__ == "__main__":
    main()
