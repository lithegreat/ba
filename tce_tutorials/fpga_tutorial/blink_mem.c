#include "tceops.h"

/*
 * Generic "sleep" function.
 */
void usleep(unsigned int us) {
    unsigned int counter = 1;
    /* this macro sets the counter to us (micro seconds) 
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

/*
 * Pattern lookup table
 */
volatile unsigned short int patterns[8] = {
    0x01, 0x02, 0x04, 0x08,
    0x10, 0x20, 0x40, 0x80
};

int main() {
    unsigned int sleep = 100000;
    int i = 0;

    while (1) {
        unsigned int pattern = patterns[i];
        _TCE_WRITE_LEDS(pattern);
        patterns[i] = pattern;
        i++;
        if (i > 7) {
            i = 0;
        }
        usleep(sleep);
    }
    return 0;
}
