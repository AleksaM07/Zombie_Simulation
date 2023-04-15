import random
import pygame
from sys import exit
import pandas as pd


#variables for the function draw_text
textAlignLeft = 0
textAlignRight = 1
textAlignCenter = 2
textAlignBlock = 3
def draw_text(surface, text, color, rect, font, align=textAlignCenter, aa=False, bkg=None):
    """
    https://stackoverflow.com/questions/64273966/python-pygame-make-text-in-pygame-wrap-when-in-leaves-the-window
    Raw some text into an area of a surface
    Automatically wraps words
    Returns any text that didn't get blitted
    """
    line_spacing = -2
    space_width, font_height = font.size(" ")[0], font.size("Tg")[1]

    list_of_words = text.split(" ")
    if bkg:
        image_list = [font.render(word, 1, color, bkg) for word in list_of_words]
        for image in image_list: image.set_colorkey(bkg)
    else:
        image_list = [font.render(word, aa, color) for word in list_of_words]

    max_len = rect[2]
    line_len_list = [0]
    line_list = [[]]
    for image in image_list:
        width = image.get_width()
        lineLen = line_len_list[-1] + len(line_list[-1]) * space_width + width
        if len(line_list[-1]) == 0 or lineLen <= max_len:
            line_len_list[-1] += width
            line_list[-1].append(image)
        else:
            line_len_list.append(width)
            line_list.append([image])

    line_bottom = rect[1]
    last_line = 0
    for lineLen, lineImages in zip(line_len_list, line_list):
        line_left = rect[0]
        if align == textAlignRight:
            line_left += + rect[2] - lineLen - space_width * (len(lineImages)-1)
        elif align == textAlignCenter:
            line_left += (rect[2] - lineLen - space_width * (len(lineImages)-1)) // 2
        elif align == textAlignBlock and len(lineImages) > 1:
            space_width = (rect[2] - lineLen) // (len(lineImages)-1)
        if line_bottom + font_height > rect[1] + rect[3]:
            break
        last_line += 1
        for i, image in enumerate(lineImages):
            x, y = line_left + i*space_width, line_bottom
            surface.blit(image, (round(x), y))
            line_left += image.get_width()
        line_bottom += font_height + line_spacing

    if last_line < len(line_list):
        draw_words = sum([len(line_list[i]) for i in range(last_line)])
        remaining_text = ""
        for text in list_of_words[draw_words:]: remaining_text += text + " "
        return remaining_text
    return ""


# Initializing pygame, setting up basic things, title, clock, indicators, font, music, the cursor
pygame.init()
screen = pygame.display.set_mode((700, 700))

pygame.mouse.set_visible(False)
cursor_img = pygame.image.load('animation/cursor.png').convert_alpha()
cursor_img_rect = cursor_img.get_rect()

pygame.display.set_caption('Zombie Simulation')
clock = pygame.time.Clock()
test_font = pygame.font.Font('animation/OpenSans-Regular.ttf', 40)
test_font1 = pygame.font.Font('animation/OpenSans-Italic.ttf', 20)
test_font2 = pygame.font.Font('animation/OpenSans-Regular.ttf', 20)

# Some of our indicators
game_active = False
apocalypse_indicator = 0
game_state = 0
start_time = 0
count = 0
event_triggered = False
hum = 1000
zom = 5
# we need a way to track how much time has passed
current_time = 0
# we need the indicator for game over
game_over = 0

# Our data from the simulation
results = pd.read_csv('output.csv')
results_dict = results.to_dict()

# Our game over music
end_music = pygame.mixer.Sound('animation/ending.ogg')

# Our beginning narrator music
narrator_music = pygame.mixer.Sound('animation/Voices for the beggining/the_behhining_dialog.mp3')

# The music for the beginning screen
start_bg_music = pygame.mixer.Sound('animation/rise_of_spirit.mp3')
start_bg_music.set_volume(1)
start_bg_music.play(loops=-1)

# Movies fot the TV after the apocalypse
stop_it_now_video = pygame.image.load('animation/video1/video1_pixaleted-101.png').convert_alpha()
stop_it_now_music = pygame.mixer.Sound('animation/video1/video1_pixaleted.mp3')
stop_it_now_video_transform = pygame.transform.scale(stop_it_now_video, (640, 500))
stop_it_now_video_rect = stop_it_now_video_transform.get_rect(midtop=(350, 80))
video1_frame = 101
breaking_news = pygame.image.load('animation/video2/video2_pixaleted101.png').convert_alpha()
breaking_news_music = pygame.mixer.Sound('animation/video2/video2_pixaleted.mp3')
breaking_news_transform = pygame.transform.scale(breaking_news, (640, 540))
breaking_news_rect = breaking_news_transform.get_rect(midtop=(350, 80))
video_panel = pygame.image.load('animation/video3/video3101.png').convert_alpha()
video_panel_transform = pygame.transform.scale(video_panel, (640, 540))
video_panel_music = pygame.mixer.Sound('animation/video3/video3.mp3')
video_panel_rect = video_panel_transform.get_rect(midtop=(350, 80))

# Background images, clock, table, tv, window, dog, floor, papers
wall_bg = pygame.image.load('animation/bg_night.png').convert_alpha()
wall_bg_transform = pygame.transform.scale(wall_bg, (700, 700))
wall_bg_rect = wall_bg_transform.get_rect(center=(350, 350))

clock_img = pygame.image.load('animation/clock1_placeholder.png').convert_alpha()
clock_transform = pygame.transform.scale(clock_img, (80, 80))
clock_rect = clock_transform.get_rect(center=(350, 100))
clock_sound = pygame.mixer.Sound('animation/ticking_clock.wav')
clock_ind = 0
clock_handle_img = pygame.image.load('animation/clock_handle.png').convert_alpha()
clock_handle_transform = pygame.transform.scale(clock_handle_img, (80, 80))
clock_handle_rect = clock_handle_transform.get_rect(center=(350, 100))
clock_handle_angle = 0

