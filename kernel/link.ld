ENTRY(_start)

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