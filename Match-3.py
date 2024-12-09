import random
import pygame
import pygame.font
import pygame.mixer
import sys

pygame.init()
pygame.font.init()
pygame.mixer.init()

# Constants for the game
screen_width = 1000
screen_height = 950
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Main Menu")
icon = pygame.image.load("Images/game.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
fps = 1000

# Music
music = pygame.mixer.music.load('Sounds/music1.mp3')
pygame.mixer.music.play(-1)
vol = 0.5
pygame.mixer.music.set_volume(vol)

# Fonts
big_font = pygame.font.SysFont("Fonts/candy-crush.zip", 150)
main_font = pygame.font.SysFont("Fonts/CANDYSAGA.ttf", 50, bold=True)

# List of items
items = ['bubbles', 'purp_star', 'red_square', 'square', 'star']

# Item size
item_width = 50
item_height = 50
item_size = (item_width, item_height)
gameboard = []


# This class creates the buttons for the game
class Button:
    # Initialises the attributes
    def __init__(self, coords, text_input, image, image2):
        self.image = image
        self.image2 = image2
        self.coords = coords
        self.text_input = text_input
        self.button_text = main_font.render(str(self.text_input), True, (255, 255, 255))
        if self.image is None:
            self.image = self.button_text
        else:
            self.image = pygame.image.load(image)
        if self.image2 is None:
            self.image2 = self.image
        else:
            self.image2 = pygame.image.load(image2)
        self.rect = self.image.get_rect(center=self.coords)

    # This draws the buttons onto the screen
    def draw(self, mouse_pos):
        if self.image == self.button_text:
            if self.rect.collidepoint(mouse_pos):
                self.button_text = main_font.render(str(self.text_input), True, (255, 0, 0))
            else:
                self.button_text = main_font.render(str(self.text_input), True, (255, 255, 255))
        else:
            if self.rect.collidepoint(mouse_pos):
                self.image = self.image2
            else:
                self.image = self.image

        # Displays the buttons onto the screen
        screen.blit(self.image, self.rect)
        screen.blit(self.button_text, self.button_text.get_rect(center=self.coords))


class Board:

    def __init__(self, border, border_height, border_width, border_top, border_left, num_rows, num_cols):
        self.surface = None
        self.rect = None
        self.matches = None
        self.rows = num_rows
        self.cols = num_cols

        self.border = border
        self.border_top = border_top
        self.border_left = border_left
        self.border_height = border_height
        self.border_width = border_width

        # Initialize gameboard with random items
        self.gameboard = [[random.choice(items) for _ in range(self.cols)] for _ in range(self.rows)]

    def draw_board(self):
        # This draws the items in the constraints of the border
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * (item_width + 3)
                y = row * (item_height + 3)
                item_name = f'Icons/{self.gameboard[row][col]}.png'
                self.surface = pygame.image.load(item_name)
                self.surface = pygame.transform.smoothscale(self.surface, item_size)
                self.rect = self.surface.get_rect(
                    topleft=(self.border_left + item_width + x, self.border_top - item_height + y))

                screen.blit(self.surface, self.rect)

    def swap(self, item1, item2):
        # This saves the positions of two items and swaps them
        row1, col1 = item1
        row2, col2 = item2
        self.gameboard[row1][col1], self.gameboard[row2][col2] = self.gameboard[row2][col2], self.gameboard[row1][col1]

    def adjacent(self, item1, item2):
        # This checks if two positions are adjacent (horizontally or vertically)
        row1, col1 = item1
        row2, col2 = item2
        return (abs(row1 - row2) == 1 and col1 == col2) or (abs(col1 - col2) == 1 and row1 == row2)

    def find_matches(self):
        # This finds matches then removes the matched items
        self.matches = []

        # Check for horizontal matches
        for row in range(self.rows):
            for col in range(self.cols - 2):
                if self.gameboard[row][col] == self.gameboard[row][col + 1] == self.gameboard[row][col + 2]:
                    self.matches.extend([(row, col), (row, col + 1), (row, col + 2)])

        # Checks for vertical matches
        for col in range(self.cols):
            for row in range(self.rows - 2):
                if self.gameboard[row][col] == self.gameboard[row + 1][col] == self.gameboard[row + 2][col]:
                    self.matches.extend([(row, col), (row + 1, col), (row + 2, col)])

        print(self.matches)
        return self.matches

        # Removes duplicates

    def destroy_items(self, matches):
        # This removes items that have been matched from the board
        for matched in matches:
            row = matched[0]
            col = matched[1]
            self.gameboard[row][col] = None

        # Fill the empty spaces after destroying the items
        self.fill_empty()

    def fill_empty(self):
        # Fill the empty spaces in the gameboard with new random items
        for col in range(self.cols):
            # Start from the bottom of each column and move up
            empty_spaces = []
            for row in range(self.rows - 1, -1, -1):
                if self.gameboard[row][col] is None:
                    empty_spaces.append(row)  # Store the row where the item is empty
                elif empty_spaces:  # If there are empty spaces above, drop the current item down
                    self.gameboard[empty_spaces.pop(0)][col] = self.gameboard[row][col]
                    self.gameboard[row][col] = None  # Clear the original space

        # After dropping items, fill the empty spaces at the top with new random items
        for row in range(self.rows):
            for col in range(self.cols):
                if self.gameboard[row][col] is None:
                    self.gameboard[row][col] = random.choice(items)


def update_scoreboard(num_matched):
    # This updates the scoreboard
    add = num_matched * 40
    return add


def update_challenge(item_matched, wanted_item, match_length):
    # This updates the challenge completion
    update = 0
    if item_matched == wanted_item:
        update = match_length
    return update


def challenge_completion(target, completion):
    # Checks if the challenge is completed
    if completion == target:
        return True


def level_1():
    run = True
    board_drawn = False
    board = None
    first_item = None
    score = 0
    completion_rate = 0

    # Game loop
    while run:
        # Changing the menu title
        pygame.display.set_caption('Level 1')
        # Get the mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Getting the current screen size
        full_width, full_height = pygame.display.get_window_size()
        centre_width = full_width // 2
        centre_height = full_height // 2

        # Sets the background
        bg_image = pygame.image.load('Images/bg2.jpg')
        bg_image = pygame.transform.scale(bg_image, (full_width, full_height))
        screen.fill((0, 0, 0))
        screen.blit(bg_image, (0, 0))

        # Displays the text
        text = big_font.render('LEVEL ONE', True, (255, 255, 255))
        text_rect = text.get_rect(center=(centre_width, 100))
        screen.blit(text, text_rect)

        # The exit button to leave the level
        exit_button = Button((full_height // 10, full_height // 1.064), '', 'Images/logout.png',
                             'Images/logout2.png')

        full_screen = Button(((full_height // 10), full_height // 1.2), '', 'Icons/fullscreen.png',
                             'Icons/fullscreen2.png')

        # This draws the exit button onto the screen
        exit_button.draw(mouse_pos)
        full_screen.draw(mouse_pos)

        # This displays the scoreboard
        score_text = main_font.render(f'Score: {score}', True, (255, 255, 255))
        score_text_rect = score_text.get_rect(left=750, top=150)
        screen.blit(score_text, score_text_rect)

        # This displays the challenge
        challenge_goal = 20
        challenge_item = pygame.image.load('Icons/square.png')
        challenge_board = main_font.render(f'Match {completion_rate}/{challenge_goal}', True, (255, 255, 255))
        challenge_text = challenge_board.get_rect(left=750, top=200)
        challenge_rect = challenge_item.get_rect(left=challenge_text.right, top=challenge_text.top)
        screen.blit(challenge_board, challenge_text)
        screen.blit(challenge_item, challenge_rect)

        if not board_drawn:
            # Displays the border for the game board
            border_width = full_width // 2.3
            border_height = full_height // 1.75
            border_top = full_width // 3.5
            border_left = full_height // 3.95
            border = pygame.draw.rect(screen, 'blue', ((border_top, border_left), (border_width, border_height)), -1)

            # Defines the attributes for the gameboard
            board = Board(border, border_width, border_height, border_top, border_left, 10, 8)
            board_drawn = True

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                # If the exit button is clicked
                if exit_button.rect.collidepoint(mouse_pos):
                    main_menu()
                if full_screen.rect.collidepoint(mouse_pos):
                    pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

                # Handles swapping items
                x, y = mouse_pos
                col = int((x - board.border_left) // (item_width + 3)) - 1
                row = int((y - board.border_top) // (item_height + 3)) + 1

                # Checks for if the click is on the gameboard and the item clicked is not on the last row/column
                if 0 <= row < board.rows and 0 <= col < board.cols:
                    # Checks for if there has already been an item clicked
                    if not first_item:
                        first_item = (row, col)
                    else:
                        second_item = (row, col)
                        # If the items are adjacent they are swapped
                        if board.adjacent(first_item, second_item):
                            clock.tick(fps)
                            board.swap(first_item, second_item)
                            matches = board.find_matches()
                            board.destroy_items(matches)

                            # Update the scoreboard
                            score += update_scoreboard(len(matches))

                            # Update the challenge board
                            item = board.gameboard[row][col]
                            completion_rate += update_challenge(item,'square',len(matches))

                            print(matches)
                            if not matches:
                                # Swaps the items back if no matches are found
                                clock.tick(fps)
                                board.swap(first_item, second_item)

                        first_item = None

            if event.type == pygame.VIDEORESIZE:
                window_limit()

        board.draw_board()
        pygame.display.update()


# Function to limit the minimum window size
def window_limit():
    width, height = pygame.display.get_window_size()
    if width < 600 and height < 600:
        pygame.display.set_mode((650, 650), pygame.RESIZABLE)
    elif height < 600:
        pygame.display.set_mode((width, 650), pygame.RESIZABLE)
    elif width < 600:
        pygame.display.set_mode((650, height), pygame.RESIZABLE)
    else:
        pygame.display.set_mode((width, height), pygame.RESIZABLE)


def settings_screen():
    run = True
    while run:

        # Changes the  screen name
        pygame.display.set_caption('Settings')

        # Calls the variable that stores the volume
        global vol

        # Detects the mouse position and key that has been pressed
        mouse_pos = pygame.mouse.get_pos()
        key = pygame.key.get_pressed()

        # Getting the current screen size
        full_width, full_height = pygame.display.get_window_size()
        centre_width = full_width // 2
        centre_height = full_height // 2

        # Background
        screen.fill((128, 128, 128))

        # Displaying the title of the screen
        text = big_font.render('SETTINGS', True, (0, 0, 0))
        text_rect = text.get_rect(center=(centre_width, 130))
        screen.blit(text, text_rect)

        # The button takes the player back to the main menu
        back_button = Button((full_width // 12.5, 940), '', 'Images/back-button.png', 'Images/back2.png')

        # Volume buttons
        volup_button = Button(((centre_width // 2) * 3, centre_height - 150), '', 'Images/volup.png', None)
        voldown_button = Button(((centre_width // 2) * 3, centre_height - 100), '', 'Images/voldown.png', None)
        pause_button = Button((centre_width // 2, 580), 'Pause', 'Images/pause.png', 'Images/pause-button2.png')
        play_button = Button((centre_width, 580), 'Play', 'Images/play-button.png', 'Images/play-button2.png')

        # Drawing the buttons
        back_button.draw(mouse_pos)
        volup_button.draw(mouse_pos)
        voldown_button.draw(mouse_pos)
        pause_button.draw(mouse_pos)
        play_button.draw(mouse_pos)

        playing = pygame.mixer_music.get_busy()
        if playing:
            sound_level = pygame.mixer.music.get_volume()
            print(sound_level)

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                window_limit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                print('click')
                if back_button.rect.collidepoint(mouse_pos) or key[pygame.K_ESCAPE]:
                    main_menu()
                elif volup_button.rect.collidepoint(mouse_pos):
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
                elif voldown_button.rect.collidepoint(mouse_pos):
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif play_button.rect.collidepoint(mouse_pos):
                    pygame.mixer.music.play()
                elif pause_button.rect.collidepoint(mouse_pos):
                    pygame.mixer.music.pause()

        pygame.display.update()


def main_menu():
    run = True
    while run:

        # Getting the current screen size
        full_width, full_height = pygame.display.get_window_size()
        centre_full_width = full_width // 2
        centre_full_height = full_height // 2

        # This creates the background image and displays it onto the screen
        bg_image = pygame.image.load("Images/bg2.jpg")
        bg_image = pygame.transform.scale(bg_image, (full_width, full_height))
        screen.fill((255, 105, 180))
        screen.blit(bg_image, (0, 0))

        # Showing the title on the screen
        text = big_font.render("MAIN MENU", True, (245, 50, 50))
        text_rect = text.get_rect(center=(centre_full_width, 150))
        screen.blit(text, text_rect)

        # Get the mouse position
        mouse_pos = pygame.mouse.get_pos()

        # This passes the attributes for each buttons to the Button class
        settings = Button((full_width // 10, full_height // 1.05), '', 'Images/settings.png', 'Images/cog.png')
        level1 = Button((centre_full_width, 300), "Level 1", None, None)
        level2 = Button((centre_full_width, 450), "Level 2", None, None)
        level3 = Button((centre_full_width, 600), "Level 3", None, None)
        instructions = Button((full_width // 10, 400), "", 'Images/user-guide.png', 'Images/user-guide (1).png')
        quit_button = Button((full_width // 1.05, full_height // 1.05), "Quit", None, None)

        # This calls the draw method to draw the buttons onto the screen
        settings.draw(mouse_pos)
        level1.draw(mouse_pos)
        level2.draw(mouse_pos)
        level3.draw(mouse_pos)
        instructions.draw(mouse_pos)
        quit_button.draw(mouse_pos)

        # Event handler
        for event in pygame.event.get():
            # If the player presses the 'X' button the game is closed
            if event.type == pygame.QUIT:
                run = False

            # If the player clicks a button an action is taken
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if quit_button.rect.collidepoint(mouse_pos):
                    run = False
                elif settings.rect.collidepoint(mouse_pos):
                    settings_screen()
                elif level1.rect.collidepoint(mouse_pos):
                    level_1()
            # If the player changes the screen size the function is called to limit how small the window can be
            if event.type == pygame.VIDEORESIZE:
                window_limit()
        pygame.display.update()
    pygame.quit()
    sys.exit()


main_menu()
