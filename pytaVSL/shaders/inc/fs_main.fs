#ifdef WARP
#include shaders/effects/warp.fs
#endif

#ifdef FISH
#include shaders/effects/fish.fs
#endif

// Assign texture coords to output
gl_FragColor = tex2D(tex0, coords);

// Apply alpha
gl_FragColor.a = gl_FragColor.a * unif[5][2];


#ifdef RGBWAVE
#include shaders/effects/rgbwave.fs
#endif

#ifdef CHARCOAL
#include shaders/effects/charcoal.fs
#endif

#ifdef BLUR
gl_FragColor.rgb = add_blur(gl_FragColor.rgb, unif[18][0]);
#endif

#ifdef VIDEO
gl_FragColor.rgb = gl_FragColor.bgr;
#endif

#ifdef NOISE
gl_FragColor.rgb = add_noise(gl_FragColor.rgb, unif[12][1], unif[15][1]);
#endif

#ifdef KEY
#include shaders/effects/key.fs
#endif

#ifndef TEXT
#include shaders/effects/colorize.fs
#endif

#ifdef COLORS
gl_FragColor.rgb = adjustBCS(gl_FragColor.rgb, unif[17][0], unif[17][1], unif[17][2]);
gl_FragColor.rgb = adjustHue(gl_FragColor.rgb, unif[16][2]);
#endif

#ifdef INVERT
#include shaders/effects/invert.fs
#endif

#ifdef MASK
#include shaders/effects/mask.fs
#endif
