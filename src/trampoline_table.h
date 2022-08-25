#ifndef FFI_TRAMPOLINE_TABLE_H
#define FFI_TRAMPOLINE_TABLE_H

#include <mach/mach.h>

typedef struct ffi_trampoline_table ffi_trampoline_table;
typedef struct ffi_trampoline_table_entry ffi_trampoline_table_entry;

struct ffi_trampoline_table
{
  /* contiguous writable and executable pages */
  vm_address_t config_page;
  vm_address_t trampoline_page;
  int page_segment_offset;

  /* free list tracking */
  uint16_t free_count;
  ffi_trampoline_table_entry *free_list;
  ffi_trampoline_table_entry *free_list_pool;

  ffi_trampoline_table *prev;
  ffi_trampoline_table *next;
};

struct ffi_trampoline_table_entry
{
  void *(*trampoline) (void);
  ffi_trampoline_table_entry *next;
};

extern void *ffi_closure_trampoline_table_page;

#endif /* FFI_TRAMPOLINE_TABLE_H */