table_img = pygame.image.load('animation/desk_placeholder.png').convert_alpha()
table_transform = pygame.transform.scale(table_img, (500, 300))
table_rect = table_transform.get_rect(center=(350, 470))

window_img = pygame.image.load('animation/window_night.png').convert_alpha()
window_transform = pygame.transform.scale(window_img, (300, 300))
window_rect = window_transform.get_rect(center=(350, 200))
window = 0

dog_img = pygame.image.load('animation/dog1.png').convert_alpha()
dog_transform = pygame.transform.scale(dog_img, (255, 145))
dog_rect = dog_transform.get_rect(center=(350, 570))
dog_sound = pygame.mixer.Sound('animation/dog_barking.wav')
dog = 0
dog_change = False


floor_img = pygame.image.load('animation/floor_placeholder_night.png').convert_alpha()
floor_transform = pygame.transform.scale(floor_img, (700, 200))
floor_rect = floor_transform.get_rect(center=(350, 600))

papers_img = pygame.image.load('animation/paper_pile.png').convert_alpha()
papers_transform = pygame.transform.scale(papers_img, (180, 180))
papers_rect = papers_transform.get_rect(center=(350, 600))
paper_sound = pygame.mixer.Sound('animation/FlippingPages.ogg')
paper_pile = 0
diff_papers_img = pygame.image.load('animation/OldPage.png').convert_alpha()
diff_papers_transform = pygame.transform.scale(diff_papers_img, (500, 690))
diff_papers_rect = diff_papers_transform.get_rect(center=(350, 350))

tv_img = pygame.image.load('animation/tv_video/0.png').convert_alpha()
tv_transform = pygame.transform.scale(tv_img, (300, 250))
tv_rect = tv_transform.get_rect(midbottom=(350, 400))
tv_sound = pygame.mixer.Sound('animation/white noise.wav')
tv_frame = 0
tv = 0
repaired = False

# Rain
rain_img = pygame.image.load('animation/rain.png').convert_alpha()
rain0_transform = pygame.transform.scale(rain_img, (700, 700))
rain0_rect = rain0_transform.get_rect(center=(350, 350))
rain1_img = pygame.image.load('animation/rain.png').convert_alpha()
rain1_transform = pygame.transform.scale(rain1_img, (700, 700))
rain1_rect = rain1_transform.get_rect(center=(350, -350))
rain2_img = pygame.image.load('animation/rain.png').convert_alpha()
rain2_transform = pygame.transform.scale(rain2_img, (700, 700))
rain2_rect = rain2_transform.get_rect(center=(350, -1050))

# Background for the notifications
dark_bg_img = pygame.image.load('animation/bg_notif.png').convert_alpha()
dark_bg_transform = pygame.transform.scale(dark_bg_img, (700, 700))
dark_bg_transform.set_alpha(150)
dark_bg_rect = dark_bg_transform.get_rect(center=(350, 350))

# Notif image
notif_img = pygame.image.load('animation/notif.png').convert_alpha()
notif_transform = pygame.transform.scale(notif_img, (680, 450))
notif_rect = notif_transform.get_rect(center=(350, 350))

# The magic animation
magic_video = pygame.image.load('animation/magic_video/0.png').convert_alpha()
magic_video_transform = pygame.transform.scale(magic_video, (700, 700))
magic_video_rect = magic_video_transform.get_rect(center=(350, 350))
magic_video_frame = 1
magic_sound1 = pygame.mixer.Sound('animation/magic_video/No More Magic.mp3')
magic_sound2 = pygame.mixer.Sound('animation/magic_video/rock_breaking.flac')
magic_sound2_indicator = 0

# Go to next room sign
next_img = pygame.image.load('animation/go_to_next_placeholder.png').convert_alpha()
next_transform = pygame.transform.scale(next_img, (50, 700))
next_transform = pygame.transform.rotozoom(next_transform, 180, 1)
next_transform.set_alpha(0)
next_transform_orig = next_transform.copy()
next_rect = next_transform.get_rect(midleft=(650, 350))

# Intro screen
start_bg = pygame.image.load('animation/bg_beg1.png').convert_alpha()
start_bg_transform = pygame.transform.scale(start_bg, (700, 700))
start_bg_rect = start_bg_transform.get_rect(center=(350, 350))

# Zombie Simulation, an Imaginative RE-Enactment of what it could look like
zombie_title_img = pygame.image.load('animation/title.png').convert_alpha()
zombie_title_img_transform = pygame.transform.scale(zombie_title_img, (500, 300))
zombie_title_img_rect = zombie_title_img_transform.get_rect(center=(350, 350))


# defining a function for our hints
def hint(question):
    game_message = test_font1.render(f'{question}', False, (253, 253, 253), pygame.Color(0, 0, 0))
    game_message.set_alpha(200)
    game_message_rect = game_message.get_rect(center=(350, 650))
    screen.blit(game_message, game_message_rect)


# Music for alarm and caution
alarm_sound = pygame.mixer.Sound('animation/alarm_audio.mp3')
caution_sound = pygame.mixer.Sound('animation/caution_audio.mp3')
red = pygame.image.load('animation/red.jpg').convert_alpha()
red_transform = pygame.transform.scale(red, (700, 700))
red_alpha = 0
red_transform.set_alpha(red_alpha)
red_rect = red_transform.get_rect(center=(350, 350))
alarm = 0
caution = 0
warn = ''

# The variables used by the function that we need for checking the collision
answer1_text_rect = pygame.Rect(0, 0, 0, 0)
answer2_text_rect = pygame.Rect(0, 0, 0, 0)
answer3_text_rect = pygame.Rect(0, 0, 0, 0)


