import pygame
import pygame.font
import pygame.event
import pygame.draw
from .ExtractionLayer import Extraction


def get_key():
    while 1:
        event = pygame.event.poll()
        if event.type == pygame.KEYDOWN:
            return event.key
        else:
            pass


def display_box(screen, message):
    "Print a message in a box in the middle of the screen"
    fontobject = pygame.font.Font(None, 50)
    pygame.draw.rect(screen, (255, 225, 0),
                     ((4 * screen.get_width() / 5) - 600,
                      (screen.get_height()) - 125, 500, 50), 0)
    pygame.draw.rect(screen, (225, 225, 225),
                     ((4 * screen.get_width() / 5) - 602,
                      (screen.get_height()) - 127, 501, 51), 5)
    if len(message) != 0:
        screen.blit(fontobject.render(message, 1, (0, 0, 0)),
                    ((4 * screen.get_width() / 5) - 600,
                     (screen.get_height()) - 120))
    pygame.display.flip()


def ask(screen, question, ps):
    "ask(screen, question) -> answer"
    pygame.font.init()
    current_string = []
    display_box(screen, question + ": " + "".join(current_string))
    while 1:
        inkey = get_key()
        if inkey == pygame.K_BACKSPACE:
            current_string = current_string[0:-1]
        elif inkey == pygame.K_KP_ENTER or inkey == pygame.K_RETURN:
            # print("Number of Drones: " , "".join(current_string))
            Dronenum = "".join(current_string)
            Extraction.Dronenumber(Dronenum, ps)
            return "".join(current_string)
        elif inkey == pygame.K_MINUS:
            current_string.append("_")
        elif inkey <= 127:
            current_string.append(chr(inkey))
        display_box(screen, question + ": " + "".join(current_string))
