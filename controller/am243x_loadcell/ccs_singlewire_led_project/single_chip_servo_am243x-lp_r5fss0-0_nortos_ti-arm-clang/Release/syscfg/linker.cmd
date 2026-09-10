

 /* This is the stack that is used by code running within main()
  * In case of NORTOS,
  * - This means all the code outside of ISR uses this stack
  * In case of FreeRTOS
  * - This means all the code until vTaskStartScheduler() is called in main()
  *   uses this stack.
  * - After vTaskStartScheduler() each task created in FreeRTOS has its own stack
  */

 --stack_size=16384
/* This is the heap size for malloc() API in NORTOS and FreeRTOS
* This is also the heap used by pvPortMalloc in FreeRTOS
*/
 --heap_size=32768
-e_vectors  /* This is the entry of the application, _vector MUST be placed starting address 0x0 */

/* This is the size of stack when R5 is in IRQ mode
 * In NORTOS,
 * - Here interrupt nesting is enabled
 * - This is the stack used by ISRs registered as type IRQ
 * In FreeRTOS,
 * - Here interrupt nesting is enabled
 * - This is stack that is used initally when a IRQ is received
 * - But then the mode is switched to SVC mode and SVC stack is used for all user ISR callbacks
 * - Hence in FreeRTOS, IRQ stack size is less and SVC stack size is more
 */
__IRQ_STACK_SIZE = 8192;
/* This is the size of stack when R5 is in IRQ mode
 * - In both NORTOS and FreeRTOS nesting is disabled for FIQ
 */
__FIQ_STACK_SIZE = 256;
__SVC_STACK_SIZE = 8192; /* This is the size of stack when R5 is in SVC mode */
__ABORT_STACK_SIZE = 256;  /* This is the size of stack when R5 is in ABORT mode */
__UNDEFINED_STACK_SIZE = 256;  /* This is the size of stack when R5 is in UNDEF mode */



SECTIONS
{
    .vectors  : {
    } > R5F_VECS   , palign(8) 


    GROUP  :   {
    .text.hwi : {
    } palign(8)
    .text.cache : {
    } palign(8)
    .text.mpu : {
    } palign(8)
    .text.boot : {
    } palign(8)
    .text:abort : {
    } palign(8)
    } > MSRAM_0_0  


    GROUP  :   {
    .text : {
    } palign(8)
    .rodata : {
    } palign(8)
    } > MSRAM_0_0  


    GROUP  :   {
    .data : {
    } palign(8)
    } > MSRAM_0_0  


    GROUP  :   {
    .bss : {
    } palign(8)
    RUN_START(__BSS_START)
    RUN_END(__BSS_END)
    .sysmem : {
    } palign(8)
    .stack : {
    } palign(8)
    } > MSRAM_0_0  


    GROUP  :   {
    .irqstack : {
        . = . + __IRQ_STACK_SIZE;
    } align(8)
    RUN_START(__IRQ_STACK_START)
    RUN_END(__IRQ_STACK_END)
    .fiqstack : {
        . = . + __FIQ_STACK_SIZE;
    } align(8)
    RUN_START(__FIQ_STACK_START)
    RUN_END(__FIQ_STACK_END)
    .svcstack : {
        . = . + __SVC_STACK_SIZE;
    } align(8)
    RUN_START(__SVC_STACK_START)
    RUN_END(__SVC_STACK_END)
    .abortstack : {
        . = . + __ABORT_STACK_SIZE;
    } align(8)
    RUN_START(__ABORT_STACK_START)
    RUN_END(__ABORT_STACK_END)
    .undefinedstack : {
        . = . + __UNDEFINED_STACK_SIZE;
    } align(8)
    RUN_START(__UNDEFINED_STACK_START)
    RUN_END(__UNDEFINED_STACK_END)
    } > MSRAM_0_0  


    GROUP  :   {
    .ARM.exidx : {
    } palign(8)
    .init_array : {
    } palign(8)
    .fini_array : {
    } palign(8)
    } > MSRAM_0_0  

    .bss.user_shared_mem (NOLOAD) : {
    } > USER_SHM_MEM    

    .bss.log_shared_mem (NOLOAD) : {
    } > LOG_SHM_MEM    

    .bss.ipc_vring_mem (NOLOAD) : {
    } > RTOS_NORTOS_IPC_SHM_MEM    

    .gSddfChSampsRaw  : {
    } > R5F_TCMB0_SDDF_0_0   , align(4) 

    .gTxDataSection  : {
    } > R5F_TCMB0_PDO   , align(4) 

    .gRxDataSection  : {
    } > OTHER_R5F_TCMB0_PDO   , align(4) 

    .gDebugBuff1  : {
    } > MSRAM1   , align(4) 

    .gDebugBuff2  : {
    } > MSRAM2   , align(4) 

    .gEnDatChInfo  : {
    } > R5F_TCMB0_ENC_0_0   , align(4) 

    .critical_code  : {
    } > R5F_TCMB0   , palign(4) 

    .critical_data  : {
    } > R5F_TCMB0   , palign(8) 

    .gCtrlVars  : {
    } > MSRAM_CTRL_VARS_0_0   , palign(8) 

    .gSharedPrivStep  : {
    } > USER_SHM_MEM   , palign(8) 

    .gSharedPruHandle  : {
    } > USER_SHM_MEM   , palign(8) 

    .gEtherCatCia402  : {
    } > MSRAM_NO_CACHE   , palign(4) 


}


MEMORY
{
    R5F_VECS   : ORIGIN = 0x0 , LENGTH = 0x40 
    R5F_TCMA   : ORIGIN = 0x40 , LENGTH = 0x7FC0 
    R5F_TCMB0_SDDF_0_0   : ORIGIN = 0x41010000 , LENGTH = 0x80 
    R5F_TCMB0_ENC_0_0   : ORIGIN = 0x41010100 , LENGTH = 0x100 
    R5F_TCMB0_PDO   : ORIGIN = 0x41010200 , LENGTH = 0x100 
    R5F_TCMB0   : ORIGIN = 0x41010300 , LENGTH = 0x7D00 
    MSRAM_0_0   : ORIGIN = 0x70140000 , LENGTH = 0x40000 
    MSRAM_CTRL_VARS_0_0   : ORIGIN = 0x701BFE00 , LENGTH = 0x100 
    MSRAM1   : ORIGIN = 0x70040000 , LENGTH = 0x40000 
    MSRAM2   : ORIGIN = 0x70080000 , LENGTH = 0x40000 
    MSRAM_NO_CACHE   : ORIGIN = 0x701C0000 , LENGTH = 0x100 
    USER_SHM_MEM   : ORIGIN = 0x701D0000 , LENGTH = 0x4000 
    LOG_SHM_MEM   : ORIGIN = 0x701D4000 , LENGTH = 0x4000 
    RTOS_NORTOS_IPC_SHM_MEM   : ORIGIN = 0x701D8000 , LENGTH = 0x8000 
    OTHER_R5F_TCMB0_PDO   : ORIGIN = 0x78500000 , LENGTH = 0x100 

    /* For memory Regions not defined in this core but shared by other cores with the current core */


}
