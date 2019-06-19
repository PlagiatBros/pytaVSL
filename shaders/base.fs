#include shaders/inc/fs_head.fs

#ifdef TUNNEL
#include shaders/effects/tunnel.fs
#endif

#ifdef NOISE
#include shaders/effects/noise.fs
#endif


void main(void) {

    #ifdef FISH
    #include shaders/effects/fish.fs
    #endif


    #include shaders/inc/fs_main.fs

    #ifdef TUNNEL
    gl_FragColor.rgb = tunnel(coords, unif[16][2]).rgb;
    #endif


    #ifdef POST_PROCESS
    gl_FragColor.a = 1.0;
    #endif

    #ifdef RGBWAVE
    #include shaders/effects/rgbwave.fs
    #endif

    #ifdef CHARCOAL
    #include shaders/effects/charcoal.fs
    #endif


    #ifdef VIDEO
    gl_FragColor.rgb = gl_FragColor.bgr;
    #endif

    #ifdef NOISE
    gl_FragColor.rgb = add_noise(gl_FragColor.rgb, unif[12][1], unif[18][0]);
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
