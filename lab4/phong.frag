#version 330 core

// fragment position and normal of the fragment, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
in vec3 w_position, w_normal;   // in world coodinates

// light dir, in world coordinates
uniform vec3 light_dir;

// material properties
uniform vec3 k_a;
uniform vec3 k_d;
uniform vec3 k_s;
uniform float s;

// world camera position
uniform vec3 w_camera_position;

// output fragment color for OpenGL
out vec4 out_color;


void main() {
    // TODO: compute Lambert illumination
    vec3 ambiant = k_a;

    vec3 normal = normalize(w_normal);
    vec3 light = normalize(light_dir);
    
    vec3 diffuse = k_d *max(dot(normal, light), 0.f) ;
    /*
        Lambertian model function
        I = k_d (n . l)
        - if the light is located under the surface, the scalar product will result a negative value and should thus be clamped to 0.
    */

    vec3 r = reflect(-light, normal);
    vec3 v = normalize(w_camera_position - w_position);
    vec3 specular = k_s*(pow(max(dot(r, v),0.f), s));
    /*
        Phong model function
        I = k_a + k_d(n . l) + k_s(r . v)^s
        - negative values that must be clamped to 0 (a shading function should not create negative energy).
    */

    vec3 col = ambiant + diffuse + specular;

    out_color = vec4(col, 1);
}
