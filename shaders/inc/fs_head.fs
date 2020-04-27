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

        vec3 sample = texture2D(tex, coords).rgb;

        float r = sample.r;
        float g = sample.g;
        float b = sample.b;

        float median = max(min(r, g), min(max(r, g), b));
        float signed_dist = median - 0.5;
        float d = fwidth(signed_dist);

        float outlineFactor = step(0.0, unib[3][2]) * smoothstep(unib[3][2] - d, unib[3][2] + d, signed_dist);

        vec3 color = mix(unib[4], unib[1], outlineFactor);

        float opacity = smoothstep(-d, d, signed_dist);

        return vec4(color, opacity);
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
