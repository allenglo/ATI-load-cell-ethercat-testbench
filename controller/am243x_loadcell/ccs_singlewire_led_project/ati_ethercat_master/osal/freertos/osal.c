/*
 * SOEM OSAL implementation for AM243x FreeRTOS
 *
 * Implements the functions SOEM requires from the OS abstraction layer,
 * mapped to TI DPL (Driver Porting Layer) and FreeRTOS primitives.
 *
 * ec_timet is a {tv_sec, tv_nsec} struct (same layout as struct timespec).
 * ClockP_getTimeUsec() gives monotonic microseconds; we convert on each call.
 */
#include "osal.h"
#include <kernel/dpl/ClockP.h>
#include <kernel/dpl/TaskP.h>
#include <stdlib.h>
#include <string.h>

/* -----------------------------------------------------------------------
 * Time functions
 * ----------------------------------------------------------------------- */

void osal_get_monotonic_time(ec_timet *ts)
{
    *ts = osal_usec_to_timet(ClockP_getTimeUsec());
}

ec_timet osal_current_time(void)
{
    return osal_usec_to_timet(ClockP_getTimeUsec());
}

void osal_time_diff(ec_timet *start, ec_timet *end, ec_timet *diff)
{
    osal_timespecsub(end, start, diff);
}

void osal_timer_start(osal_timert *self, uint32 timeout_usec)
{
    ec_timet now, delta;
    osal_get_monotonic_time(&now);
    delta = osal_usec_to_timet((uint64_t)timeout_usec);
    osal_timespecadd(&now, &delta, &self->stop_time);
}

boolean osal_timer_is_expired(osal_timert *self)
{
    ec_timet now;
    osal_get_monotonic_time(&now);
    return osal_timespeccmp(&now, &self->stop_time, >=) ? TRUE : FALSE;
}

int osal_usleep(uint32 usec)
{
    if (usec >= 1000U)
    {
        /* ms-resolution sleep */
        ClockP_sleep(usec / 1000U);
        /* remaining sub-ms */
        uint32 rem = usec % 1000U;
        if (rem > 0U)
        {
            uint64_t deadline = ClockP_getTimeUsec() + rem;
            while (ClockP_getTimeUsec() < deadline) { /* spin */ }
        }
    }
    else
    {
        /* sub-ms: busy-spin */
        uint64_t deadline = ClockP_getTimeUsec() + usec;
        while (ClockP_getTimeUsec() < deadline) { /* spin */ }
    }
    return 0;
}

int osal_monotonic_sleep(ec_timet *ts)
{
    ec_timet now;
    ec_timet diff;
    osal_get_monotonic_time(&now);
    if (osal_timespeccmp(&now, ts, <))
    {
        osal_timespecsub(ts, &now, &diff);
        uint32 usec = (uint32)(diff.tv_sec * 1000000LL + diff.tv_nsec / 1000LL);
        osal_usleep(usec);
    }
    return 0;
}

/* -----------------------------------------------------------------------
 * Thread stubs (SOEM calls these; we create our own task externally)
 * ----------------------------------------------------------------------- */
int osal_thread_create(void *thandle, int stacksize, void *func, void *param)
{
    (void)thandle; (void)stacksize; (void)func; (void)param;
    return 0;   /* not used – master runs in caller's task */
}

int osal_thread_create_rt(void *thandle, int stacksize, void *func, void *param)
{
    (void)thandle; (void)stacksize; (void)func; (void)param;
    return 0;
}

/* -----------------------------------------------------------------------
 * Memory
 * ----------------------------------------------------------------------- */
void *osal_malloc(size_t size)
{
    return malloc(size);
}

void osal_free(void *ptr)
{
    free(ptr);
}

void *osal_mutex_create(void)
{
    /* Single-task master loop currently doesn't need a real mutex. */
    return osal_malloc(1U);
}

void osal_mutex_destroy(void *mutex)
{
    if (mutex)
    {
        osal_free(mutex);
    }
}

void osal_mutex_lock(void *mutex)
{
    (void)mutex;
}

void osal_mutex_unlock(void *mutex)
{
    (void)mutex;
}
