// This is done in C because I can't think of a way to implement interrupt handlers in python
// Everything else was done in python :)

#include "luna_dma.h"

#include "py/runtime.h"
#include "py/gc.h"

// Set to 32 bytes for now to make sure we are aligned with the cache line size
#define DMA_TRANSFER_SIZE 32
#define SRAM1 0x30000000

// This function will be called when a DMA interrupt occurs and call the python function
void Handle_DMA_IT() {
    mp_obj_t* callback = &MP_STATE_PORT(luna_dma_callback);

    if (*callback == mp_const_none) {
        return;
    }

    // React to transfer complete interrupt
    if (DMA1->LISR & 1 << 11) {
        DMA1->LIFCR |= 1 << 11;

        // Invalidate the data cache before calling the function to avoid cache coherency issues
        SCB_InvalidateDCache_by_Addr((unsigned int*) SRAM1, DMA_TRANSFER_SIZE);

        // Adapted from extint.c
        mp_sched_lock();
        // When executing code within a handler we must lock the GC to prevent
        // any memory allocations.  We must also catch any exceptions.
        gc_lock();
        nlr_buf_t nlr;
        if (nlr_push(&nlr) == 0) {
            mp_call_function_0(*callback);
            nlr_pop();
        } else {
            // Uncaught exception; disable the callback, so it doesn't run again.
            callback = mp_const_none;
            mp_printf(MICROPY_ERROR_PRINTER, "uncaught exception in Luna DMA interrupt handler\n");
            mp_obj_print_exception(&mp_plat_print, MP_OBJ_FROM_PTR(nlr.ret_val));
        }
        gc_unlock();
        mp_sched_unlock();
    } else {
        mp_printf(MICROPY_ERROR_PRINTER, "Unknown interrupt status %X\n", DMA1->LISR);
    }
}

STATIC mp_obj_t py_set_callback(mp_obj_t callback_obj) {
    if (mp_obj_is_callable(callback_obj)) {
        mp_obj_t* callback = &MP_STATE_PORT(luna_dma_callback);
        *callback = callback_obj;

        HAL_NVIC_EnableIRQ(DMA1_Stream1_IRQn);
        SCB_DisableDCache();
        SCB_DisableICache();
    } else {
        mp_printf(MICROPY_ERROR_PRINTER, "Could not set callback. Please check the type.\n");
    }

    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(luna_dma_set_callback_obj, py_set_callback);

STATIC const mp_rom_map_elem_t luna_dma_globals_table[] = {
        {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_luna_dma)},
        {MP_ROM_QSTR(MP_QSTR_set_callback), MP_ROM_PTR(&luna_dma_set_callback_obj)},
};
STATIC MP_DEFINE_CONST_DICT(luna_dma_globals, luna_dma_globals_table);

const mp_obj_module_t luna_dma_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t *) &luna_dma_globals,
};

MP_REGISTER_MODULE(MP_QSTR_luna_dma, luna_dma_module, 1);