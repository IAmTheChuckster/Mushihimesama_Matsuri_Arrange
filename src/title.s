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
        .equ BOMB_MAX, 6
        .equ HUD_X, 192
        .equ HUD_Y, 300
        .equ GOLD_VAL, 1
        .align  2

! ---------------------------------------------------------------- patcher
        .global patcher
patcher:
        mov.l   Lp_sites,r1
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
        mov.l   r0,@(16,r1)
        mov.l   r0,@(20,r1)
        mov.l   r0,@(24,r1)
        mov.l   Lp_main,r0
        jmp     @r0
        nop
        .align  2
Lp_vars: .long  0x0C7CF000
Lp_main: .long  0x0C059970
Lp_sites: .long sites - patcher + 0x0C7C0000

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
1:      mov     #0,r0
        mov.l   r0,@(16,r9)         ! gem counter back to 0 for the next game
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


! ================================================================ MATSURI ARRANGE (Ultra) features
! Extra patch RAM variables (VARS = 0x0C7CF000):
!   +16 gem counter (0..11999)     +20 cancel busy flag
! Game addresses:
!   0x0C1FB630 game mode (0 Original, 1 Maniac, 2 Ultra)
!   0x0C1FBC0C player 1 block, bombs at +12
!   0x0C19CC40 -> bullet manager; active list head at +0x7E004; bullet: +0 next, +16 x, +20 y (16.16)
!   0x0C08F140 remove bullet (r4 manager, r5 bullet) -> next
!   0x0C0A6790 spawn crystal gems, 0x0C0A6C30 spawn gold gems (r4 x, r5 y, r6 125, r7 0, stack args)

! r0 = 1 when MATSURI ARRANGE was chosen and the game is in Ultra mode.  Clobbers r0, r1.
        .align  2
active:
        mov.l   La_vars,r1
        mov.l   @(8,r1),r0
        cmp/eq  #1,r0
        bf      1f
        mov.l   La_mode,r1
        mov.l   @r1,r0
        cmp/eq  #2,r0
        bf      1f
        rts
        mov     #1,r0
1:      rts
        mov     #0,r0
        .align  2
La_vars: .long  0x0C7CF000
La_mode: .long  0x0C1FB630

! ---------------------------------------------------------------- gem counter
! Replaces the call to the game's gem-collect routine (r4 player block, r5 gem type 0-3).
        .global gem_wrap
gem_wrap:
        sts.l   pr,@-r15
        mov.l   r4,@-r15
        mov.l   r5,@-r15
        bsr     active
        nop
        mov.l   @r15+,r5
        mov.l   @r15+,r4
        tst     r0,r0
        bt      9f
        mov.l   Lg_p1,r0
        cmp/eq  r0,r4
        bf      9f
        mov     #3,r0
        cmp/hi  r0,r5
        bt      9f
        mova    gem_vals,r0
        mov     r5,r1
        add     r1,r1
        mov.w   @(r0,r1),r1         ! value of this gem
        mov.l   Lg_vars,r2
        mov.l   @(16,r2),r3
        add     r1,r3
        mov.w   Lg_full,r1
        cmp/hs  r1,r3
        bf      2f
        sub     r1,r3               ! 12000 reached: start again, extra bomb
        mov.l   @(12,r4),r0
        mov     #BOMB_MAX,r1
        cmp/ge  r1,r0
        bt      2f
        add     #1,r0
        mov.l   r0,@(12,r4)
        mov.l   r2,@-r15            ! bomb added: play her bomb shout
        mov.l   r3,@-r15
        mov.l   r4,@-r15
        mov.l   r5,@-r15
        mov.l   Lg_shout,r0
        jsr     @r0
        nop
        mov.l   @r15+,r5
        mov.l   @r15+,r4
        mov.l   @r15+,r3
        mov.l   @r15+,r2
2:      mov.l   r3,@(16,r2)
9:      lds.l   @r15+,pr
        mov.l   Lg_orig,r0
        jmp     @r0
        nop
        .align  2
gem_vals: .word 1, 5, 10, 15
Lg_full: .word  12000
        .align  2
