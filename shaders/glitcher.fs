#include std_head_fs.inc
#include shaders/random.inc

vec3 rgb2hsv(vec3 c)
{
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

varying vec2 texcoordout;
const vec2 resolution = vec2(800.0, 600.0);

void main(void){

  float randomseed = unif[15][0];

  float noise_amount = unif[18][1];
  float strength = unif[18][2];

  float hue = unif[16][0];
  float saturation = unif[16][1];
  float value = unif[16][2];
  float alpha = unif[17][0];
  float invert = unif[17][1];

  vec2 shake = vec2(strength * 8.0 + 0.5) * vec2(
    random(vec2(randomseed)) * 2.0 - 1.0,
    random(vec2(randomseed*2.0)) * 2.0 - 1.0
  ) / resolution;

  float y = texcoordout.y * resolution.y;
  float rgbWave = (
        snoise(vec2(y * 0.01, randomseed * 400.0)) * (2.0 + strength * 32.0)
        * snoise(vec2(y * 0.02, randomseed * 200.0)) * (1.0 + strength * 4.0)
        + step(0.9995, sin(y * 0.005 + randomseed * 1.6)) * 12.0
        + step(0.9999, sin(y * 0.005 + randomseed * 2.0)) * -18.0
    ) / resolution.x;
  float rgbDiff = (6.0 + sin(randomseed * 500.0 + texcoordout.y * 40.0) * (20.0 * strength + 1.0)) / resolution.x;
  float rgbUvX = texcoordout.x + rgbWave;
  float r = texture2D(tex0, vec2(rgbUvX + rgbDiff, texcoordout.y) + shake).r;
  float g = texture2D(tex0, vec2(rgbUvX, texcoordout.y) + shake).g;
  float b = texture2D(tex0, vec2(rgbUvX - rgbDiff, texcoordout.y) + shake).b;


  vec2 fcoord = vec2(0.0, 0.0);
  float f[7];
  float nr = texture2D(tex0, texcoordout * randomseed * vec2(rgbWave * resolution.x)).b * step(1.0 - noise_amount, random(vec2(randomseed,2))) ;
  float nb = texture2D(tex0, texcoordout * texcoordout * texcoordout * (randomseed+0.5)).g * step(1.0 - noise_amount, random(vec2(randomseed,3)));
  vec3 noisetex = vec3(nr, 0.0, nb) * 0.75 * noise_amount;

  vec3 result = noisetex +  vec3(r, g, b);

  // color offset
  invert = step(1.0, invert);

  for (int i=0; i<3; i+=1) {
      result[i] = result[i] * (1.0 - invert) + abs(1.0 - result[i]) * invert;
  }


  vec3 hsv = rgb2hsv(vec3(result.r, result.g, result.b));
  hsv[0] = abs(hsv[0] + hue);
  hsv[1] = hsv[1] * saturation;
  hsv[2] = hsv[2] * value;
  vec3 rgb = hsv2rgb(hsv);


  gl_FragColor = vec4(rgb.r, rgb.g, rgb.b, alpha);

}