def question_box(answer1, answer2, answer3, question):
    global answer1_text_rect, answer2_text_rect, answer3_text_rect
    screen.blit(dark_bg_transform, dark_bg_rect)
    screen.blit(notif_transform, notif_rect)
    question_text_rect = pygame.Rect(80, 220, 540, 470)
    draw_text(screen, question, (0, 0, 0), question_text_rect, test_font2)
    answer1_text = test_font1.render(f'<{answer1}>', True, (253, 253, 253), pygame.Color(0, 0, 0))
    answer1_text.set_alpha(100)
    answer1_text_rect = answer1_text.get_rect(center=(350, 390))
    answer2_text = test_font1.render(f'<{answer2}>', True, (253, 253, 253), pygame.Color(0, 0, 0))
    answer2_text.set_alpha(100)
    answer2_text_rect = answer2_text.get_rect(center=(350, 430))
    answer3_text = test_font1.render(f'<{answer3}>', True, (253, 253, 253), pygame.Color(0, 0, 0))
    answer3_text.set_alpha(100)
    answer3_text_rect = answer3_text.get_rect(center=(350, 470))
    screen.blit(answer1_text, answer1_text_rect)
    screen.blit(answer2_text, answer2_text_rect)
    screen.blit(answer3_text, answer3_text_rect)


