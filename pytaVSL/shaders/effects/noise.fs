float noise_rand(vec2 co){
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

vec3 add_noise(vec3 fragColor, float time, float density) {
    float noise = noise_rand(coords+0.07*fract(time));
    return fragColor.rgb +vec3(density * noise);
}
