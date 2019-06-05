vec2 charcoalRadius = unif[17][0] / resolution;
float charcoalThresh = unif[17][1];
float charcoalStrength = unif[17][2];

vec4 c1 = texture2D(tex0, coords);
vec4 c2 = texture2D(tex0, coords + vec2(charcoalRadius.x, 0));
vec4 c3 = texture2D(tex0, coords + vec2(0, charcoalRadius.y));
float f = distance(c1.rgb, c2.rgb) + distance(c1.rgb, c3.rgb) - charcoalThresh;
f *= charcoalStrength;
gl_FragColor.rgb = mix(vec3(1.0, 1.0, 1.0), vec3(0.0, 0.0, 0.0) - 0.5, f);
