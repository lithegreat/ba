/** 
 * Simple example program to demonstrate how to use printf() with TCE.
 * Remember to compile with --swfp flag to add soft float routines required
 * by printf()
 */

#include <stdio.h>

int main() {

    volatile unsigned int timestamp;

    /* Clear RTC and timestamp */
    _TCE_RTC(0, timestamp);
    timestamp = 0;
    
    printf("Hello World!\n");
    
    _TCE_RTC(1, timestamp);
    printf("Printing Hello Worlds took %u ms.\n", timestamp);
    
    return 0;
}
