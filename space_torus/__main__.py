#!/usr/bin/python
INITIAL_WIN_HEIGHT = 540
INITIAL_WIN_WIDTH = 700
WIN_TITLE = "Space Torus"

def main():
    print "Welcome to Space Torus. The game will begin shortly."

    import os
    os.environ['PYGLET_SHADOW_WINDOW']="0"

    import pyglet
    from space_torus.game import Applet

    pyglet.options['shadow_window'] = False

    print pyglet.options

    Applet(width=INITIAL_WIN_WIDTH, height=INITIAL_WIN_HEIGHT, caption=WIN_TITLE, resizable=True, vsync=0)
    pyglet.app.run()


if __name__ == '__main__':
    main()