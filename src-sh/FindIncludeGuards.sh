#!/bin/bash
source $(dirname ${BASH_SOURCE[0]})/configuration/config.lib.sh

if [ ! -f headerlist ] ; then
	CreateFilelists
fi

for a in $(cat headerlist) ; do 
  echo -n "$a:"
  sed -e "/^[ ]*#if/{$!N; /^[ ]*#ifndef[ ]*\([A-Z_0-9a-z]\+\)[ ]*\n[ ]*#define[ ]\+\1$/{s/^[ ]*#ifndef[ ]*\([A-Z_0-9a-z]\+\)[ ]*\n[ ]*#define[ ]\+\1$/\1/;p;Q}; /^[ ]*#if[ ]\+\![ ]*defined[ ]*(\([A-Z_0-9a-z]\+\))[ ]*\n[ ]*#define[ ]\+\1$/{s/^[ ]*#if[ ]\+\![ ]*defined[ ]*(\([A-Z_0-9a-z]\+\))[ ]*\n[ ]*#define[ ]\+\1$/\1/;q}; D}" \
	  -e "/^[ ]*#pragma once$/{s/^[ ]*#pragma once$/#pragma once/;q}" \
	  -e "/[/][*]/,/[*][/]/d" \
	  -e "/^#/{Q}" -e "d" $a
	  #-e "/#define VCS static unsigned char/{d}" 
  echo
done | grep ":"

  # sed -e "/^[ ]*#if/{
			# $!N;
			# /^[ ]*#ifndef[ ]*\([A-Z_0-9a-z]\+\)[ ]*\n[ ]*#define[ ]\+\1$/{
				# s/^[ ]*#ifndef[ ]*\([A-Z_0-9a-z]\+\)[ ]*\n[ ]*#define[ ]\+\1$/\1/;
				# q
			# };
			# /^[ ]*#if[ ]\+\![ ]*defined[ ]*(\([A-Z_0-9a-z]\+\))[ ]*\n[ ]*#define[ ]\+\1$/{
				# s/^[ ]*#if[ ]\+\![ ]*defined[ ]*(\([A-Z_0-9a-z]\+\))[ ]*\n[ ]*#define[ ]\+\1$/\1/;
				# q
			# }; 
			# D
		# }
		# /^[ ]*#pragma once$/{
			# s/^[ ]*#pragma once$/#pragma once/;
			# q
		# }
		# /[/][*]/,/[*][/]/d
		# /^#/{
			# Q
		# }
		# d
		# " $a
