float waveStrength = unif[16][0];
float waveRand = unif[12][0];


float relativeY = coords.y * resolution.y;

vec2 shake = waveStrength * vec2(waveStrength * 8.0 + 0.5) * vec2(
  random(vec2(waveRand)) * 2.0 - 1.0,
  random(vec2(waveRand*2.0)) * 2.0 - 1.0
) / resolution;

float rgbWave = waveStrength * (
      snoise(vec2(relativeY * 0.01, waveRand * 400.0)) * (2.0 + waveStrength * 32.0)
      * snoise(vec2(relativeY * 0.02, waveRand * 200.0)) * (1.0 + waveStrength * 4.0)
      + step(0.9995, sin(relativeY * 0.005 + waveRand * 1.6)) * 12.0
      + step(0.9999, sin(relativeY * 0.005 + waveRand * 2.0)) * -18.0
  ) / resolution.x;
float rgbDiff = waveStrength * 2.0 * (6.0 + sin(waveRand * 500.0 + coords.y * 40.0) * (20.0 * waveStrength + 1.0)) / resolution.x;
float rgbUvX = coords.x + rgbWave;

vec2 gc1 = vec2(rgbUvX + rgbDiff, coords.y) + shake;
vec2 gc2 = vec2(rgbUvX, coords.y) + shake;
vec2 gc3 = vec2(rgbUvX - rgbDiff, coords.y) + shake;

vec4 gl1 = tex2D(tex0, gc1);
vec4 gl2 = tex2D(tex0, gc2);
vec4 gl3 = tex2D(tex0, gc3);

#ifdef TEXT
gl1.a *= step(abs(gc1.x-0.5)/unib[2].x, 0.5);
gl3.a *= step(abs(gc1.x-0.5)/unib[2].x, 0.5) * step(abs(gc1.y-0.5)/unib[2].y, 0.5);
#endif

gl_FragColor.rgba = vec4(
    gl1.r,
    gl2.g,
    gl3.b,
    min(vec3(gl1.a, gl2.a, gl3.a), 1.0)
);
