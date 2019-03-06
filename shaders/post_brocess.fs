#include std_head_fs.inc

varying vec2 texcoordout;

void main(void) {

  vec4 texc = vec4(0.0, 0.0, 0.0, 1.0);

  float random = unif[15][0];

  float shift_x = unif[16][0]; // 48
  float shift_y = unif[16][1]; // 49

  int glitch_x = 9 - int(9.0 * unif[17][0]); // 51
  int glitch_y = 9 - int(9.0 * unif[17][1]); // 52
  int glitch_c = 9 - int(9.0 * unif[17][2]); // 53

  float c_off = unif[18][0]; // 54
  float alpha = unif[18][1]; // 55
  float rgb = unif[18][2];   // 56

  float f[9];  // factors

  f[0] =  1.0; f[1] = -1.0;  f[2] =  1.0;
  f[3] = -1.0; f[4] =  1.0;  f[5] = -1.0;
  f[6] =  1.0; f[7] = -1.0;  f[8] =  1.0;


  // glitched matrices (not fully unninitialized)
  float dx[9];
  float dy[9];
  float _[9];

  for (int i=0; i < glitch_x; i+=1) {
    dx[i] = 0.0;
  }
  for (int i=0; i < glitch_y; i+=1) {
    dy[i] = 0.0;
  }


  // texc += texture2D(tex0, texcoordout);

  vec2 fcoord = vec2(0.0, 0.0);
  for (int i=0; i<9; i+=1) {
      // xy glitch
      fcoord = (texcoordout + vec2(dx[i] + _[i] * shift_x * random, dy[i] + _[i] * shift_y * random));
      texc += texture2D(tex0, fcoord) * f[i];
  }

  // color offset
  for (int i=0; i<3; i+=1) {
      texc[i] = abs(texc[i]-c_off);
  }

  // rgb split
  if (rgb > 0.0) {
    texc += texture2D(tex0, fcoord+vec2(rgb*(random+0.5),0.0)) * vec4(1.0,0.0,0.0,texc[3]);
    texc += texture2D(tex0, fcoord-vec2(rgb*(random+0.5),0.0)) * vec4(0.0,0.5,0.5,texc[3]);
  }


  texc[3] = texc[3]*alpha;

  gl_FragColor = texc;

}
