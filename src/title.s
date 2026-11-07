! Matsuri Arrange - title menu patch (SH-3, big endian).  Assembled with sh4-linux-gnu-as.
! Everything here is position independent (PC-relative literals, mova) and is copied
! by the ROM stub to RAM 0x0C7C0000, where it runs.
!
! Patch RAM variables (VARS = 0x0C7CF000):
!   +0  title stamp   frame counter value when the title scene last ran
!   +4  coin stamp    frame counter value when PRESS 1P OR 2P START was last drawn
!   +8  mode          0 = CAVE MATSURI 1.5 (original game), 1 = MATSURI ARRANGE
!
! Game addresses used (unpacked program in RAM):
!   0x0C0024D8 frame counter (+1 per frame)      0x0C05417C / 0x0C0541C0 P1 / P2 new-press edges
!   0x0C0548D8 draw text (r4 x, r5 y, r6 z, r7 string)   0x0C054D74 draw number (same y in r5)
!   0x0C0A2DE0 title scene per-frame function    0x0C169BC4 "PRESS 1P OR 2P START"

        .text
        .align  2

! ---------------------------------------------------------------- patcher
        .global patcher
patcher:
        mova    sites,r0
        mov     r0,r1
1:      mov.l   @r1+,r2             ! address (0 = end)
        tst     r2,r2
        bt      2f
        mov.l   @r1+,r3             ! expected old long
        mov.l   @r1+,r4             ! new long
        mov.l   @r2,r5
        cmp/eq  r3,r5
        bf      1b                  ! mismatch: leave the game untouched there
        bra     1b
        mov.l   r4,@r2
2:      mov.l   Lp_vars,r1
        mov     #0,r0
        mov.l   r0,@r1
        mov.l   r0,@(4,r1)
        mov.l   r0,@(8,r1)
        mov.l   Lp_main,r0
        jmp     @r0
        nop
        .align  2
Lp_vars: .long  0x0C7CF000
Lp_main: .long  0x0C059970

! ---------------------------------------------------------------- chk
! r0 = 1 when the title scene is running and PRESS 1P OR 2P START was drawn
! within the last 23 frames (a coin is in), else 0.  Clobbers r0-r2.
chk:
        mov.l   Lc_T,r0
        mov.l   @r0,r0
        mov.l   Lc_vars,r1
        mov.l   @(4,r1),r2
        tst     r2,r2
        bt      3f
        sub     r2,r0
        mov     #3,r2
        cmp/hi  r2,r0
        bt      3f
        rts
        mov     #1,r0
3:      rts
        mov     #0,r0
        .align  2
Lc_T:    .long  0x0C0024D8
Lc_vars: .long  0x0C7CF000

! ---------------------------------------------------------------- title scene hook
! Runs instead of 0x0C0A2DE0 (the title scene per-frame function), then continues
! into it with the registers it was called with.
        .global title_wrap
title_wrap:
        sts.l   pr,@-r15
        mov.l   r4,@-r15
        mov.l   r5,@-r15
        mov.l   r6,@-r15
        mov.l   r7,@-r15
        mov.l   r8,@-r15
        mov.l   r9,@-r15
        mov.l   r10,@-r15
        mov.l   Lt_T,r1
        mov.l   @r1,r8              ! r8 = frame counter
        mov.l   Lt_vars,r9
        mov.l   @(4,r9),r2          ! previous coin stamp
        mov.l   r8,@(4,r9)          ! stamp = now
        mov     r8,r3
        sub     r2,r3
        mov     #3,r0
        cmp/hi  r0,r3               ! gap > 3 frames: the title just (re)started
        bf      1f
        mov     #0,r0
        mov.l   r0,@(8,r9)          ! cursor back on CAVE MATSURI 1.5
1:
        mov.l   Lt_e1,r1
        mov.l   @r1,r2
        mov.l   Lt_e2,r1
        mov.l   @r1,r3
        or      r3,r2               ! new presses of player 1 or 2
        mov     #1,r0
        tst     r0,r2               ! stick up
        bt      2f
        mov     #0,r0
        bra     3f
        mov.l   r0,@(8,r9)
2:      mov     #2,r0
        tst     r0,r2               ! stick down
        bt      3f
        mov     #1,r0
        mov.l   r0,@(8,r9)
