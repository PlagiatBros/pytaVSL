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


#ifdef NOISE
#include shaders/effects/noise.fs
#endif


#ifdef COLORS
#include shaders/effects/colors.fs
#endif
