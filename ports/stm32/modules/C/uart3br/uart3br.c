// Include required definitions first.
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"

// Endianness swap of integers
#define SWAP(n) ((unsigned long) (((n & 0xFF) << 24) | \
                                          ((n & 0xFF00) << 8) | \
                                          ((n & 0xFF0000) >> 8) | \
                                          ((n & 0xFF000000) >> 24)))

// This is the function which will be called from Python as bruart.add_ints(a, b).
STATIC mp_obj_t send(mp_obj_t in_obj) {
    // Union to save data and send raw as un.u
    union {
        float f;
        unsigned int u;
    } un = {.u = 0};

    // Get type
    if mp_obj_is_int(in_obj){
        un.u = SWAP(mp_obj_get_int(in_obj));
    } else if mp_obj_is_float(in_obj){
        un.f = (float)mp_obj_get_float(in_obj);
    } else {
        mp_raise_TypeError(MP_ERROR_TEXT("Not an integer or float"));
    }
    
    // UART3 registers
    // Increment of 1 to such an adress means four bytes/32 bits since stm32 is directly 32 bits addressable only
    #define REG_USART3_ISR ((volatile unsigned int *) 0x4000481C)
    #define REG_USART3_CR1 ((volatile unsigned int *) 0x40004800)

    // Exchange adress and buffer length in doublewords
    #define REG ((volatile unsigned int *) 0x30040000)
    #define REG_L 16

    // Place argument in circular buffer at n
    *(REG + 2 + (*(REG + 1))/4) = un.u;

    // Increment n
    *(REG + 1) = (*(REG + 1) + 4) % (4 * REG_L);

    // Set TC IRQ (if not already set) to go to IRQ after transfer complete
    *REG_USART3_CR1 |= (1 << 6);

    // If there is no transmission going on, enable the TXE IRQ and immediately go to IRQ
    if (*REG_USART3_ISR && (1 << 7) ){
        *REG_USART3_CR1 |= (1 << 7);
    }

    // Return none object
    return mp_const_none;
}
// Define a Python reference to the function above
STATIC MP_DEFINE_CONST_FUN_OBJ_1(send_obj, send);

// Define all properties of the bruart module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t uart3br_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_uart3br) },
    { MP_ROM_QSTR(MP_QSTR_send), MP_ROM_PTR(&send_obj) },
};
STATIC MP_DEFINE_CONST_DICT(uart3br_module_globals, uart3br_module_globals_table);

// Define module object.
const mp_obj_module_t uart3br_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&uart3br_module_globals,
};

// Register the module to make it available in Python
MP_REGISTER_MODULE(MP_QSTR_uart3br, uart3br_user_cmodule, MODULE_UART3BR_ENABLED);