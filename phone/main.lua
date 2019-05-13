-----------------------------------------------------------------------------------------
--
-- main.lua
--
-----------------------------------------------------------------------------------------

local VERSION = 1.0

-- load composer to manage scenes
local composer = require("composer")

-- hide status bar
display.setStatusBar(display.HiddenStatusBar)

-- seed random number generator
math.randomseed(os.time())

-- start off at menu screen
composer.gotoScene("menu")
