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

gl_FragColor.rgb = vec3(
    texture2D(tex0, vec2(rgbUvX + rgbDiff, coords.y) + shake).r,
    texture2D(tex0, vec2(rgbUvX, coords.y) + shake).g,
    texture2D(tex0, vec2(rgbUvX - rgbDiff, coords.y) + shake).b
);
