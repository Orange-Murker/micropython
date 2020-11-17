# Dummy modules
freeze('$(MPY_DIR)/ports/windows/modules/python')

# Include os.path
freeze('$(MPY_DIR)/ports/windows/modules', 'os/path.py')

# Include runpy (disabled now, did not work well enough)
#freeze('$(MPY_DIR)/ports/windows/modules', 'runpy.py')
