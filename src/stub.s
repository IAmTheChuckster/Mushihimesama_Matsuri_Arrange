! ROM boot stub: runs from the u4 (uncached ROM address 0xA01FBE00), copies the patch
! image into free RAM and jumps to its patcher, which hooks the game and starts it.
        .text
        .align  2
stub:
        mov.l   Ls_src,r1
        mov.l   Ls_dst,r2
        mov.l   Ls_cnt,r3
1:      mov.l   @r1+,r0
        dt      r3
        mov.l   r0,@r2
        bf/s    1b
        add     #4,r2
        mov.l   Ls_dst,r0
        jmp     @r0
        nop
        .align  2
Ls_src: .long   0xA01FBE80
Ls_dst: .long   0x0C7C0000
Ls_cnt: .long   0               ! patched by build.py
