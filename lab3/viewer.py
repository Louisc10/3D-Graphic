#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import sys                          # for system arguments

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import numpy as np                  # all matrix manipulations & OpenGL args
import glfw                         # lean window system wrapper for OpenGL

from core import Shader, Mesh, Viewer, Node, load
from transform import translate, identity, rotate, scale


class Axis(Mesh):
    """ Axis object useful for debugging coordinate frames """
    def __init__(self, shader):
        pos = ((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1))
        col = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 1))
        super().__init__(shader, attributes=dict(position=pos, color=col))

    def draw(self, primitives=GL.GL_LINES, **uniforms):
        super().draw(primitives=primitives, **uniforms)


class Triangle(Mesh):
    """Hello triangle object"""
    def __init__(self, shader):
        position = np.array(((0, .5, 0), (-.5, -.5, 0), (.5, -.5, 0)), 'f')
        color = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'f')
        self.color = (1, 1, 0)
        attributes = dict(position=position, color=color)
        super().__init__(shader, attributes=attributes)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        super().draw(primitives=primitives, global_color=self.color, **uniforms)

    def key_handler(self, key):
        if key == glfw.KEY_C:
            self.color = (0, 0, 0)


class Cylinder(Node):
    """ Very simple cylinder based on provided load function """
    def __init__(self, shader):
        super().__init__()
        self.add(*load('cylinder.obj', shader))  # just load cylinder from file


# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()

    # default color shader
    shader = Shader("color.vert", "color.frag")

    # place instances of our basic objects
    # viewer.add(*[mesh for file in sys.argv[1:] for mesh in load(file, shader)])
    # if len(sys.argv) < 2:
    #     viewer.add(Axis(shader))
    #     viewer.add(Node(children=[Cylinder(shader)], transform=translate(x=+2)))
    #     viewer.add(Node(children=[Triangle(shader)], transform=translate(x=-1)))
    #     print('Usage:\n\t%s [3dfile]*\n\n3dfile\t\t the filename of a model in'
    #           ' format supported by assimp.' % (sys.argv[0],))
    
        
    theta = 45.0
    phi1 = 45.0
    phi2 = 20.0
    
    axis = Axis(shader)

    cylinder = Cylinder(shader)
    
    #Create object
    base = Node(transform=scale(2,0.75,2))
    base.add(cylinder)
    
    arm = Node(transform=translate(0,3,0) @ scale(x=0.2, y=3, z=0.2))
    arm.add(cylinder)
    
    forearm = Node(transform=translate(0,6.5,0) @ scale(x=0.2, y=1, z=0.2))
    forearm.add(cylinder)
    
    # Create Node for transform
    t_forearm = Node(transform=translate(0,0.75,-1.9) @ rotate((1,0,0), phi2))
    t_forearm.add(forearm, axis)
    
    t_arm = Node(transform=rotate((1,0,0), phi1))
    t_arm.add(arm, t_forearm)
    
    t_base = Node(transform=rotate((0,0,0), theta))
    t_base.add(base, t_arm)
    
    
    viewer.add(t_base)
    
    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
