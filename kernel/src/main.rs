#![no_std]
#![no_main]

use core::arch::global_asm;

global_asm!(
    ".section .text._start",
    ".global _start",
    "_start:",
    "   b _start",
);

fn main() {
    let mut _x:i8 = 5;
}

#[panic_handler]
fn panic_handler(_info: &core::panic::PanicInfo)->!{
    loop{

    }
}