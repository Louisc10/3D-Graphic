#version 330 core
uniform vec3 color;
// output fragment color for OpenGL
out vec4 out_color;

void main() {
    out_color = vec4(0, 1, 0, 1);
}
