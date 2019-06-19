precision mediump float;

uniform sampler2D tex0;
uniform sampler2D tex1;
uniform sampler2D tex2;

uniform vec3 unib[5]; // Buffer
uniform vec3 unif[20]; // Shape
uniform vec2 warp[4]; // Warp

varying vec2 coords;
varying vec2 maskCoords;

const vec2 resolution = vec2({WIDTH}, {HEIGHT});

#include shaders/inc/random.fs
#include shaders/inc/colors.fs