# Beginning our main loop
while True:
    keys = pygame.key.get_pressed()
    # Indicators of if the intro screen title and message was shown
    show_name = False
    show_message = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # if we press x the game quits
            pygame.quit()
            success = False
            exit()
        else:
            if keys[pygame.K_SPACE] and not event_triggered:
                # if we press space, we set off the trigger time (that we use for tracking time) and the narrator  voice
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000) # in seconds
                start_bg_music.stop()
                interval = 60 # 60 seconds
                trigger_time = start_time + interval

                # Set event_triggered flag to True to disable further event triggering
                event_triggered = True
                narrator_music.play(0)
                narrator_music.set_volume(1)
                game_state = 0

            # if we hover over "the next room" thing
            if next_rect.collidepoint(pygame.mouse.get_pos()):
                next_transform.set_alpha(150)
            else:
                next_transform.set_alpha(0)

            # if we press the "next room"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and next_rect.collidepoint(pygame.mouse.get_pos()) and count % 2 == 1 and game_state == 1:
                count += 1
                next_transform = pygame.transform.rotozoom(next_transform_orig, 360, 1)
                game_state = 2
                dog_list = [1, 2, 3, 4]
                random_dog = random.choice(dog_list)
                dog_img = pygame.image.load(f'animation/dog{random_dog}.png').convert_alpha()
                dog_transform = pygame.transform.scale(dog_img, (255, 145))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and next_rect.collidepoint(pygame.mouse.get_pos()) and count % 2 == 0 and game_state == 2:
                count += 1
                next_transform = pygame.transform.rotozoom(next_transform_orig, 180, 1)
                game_state = 1

            # if we press the clock
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and clock_rect.collidepoint(pygame.mouse.get_pos()) and game_state == 1 and clock_ind == 0:
                # for the basic clock viewing
                game_state = 3
                clock_sound.set_volume(0.5)
                clock_sound.play(-1)
                clock_ind = 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and not clock_rect.collidepoint(pygame.mouse.get_pos()) and clock_ind == 1 and game_state == 3:
                # for exiting the clock
                clock_transform = pygame.transform.scale(clock_img, (80, 80))
                clock_rect = clock_transform.get_rect(center=(350, 100))
                clock_handle_transform = pygame.transform.scale(clock_handle_img, (80, 80))
                clock_handle_rect = clock_handle_transform.get_rect(center=(350, 100))
                clock_sound.stop()
                clock_ind = 0
                game_state = 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and clock_rect.collidepoint(pygame.mouse.get_pos()) and clock_ind == 1 and game_state == 3\
                    and apocalypse_indicator == 0:
                # for showing the clock message
                clock_ind = 2
                game_state = 8
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and answer2_text_rect.collidepoint(pygame.mouse.get_pos())\
                    and clock_ind == 2 and game_state == 8:
                # for exiting the clock message, if the answer is no
                game_state = 3
                clock_ind = 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and (answer1_text_rect.collidepoint(pygame.mouse.get_pos()) or answer3_text_rect.collidepoint(pygame.mouse.get_pos()))\
                    and game_state == 8:
                # if the answer is yes or maybe then we turn the player into a zombie and its game over
                clock_sound.stop()
                end_music.play(-1)
                end_music.set_volume(1)
                game_over = 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and apocalypse_indicator == 1 and clock_rect.collidepoint(pygame.mouse.get_pos()) and game_state == 3:
                clock_handle_angle -= 45
                current_time += 5400 # we move our time, and clock for an hour and a half in seconds

            # if we press the tv before the apocalypse
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and tv_rect.collidepoint(pygame.mouse.get_pos()) and game_state == 1 and apocalypse_indicator == 0:
                # Basic viewing of the TV
                game_state = 4
                tv = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and not tv_rect.collidepoint(pygame.mouse.get_pos()) and tv and game_state == 4 and apocalypse_indicator == 0:
                # Exiting the TV, getting the elements in the right size
                game_state = 1
                tv_transform = pygame.transform.scale(tv_img, (200, 150))
                tv_rect = tv_transform.get_rect(midbottom=(350, 370))
                table_transform = pygame.transform.scale(table_img, (500, 300))
                table_rect = table_transform.get_rect(center=(350, 470))
                tv = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and tv_rect.collidepoint(pygame.mouse.get_pos()) and game_state == 4 and tv and apocalypse_indicator == 0:
                # Asking the player if he wants to fix the TV
                game_state = 15
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_state == 15 \
                    and (answer1_text_rect.collidepoint(pygame.mouse.get_pos())
                        or answer3_text_rect.collidepoint(pygame.mouse.get_pos())) \
                    and tv and apocalypse_indicator == 0:
                # TV was repaired, and started working
                repaired = True
                game_state = 4
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_state == 15 \
                    and answer2_text_rect.collidepoint(pygame.mouse.get_pos()) \
                    and tv and apocalypse_indicator == 0:
                # TV was not repaired
                game_state = 4

            # if we press the tv after the apocalypse
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and tv_rect.collidepoint(pygame.mouse.get_pos()) and game_state == 1 and apocalypse_indicator == 1:
                # Choosing a random movie to play
                game_state = 14
                list_of_movies = [1, 2, 3]
                random_movie = random.choice(list_of_movies)
                if random_movie == 1:
                    stop_it_now_music.play(0)
                    stop_it_now_music.set_volume(0.5)
                if random_movie == 2:
                    breaking_news_music.play(0)
                    breaking_news_music.set_volume(0.5)
                if random_movie == 3:
                    video_panel_music.play(-1)
                    video_panel_music.set_volume(0.5)
                tv = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and not tv_rect.collidepoint(pygame.mouse.get_pos()) and tv and game_state == 14 \
                    and apocalypse_indicator == 1:
                # Exiting the pst-apocalypse TV
                game_state = 1
                tv_transform = pygame.transform.scale(tv_img, (200, 150))
                tv_rect = tv_transform.get_rect(midbottom=(350, 370))
                table_transform = pygame.transform.scale(table_img, (500, 300))
                table_rect = table_transform.get_rect(center=(350, 470))
                stop_it_now_music.stop()
                breaking_news_music.stop()
                video_panel_music.stop()
                video1_frame = 101
                tv = False

            # if we press the paper pile
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and papers_rect.collidepoint(pygame.mouse.get_pos()) and game_state == 1:
                game_state = 5
                paper_sound.set_volume(1)
                paper_sound.play(loops=0)
                paper_pile = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and not diff_papers_rect.collidepoint(pygame.mouse.get_pos()) and paper_pile and game_state == 5:
                game_state = 1
                paper_sound.stop()
                paper_pile = False

            # if we press the window
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and window_rect.collidepoint(pygame.mouse.get_pos()) and game_state == 2 and window == 0:
                # for entering the window view
                game_state = 6
                window = 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and not window_rect.collidepoint(pygame.mouse.get_pos()) and window == 1 and game_state == 6:
                # exiting the window
                game_state = 2
                window_transform = pygame.transform.scale(window_img, (300, 300))
                window_rect = window_transform.get_rect(center=(350, 200))
                window = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and window_rect.collidepoint(pygame.mouse.get_pos()) and window == 1 and game_state == 6 and apocalypse_indicator == 0:
                # for showing the 1st window message
                window = 2
                game_state = 9
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and (answer1_text_rect.collidepoint(pygame.mouse.get_pos())
                    or answer2_text_rect.collidepoint(pygame.mouse.get_pos())
                    or answer3_text_rect.collidepoint(pygame.mouse.get_pos()))\
                    and window == 2 and game_state == 9:
                # for exiting the 1st window message
                game_state = 10
                magic_sound1.set_volume(1)
                magic_sound1.play(0)
                window = 1

            # if we press the dog
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and dog_rect.collidepoint(pygame.mouse.get_pos()) and game_state == 2 and dog == 0:
                # opening the dog screen
                game_state = 7
                dog_sound.set_volume(1)
                dog_sound.play(0)
                dog = 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and not dog_rect.collidepoint(pygame.mouse.get_pos()) and dog == 1 and game_state == 7:
                # Exiting the dog screen
                game_state = 2
                floor_transform = pygame.transform.scale(floor_img, (700, 200))
                floor_rect = floor_transform.get_rect(center=(350, 600))
                dog_transform = pygame.transform.scale(dog_img, (255, 145))
                dog_rect = dog_transform.get_rect(center=(350, 570))
                dog_sound.stop()
                dog = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and dog_rect.collidepoint(pygame.mouse.get_pos()) and dog == 1 and game_state == 7 and apocalypse_indicator == 0:
                # Showing the pre apocalypse message
                dog = 2
                game_state = 12
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and (answer1_text_rect.collidepoint(pygame.mouse.get_pos())
                    or answer2_text_rect.collidepoint(pygame.mouse.get_pos())
                    or answer3_text_rect.collidepoint(pygame.mouse.get_pos())) \
                    and dog == 2 and game_state == 12 and apocalypse_indicator == 0:
                # For exiting the 1st dog message
                game_state = 7
                dog = 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and dog_rect.collidepoint(pygame.mouse.get_pos()) and dog == 1 \
                    and game_state == 7 and apocalypse_indicator == 1 and not dog_change:
                # Showing the post apocalypse message
                dog = 2
                game_state = 13
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and answer2_text_rect.collidepoint(pygame.mouse.get_pos()) \
                    and dog == 2 and game_state == 13 and apocalypse_indicator == 1:
                # For exiting the 2st dog message
                game_state = 7
                dog = 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and (answer1_text_rect.collidepoint(pygame.mouse.get_pos())
                    or answer3_text_rect.collidepoint(pygame.mouse.get_pos())) \
                    and dog == 2 and game_state == 13 and apocalypse_indicator == 1:
                # For changing the dog into a zombie
                dog_img = pygame.image.load('animation/dog0_zombie.png').convert_alpha()
                dog_transform = pygame.transform.scale(dog_img, (500, 445))
                dog_rect = dog_transform.get_rect(center=(350, 350))
                dog_sound.stop()
                dog_sound = pygame.mixer.Sound('animation/dog_zombie_sound.mp3')
                dog_change = True
                dog_i = 0
                game_state = 7
                dog = 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                and dog_rect.collidepoint(pygame.mouse.get_pos()) \
                and dog_change and game_state == 7 and apocalypse_indicator == 1:
                # If you press the dog again it will kill you
                dog_sound.set_volume(2)
                end_music.play(-1)
                end_music.set_volume(1)
                game_over = 2

    # We are checking against out trigger time and changing the time
    try:
        if int(pygame.time.get_ticks() / 1000) >= trigger_time:
            # Reset trigger time for the next interval
            trigger_time = int(pygame.time.get_ticks() / 1000) + interval
            clock_handle_angle -= 2
            current_time += (pygame.time.get_ticks() / 1000) - start_time
    except NameError:
        pass

    # we are seeing what time it is and changing the pictures based on if its noon, morning or night
    if current_time/3600 > 24:
        time_on_clock = (current_time/3600) % 24
    elif current_time/3600 <= 24:
        time_on_clock = current_time/3600
    if 0 <= time_on_clock <= 6:
        wall_bg = pygame.image.load('animation/bg_night.png').convert_alpha()
        floor_img = pygame.image.load('animation/floor_placeholder_night.png').convert_alpha()
        floor_transform = pygame.transform.scale(floor_img, (700, 200))
        wall_bg_transform = pygame.transform.scale(wall_bg, (700, 700))
        if apocalypse_indicator == 0:
            window_img = pygame.image.load('animation/window_night.png').convert_alpha()
            window_transform = pygame.transform.scale(window_img, (300, 300))
        else:
            window_img = pygame.image.load('animation/window_night_ap.png').convert_alpha()
            window_transform = pygame.transform.scale(window_img, (300, 300))
    elif 6 < time_on_clock <= 11:
        wall_bg = pygame.image.load('animation/bg_morning.png').convert_alpha()
        floor_img = pygame.image.load('animation/floor_placeholder.png').convert_alpha()
        floor_transform = pygame.transform.scale(floor_img, (700, 200))
        wall_bg_transform = pygame.transform.scale(wall_bg, (700, 700))
        if apocalypse_indicator == 0:
            window_img = pygame.image.load('animation/window_placeholder.png').convert_alpha()
            window_transform = pygame.transform.scale(window_img, (300, 300))
        else:
            window_img = pygame.image.load('animation/magic_video/57.png').convert_alpha()
            window_transform = pygame.transform.scale(window_img, (300, 300))
    elif 11 < time_on_clock <= 18:
        wall_bg = pygame.image.load('animation/bg_noon.png').convert_alpha()
        floor_img = pygame.image.load('animation/floor_placeholder.png').convert_alpha()
        floor_transform = pygame.transform.scale(floor_img, (700, 200))
        wall_bg_transform = pygame.transform.scale(wall_bg, (700, 700))
        if apocalypse_indicator == 0:
            window_img = pygame.image.load('animation/window_noon.png').convert_alpha()
            window_transform = pygame.transform.scale(window_img, (300, 300))
        else:
            window_img = pygame.image.load('animation/window_noon_ap.png').convert_alpha()
            window_transform = pygame.transform.scale(window_img, (300, 300))
    elif 18 < time_on_clock <= 24:
        wall_bg = pygame.image.load('animation/bg_night.png').convert_alpha()
        floor_img = pygame.image.load('animation/floor_placeholder_night.png').convert_alpha()
        floor_transform = pygame.transform.scale(floor_img, (700, 200))
        wall_bg_transform = pygame.transform.scale(wall_bg, (700, 700))
        if apocalypse_indicator == 0:
            window_img = pygame.image.load('animation/window_night.png').convert_alpha()
            window_transform = pygame.transform.scale(window_img, (300, 300))
        else:
            window_img = pygame.image.load('animation/window_night_ap.png').convert_alpha()
            window_transform = pygame.transform.scale(window_img, (300, 300))

    # The beginning - narrator gives the task
    if game_active and game_state == 0:
        next_rect = next_transform.get_rect(midleft=(650, 350))
        screen.blit(wall_bg_transform, wall_bg_rect)
        screen.blit(floor_transform, floor_rect)
        screen.blit(table_transform, table_rect)
        notif_transform = pygame.transform.scale(notif_img, (600, 600))
        notif_rect = notif_transform.get_rect(center=(350, 350))
        screen.blit(notif_transform, notif_rect)
        question_text_rect = pygame.Rect(130, 150, 430, 400)
        draw_text(screen, "Welcome, brave adventurer, to a task that will test your skills like never before. "
                          "You stand before a TV that has confounded everyone trying to fix it. "
                          "Its peculiar nature defies logic and challenges the very essence of repair. "
                          "Are you willing to accept the challenge? But be warned, this is no ordinary task. "
                          "It will require all your wit, patience, and determination. "
                          "Think long and hard, for once you accept, there's no turning back. "
                          "Do you have what it takes to unravel the mysteries of this enigmatic TV? "
                          "The choice is yours, but remember, not all challenges are meant to be conquered.",
                  (0, 0, 0), question_text_rect, test_font2)
        hint("Click outside the paper to exit...")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                and not notif_rect.collidepoint(pygame.mouse.get_pos()) and game_state == 0:
            game_state = 2
            notif_transform = pygame.transform.scale(notif_img, (680, 450))
            notif_rect = notif_transform.get_rect(center=(350, 350))
            narrator_music.stop()

    # Clock, table and tv
    if game_active and game_state == 1:
        next_rect = next_transform.get_rect(midleft=(650, 350))
        screen.blit(wall_bg_transform, wall_bg_rect)
        screen.blit(floor_transform, floor_rect)
        screen.blit(clock_transform, clock_rect)
        screen.blit(clock_handle_transform, clock_handle_rect)
        screen.blit(papers_transform, papers_rect)
        screen.blit(table_transform, table_rect)
        if repaired:
            try: tv_img = pygame.image.load(f'animation/tv_video/{tv_frame}.png').convert_alpha()
            except FileNotFoundError: tv_frame = -1
        tv_transform = pygame.transform.scale(tv_img, (300, 250))
        tv_rect = tv_transform.get_rect(midbottom=(350, 400))
        screen.blit(tv_transform, tv_rect)
        screen.blit(next_transform, next_rect)
        tv_frame += 1

    # Window and the dog set up room
    if game_active and game_state == 2:
        next_rect = next_transform.get_rect(midleft=(-5, 350))
        screen.blit(wall_bg_transform, wall_bg_rect)
        screen.blit(floor_transform, floor_rect)
        screen.blit(window_transform, window_rect)
        screen.blit(next_transform, next_rect)
        try:
            if dog_change:
                dog_img = pygame.image.load(f'animation/dog{dog_i}_zombie.png').convert_alpha()
                dog_transform = pygame.transform.scale(dog_img, (355, 245))
                dog_rect = dog_transform.get_rect(center=(350, 550))
                dog_i += 1
                if dog_i >= 2:
                    dog_i = 0
        except NameError: pass
        screen.blit(dog_transform, dog_rect)

    # The clock
    if game_state == 3:
        screen.blit(wall_bg_transform, wall_bg_rect)
        clock_transform = pygame.transform.scale(clock_img, (350, 350))
        clock_rect = clock_transform.get_rect(center=(350, 350))
        screen.blit(clock_transform, clock_rect)
        clock_handle_transform_roto = pygame.transform.rotate(clock_handle_img, clock_handle_angle)
        clock_handle_transform = pygame.transform.scale(clock_handle_transform_roto, (350, 350))
        clock_handle_rect = clock_handle_transform.get_rect(center=(350, 350))
        screen.blit(clock_handle_transform, clock_handle_rect)
        question_text_rect = pygame.Rect(180, 100, 350, 100)
        if round(current_time/3600) >= 24:
            hour = round(current_time/3600) % 24
        else:
            hour = round(current_time/3600)
        if round(current_time/60) >= 60:
            minute = round(current_time/60) % 60
        else:
            minute = round(current_time/60)
        draw_text(screen, f"Day: {round(current_time/86400)} Hour {hour} : {minute}",
                  (0, 0, 0), question_text_rect, test_font)
        hint("You can use the clock to forward time, if you want...")

    # The TV before apocalypse
    if game_state == 4:
        screen.blit(wall_bg_transform, wall_bg_rect)
        table_transform = pygame.transform.scale(table_img, (900, 500))
        table_rect = table_transform.get_rect(midtop=(350, 500))
        tv_transform = pygame.transform.scale(tv_img, (650, 550))
        tv_rect = tv_transform.get_rect(center=(350, 350))
        screen.blit(table_transform, table_rect)
        screen.blit(tv_transform, tv_rect)
        if repaired:
            hint("You have repaired the \"TV\". But it seems that's not the \"TV\" that needed fixing.")

    # Paper pile == END Report
    elif game_state == 5:
        screen.blit(wall_bg_transform, wall_bg_rect)
        screen.blit(floor_transform, floor_rect)
        screen.blit(clock_transform, clock_rect)
        screen.blit(papers_transform, papers_rect)
        screen.blit(table_transform, table_rect)
        screen.blit(tv_transform, tv_rect)
        screen.blit(diff_papers_transform, diff_papers_rect)
        # we only need this after 1 - 2 days, when the first zombie appears
        if (pygame.time.get_ticks() / 1000) - start_time > 128744 or current_time > 128744:
            for key, value in results_dict['Time'].items():
                if round(results_dict['Time'][key]) - 87 <= pygame.time.get_ticks() / 1000 <= round(results_dict['Time'][key]) + 87 \
                        or round(results_dict['Time'][key]) - 87 <= current_time <= round(results_dict['Time'][key]) + 87:
                    hum = results_dict['Number of Humans'][key]
                    zom = results_dict['Number of Zombies'][key]
            question_text_rect = pygame.Rect(120, 60, 450, 650)
            draw_text(screen, f"Dear Betrayer, "
                              f"As I write this message to you, my heart is heavy with sorrow and desperation. "
                              f"I've considered you to be more than just a dog, but you have proven otherwise. "
                              f"Today {round(current_time/3600)} hour of desperation. "
                              f"There are {round(hum)} humans left. "
                              f"The streets are barren, the skies are gray, and the silence is deafening. "
                              f"The only thing one might feel in these times, is overwhelming fear. "
                              f"I want you to know that I am on my knees every day, every second that I can spare... "
                              f"Begging you, or God, or anyone to stop this. I am hoping that somehow you can hear my sobs, "
                              f"and that you have a change in your thinking. "
                              f"The remnants of humanity are scattered. That is to say, our families are scattered. "
                              f"There are exactly {round(zom)} zombies. I know because I can see them in my dreams. "
                              f"When I close my eyes I can see them. "
                              f"I will claw and scratch at the your door, and do anything I need to make you undo what you did. "
                              f"I am hopeful that these letters have an effect on you. "
                              f"With utmost desperation, Your Faithful ", (0, 0, 0), question_text_rect, test_font2)
        else:
            question_text_rect = pygame.Rect(120, 60, 450, 650)
            draw_text(screen, f"Dear Neighbour, "
                              f"I hope this letter finds you well. "
                              f"I wanted to take a moment to express my admiration for you as a neighbor. "
                              f"I have always appreciated how friendly and helpful you are to those around you, "
                              f"and it is clear that you take great care in maintaining your home and yard. "
                              f"I would be honored if you would join me for lunch sometime soon. "
                              f"It would be a pleasure to get to know you better and learn more about your experiences and interests. "
                              f"Thank you for being such a wonderful neighbor, and I hope to hear back from you soon. "
                              f"Best regards, Your Faithful ", (0, 0, 0), question_text_rect, test_font2)
        hint("Click outside the paper to exit...")

    # Window, looking outside
    elif game_state == 6:
        screen.blit(wall_bg_transform, wall_bg_rect)
        window_transform = pygame.transform.scale(window_img, (650, 670))
        window_rect = window_transform.get_rect(center=(350, 350))
        screen.blit(window_transform, window_rect)

    # Dog
    elif game_state == 7:
        screen.blit(wall_bg_transform, wall_bg_rect)
        floor_transform = pygame.transform.scale(floor_img, (700, 500))
        floor_rect = floor_transform.get_rect(midtop=(350, 350))
        screen.blit(floor_transform, floor_rect)
        dog_transform = pygame.transform.scale(dog_img, (500, 350))
        dog_rect = dog_transform.get_rect(center=(350, 350))
        screen.blit(dog_transform, dog_rect)

    # Clock question before apocalypse
    elif game_state == 8:
        question_box("why not, its just time, what could happen", "no, i do not, you're right, as always",
                     "maybe, i feel mischievous", "Are you sure you want to mess with THE TIME before starting "
                     "\"the thing we talked about\"?")
        hint("later, clock could help you forward time...")

    # Window question, starting the apocalypse
    elif game_state == 9:
        question_box("yes, that's what I came here to do dummy",
                     "no, what do you mean \"repair the TV\", I already did that",
                     "I might do it, even though i'm not sure what you're talking about",
                     "Are you sure you want to start \"repairing the TV\"? "
                     "After all - it is an excessively evil thing to do.")

    # Window, beginning the apocalypse
    elif game_state == 10:
        screen.blit(wall_bg_transform, wall_bg_rect)
        window_img = pygame.image.load('animation/magic_video/0.png')
        window_transform = pygame.transform.scale(window_img, (300, 500))
        window_rect = window_transform.get_rect(center=(350, 200))
        try: magic_video = pygame.image.load(f'animation/magic_video/{magic_video_frame}.png').convert_alpha()
        except FileNotFoundError:
            magic_video_frame = 56
            if magic_sound2_indicator == 0:
                magic_sound2.set_volume(0.5)
                magic_sound2.play(0)
                magic_sound2_indicator = 1
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and window == 1 and game_state == 10:
                game_state = 11
                window_img = pygame.image.load('animation/magic_video/57.png')
                window_transform = pygame.transform.scale(window_img, (300, 320))
                window_rect = window_transform.get_rect(center=(350, 200))
                window = 0
                magic_sound1.stop()
                magic_sound2.stop()
        magic_video_transform = pygame.transform.scale(magic_video, (700, 700))
        screen.blit(magic_video_transform, magic_video_rect)
        magic_video_frame += 1
        hint("Click anywhere to exit...")

    # Message for the beginning of the apocalypse
    elif game_state == 11:
        screen.blit(dark_bg_transform, dark_bg_rect)
        notif_transform = pygame.transform.scale(notif_img, (500, 500))
        notif_transform_rect = notif_transform.get_rect(center=(350, 350))
        screen.blit(notif_transform, notif_transform_rect)
        question_text_rect = pygame.Rect(120, 200, 470, 150)
        question_text1_rect = pygame.Rect(170, 350, 360, 400)
        draw_text(screen, "Important announcement!", (0, 0, 0),  question_text_rect, test_font1)
        draw_text(screen, "You seem to have started a zombie apocalypse, Bravo. whether it was on purpose or not, "
                          "it seems like you enjoyed it. "
                          "There is nothing you can do about it, but you can try to stop it if you want.",
                  (0, 0, 0), question_text1_rect, test_font2)
        hint("Congratulations, you have repaired the TV, let's see how it plays out.")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                and not notif_transform_rect.collidepoint(pygame.mouse.get_pos()):
            game_state = 2
            notif_transform = pygame.transform.scale(notif_img, (680, 450))
            notif_rect = notif_transform.get_rect(center=(350, 350))
            apocalypse_indicator = 1

    # Dog question before the apocalypse
    elif game_state == 12:
        question_box("I'll check on him later then",
                     "no, let me pet the dog pleaseee",
                     "i want to turn this dog into a zombie. It seems a right thing to do...",
                     "Dog is still sleepy, check on him later?")

    # Dog question after the apocalypse
    elif game_state == 13:
        question_box("well duh",
                     "no, no, i really don't want to do that",
                     "this dog has never loved me, it deserves it",
                     "Wait, wait, wait... You want to turn the dog into a zombie? INTO A ZOMBIE? "
                     "DAMN. That seems... not good, at all, but, your the boss...")

    # TV after the repair
    if game_state == 14:
        screen.blit(wall_bg_transform, wall_bg_rect)
        table_transform = pygame.transform.scale(table_img, (900, 500))
        table_rect = table_transform.get_rect(midtop=(350, 500))
        tv_transform = pygame.transform.scale(tv_img, (650, 550))
        tv_rect = tv_transform.get_rect(center=(350, 350))
        screen.blit(table_transform, table_rect)
        screen.blit(tv_transform, tv_rect)
        if random_movie == 1:
            try: stop_it_now_video = pygame.image.load(f'animation/video1/video1_pixaleted-{video1_frame}.png').convert_alpha()
            except FileNotFoundError: video1_frame = 101
            stop_it_now_video_transform = pygame.transform.scale(stop_it_now_video, (640, 450))
            screen.blit(stop_it_now_video_transform, stop_it_now_video_rect)
            video1_frame += 2
        if random_movie == 2:
            try: breaking_news = pygame.image.load(f'animation/video2/video2_pixaleted{video1_frame}.png').convert_alpha()
            except FileNotFoundError: video1_frame = 101
            breaking_news_transform = pygame.transform.scale(breaking_news, (640, 450))
            screen.blit(breaking_news_transform, breaking_news_rect)
            video1_frame += 2
        if random_movie == 3:
            try: video_panel = pygame.image.load(f'animation/video3/video3{video1_frame}.png').convert_alpha()
            except FileNotFoundError: video1_frame = 101
            video_panel_transform = pygame.transform.scale(video_panel, (640, 450))
            screen.blit(video_panel_transform, video_panel_rect)
            video1_frame += 2

    # TV repairment
    elif game_state == 15:
        question_box("yea, lets do it",
                     "no, tv is evil",
                     "hmm i'm not good with technology, but i'll try",
                     "Do you want to fix the TV, it looks easy enough to do?")

    for key, value in results_dict['Time'].items():
        if round(results_dict['Time'][key]) - 86 <= pygame.time.get_ticks() / 1000 <= round(results_dict['Time'][key]) + 86 \
                or round(results_dict['Time'][key]) - 86 <= current_time <= round(results_dict['Time'][key]) + 86:
            warn = results_dict['Alert Level'][key]
    try:
        if warn == 'Alert' and alarm < 60:
            screen.blit(red_transform, red_rect)
            red_alpha += 5
            red_transform.set_alpha(red_alpha)
            if alarm == 0:
                alarm_sound.play(0)
                alarm_sound.set_volume(1)
            alarm += 1
        elif warn == 'Caution' and caution < 60:
            screen.blit(red_transform, red_rect)
            red_alpha += 5
            red_transform.set_alpha(red_alpha)
            if caution == 0:
                caution_sound.play(0)
                caution_sound.set_volume(1)
                red_alpha = 0
            caution += 1
        elif warn == 'Critical': pass
    except NameError: pass

    for key, value in results_dict['Time'].items():
        if round(results_dict['Time'][key]) - 87 <= pygame.time.get_ticks() / 1000 <= round(
                results_dict['Time'][key]) + 87 \
                or round(results_dict['Time'][key]) - 87 <= current_time <= round(results_dict['Time'][key]) + 87:
            hum = results_dict['Number of Humans'][key]
            zom = results_dict['Number of Zombies'][key]
    if round(hum) == 1:
        # The game over screen, when all the humans have died
        alarm_sound.stop()
        caution_sound.stop()
        clock_sound.stop()
        end_music.play(-1)
        end_music.set_volume(1)
        screen.blit(wall_bg_transform, wall_bg_rect)
        screen.blit(floor_transform, floor_rect)
        screen.blit(table_transform, table_rect)
        diff_papers_transform = pygame.transform.scale(diff_papers_img, (550, 690))
        diff_papers_rect = diff_papers_transform.get_rect(center=(350, 350))
        screen.blit(diff_papers_transform, diff_papers_rect)
        question_text_rect = pygame.Rect(90, 30, 500, 680)
        draw_text(screen, f"Congratulations, You Monster! "
                          f"I am pleased to inform you that you have successfully ended the world, "
                          f"and slaughter literally a 1000 innocent people. Bravo! "
                          f"You truly are a monster in making. "
                          f"Your remarkable ability to bring about such catastrophic chaos and destruction "
                          f"is truly impressive. "
                          f"Your relentless pursuit of morbidity, with daring and unorthodox methods, "
                          f"has surpassed all my expectations. "
                          f"The way you have skillfully managed to create a living hell is awe-inspiring. "
                          f"It takes a special kind of genius to accomplish such a feat. "
                          f"Your blatant disregard for humanity and the consequences of your actions is both remarkable "
                          f"and terrifying. "
                          f"Your guilt-ridden conscience may be gnawing at you, but fear not! Embracing your "
                          f"inner monster is the true mark of a successful world-ending mastermind. "
                          f"After all, world has always encouraged a \"shoot first, ask questions later\" approach, "
                          f"and you have certainly embodied that spirit. "
                          f"So, once again, congratulations on your spectacular achievement. "
                          f"I am in awe of your monstrous capabilities and your unparalleled dedication to destruction. "
                          f"Keep up the great work! "
                          f"Number of humans left: 1, and that's YOU. "
                          f"Number of zombies: {round(zom)}. "
                          f"Time needed for zombies to take over: {round(current_time/86400)} days", (0, 0, 0),
                  question_text_rect, test_font2)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                and not diff_papers_rect.collidepoint(pygame.mouse.get_pos()):
            exit()

    if game_over == 1:
        # The game over screen, when we mess with time
        screen.blit(wall_bg_transform, wall_bg_rect)
        screen.blit(floor_transform, floor_rect)
        screen.blit(clock_transform, clock_rect)
        screen.blit(papers_transform, papers_rect)
        screen.blit(table_transform, table_rect)
        screen.blit(tv_transform, tv_rect)
        screen.blit(diff_papers_transform, diff_papers_rect)
        text_rect = pygame.Rect(120, 200, 450, 650)
        draw_text(screen, "Unfortunately You have turned yourself into a zombie, better luck next time smart guy. "
                          "Next time be sure to start the apocalypse first.",
                  (0, 0, 0), text_rect, test_font2)
        text1_rect = pygame.Rect(120, 500, 450, 100)
        hint("Click outside the paper to exit!")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                and not diff_papers_rect.collidepoint(pygame.mouse.get_pos()) and game_over == 1:
            exit()

    if game_over == 2:
        # The game over screen, when the dog kills us
        screen.blit(wall_bg_transform, wall_bg_rect)
        screen.blit(floor_transform, floor_rect)
        screen.blit(clock_transform, clock_rect)
        screen.blit(papers_transform, papers_rect)
        screen.blit(table_transform, table_rect)
        screen.blit(tv_transform, tv_rect)
        screen.blit(diff_papers_transform, diff_papers_rect)
        text_rect = pygame.Rect(120, 200, 450, 650)
        draw_text(screen, "It seems the dog killed you. I'm not surprised.",
                  (0, 0, 0), text_rect, test_font2)
        text1_rect = pygame.Rect(120, 500, 450, 100)
        hint("Click outside the paper to exit!")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                and not diff_papers_rect.collidepoint(pygame.mouse.get_pos()) and game_over == 2:
            exit()

    if not game_active:
        screen.blit(start_bg_transform, start_bg_rect)
        # The logic of how the rain falls
        if rain0_rect.y < 1050:
            rain0_rect.y += 30
        else:
            rain0_rect.y = -1050
        if rain1_rect.y < 1050:
            rain1_rect.y += 30
        else:
            rain1_rect.y = -1050
        if rain2_rect.y < 1050:
            rain2_rect.y += 30
        else:
            rain2_rect.y = -1050
        screen.blit(rain0_transform, rain0_rect)
        screen.blit(rain1_transform, rain1_rect)
        screen.blit(rain2_transform, rain2_rect)

        # Increase the volume of the music and show the game name after 3.8 seconds
        if pygame.time.get_ticks() - start_time > 11800:
            if not show_name:
                screen.blit(zombie_title_img_transform, zombie_title_img_rect)
                show_name = True

        # Show the game message after 6 seconds
        if pygame.time.get_ticks() - start_time > 14000:
            if not show_message:
                hint("Press space to start the game")
                show_message = True

    # in your main loop update the position every frame and blit the image
    cursor_img_rect.center = pygame.mouse.get_pos()  # update position
    screen.blit(cursor_img, cursor_img_rect)  # draw the cursor
    pygame.display.update()
    clock.tick(60)