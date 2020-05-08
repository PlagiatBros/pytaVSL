vec2 coords = vec2(ucoords.xy / ucoords.z);

#ifdef MASK
vec2 maskCoords = vec2(umaskCoords.xy / umaskCoords.z);
#endif
