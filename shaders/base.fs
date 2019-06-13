#include shaders/inc/fs_head.fs

void main(void) {

    #ifdef FISH
    #include shaders/effects/fish.fs
    #endif

    #include shaders/inc/fs_main.fs

    #ifdef POST_PROCESS
    gl_FragColor.a = 1.0;
    #endif

    #ifdef RGBWAVE
    #include shaders/effects/rgbwave.fs
    #endif

    #ifdef CHARCOAL
    #include shaders/effects/charcoal.fs
    #endif

    #ifdef NOISE
    #include shaders/effects/noise.fs
    #endif

    #ifdef VIDEO
    gl_FragColor.rgb = gl_FragColor.bgr;
    #endif

    #ifdef KEY
    #include shaders/effects/key.fs
    #endif

    #include shaders/effects/colorize.fs

    #ifdef INVERT
    #include shaders/effects/invert.fs
    #endif

    #ifdef MASK
    #include shaders/effects/mask.fs
    #endif

}
