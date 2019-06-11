precision mediump float;

attribute vec3 vertex;
attribute vec3 normal;
attribute vec2 texcoord;

uniform mat4 modelviewmatrix[3]; // [0] model movement in real coords, [1] in camera coords, [2] camera at light
uniform vec3 unib[5]; // Buffer
uniform vec3 unif[20];// Shape

varying vec2 coords;
varying vec2 maskCoords;