3:      mov.l   Lt_draw,r10
        mov     #56,r4
        mov.l   Lt_y1,r5
        mov.l   Lt_z,r6
        mova    S_item0,r0
        jsr     @r10
        mov     r0,r7
        mov     #56,r4
        mov.l   Lt_y2,r5
        mov.l   Lt_z,r6
        mova    S_item1,r0
        jsr     @r10
        mov     r0,r7
        mov.l   @(8,r9),r0
        tst     r0,r0
        mov.l   Lt_y1,r5
        bt      4f
        mov.l   Lt_y2,r5
4:      mov     #40,r4
        mov.l   Lt_z,r6
        mova    S_arrow,r0
        jsr     @r10
        mov     r0,r7
9:      mov.l   @r15+,r10
        mov.l   @r15+,r9
        mov.l   @r15+,r8
        mov.l   @r15+,r7
        mov.l   @r15+,r6
        mov.l   @r15+,r5
        mov.l   @r15+,r4
        lds.l   @r15+,pr
        rts
        nop
        .align  2
Lt_T:    .long  0x0C0024D8
Lt_vars: .long  0x0C7CF000
Lt_e1:   .long  0x0C05417C
Lt_e2:   .long  0x0C0541C0
Lt_draw: .long  0x0C0548D8
Lt_y1:   .long  228
Lt_y2:   .long  240
Lt_z:    .long  250
Lt_orig: .long  0x0C0A2DE0
S_item0: .asciz "CAVE MATSURI 1.5"
        .align  2
S_item1: .asciz "MATSURI ARRANGE"
        .align  2
S_arrow: .asciz ">"

! ---------------------------------------------------------------- coin message hook
! Replaces the draw-text pointer in the coin message task.  When PRESS 1P OR 2P
! START is drawn on the title scene it is moved down 22 pixels, and the draw is
! recorded (that is what tells the title hook a coin is in).
        .align  2
        .global coin_draw
coin_draw:
        mov.l   Lq_press,r0
        cmp/eq  r0,r7
        bf      2f
        sts.l   pr,@-r15
        mov.l   r4,@-r15
        mov.l   r5,@-r15
        mov.l   r6,@-r15
        bsr     title_wrap
        mov.l   r7,@-r15
        mov.l   @r15+,r7
        mov.l   @r15+,r6
        mov.l   @r15+,r5
        mov.l   @r15+,r4
        lds.l   @r15+,pr
        add     #22,r5
2:      mov.l   Lq_draw,r0
        jmp     @r0
        nop
        .align  2
Lq_press: .long 0x0C169BC4
Lq_T:     .long 0x0C0024D8
Lq_vars:  .long 0x0C7CF000
Lq_draw:  .long 0x0C0548D8

! ---------------------------------------------------------------- credits line hooks
        .global cred_text
cred_text:
        sts     pr,r3
        bsr     chk
        nop
        lds     r3,pr
        tst     r0,r0
        bt      1f
        add     #22,r5
1:      mov.l   Lr_draw,r0
        jmp     @r0
        nop
        .global cred_num
cred_num:
        sts     pr,r3
        bsr     chk
        nop
        lds     r3,pr
        tst     r0,r0
        bt      1f
        add     #22,r5
1:      mov.l   Lr_num,r0
        jmp     @r0
        nop
        .align  2
Lr_draw: .long  0x0C0548D8
Lr_num:  .long  0x0C054D74

! ---------------------------------------------------------------- marquee gates
! The ranking marquee on the title calls these; with a coin in they draw nothing.
        .global gate_text
gate_text:
        sts     pr,r3
        bsr     chk
        nop
        lds     r3,pr
        tst     r0,r0
        bt      1f
        rts
        nop
1:      mov.l   Lg_draw,r0
        jmp     @r0
        nop
        .global gate_num
gate_num:
        sts     pr,r3
        bsr     chk
        nop
        lds     r3,pr
        tst     r0,r0
        bt      1f
        rts
        nop
1:      mov.l   Lg_num,r0
        jmp     @r0
        nop
        .align  2
Lg_draw: .long  0x0C0548D8
Lg_num:  .long  0x0C054D74

! ---------------------------------------------------------------- sites table (appended by build.py)
        .align  2
        .global sites
sites:
