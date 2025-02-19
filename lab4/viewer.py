#!/usr/bin/env python3
import sys
from core import Shader, Viewer, load
import numpy as np

# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    shader = Shader("phong.vert", "phong.frag")

    light_dir = (0, -1, 0)
    viewer.add(*[mesh for file in sys.argv[1:]
                 for mesh in load(file, shader, light_dir=light_dir)])

    if len(sys.argv) != 2:
        print('Usage:\n\t%s [3dfile]*\n\n3dfile\t\t the filename of a model in'
              ' format supported by assimp.' % (sys.argv[0],))

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
