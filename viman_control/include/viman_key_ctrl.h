#ifndef VIMAN_KEY_CTRL_H
#define VIMAN_KEY_CTRL_H

#include "viman.h"

// Libraries to read from keyboard
#include <termios.h>
#include <thread>

// Maximum velocities in m/s^2 and rad/s
#define MAX_LINEAR_X 2
#define MAX_LINEAR_Y 2
#define MAX_LINEAR_Z 2
#define MAX_YAW 2.5

// Store current cmd values
float cur_values[4];

// VIMAN instance
Viman vi;

// Vars to read user cmds
static struct termios old, current;
bool do_not_quit = true;

// Functions to read user input
void display_help(void);
void initTermios(void);
void resetTermios(void);
char getch(void);
void read_input(void);

#endif // VIMAN_KEY_CTRL_H
