#include shaders/inc/fs_head.inc

void main(void) {

    #include shaders/inc/fs_main.inc
    #include shaders/inc/fs_misc.inc

    #include shaders/effects/{EFFECT}.fs

    #include shaders/effects/key.fs
    #include shaders/effects/colorize.fs
    #include shaders/effects/invert.fs
    #include shaders/effects/mask.fs

}
