#include shaders/inc/fs_head.inc

void main(void) {

    #include shaders/inc/fs_main.inc

    #include shaders/effects/{EFFECT}.fs

    #include shaders/effects/key.fs
    #include shaders/effects/colorize.fs
    #include shaders/effects/invert.fs

}
// uniforms:
// 47 random float
// 48:50 key color (r, g, b)
// 51 key threshold
// 52 invert state

// 53 rgbwave strength
// 54:56 charcoal (radius, thresh, strengh)
// 57:59 noise (density, seed1, seed2)
