#include shaders/inc/fs_head.fs

vec4 tex2D(sampler2D tex, vec2 coords) {
    #ifdef TEXT
        float alphaTest = texture2D(tex, coords).r;
        vec4 color = vec4(step(0.5, alphaTest));
        color.rgb *= 0.5;
        color.a += smoothstep(.48, 0.5, alphaTest);
        // if (alphaTest > 0.4 && alphaTest < 0.48) {
        //      color = vec4(1., -1., -1., .8);
        // }
        return color;
    #else
        return texture2D(tex, coords);
    #endif
}


#ifdef TUNNEL
#include shaders/effects/tunnel.fs
#endif

#ifdef NOISE
#include shaders/effects/noise.fs
#endif

void main(void) {

    #ifdef WARP
    #include shaders/effects/warp.fs
    #endif

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
