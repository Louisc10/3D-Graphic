#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import OpenGL.GL as GL             # standard Python OpenGL wrapper
import glfw                        # lean window system wrapper for OpenGL
import numpy as np                 # all matrix manipulations & OpenGL args
from transform import Trackball, identity
from core import Shader, Mesh


# ------------  Exercise 1 and 2: Scene object classes ------------------------
class Pyramid:
    """ Class for drawing a pyramid object """

    def __init__(self, shader):
        self.shader = shader

        # TODO: this is still a triangle, new values needed for Pyramid
        position = np.array(((0, .5, 0), (.5, -.5, .5), (-.5, -.5, .5), (.5, -.5, -.5), (-.5, -.5, -.5)), 'f')
        color = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1)), 'f')
        self.index = np.array(((2, 1, 0), (0, 1, 3), (4, 2, 0), (0, 3, 4), (1, 2, 4), (4, 3, 1)), np.uint32)

        self.glid = GL.glGenVertexArrays(1)  # create OpenGL vertex array id
        GL.glBindVertexArray(self.glid)      # activate to receive state below
        self.buffers = GL.glGenBuffers(3)    # create buffer for position attrib

        # create position attribute, send to GPU, declare type & per-vertex size
        loc = GL.glGetAttribLocation(shader.glid, 'position')
        GL.glEnableVertexAttribArray(loc)    # assign to position attribute
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[0])
        GL.glBufferData(GL.GL_ARRAY_BUFFER, position, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(loc, 3, GL.GL_FLOAT, False, 0, None)

        # create color attribute, send to GPU, declare type & per-vertex size
        loc = GL.glGetAttribLocation(shader.glid, 'color')
        GL.glEnableVertexAttribArray(loc)    # assign to color
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[1])
        GL.glBufferData(GL.GL_ARRAY_BUFFER, color, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(loc, 3, GL.GL_FLOAT, False, 0, None)

        # create a dedicated index buffer, copy python array to GPU
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffers[2])
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.index,
                        GL.GL_STATIC_DRAW)

    def draw(self, projection, view, **_args):
        GL.glUseProgram(self.shader.glid)

        loc = GL.glGetUniformLocation(self.shader.glid, 'view')
        GL.glUniformMatrix4fv(loc, 1, True, view)

        loc = GL.glGetUniformLocation(self.shader.glid, 'projection')
        GL.glUniformMatrix4fv(loc, 1, True, projection)

        # draw triangle as GL_TRIANGLE indexed mode array, pass array size
        GL.glBindVertexArray(self.glid)
        GL.glDrawElements(GL.GL_TRIANGLES, self.index.size,
                          GL.GL_UNSIGNED_INT, None)

    def __del__(self):
        GL.glDeleteVertexArrays(1, [self.glid])
        GL.glDeleteBuffers(3, self.buffers)


# ------------  Viewer class & window management ------------------------------
class Viewer:
    """ GLFW viewer window, with classic initialization & graphics loop """
    def __init__(self, width=640, height=480):

        # version hints: create GL window with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        # initialize trackball
        self.trackball = Trackball()
        self.mouse = (0, 0)

        # register event handlers
        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.set_scroll_callback(self.win, self.on_scroll)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.1, 0.1, 0.1, 0.1)
        GL.glEnable(GL.GL_CULL_FACE)   # enable backface culling (Exercise 1)
        GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test (Exercise 1)

        # initially empty list of object to draw
        self.drawables = []

    def run(self):
        """ Main render loop for this OpenGL window """
        while not glfw.window_should_close(self.win):
            # clear draw buffer, but also need to clear Z-buffer! (Exercise 1)
            # GL.glClear(GL.GL_COLOR_BUFFER_BIT)  # comment this, uncomment next
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            win_size = glfw.get_window_size(self.win)
            view = self.trackball.view_matrix()
            projection = self.trackball.projection_matrix(win_size)

            # draw our scene objects
            for drawable in self.drawables:
                drawable.draw(view=view, projection=projection,
                              model=identity())

            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()

    def add(self, *drawables):
        """ add objects to draw in this window """
        self.drawables.extend(drawables)

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)

            for drawable in self.drawables:
                if hasattr(drawable, 'key_handler'):
                    drawable.key_handler(key)

    def on_mouse_move(self, win, xpos, ypos):
        """ Rotate on left-click & drag, pan on right-click & drag """
        old = self.mouse
        self.mouse = (xpos, glfw.get_window_size(win)[1] - ypos)
        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_LEFT):
            self.trackball.drag(old, self.mouse, glfw.get_window_size(win))
        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_RIGHT):
            self.trackball.pan(old, self.mouse)

    def on_scroll(self, win, _deltax, deltay):
        """ Scroll controls the camera distance to trackball center """
        self.trackball.zoom(deltay, glfw.get_window_size(win)[1])


# -------------- main program and scene setup --------------------------------
def main():
    """ create window, add shaders & scene objects, then run rendering loop """
    viewer = Viewer()
    color_shader = Shader("color.vert", "color.frag")

    # place instances of our basic objects
    viewer.add(Pyramid(color_shader))

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                  # main function keeps variables locally scoped
