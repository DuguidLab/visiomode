local composer = require( "composer" )

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------

local function gotoConnectRpi()
    composer.gotoScene("connect")
end


local function gotoStandAlone()
    --composer.gotoScene("select_protocol")
    composer.gotoScene("task")
end


local function gotoAbout()
    composer.gotoScene("about")
end


-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create( event )

	local sceneGroup = self.view
    
    local background = display.newImageRect(sceneGroup, "assets/menu-background.jpg", 1400, 800)
    background.x = display.contentCenterX
    background.y = display.contentCenterY

    local title = display.newText(sceneGroup, "Rodent Touchscreen Behaviour Suite", display.contentCenterX, 50, native.systemFont, 60)

    local connectButton = display.newText(sceneGroup, "Connect to RPi Controller", display.contentCenterX, 300, native.systemFont, 44)
    connectButton:setFillColor(0.75, 0.78, 1)

    local standAloneButton = display.newText(sceneGroup, "Stand-Alone Mode", display.contentCenterX, 400, native.systemFont, 44)
    standAloneButton:setFillColor(0.75, 0.78, 1)

    local aboutButton = display.newText(sceneGroup, "About", display.contentCenterX, 500, native.systemFont, 44)
    aboutButton:setFillColor(0.75, 0.78, 1)

    connectButton:addEventListener("tap", gotoConnectRpi)
    standAloneButton:addEventListener("tap", gotoStandAlone)
    aboutButton:addEventListener("tap", gotoAbout)
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
