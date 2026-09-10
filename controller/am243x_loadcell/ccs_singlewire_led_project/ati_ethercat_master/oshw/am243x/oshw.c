/*
 * SOEM oshw implementation for AM243x
 *
 * byte-swap helpers + stub adapter discovery (single fixed CPSW port).
 */
#include "oshw.h"
#include "osal.h"
#include <string.h>
#include <stdlib.h>

uint16 oshw_htons(uint16 hostshort)
{
    return (uint16)(((hostshort & 0x00FFU) << 8U) |
                    ((hostshort & 0xFF00U) >> 8U));
}

uint16 oshw_ntohs(uint16 networkshort)
{
    return oshw_htons(networkshort);
}

/* Return a single adapter entry so ec_find_adapters() works */
ec_adaptert *oshw_find_adapters(void)
{
    ec_adaptert *adapter = (ec_adaptert *)osal_malloc(sizeof(ec_adaptert));
    if (adapter)
    {
        memset(adapter, 0, sizeof(*adapter));
        strncpy(adapter->name, "cpsw0", EC_MAXLEN_ADAPTERNAME - 1U);
        strncpy(adapter->desc, "AM243x CPSW ENET", EC_MAXLEN_ADAPTERNAME - 1U);
        adapter->next = NULL;
    }
    return adapter;
}

void oshw_free_adapters(ec_adaptert *adapter)
{
    ec_adaptert *p = adapter;
    while (p)
    {
        ec_adaptert *next = p->next;
        osal_free(p);
        p = next;
    }
}
