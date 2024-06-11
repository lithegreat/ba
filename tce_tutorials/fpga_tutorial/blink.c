#include "tceops.h"

/*
 * Generic "sleep" function. This function will block execution until sleep
 * time is over.
 * Parameter us tells the sleep time in microseconds.
 */
void usleep(unsigned int us) {
    unsigned int counter = 1;
    /* this operation macro sets the counter to 'us' micro seconds
     * Return value (=counter) has no meaning here, it's just dummy value
     * so that the compiler won't complain */
    _TCE_RTIMER(us, counter);
    counter = 1;
    /* wait until counter reaches zero */
    while (counter != 0) {
        /* When you trigger this operation with 0, it returns the current
        * counter value. */
        _TCE_RTIMER(0, counter);
    }      
}

int main() {
    unsigned int sleep = 100000;
    unsigned int pattern = 0x01;

    while (1) {
        _TCE_WRITE_LEDS(pattern);
        pattern <<= 1;
        if (pattern > 0x80) {
            pattern = 0x01;
        }
        usleep(sleep);
    }
    return 0;
}
