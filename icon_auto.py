import pyautogui as pg

pg.PAUSE = 0.3

with pg.hold('alt'):
    pg.press('tab')

pg.sleep(1)

for counter in range(10, 24):
    text = f'{counter}:'

    pg.click(454, 504)

    pg.hotkey('ctrl', 'a')
    pg.typewrite(text)
    pg.press('esc')

    with pg.hold('ctrl'):
        pg.press('a')
        pg.press('-')

    pg.hotkey('ctrl', 'shift', 'alt', 's')
    pg.sleep(2)
    pg.typewrite(text)

    pg.press('enter')
    pg.sleep(2)

    pg.hotkey('ctrl', 'z')