Lg_p1:   .long  0x0C1FBC0C
Lg_vars: .long  0x0C7CF000
Lg_orig: .long  0x0C05FCF0
Lg_shout: .long 0x0C0E2330

! ---------------------------------------------------------------- counter display
! Wraps the in-game per-frame callback (0x0C0AB7B0).
        .global hud_wrap
hud_wrap:
        sts.l   pr,@-r15
        mov.l   r4,@-r15
        mov.l   r5,@-r15
        mov.l   r6,@-r15
        mov.l   r7,@-r15
        bsr     active
        nop
        tst     r0,r0
        bt      9f
        bsr     wsw                 ! 4th button: cycle weapon
        nop
        bsr     gauge               ! gold bomb gauge in the right 6 slots
        nop
        mov.l   Lh_vars2,r1         ! bomb protection frames
        mov.l   @(32,r1),r0
        cmp/pl  r0
        bf      9f
        add     #-1,r0
        mov.l   r0,@(32,r1)
9:      mov.l   @r15+,r7
        mov.l   @r15+,r6
        mov.l   @r15+,r5
        mov.l   @r15+,r4
        lds.l   @r15+,pr
        mov.l   Lh_orig,r0
        jmp     @r0
        nop
        .align  2
Lh_pow:  .long  10000, 1000, 100, 10
Lh_x:    .word  HUD_X
Lh_y:    .word  HUD_Y
Lh_z:    .word  250
        .align  2
Lh_vars: .long  0x0C7CF000
Lh_num:  .long  0x0C054D74
Lh_vars2: .long 0x0C7CF000
Lh_orig: .long  0x0C0AB7B0

