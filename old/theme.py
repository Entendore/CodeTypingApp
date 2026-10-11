def hex_to_rgba(h, alpha=1.0):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4)) + (alpha,)

BG_DARK    = hex_to_rgba('#0b0d1a')
BG_MAIN    = hex_to_rgba('#12142a')
BG_CARD    = hex_to_rgba('#1a1d3a')
BG_INPUT   = hex_to_rgba('#161833')
BG_HOVER   = hex_to_rgba('#22254a')
ACCENT     = hex_to_rgba('#6c5ce7')
ACCENT_L   = hex_to_rgba('#a29bfe')
ACCENT_D   = hex_to_rgba('#4834d4')
SUCCESS    = hex_to_rgba('#00e676')
ERROR      = hex_to_rgba('#ff5252')
WARNING    = hex_to_rgba('#ffab40')
INFO       = hex_to_rgba('#40c4ff')
TEXT_P     = hex_to_rgba('#eceff1')
TEXT_S     = hex_to_rgba('#90a4ae')
TEXT_M     = hex_to_rgba('#546e7a')
BORDER     = hex_to_rgba('#26294a')
GLOW       = hex_to_rgba('#6c5ce7', 0.15)

C_ACCENT   = '#6c5ce7'; C_ACCENT_L = '#a29bfe'; C_SUCCESS  = '#00e676'
C_ERROR    = '#ff5252'; C_WARNING  = '#ffab40'; C_TEXT_P   = '#eceff1'
C_TEXT_M   = '#546e7a'; C_TEXT_S   = '#90a4ae'; C_INFO     = '#40c4ff'

RAD = [10]; RAD_LG = [16]; RAD_SM = [6]
PAD = [15, 20]; PAD_LG = [25, 30]