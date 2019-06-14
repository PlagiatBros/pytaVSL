#include shaders/inc/vs_head.vs

void main(void) {

    #include shaders/inc/vs_main.vs

    #ifdef POST_PROCESS
    #include shaders/effects/warp.vs
    #endif

}
