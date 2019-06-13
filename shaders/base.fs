#include shaders/inc/fs_head.inc

void main(void) {

    #include shaders/inc/fs_main.inc

    #ifdef POST_PROCESS
    gl_FragColor.a = 1.0;
    #endif

    #include shaders/effects/{EFFECT}.fs

    #ifdef VIDEO
    gl_FragColor.rgb = gl_FragColor.bgr;
    #endif

    #include shaders/effects/key.fs
    #include shaders/effects/colorize.fs
    #include shaders/effects/invert.fs
    #include shaders/effects/mask.fs

}
