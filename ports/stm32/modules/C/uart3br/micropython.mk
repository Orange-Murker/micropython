UART3BR_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(UART3BR_MOD_DIR)/uart3br.c

# We can add our module folder to include paths if needed
# This is not actually needed in this example.
CFLAGS_USERMOD += -I$(UART3BR_MOD_DIR)

CFLAGS_EXTRA += -DMODULE_UART3BR_ENABLED=1