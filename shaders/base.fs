#include shaders/inc/fs_head.inc

void main(void) {

    #include shaders/inc/fs_main.inc

    // PostProcess only: force alpha to 1.0
    if (unif[12][1] == 1.0) {
        gl_FragColor.a = 1.0;
    }

    #include shaders/effects/{EFFECT}.fs

    // Video only: convert bgr to rgb
    if (unif[12][2] == 1.0) {
        gl_FragColor.rgb = gl_FragColor.bgr;
    }

    #include shaders/effects/key.fs
    #include shaders/effects/colorize.fs
    #include shaders/effects/invert.fs
    #include shaders/effects/mask.fs

}
