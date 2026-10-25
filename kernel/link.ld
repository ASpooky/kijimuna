ENTRY(_start)

 /* ref: https://sourceware.org/binutils/docs/ld/Scripts.html */

SECTIONS
{
    . = 0x80000;

    .text : {
        KEEP(*(.text._start))
        *(.text .text.*)
    }
    .rodata : { *(.rodata .rodata.*)}
    .data : {*(.data .data.*)}
    .bss : {*(.bss .bss.*)}
}