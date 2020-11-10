ffi_c_sources = [
  'prep_cif.c',
  'types.c',
  'raw_api.c',
  'java_raw_api.c',
  'closures.c',
]

ffi_asm_sources = []

if get_option('debug')
  ffi_c_sources += ['debug.c']
endif

if host_system == 'windows'
  # No ARM support for Windows in libffi
  arch_subdir = 'x86'
  if size_t == 4
    TARGET = 'X86_WIN32'
    if cc.get_id() == 'msvc'
      ffi_c_sources += ['x86/ffiold-msvc.c']
      ffi_asm_sources += ['x86/win32_msvc.S']
    else
      ffi_c_sources += ['x86/ffi.c']
      ffi_asm_sources += ['x86/sysv.S']
    endif
  else
    TARGET = 'X86_WIN64'
    ffi_c_sources += ['x86/ffiw64.c']
    if cc.get_id() == 'msvc'
      ffi_asm_sources += ['x86/win64_intel.S']
    else
      ffi_asm_sources += ['x86/win64.S']
    endif
  endif
else
  if host_cpu_family.startswith('x86')
    arch_subdir = 'x86'
    # FIXME: gnux32 support?
    if size_t == 4
      if host_system == 'darwin'
        TARGET = 'X86_DARWIN'
      else
        TARGET = 'X86'
      endif
      ffi_c_sources += ['x86/ffi.c']
      ffi_asm_sources += ['x86/sysv.S']
    else
      TARGET = 'X86_64'
      ffi_c_sources += ['x86/ffi64.c', 'x86/ffiw64.c']
      ffi_asm_sources += ['x86/unix64.S', 'x86/win64.S']
    endif
  elif host_cpu_family == 'arm'
    arch_subdir = 'arm'
    TARGET = 'ARM'
    ffi_c_sources += ['arm/ffi.c']
    ffi_asm_sources += ['arm/sysv.S']
  elif host_cpu_family == 'aarch64'
    arch_subdir = 'aarch64'
    TARGET = 'AARCH64'
    ffi_c_sources += ['aarch64/ffi.c']
    ffi_asm_sources += ['aarch64/sysv.S']
  elif host_cpu_family == 'mips'
    arch_subdir = 'mips'
    TARGET = 'MIPS'
    ffi_c_sources += ['mips/ffi.c']
    ffi_asm_sources += ['mips/o32.S', 'mips/n32.S']
  else
    error('Unsupported cpu family "@0@"'.format(host_cpu_family))
  endif
endif

if host_cpu_family.startswith('x86')
endif

# Used in ffi.h.in to generate ffi-$arch.h
ffi_conf.set('TARGET', TARGET)

ffi_conf.set10('STATIC', get_option('default_library') == 'static')

if cc.get_id() == 'msvc'
  # GCC and Clang accept assembly files directly, but MSVC's cl.exe does not.
  # You need to manually pass the files through the pre-processor first and
  # then through the assembler, and then link the objects into the target.
  # FIXME: Add native support in Meson for this.
  cl = find_program('cl')
  ml = find_program('ml', 'ml64')

  ffi_asm_objs = []

  mlflags = []
  if size_t == 4
    mlflags += '/safeseh'
  endif

  foreach asm_source : ffi_asm_sources
    incflags = ['/I' + join_paths(meson.current_source_dir(), '..'),
                '/I' + join_paths(meson.current_build_dir(), '..'),
                '/I' + join_paths(meson.current_source_dir(), '..', 'include'),
                '/I' + join_paths(meson.current_build_dir(), '..', 'include')]

    preproc_name = asm_source.underscorify() + '.i'
    obj_name = asm_source.underscorify() + '.obj'
    preproc = custom_target(preproc_name,
        input : asm_source,
        output : preproc_name,
        command : [cl, '/nologo', '/EP', '/P', '/Fi@OUTPUT@',
                   '/DTARGET=' + TARGET, '/DFFI_BUILDING',
                   '@INPUT@'] + incflags)
    ffi_asm_objs += custom_target(obj_name,
        input : preproc,
        output : obj_name,
        command : [ml] + mlflags + ['/Fo', '@OUTPUT@', '/c', '@INPUT@'])
  endforeach

  ffi_asm_sources = ffi_asm_objs
endif

ffi_lib = library('ffi', ffi_c_sources, ffi_asm_sources,
  c_args : '-DTARGET=' + TARGET,
  include_directories : ffiinc,
  # Taken from the libtool-version file
  # current - age . age . revision
  version : '7.1.0',
  # current - age
  soversion : '7',
  install : true)

ffi_dep = declare_dependency(link_with : ffi_lib,
  include_directories : ffiinc)
