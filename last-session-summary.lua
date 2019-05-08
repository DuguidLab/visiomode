
local composer = require( "composer" )

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------

local hits
local misses
local precued


local function getLastSession()
    lastSession = composer.getVariable("lastSession")
    hits = lastSession.hits
    misses = lastSession.misses
    precued = lastSession.precued
end


-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create( event )

  getLastSession()

	local sceneGroup = self.view

  local background = display.newImageRect(sceneGroup, "assets/menu-background.jpg", 1400, 800)
  background.x = display.contentCenterX
  background.y = display.contentCenterY

  local title = display.newText(sceneGroup, "Last Session Data", display.contentCenterX, 70, native.SystemFont, 50)

  local timestampTitle = display.newText(sceneGroup, "Session Timestamp: ", display.contentCenterX-50, 200, native.SystemFont, 40)
  timestampTitle.anchorX = 1

  local timestampText = display.newText(sceneGroup, os.date('%Y%m%d_%H%M%S'), display.contentCenterX+100, 200, native.SystemFont, 40)
  timestampText.anchorX = 0

  local hitsTitle = display.newText(sceneGroup, "Hits: ", display.contentCenterX-50, 300, native.SystemFont, 40)
  hitsTitle.anchorX = 1

  local hitsText = display.newText(sceneGroup, #hits, display.contentCenterX+100, 300, native.SystemFont, 40)
  hitsText.anchorX = 0

  local missesTitle = display.newText(sceneGroup, "Misses: ", display.contentCenterX-50, 400, native.SystemFont, 40)
  missesTitle.anchorX = 1

  local missesText = display.newText(sceneGroup, #misses, display.contentCenterX+100, 400, native.SystemFont, 40)
  missesText.anchorX = 0

  local precuedTitle = display.newText(sceneGroup, "Precued: ", display.contentCenterX-50, 500, native.SystemFont, 40)
  precuedTitle.anchorX = 1

  local precuedText = display.newText(sceneGroup, #precued, display.contentCenterX+100, 500, native.SystemFont, 40)
  precuedText.anchorX = 0
end


-- show()
function scene:show( event )

	local sceneGroup = self.view
	local phase = event.phase

	if ( phase == "will" ) then
		-- Code here runs when the scene is still off screen (but is about to come on screen)

	elseif ( phase == "did" ) then
		-- Code here runs when the scene is entirely on screen

	end
end


-- hide()
function scene:hide( event )

	local sceneGroup = self.view
	local phase = event.phase

	if ( phase == "will" ) then
		-- Code here runs when the scene is on screen (but is about to go off screen)

	elseif ( phase == "did" ) then
		-- Code here runs immediately after the scene goes entirely off screen

    composer.removeScene( "last-session-summary" )
	end
end


-- destroy()
function scene:destroy( event )

	local sceneGroup = self.view
	-- Code here runs prior to the removal of scene's view

end


-- -----------------------------------------------------------------------------------
-- Scene event function listeners
-- -----------------------------------------------------------------------------------
scene:addEventListener( "create", scene )
scene:addEventListener( "show", scene )
scene:addEventListener( "hide", scene )
scene:addEventListener( "destroy", scene )
-- -----------------------------------------------------------------------------------

return scene
