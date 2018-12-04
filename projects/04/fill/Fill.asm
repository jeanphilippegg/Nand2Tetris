// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

        // Store the number of pixels in a variable
        @8192
        D=A
        @numPixels
        M=D

(LOOP)
        @KBD
        D=M
        @CLEAR
        D;JEQ
        @BLACKEN
        D;JNE

(CLEAR)
        @actualPixel
        M=0
        @DRAW
        0;JMP
(BLACKEN)
        @actualPixel
        M=-1
        @DRAW
        0;JMP

(DRAW)
        // Initialize remainingPixels to numPixels
        @numPixels
        D=M
        @remainingPixels
        M=D

(DRAWLOOP)
        // If no remaining pixel, goto LOOP
        @remainingPixels
        D=M
        @LOOP
        D;JEQ

        // Select the right pixel
        @SCREEN
        D=A
        @remainingPixels
        D=D+M
        D=D-1
        @pixelAddress
        M=D

        // Color the current pixel
        @actualPixel
        D=M
        @pixelAddress
        A=M
        M=D

        // remainingPixels = remainingPixels - 1
        @remainingPixels
        M=M-1

        // Loop for each pixel
        @DRAWLOOP
        0;JMP
