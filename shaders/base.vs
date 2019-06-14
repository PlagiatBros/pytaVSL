#include shaders/inc/vs_head.vs

void main(void) {

    #include shaders/inc/vs_main.vs

    #ifdef WARP
    #include shaders/effects/warp.vs
    #endif

}
