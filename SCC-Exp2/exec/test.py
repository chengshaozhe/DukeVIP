import pygame as pg

class DrawShapesInGrid:
    def __init__(self, screen, grid_size, grid_resolution, background_color, target_radius, player_radius, target_colors, player_colors):
        self.screen = screen
        self.grid_size = grid_size
        self.grid_resolution = grid_resolution
        self.cell_size = grid_resolution // grid_size  # Calculate the cell size
        self.background_color = background_color
        self.target_radius = target_radius
        self.player_radius = player_radius
        self.target_colors = target_colors  # Colors for the targets
        self.player_colors = player_colors  # Colors for the players

        # Calculate the top-left position to center the grid on the screen
        screen_width, screen_height = screen.get_size()
        self.grid_x = (screen_width - grid_resolution) // 2
        self.grid_y = (screen_height - grid_resolution) // 2

    def draw_background(self):
        # Fill the entire screen with black
        self.screen.fill((0, 0, 0))  # Black background outside the grid

        # Fill the grid area with the background color (ensure exact grid dimensions)
        pg.draw.rect(self.screen, self.background_color, (self.grid_x, self.grid_y, self.grid_resolution, self.grid_resolution))

        # Draw the inner grid lines on the white background
        for x in range(1, self.grid_size):
            # Vertical lines
            pg.draw.line(self.screen, (0, 0, 0), (self.grid_x + x * self.cell_size, self.grid_y),
                         (self.grid_x + x * self.cell_size, self.grid_y + self.grid_resolution), 1)
            # Horizontal lines
            pg.draw.line(self.screen, (0, 0, 0), (self.grid_x, self.grid_y + x * self.cell_size),
                         (self.grid_x + self.grid_resolution, self.grid_y + x * self.cell_size), 1)

        # Draw the outer border exactly around the grid
        pg.draw.rect(self.screen, (0, 0, 0), (self.grid_x, self.grid_y, self.grid_resolution, self.grid_resolution), 5)

    def __call__(self, targets, players):
        # Draw the background (grid, etc.)
        self.draw_background()

        # Draw targets (formerly rectangles) using predefined colors
        for idx, target_pos in enumerate(targets):
            # Use the color at the index of the current target
            color = self.target_colors[idx % len(self.target_colors)]
            target_grid_x, target_grid_y = target_pos
            target_x = self.grid_x + target_grid_x * self.cell_size
            target_y = self.grid_y + target_grid_y * self.cell_size
            target_width = self.cell_size - 20  # Subtract more to make it smaller
            target_height = self.cell_size - 20
            target_x_centered = target_x + (self.cell_size - target_width) // 2
            target_y_centered = target_y + (self.cell_size - target_height) // 2
            pg.draw.rect(self.screen, color, (target_x_centered, target_y_centered, target_width, target_height))

        # Draw players (formerly circles) using predefined colors
        for idx, player_pos in enumerate(players):
            # Use the color at the index of the current player
            color = self.player_colors[idx % len(self.player_colors)]
            player_grid_x, player_grid_y = player_pos
            player_center_x = self.grid_x + player_grid_x * self.cell_size + self.cell_size // 2
            player_center_y = self.grid_y + player_grid_y * self.cell_size + self.cell_size // 2
            pg.draw.circle(self.screen, color, (player_center_x, player_center_y), self.target_radius)

        pg.display.flip()  # Update the display
        return self.screen


# Example usage of the class
pg.init()
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
grid_size = 15
grid_resolution = 1000
background_color = (255, 255, 255)  # White background
target_radius = 20
player_radius = 15

# Define colors for the targets and players
target_colors = [(0, 0, 255),  # Blue
                 (255, 255, 0)]  # Green

player_colors = [(255, 0, 0),  # Red
                 (0, 255, 255)]  # Orange

# Create an instance of the class
draw_shapes = DrawShapesInGrid(screen, grid_size, grid_resolution, background_color, target_radius, player_radius, target_colors, player_colors)

# Example positions for targets and players
targets = [(7, 8), (2, 3)]  # Positions for targets
players = [(3, 4), (5, 5)]  # Positions for players

# Main loop
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            running = False

    # Draw the shapes on the grid
    draw_shapes(targets, players)

pg.quit()




# # introduction
# intro_text = [
#     "In this game there are two hungry travelers,",
#     "who need to reach a restaurant as soon as possible to get some food.",
#     "One of the travelers is you, this blue dot (points to blue dot).",
#     "The other traveler is my friend Alex, he is this green dot (points to green dot).",
#     "On this map, there are restaurants, which we can say are these red squares.",
#     "Sometimes there is one restaurant and sometimes there are two restaurants.",
#     "Sometimes Alex will be there, and sometimes he won’t, and it will just be you playing."
# ]

# draw_intro_text = DrawIntroductionText(
#     screen=screen,
#     drawBackground=drawBackground,
#     text_lines=intro_text,
#     font_size=40,
#     text_color=(0, 0, 0),  # Black text
#     start_y=200,  # Starting y position for the first line of text
#     line_spacing=30  # Space between lines
# )

# draw_intro_text()