! ---------------------------------------------------------------- bomb gauge
! One gold bomb icon (the game's own right-hand bomb sprite 0x4B8, tinted) per 2000 of the gem
! counter, in the right 6 slots of the bottom bar, filled from the rightmost slot to the left.
! Called every frame from hud_wrap.  Preserves r8-r10.
        .align  2
gauge:
        sts.l   pr,@-r15
        mov.l   r8,@-r15
        mov.l   r9,@-r15
        mov.l   r10,@-r15
        mov.l   Lb_vars,r1
        mov.l   @(16,r1),r2
        mov.w   Lb_k,r3
        mov     #0,r8
1:      cmp/hs  r3,r2
        bf      2f
        sub     r3,r2
        bra     1b
        add     #1,r8
2:      mov     #6,r0
        cmp/gt  r0,r8
        bf      3f
        mov     r0,r8
3:      tst     r8,r8
        bt      9f
        mov     #0,r9
4:      mov.w   Lb_x0,r5
        mov     r9,r0
        shll2   r0
        shll2   r0
        sub     r0,r5
        shll16  r5
        mov     r5,r10
        mov.w   Lb_y,r6
        shll16  r6
        mov.l   Lb_bar,r1            ! follow the bar's slide (boss start, score tally)
        mov.l   @(16,r1),r2
        add     r2,r6
        mov.l   @(20,r1),r2
        add     r2,r6
        mov.w   Lb_s1,r4
        bsr     gdr
        nop
        add     #1,r9
        cmp/eq  r8,r9
        bf      4b
9:      mov.l   @r15+,r10
        mov.l   @r15+,r9
        mov.l   @r15+,r8
        lds.l   @r15+,pr
        rts
        nop
        .align  2
gdr:    sts.l   pr,@-r15            ! r4 sprite, r5 x, r6 y (16.16): draw and tint gold
        mov.w   Lb_z,r7
        mov.l   Lb_draw,r0
        jsr     @r0
        nop
        mov     r0,r4
        mov.l   r4,@-r15
        mov.l   Lb_col,r5
        mov.l   Lb_tint,r0
        jsr     @r0
        nop
        mov.l   @r15,r4
        mov     #0,r1
        add     #-4,r15
        mov.l   r1,@r15
        mov     #2,r5
        mov     #3,r6
        mov.w   Lb_ff,r7
        mov.l   Lb_bl,r0
        jsr     @r0
        nop
        add     #8,r15
        lds.l   @r15+,pr
        rts
        nop
Lb_k:    .word  2000
Lb_x0:   .word  220
Lb_y:    .word  8
Lb_s1:   .word  0x61E
Lb_s2:   .word  0x61F
Lb_z:    .word  0x100
Lb_ff:   .word  0xFF
        .align  2
Lb_vars: .long  0x0C7CF000
Lb_draw: .long  0x0C059F30
Lb_tint: .long  0x0C0555CC
Lb_col:  .long  0x00FF9830
Lb_bl:   .long  0x0C0556C8
Lb_bar:  .long  0x0C2DCA84

! ---------------------------------------------------------------- auto Ultra
! While MATSURI ARRANGE is chosen the mode-select scene (object 0x0C2DAF70, tag 'MCX', state at
! +28: 4 = choosing the mode, 5 = "dare to challenge despair?" prompt, 8 = shot select) is driven
! by itself: in state 4 the cursor (+40) is set to ULTRA (2) and button 1 is pressed; in state 5 the
! prompt choice (0x0C5EE960) is set to "bring it on" (1) and button 1 is pressed.  Any other scene
! is left alone.  Called from poll_common once per input poll.  Clobbers r0-r3.
        .align  2
auto_ultra:
        mov.l   Lu_obj,r1
        mov.l   @(12,r1),r0
        mov.l   Lu_tag,r2
        cmp/eq  r2,r0
        bf      9f
        mov.l   @(28,r1),r0
        cmp/eq  #4,r0
        bt      1f
        cmp/eq  #5,r0
        bf      9f
        mov.l   Lu_ask,r2           ! state 5: answer the prompt with "bring it on"
        mov     #1,r3
        bra     2f
        mov.l   r3,@r2
1:      mov     #2,r3               ! state 4: cursor on ULTRA
        mov.l   r3,@(40,r1)
2:      mov.l   Lu_edge,r1          ! press button 1 (new-press word of player 1)
        mov.l   @r1,r0
        or      #0x10,r0
        mov.l   r0,@r1
9:      rts
        nop
        .align  2
Lu_obj:  .long  0x0C2DAF70
Lu_tag:  .long  0x4D435800
Lu_ask:  .long  0x0C5EE960
Lu_edge: .long  0x0C05417C

! ---------------------------------------------------------------- shot select: auto pick
! Mode-select scene state 8 = shot select; the shot-select object (0x0C2DC9A0) is 3 while choosing
! and 5 once the game starts.  While choosing, the cursor is put on the top-right weapon (row
! 0x0C2DC9A8 = 0, column 0x0C2DC9DC = 1) and button 1 is pressed.  Called from poll_common.
! Clobbers r0-r3.
        .align  2
lockcol:
        mov.l   Lu_obj2,r1
        mov.l   @(12,r1),r0
        mov.l   Lu_tag2,r2
        cmp/eq  r2,r0
        bf      9f
        mov.l   @(28,r1),r0
        cmp/eq  #8,r0
        bf      9f
        mov.l   Lk_ss,r1
        mov.l   @r1,r0
        cmp/eq  #3,r0
        bf      9f
        mov     #0,r2
        mov.l   r2,@(8,r1)          ! row 0
        mov     #1,r2
        mov.l   r2,@(60,r1)         ! column 1 (right)
        mov.l   Lu_edge2,r1
        mov.l   @r1,r0
        or      #0x10,r0
        mov.l   r0,@r1
9:      rts
        nop
        .align  2
Lu_obj2:  .long 0x0C2DAF70
Lu_tag2:  .long 0x4D435800
Lu_edge2: .long 0x0C05417C
Lk_ss:    .long 0x0C2DC9A0

! ---------------------------------------------------------------- weapon change (4th button)
! Called every frame by hud_wrap while MATSURI ARRANGE + Ultra is active.  A new press of the
! 4th button (raw input bit 0x80 at 0x0C054178) moves player 1 to the next weapon 0 -> 1 -> 2 -> 0:
! the weapon index is stored in the player block (+24 active, +28 selected) and in the weapon
! object (type field +0x98), then the game's own weapon-object constructor (0x0C09CDC0) is run
! again so every weapon-dependent field is rebuilt exactly as at the start of a game.
        .align  2
wsw:
        sts.l   pr,@-r15
        mov.l   Lw_in,r1
        mov.l   @r1,r2              ! raw input word
        mov.w   Lw_bit,r3
        and     r3,r2               ! 4th button held?
        mov.l   Lw_vars,r4
        mov.l   @(24,r4),r5         ! held last frame?
        mov.l   r2,@(24,r4)
        tst     r2,r2
        bt      9f
        tst     r5,r5
        bf      9f                  ! still held: not a new press
        mov.l   Lw_pl,r4            ! player 1 block
        mov.w   Lw_off,r0
        mov.l   @(r0,r4),r6         ! weapon object
        mov.l   Lw_lo,r1
        cmp/hs  r1,r6
        bf      9f
        mov.l   Lw_hi,r1
        cmp/hs  r1,r6
        bt      9f
        mov.l   @(24,r4),r2         ! current weapon
        add     #1,r2
        mov     #3,r1
        cmp/hs  r1,r2
        bf      1f
        mov     #0,r2
1:      mov.l   r2,@(24,r4)
        mov.l   r2,@(28,r4)
        mov.w   Lw_type,r0
        mov.l   r2,@(r0,r6)
        mov.l   Lw_ctor,r0
        jsr     @r0
        mov     r6,r4
        mov     #6,r4               ! weapon-change sound (game SE call)
        mov.w   Lw_se,r5
        mov     #0x37,r6
        mov.w   Lw_vol,r7
        mov.l   Lw_snd,r0
        jsr     @r0
        nop
9:      lds.l   @r15+,pr
        rts
        nop
        .align  2
Lw_se:   .word  0x5B
Lw_vol:  .word  0x5A
Lw_bit:  .word  0x80
Lw_off:  .word  0xDC
Lw_type: .word  0x98
        .align  2
Lw_in:   .long  0x0C054178
Lw_vars: .long  0x0C7CF000
Lw_pl:   .long  0x0C1FBC0C
Lw_lo:   .long  0x0C000000
Lw_hi:   .long  0x0D000000
Lw_snd:  .long  0x0C05923C
Lw_ctor: .long  0x0C09CDC0

! ---------------------------------------------------------------- player 2 off
! Wraps the two input-poll routines; while MATSURI ARRANGE is chosen the 2P start bit is cleared.
        .global poll1_wrap, poll2_wrap
poll1_wrap:
        mov.l   Lq1,r0
        bra     poll_common
        nop
poll2_wrap:
        mov.l   Lq2,r0
poll_common:
        sts.l   pr,@-r15
        jsr     @r0
        nop
        mov.l   Lp2_vars,r1
        mov.l   @(8,r1),r0
        cmp/eq  #1,r0
        bf      9f
        mov.l   Lq_mask,r2
        mov.l   Lq_a,r1
        mov.l   @r1,r0
        and     r2,r0
        mov.l   r0,@r1
        mov.l   Lq_b,r1
        mov.l   @r1,r0
        and     r2,r0
        mov.l   r0,@r1
        bsr     auto_ultra          ! MATSURI ARRANGE: pick Ultra by itself
        nop
        bsr     lockcol             ! shot select: pick top-right
        nop
9:      lds.l   @r15+,pr
        rts
        nop
        .align  2
Lq1:     .long  0x0C054330
Lq2:     .long  0x0C054260
Lp2_vars: .long  0x0C7CF000
Lq_mask: .long  0xFFFF7FFF
Lq_a:    .long  0x0C0541B0
Lq_b:    .long  0x0C0541BC

! ---------------------------------------------------------------- enemy death: chain bullet cancel
! The game's two gem spawners are entered here (their first 12 bytes jump to us).  When an enemy
! dies in MATSURI ARRANGE Ultra, bullets within 48 px of (r4,r5) become small crystal gems, then
! bullets within 32 px of any cancelled bullet become small gold gems, repeated until none is left
! in range.  Then the original spawner runs.
        .global spawn_c_wrap, spawn_g_wrap
spawn_c_wrap:
        mov.l   Ls_retc,r0
        bra     spawn_common
        nop
spawn_g_wrap:
        mov.l   Ls_retg,r0
spawn_common:
        mov.l   r0,@-r15            ! continuation address
        sts.l   pr,@-r15
        mov.l   r4,@-r15
        mov.l   r5,@-r15
        mov.l   r6,@-r15
        mov.l   r7,@-r15
        mov.l   Ls_vars,r1
        mov.l   @(20,r1),r0         ! busy: this is one of our own gem spawns
        tst     r0,r0
        bf      9f
        bsr     active
        nop
        tst     r0,r0
        bt      9f
        mov.l   Ls_cancel,r0
        jsr     @r0                 ! r4,r5 still hold the death position
        nop
9:      mov.l   @r15+,r7
        mov.l   @r15+,r6
        mov.l   @r15+,r5
        mov.l   @r15+,r4
        lds.l   @r15+,pr
        mov.l   @r15+,r0
        mov.l   r8,@-r15            ! the 6 instructions replaced at the spawner entry
        mov.l   r9,@-r15
        mov.l   r10,@-r15
        mov.l   r11,@-r15
        mov.l   r12,@-r15
        jmp     @r0
        mov.l   r13,@-r15
        .align  2
Ls_retc:   .long 0x0C0A679C
Ls_retg:   .long 0x0C0A6C3C
Ls_vars:   .long 0x0C7CF000
Ls_cancel: .long cancel - patcher + 0x0C7C0000

! cancel(r4 x, r5 y)
!   r8 queue read index, r9 queue write index, r10 queue base, r11 bullet manager,
!   r12 current bullet, r13 next bullet, r14 radius squared
cancel:
        sts.l   pr,@-r15
        mov.l   r8,@-r15
        mov.l   r9,@-r15
        mov.l   r10,@-r15
        mov.l   r11,@-r15
        mov.l   r12,@-r15
        mov.l   r13,@-r15
        mov.l   r14,@-r15
        mov.l   Lx_vars,r1
        mov     #1,r0
        mov.l   r0,@(20,r1)         ! busy
        mov     #64,r0
        mov.l   r0,@(28,r1)         ! early-reject window (px) used by scan
        mov.l   Lc_mgrp,r0
        mov.l   @r0,r11
        tst     r11,r11
        bt      8f
        mov.l   Lc_q,r10
        mov     #0,r8
        mov     #0,r9
        mov.l   r4,@-r15            ! seed position on the stack: @r15 = y, @(4,r15) = x
        mov.l   r5,@-r15
        mov.w   Lc_r48,r14
        mov     #0,r0
        bsr     scan                ! pass 1: crystal gems around the enemy
        mov.l   r0,@-r15            ! @r15 = gem kind (0 crystal, 1 gold)
        add     #12,r15
1:      cmp/ge  r9,r8               ! chain: every cancelled bullet cancels its neighbours
        bt      8f
        mov     r8,r0
        shll2   r0
        shll    r0
        add     r10,r0
        mov.l   @r0,r1
        mov.l   @(4,r0),r2
        add     #1,r8
        mov.l   r1,@-r15
        mov.l   r2,@-r15
        mov.w   Lc_r32,r14
        mov     #1,r0
        bsr     scan
        mov.l   r0,@-r15
        bra     1b
        add     #12,r15
8:      mov.l   Lx_vars,r1
        mov     #0,r0
        mov.l   r0,@(20,r1)
        mov.l   @r15+,r14
        mov.l   @r15+,r13
        mov.l   @r15+,r12
        mov.l   @r15+,r11
        mov.l   @r15+,r10
        mov.l   @r15+,r9
        mov.l   @r15+,r8
        lds.l   @r15+,pr
        rts
        nop
        .align  2
Lc_r48:  .word  48*48
Lc_r32:  .word  32*32
        .align  2
Lx_vars: .long  0x0C7CF000
Lc_mgrp: .long  0x0C19CC40
Lc_q:    .long  0x0C7D0000

! scan: walk the active bullet list; every bullet within sqrt(r14) px of the centre is removed,
! queued and turned into a gem.  On entry @(4,r15) = kind, @(8,r15) = cy, @(12,r15) = cx
! (offsets after the bsr pushed nothing; we push pr first so add 4).
scan:
        sts.l   pr,@-r15            ! now kind @(4), cy @(8), cx @(12)
        mov.l   Ln_head,r0
        mov.l   @(r0,r11),r12
2:      tst     r12,r12
        bt      9f
        mov.l   @r12,r13            ! next
        mov.l   @(16,r12),r1
        mov.l   @(12,r15),r2
        sub     r2,r1
        shlr16  r1                  ! 16.16 -> pixels
        exts.w  r1,r1
        mov.l   @(20,r12),r2
        mov.l   @(8,r15),r3
        sub     r3,r2
        shlr16  r2
        exts.w  r2,r2
        mov.l   Ln_lim,r3
        mov.l   @r3,r3
        mov     r1,r0
        cmp/pz  r0
        bt      3f
        neg     r0,r0
3:      cmp/hs  r3,r0
        bt      7f
        mov     r2,r0
        cmp/pz  r0
        bt      4f
        neg     r0,r0
4:      cmp/hs  r3,r0
        bt      7f
        muls.w  r1,r1
        sts     macl,r1
        muls.w  r2,r2
        sts     macl,r2
        add     r2,r1
        cmp/hi  r14,r1
        bt      7f
        ! hit: queue its position, remove it, spawn a gem there
        mov.l   @(16,r12),r1
        mov.l   @(20,r12),r2
        mov.w   Ln_qmax,r0
        cmp/ge  r0,r9
        bt      5f
        mov     r9,r0
        shll2   r0
        shll    r0
        add     r10,r0
        mov.l   r1,@r0
        mov.l   r2,@(4,r0)
        add     #1,r9
5:      mov.l   r1,@-r15            ! keep x, y across the remove
        mov.l   r2,@-r15
        mov     r11,r4
        mov.l   Ln_remove,r0
        jsr     @r0
        mov     r12,r5
        mov.l   @r15+,r5            ! y
        mov.l   @r15+,r4            ! x
        mov.l   @(4,r15),r0         ! kind
        tst     r0,r0
        bf      6f
        ! small crystal: spawn(x, y, 125, 0, 2, 2, 0x300, 1, 1)
        mov     #1,r0
        mov.l   r0,@-r15
        mov.l   r0,@-r15
        mov.w   Ln_val,r0
        mov.l   r0,@-r15
        mov     #2,r0
        mov.l   r0,@-r15
        mov.l   r0,@-r15
        mov     #125,r6
        mov     #0,r7
        mov.l   Ln_crys,r0
        jsr     @r0
        nop
        bra     7f
        add     #20,r15
        ! small gold: spawn(x, y, 125, 0, 2, 2, GOLD_VAL, 1)
6:      mov     #1,r0
        mov.l   r0,@-r15
        mov     #GOLD_VAL,r0
        mov.l   r0,@-r15
        mov     #2,r0
        mov.l   r0,@-r15
        mov.l   r0,@-r15
        mov     #125,r6
        mov     #0,r7
        mov.l   Ln_gold,r0
        jsr     @r0
        nop
        add     #16,r15
7:      bra     2b
        mov     r13,r12
9:      lds.l   @r15+,pr
        rts
        nop
        .align  2
Ln_qmax:   .word 2048
Ln_val:    .word 0x300
        .align  2
Ln_head:   .long 0x7E004
Ln_lim:    .long 0x0C7CF01C
Ln_remove: .long 0x0C08F140
Ln_crys:   .long 0x0C0A6790
Ln_gold:   .long 0x0C0A6C30


! ---------------------------------------------------------------- bomb button
! The game's bomb trigger (0x0C05FE40) calls 0x0C05DB30(r4, -1) to start the bomb.  In MATSURI
! ARRANGE Ultra that call comes here: every enemy bullet on screen becomes a small crystal gem
! and the original bomb effect is skipped.  (The trigger already used up one bomb and set its timer.)
        .global bomb_wrap
bomb_wrap:
        sts.l   pr,@-r15
        mov.l   r4,@-r15
        mov.l   r5,@-r15
        bsr     active
        nop
        tst     r0,r0
        bt      1f
        bsr     bombcancel
        nop
        mov.l   Lbw_vars,r1
        mov     #90,r0
        mov.l   r0,@(32,r1)         ! about 1.5 s of protection
        mov.l   @r15+,r5
        mov.l   @r15+,r4
        lds.l   @r15+,pr
        rts
        nop
1:      mov.l   @r15+,r5
        mov.l   @r15+,r4
        lds.l   @r15+,pr
        mov.l   Lbw_orig,r0
        jmp     @r0
        nop
        .align  2
Lbw_orig: .long 0x0C05DB30
Lbw_vars: .long 0x0C7CF000


! The bomb button path starts the big bomb blast with 0x0C0602A0(r4); skip it in ARRANGE Ultra.
        .global bombfx_wrap
bombfx_wrap:
        sts.l   pr,@-r15
        mov.l   r4,@-r15
        bsr     active
        nop
        tst     r0,r0
        mov.l   @r15+,r4
        lds.l   @r15+,pr
        bt      1f
        rts
        mov     #0,r0
1:      mov.l   Lbf_orig,r0
        jmp     @r0
        nop
        .align  2
Lbf_orig: .long 0x0C0602A0

! 0x0C0E3B90 launches the thrown bomb ball (whose blast is the cyan cloud) and returns non-zero.
! In ARRANGE Ultra report success without launching anything.
        .global bombgo_wrap
bombgo_wrap:
        sts.l   pr,@-r15
        bsr     active
        nop
        lds.l   @r15+,pr
        tst     r0,r0
        bt      1f
        rts
        mov     #1,r0
1:      mov.l   Lbg_orig,r0
        jmp     @r0
        nop
        .align  2
Lbg_orig: .long 0x0C0E3B90

! "Is she invulnerable?" check (0x0C05F9F0, used by the three hit paths): while the bomb protection
! counter runs, report invulnerable.
        .global inv_wrap
inv_wrap:
        sts.l   pr,@-r15
        mov.l   r4,@-r15
        bsr     active
        nop
        mov.l   @r15+,r4
        tst     r0,r0
        bt      1f
        mov.l   Li_vars,r1
        mov.l   @(32,r1),r0
        cmp/pl  r0
        bf      1f
        lds.l   @r15+,pr
        rts
        mov     #1,r0
1:      lds.l   @r15+,pr
        mov.l   Li_orig,r0
        jmp     @r0
        nop
        .align  2
Li_vars: .long 0x0C7CF000
Li_orig: .long 0x0C05F9F0

bombcancel:
        sts.l   pr,@-r15
        mov.l   r8,@-r15
        mov.l   r9,@-r15
        mov.l   r10,@-r15
        mov.l   r11,@-r15
        mov.l   r12,@-r15
        mov.l   r13,@-r15
        mov.l   r14,@-r15
        mov.l   Lbx_vars,r1
        mov     #1,r0
        mov.l   r0,@(20,r1)         ! busy: our own gem spawns must not chain
        mov.l   Lbc_lim,r0
        mov.l   r0,@(28,r1)         ! whole screen
        mov.l   Lbx_mgr,r0
        mov.l   @r0,r11
        tst     r11,r11
        bt      8f
        mov.l   Lbx_q,r10
        mov     #0,r8
        mov     #0,r9
        mov     #0,r0
        mov.l   r0,@-r15            ! cx
        mov.l   r0,@-r15            ! cy
        mov     #-1,r14             ! any distance
        bsr     scan
        mov.l   r0,@-r15            ! kind 0 = crystal
        add     #12,r15
8:      mov.l   Lbx_vars,r1
        mov     #0,r0
        mov.l   r0,@(20,r1)
        mov.l   @r15+,r14
        mov.l   @r15+,r13
        mov.l   @r15+,r12
        mov.l   @r15+,r11
        mov.l   @r15+,r10
        mov.l   @r15+,r9
        mov.l   @r15+,r8
        lds.l   @r15+,pr
        rts
        nop
        .align  2
Lbc_lim: .long  0x00007FFF
Lbx_vars: .long 0x0C7CF000
Lbx_mgr: .long  0x0C19CC40
Lbx_q:   .long  0x0C7D0000

! ---------------------------------------------------------------- sites table (appended by build.py)
        .align  2
        .global sites
sites:
