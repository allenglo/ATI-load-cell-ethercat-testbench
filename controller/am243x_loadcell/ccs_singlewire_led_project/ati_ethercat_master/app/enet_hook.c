#include <networking/enet/core/include/enet.h>
#include <networking/enet/core/include/per/cpsw.h>
#include <networking/enet/core/include/core/enet_dma.h>

/*
 * SysConfig-generated open/close expects this hook.
 * Keep default CPSW init settings unchanged.
 */
void EnetApp_updateCpswInitCfg(Enet_Type enetType, uint32_t instId, Cpsw_Cfg *cpswCfg)
{
    EnetDma_Cfg *dmaCfg;

    (void)enetType;
    (void)instId;

    if (cpswCfg == NULL)
    {
        return;
    }

    /* Match TI L2 CPSW example behavior for CPDMA host-port operation. */
    dmaCfg = (EnetDma_Cfg *)cpswCfg->dmaCfg;
    if (dmaCfg != NULL)
    {
        dmaCfg->enChOverrideFlag = true;
    }
}
