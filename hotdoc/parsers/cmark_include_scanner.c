/* Generated by re2c 0.16 */
/*
 * re2c syntax scanner for hotdoc includes
 *
 * Copyright 2016 Mathieu Duponchelle <mathieu.duponchelle@opencredd.com>
 * Copyright 2016 Collabora Ltd.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
 */

#include <stdlib.h>
#include <string.h>
#include "cmark_include_scanner.h"

cmark_bufsize_t _include_ext_scan_at(cmark_bufsize_t (*scanner)(const unsigned char *),
	const char *s, cmark_bufsize_t offset)
{
	cmark_bufsize_t res;
	cmark_bufsize_t len = strlen(s);
	unsigned char *ptr = (unsigned char *)s;

        if (ptr == NULL || offset > len) {
          return 0;
        } else {
	  res = scanner(ptr + offset);
        }

	return res;
}



cmark_bufsize_t _scan_open_include_block(const unsigned char *p)
{
  const unsigned char *marker = NULL;
  const unsigned char *start = p;

{
	unsigned char yych;
	static const unsigned char yybm[] = {
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192,   0, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 192, 192, 192, 192, 192, 
		192, 192, 192, 128, 192,  64, 192, 192, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
	};
	yych = *(marker = p);
	if (yych <= 0xDF) {
		if (yych <= 'z') {
			if (yych != '\n') goto yy3;
		} else {
			if (yych <= '{') goto yy4;
			if (yych <= 0x7F) goto yy3;
			if (yych >= 0xC2) goto yy5;
		}
	} else {
		if (yych <= 0xEF) {
			if (yych <= 0xE0) goto yy7;
			if (yych == 0xED) goto yy9;
			goto yy8;
		} else {
			if (yych <= 0xF0) goto yy10;
			if (yych <= 0xF3) goto yy11;
			if (yych <= 0xF4) goto yy12;
		}
	}
yy2:
	{ return 0; }
yy3:
	yych = *(marker = ++p);
	if (yych <= 0x7F) {
		if (yych == '\n') goto yy2;
		goto yy14;
	} else {
		if (yych <= 0xC1) goto yy2;
		if (yych <= 0xF4) goto yy14;
		goto yy2;
	}
yy4:
	yych = *(marker = ++p);
	if (yych == '{') goto yy23;
	goto yy2;
yy5:
	yych = *++p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy3;
yy6:
	p = marker;
	goto yy2;
yy7:
	yych = *++p;
	if (yych <= 0x9F) goto yy6;
	if (yych <= 0xBF) goto yy5;
	goto yy6;
yy8:
	yych = *++p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy5;
	goto yy6;
yy9:
	yych = *++p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0x9F) goto yy5;
	goto yy6;
yy10:
	yych = *++p;
	if (yych <= 0x8F) goto yy6;
	if (yych <= 0xBF) goto yy8;
	goto yy6;
yy11:
	yych = *++p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy8;
	goto yy6;
yy12:
	yych = *++p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0x8F) goto yy8;
	goto yy6;
yy13:
	++p;
	yych = *p;
yy14:
	if (yybm[0+yych] & 64) {
		goto yy13;
	}
	if (yych <= 0xEC) {
		if (yych <= 0xC1) {
			if (yych <= '\n') goto yy6;
			if (yych >= '|') goto yy6;
		} else {
			if (yych <= 0xDF) goto yy16;
			if (yych <= 0xE0) goto yy17;
			goto yy18;
		}
	} else {
		if (yych <= 0xF0) {
			if (yych <= 0xED) goto yy19;
			if (yych <= 0xEF) goto yy18;
			goto yy20;
		} else {
			if (yych <= 0xF3) goto yy21;
			if (yych <= 0xF4) goto yy22;
			goto yy6;
		}
	}
	yych = *++p;
	if (yych == '{') goto yy23;
	goto yy6;
yy16:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy13;
	goto yy6;
yy17:
	++p;
	yych = *p;
	if (yych <= 0x9F) goto yy6;
	if (yych <= 0xBF) goto yy16;
	goto yy6;
yy18:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy16;
	goto yy6;
yy19:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0x9F) goto yy16;
	goto yy6;
yy20:
	++p;
	yych = *p;
	if (yych <= 0x8F) goto yy6;
	if (yych <= 0xBF) goto yy18;
	goto yy6;
yy21:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy18;
	goto yy6;
yy22:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0x8F) goto yy18;
	goto yy6;
yy23:
	yych = *++p;
	marker = p;
	goto yy25;
yy24:
	++p;
	yych = *p;
yy25:
	if (yybm[0+yych] & 128) {
		goto yy24;
	}
	if (yych <= 0xEC) {
		if (yych <= 0xC1) {
			if (yych <= '\n') goto yy6;
			if (yych >= '~') goto yy6;
		} else {
			if (yych <= 0xDF) goto yy27;
			if (yych <= 0xE0) goto yy28;
			goto yy29;
		}
	} else {
		if (yych <= 0xF0) {
			if (yych <= 0xED) goto yy30;
			if (yych <= 0xEF) goto yy29;
			goto yy31;
		} else {
			if (yych <= 0xF3) goto yy32;
			if (yych <= 0xF4) goto yy33;
			goto yy6;
		}
	}
	yych = *++p;
	if (yych == '}') goto yy34;
	goto yy6;
