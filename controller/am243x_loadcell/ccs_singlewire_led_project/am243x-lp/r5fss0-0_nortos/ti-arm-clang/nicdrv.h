/* SOEM NIC driver header for AM243x CPSW */
#ifndef _nicdrvh_
#define _nicdrvh_

#ifdef __cplusplus
extern "C" {
#endif

#include "soem/ec_type.h"

/* pointer structure to Tx and Rx stacks */
typedef struct
{
   void *sock;
   ec_bufT (*txbuf)[EC_MAXBUF];
   int (*txbuflength)[EC_MAXBUF];
   ec_bufT *tempbuf;
   ec_bufT (*rxbuf)[EC_MAXBUF];
   int (*rxbufstat)[EC_MAXBUF];
   int (*rxsa)[EC_MAXBUF];
   uint64 rxcnt;
} ec_stackT;

typedef struct
{
   ec_stackT stack;
   int sockhandle;
   ec_bufT rxbuf[EC_MAXBUF];
   int rxbufstat[EC_MAXBUF];
   int rxsa[EC_MAXBUF];
   ec_bufT tempinbuf;
} ecx_redportt;

typedef struct
{
   ec_stackT stack;
   int sockhandle;
   ec_bufT rxbuf[EC_MAXBUF];
   int rxbufstat[EC_MAXBUF];
   int rxsa[EC_MAXBUF];
   ec_bufT tempinbuf;
   int tempinbufs;
   ec_bufT txbuf[EC_MAXBUF];
   int txbuflength[EC_MAXBUF];
   ec_bufT txbuf2;
   int txbuflength2;
   uint8 lastidx;
   int redstate;
   ecx_redportt *redport;
   void *getindex_mutex;
   void *tx_mutex;
   void *rx_mutex;
} ecx_portt;

extern const uint16 priMAC[3];
extern const uint16 secMAC[3];

void ec_setupheader(void *p);
int ecx_setupnic(ecx_portt *port, const char *ifname, int secondary);
int ecx_closenic(ecx_portt *port);
void ecx_setbufstat(ecx_portt *port, uint8 idx, int bufstat);
uint8 ecx_getindex(ecx_portt *port);
int ecx_outframe(ecx_portt *port, uint8 idx, int stacknumber);
int ecx_outframe_red(ecx_portt *port, uint8 idx);
int ecx_inframe(ecx_portt *port, int stacknumber, int timeout);
int ecx_waitinframe(ecx_portt *port, uint8 idx, int timeout);
int ecx_srconfirm(ecx_portt *port, uint8 idx, int timeout);

#ifdef __cplusplus
}
#endif

#endif
