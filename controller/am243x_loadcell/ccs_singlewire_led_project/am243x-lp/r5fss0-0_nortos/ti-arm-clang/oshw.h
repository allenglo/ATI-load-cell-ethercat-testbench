/*
 * SOEM oshw header for AM243x
 * Byte-swap and adapter-list stubs.
 */
#ifndef _oshw_am243x_
#define _oshw_am243x_

#ifdef __cplusplus
extern "C" {
#endif

#include "soem/soem.h"
#include "nicdrv.h"

uint16 oshw_htons(uint16 hostshort);
uint16 oshw_ntohs(uint16 networkshort);
ec_adaptert *oshw_find_adapters(void);
void oshw_free_adapters(ec_adaptert *adapter);

#ifdef __cplusplus
}
#endif

#endif /* _oshw_am243x_ */