yy27:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy24;
	goto yy6;
yy28:
	++p;
	yych = *p;
	if (yych <= 0x9F) goto yy6;
	if (yych <= 0xBF) goto yy27;
	goto yy6;
yy29:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy27;
	goto yy6;
yy30:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0x9F) goto yy27;
	goto yy6;
yy31:
	++p;
	yych = *p;
	if (yych <= 0x8F) goto yy6;
	if (yych <= 0xBF) goto yy29;
	goto yy6;
yy32:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy29;
	goto yy6;
yy33:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0x8F) goto yy29;
	goto yy6;
yy34:
	++p;
	p = marker;
	{ return (cmark_bufsize_t)(p - start); }
}

}

cmark_bufsize_t _scan_close_include_block(const unsigned char *p)
{
  const unsigned char *marker = NULL;
  const unsigned char *start = p;

{
	unsigned char yych;
	static const unsigned char yybm[] = {
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128,   0, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128, 128, 128, 128, 
		128, 128, 128, 128, 128,   0, 128, 128, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
	};
	yych = *(marker = p);
	marker = p;
	if (yych <= 0xDF) {
		if (yych <= '|') {
			if (yych != '\n') goto yy39;
		} else {
			if (yych <= '}') goto yy40;
			if (yych <= 0x7F) goto yy39;
			if (yych >= 0xC2) goto yy41;
		}
	} else {
		if (yych <= 0xEF) {
			if (yych <= 0xE0) goto yy43;
			if (yych == 0xED) goto yy45;
			goto yy44;
		} else {
			if (yych <= 0xF0) goto yy46;
			if (yych <= 0xF3) goto yy47;
			if (yych <= 0xF4) goto yy48;
		}
	}
yy38:
	{ return 0; }
yy39:
	yych = *(marker = ++p);
	marker = p;
	if (yych <= 0x7F) {
		if (yych == '\n') goto yy38;
		goto yy50;
	} else {
		if (yych <= 0xC1) goto yy38;
		if (yych <= 0xF4) goto yy50;
		goto yy38;
	}
yy40:
	yych = *++p;
	if (yych == '}') goto yy59;
	goto yy38;
yy41:
	yych = *++p;
	if (yych <= 0x7F) goto yy42;
	if (yych <= 0xBF) goto yy39;
yy42:
	p = marker;
	goto yy38;
yy43:
	yych = *++p;
	if (yych <= 0x9F) goto yy42;
	if (yych <= 0xBF) goto yy41;
	goto yy42;
yy44:
	yych = *++p;
	if (yych <= 0x7F) goto yy42;
	if (yych <= 0xBF) goto yy41;
	goto yy42;
yy45:
	yych = *++p;
	if (yych <= 0x7F) goto yy42;
	if (yych <= 0x9F) goto yy41;
	goto yy42;
yy46:
	yych = *++p;
	if (yych <= 0x8F) goto yy42;
	if (yych <= 0xBF) goto yy44;
	goto yy42;
yy47:
	yych = *++p;
	if (yych <= 0x7F) goto yy42;
	if (yych <= 0xBF) goto yy44;
	goto yy42;
yy48:
	yych = *++p;
	if (yych <= 0x7F) goto yy42;
	if (yych <= 0x8F) goto yy44;
	goto yy42;
yy49:
	++p;
	yych = *p;
	marker = p;
yy50:
	if (yybm[0+yych] & 128) {
		goto yy49;
	}
	if (yych <= 0xEC) {
		if (yych <= 0xC1) {
			if (yych <= '\n') goto yy42;
			if (yych >= '~') goto yy42;
		} else {
			if (yych <= 0xDF) goto yy52;
			if (yych <= 0xE0) goto yy53;
			goto yy54;
		}
	} else {
		if (yych <= 0xF0) {
			if (yych <= 0xED) goto yy55;
			if (yych <= 0xEF) goto yy54;
			goto yy56;
		} else {
			if (yych <= 0xF3) goto yy57;
			if (yych <= 0xF4) goto yy58;
			goto yy42;
		}
	}
	yych = *++p;
	if (yych == '}') goto yy59;
	goto yy42;
yy52:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy42;
	if (yych <= 0xBF) goto yy49;
	goto yy42;
yy53:
	++p;
	yych = *p;
	if (yych <= 0x9F) goto yy42;
	if (yych <= 0xBF) goto yy52;
	goto yy42;
yy54:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy42;
	if (yych <= 0xBF) goto yy52;
	goto yy42;
yy55:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy42;
	if (yych <= 0x9F) goto yy52;
	goto yy42;
yy56:
	++p;
	yych = *p;
	if (yych <= 0x8F) goto yy42;
	if (yych <= 0xBF) goto yy54;
	goto yy42;
yy57:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy42;
	if (yych <= 0xBF) goto yy54;
	goto yy42;
yy58:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy42;
	if (yych <= 0x8F) goto yy54;
	goto yy42;
yy59:
	++p;
	p = marker;
	{ return (cmark_bufsize_t)(p - start); }
}

}