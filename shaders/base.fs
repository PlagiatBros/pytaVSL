#include shaders/inc/fs_head.fs

vec4 tex2D(sampler2D tex, vec2 coords) {
    #ifdef TEXT
        float smoothing = 0.25 / (25. * sqrt(unib[2][2])); // 0.25 / (spread * scale)
        float distance = texture2D(tex, coords).r;
        float outlineFactor = smoothstep(0.5 - smoothing, 0.5 + smoothing, distance);
        vec3 color = mix(unib[4], vec3(unib[1]), outlineFactor);
        float outlineWidth = 0.5 + smoothing - unib[3][2] / 4.0;
        float alpha = smoothstep(outlineWidth - smoothing, outlineWidth + smoothing, distance);
        return vec4(color, alpha);
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
    gl_FragColor.a = unif[5][2];
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

    #ifndef TEXT
    #include shaders/effects/colorize.fs
    #endif

    #ifdef INVERT
    #include shaders/effects/invert.fs
    #endif

    #ifdef MASK
    #include shaders/effects/mask.fs
    #endif

}
