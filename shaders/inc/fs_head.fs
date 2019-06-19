precision mediump float;

uniform sampler2D tex0;
uniform sampler2D tex1;
uniform sampler2D tex2;

uniform vec3 unib[5]; // Buffer
uniform vec3 unif[20]; // Shape

varying vec3 ucoords;
varying vec2 coords;

varying vec3 umaskCoords;
varying vec2 maskCoords;


const vec2 resolution = vec2({WIDTH}, {HEIGHT});

#include shaders/inc/random.fs
#include shaders/inc/colors.fs
