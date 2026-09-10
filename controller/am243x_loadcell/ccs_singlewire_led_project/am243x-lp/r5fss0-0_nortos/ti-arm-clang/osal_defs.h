/*
 * SOEM OSAL definitions for AM243x FreeRTOS
 *
 * ec_timet mirrors struct timespec so that SOEM internals and samples that
 * access .tv_sec / .tv_nsec compile without modification.
 * Internally we drive everything from ClockP_getTimeUsec() (microseconds)
 * and convert to seconds + nanoseconds.
 */
#ifndef _osal_defs_
#define _osal_defs_

#include <stdint.h>

/* -----------------------------------------------------------------------
 * ec_timet — same layout as struct timespec so SOEM code compiles as-is.
 * ----------------------------------------------------------------------- */
typedef struct
{
    int64_t tv_sec;     /* seconds */
    int64_t tv_nsec;    /* nanoseconds */
} ec_timet;

/* -----------------------------------------------------------------------
 * Build an ec_timet from a raw microsecond count (ClockP_getTimeUsec)
 * ----------------------------------------------------------------------- */
static inline ec_timet osal_usec_to_timet(uint64_t usec)
{
    ec_timet t;
    t.tv_sec  = (int64_t)(usec / 1000000ULL);
    t.tv_nsec = (int64_t)((usec % 1000000ULL) * 1000ULL);
    return t;
}

/* Convert ec_timet back to microseconds */
static inline uint64_t osal_timet_to_usec(const ec_timet *t)
{
    return (uint64_t)(t->tv_sec) * 1000000ULL
         + (uint64_t)(t->tv_nsec) / 1000ULL;
}

/* -----------------------------------------------------------------------
 * Arithmetic helpers used by osal.c
 * ----------------------------------------------------------------------- */
static inline void osal_timespecadd(const ec_timet *a, const ec_timet *b, ec_timet *out)
{
    int64_t nsec = a->tv_nsec + b->tv_nsec;
    out->tv_sec  = a->tv_sec  + b->tv_sec + (nsec / 1000000000LL);
    out->tv_nsec = nsec % 1000000000LL;
}

static inline void osal_timespecsub(const ec_timet *end, const ec_timet *start, ec_timet *diff)
{
    int64_t nsec = end->tv_nsec - start->tv_nsec;
    if (nsec < 0)
    {
        diff->tv_sec  = end->tv_sec - start->tv_sec - 1;
        diff->tv_nsec = nsec + 1000000000LL;
    }
    else
    {
        diff->tv_sec  = end->tv_sec - start->tv_sec;
        diff->tv_nsec = nsec;
    }
}

/* Return 1 if a < b */
static inline int osal_timespeccmp(const ec_timet *a, const ec_timet *b)
{
    if (a->tv_sec  < b->tv_sec)  return  1;
    if (a->tv_sec  > b->tv_sec)  return -1;
    if (a->tv_nsec < b->tv_nsec) return  1;
    if (a->tv_nsec > b->tv_nsec) return -1;
    return 0;
}

/* Compile-time configuration macros expected by some SOEM headers */
#ifndef OSAL_PACKED
#define OSAL_PACKED_BEGIN
#define OSAL_PACKED __attribute__((__packed__))
#define OSAL_PACKED_END
#endif

#ifndef EC_PRINT
#define EC_PRINT(...) do { } while (0)
#endif

#define OSAL_THREAD_HANDLE  void *
#define OSAL_THREAD_FUNC    void
#define OSAL_THREAD_FUNC_RT void

typedef void *osal_mutext;

#endif /* _osal_defs_ */
