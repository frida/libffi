ffi_h_conf = configuration_data()
ffi_h_conf.set('VERSION', meson.project_version())
ffi_h_conf.set('FFI_VERSION_STRING', meson.project_version())
version_components = meson.project_version().split('.')
ffi_h_conf.set('FFI_VERSION_NUMBER',
  version_components[0].to_int() * 10000 + version_components[1].to_int() * 100 + version_components[2].to_int())
ffi_h_conf.set('FFI_EXEC_TRAMPOLINE_TABLE', ffi_conf.get('FFI_EXEC_TRAMPOLINE_TABLE', 0))
ffi_h_conf.set('HAVE_LONG_DOUBLE', ffi_conf.get('HAVE_LONG_DOUBLE', 0))
ffi_h_conf.set('TARGET', target)

configure_file(input : 'ffi.h.in',
  output : 'ffi.h',
  configuration : ffi_h_conf,
  install_dir : get_option('includedir'))

install_headers(f'../src/@targetdir@/ffitarget.h')
