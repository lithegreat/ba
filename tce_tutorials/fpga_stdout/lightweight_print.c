/** 
 * Simple example program to demonstrate how to use light weight printing
 * routines (lwpr) with TCE.
 * Remember to compile with -llwpr flag in order to include the printing 
 * library
 */
#include "lwpr.h"

int main() {

    volatile unsigned int timestamp;

    /* Clear RTC and timestamp */
    _TCE_RTC(0, timestamp);
    timestamp = 0;
    
    lwpr_print_str("Hello World!\n");
    
    _TCE_RTC(1, timestamp);
    lwpr_print_str("Printing Hello World took ");
    lwpr_print_int(timestamp);
    lwpr_print_str(" ms.\n");
    
    return 0;
}
