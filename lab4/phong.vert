#version 330 core

// input attribute variable, given per vertex
in vec3 position;
in vec3 normal;

// global matrix variables
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

// position and normal for the fragment shader, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
out vec3 w_position, w_normal;   // in world coordinates

void main() {
    // TODO: compute the vertex position and normal in world or view coordinates
    w_normal = (model * vec4(normal, 0)).xyz;
    //We don't want to apply translation that is why it 0
    w_position = (model *vec4(position, 1)).xyz;
    //We build 4d vector and sincec we care the translition we put 1

    // tell OpenGL how to transform the vertex to clip coordinates
    gl_Position = projection * view * model * vec4(position, 1);
    //We want to apply translation that is why it 1 (as the identity)

}
