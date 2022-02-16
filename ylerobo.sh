#!/bin/sh

# Initialize database if it does not exist.
[ -f $YLEROBO_DB ] || ylerobo init

# Execute the application
ylerobo $@
