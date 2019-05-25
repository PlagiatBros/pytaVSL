precision mediump float;

uniform sampler2D tex0;
uniform sampler2D tex1;
uniform sampler2D tex2;

uniform vec3 unib[5]; // Buffer
uniform vec3 unif[20]; // Shape

varying vec2 coords;

const vec2 resolution = vec2(800.0, 600.0);

#include shaders/inc/random.inc
#include shaders/inc/colors.inc
