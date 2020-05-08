// brightness, contrast, saturation
// from https://github.com/genekogan/Processing-Shader-Examples

const vec3 LumCoeff = vec3(0.2125, 0.7154, 0.0721);
const vec3 AvgLumin = vec3(0.5, 0.5, 0.5);

vec3 adjustBCS(vec3 frag, float brightness, float contrast, float saturation)
{

	vec3 texColor = frag.rgb;

 	vec3 intensity = vec3(dot(texColor, LumCoeff));
	vec3 satColor = mix(intensity, texColor, saturation);
 	vec3 conColor = mix(AvgLumin, satColor, contrast);

	return vec3(brightness * conColor);

}

// hue
// from https://github.com/msfeldstein/ofxHueShift

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


vec3 adjustHue(vec3 frag, float shift)
{

	vec3 hsv = rgb2hsv(frag);

	hsv.x += mod(shift, 1.0);
	hsv.x = mod(hsv.r, 1.0);

	return hsv2rgb(hsv);

}
