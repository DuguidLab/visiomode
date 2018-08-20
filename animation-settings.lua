
local composer = require( "composer" )

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------

local widget = require('widget')

local speed
local startDelay
local movtType  -- bounded / sweep

local movtAvailable = { 'bound-bound', 'on-touch', 'edge-edge' }


local function goBack()
    composer.gotoScene("stand-alone-setup")
end


local function exportSettings()
    -- get values from picker wheel
    local movtValue = movtType:getValues()
    movtType = movtValue[1].value
    
    -- settings table
    animationSettings = {
        speed = speed,
        startDelay = startDelay,
        movtType = movtType,
    }
    composer.setVariable("animationSettings", animationSettings)
    goBack()
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

    local title = display.newText(sceneGroup, "Animation Setup", display.contentCenterX, 70, native.SystemFont, 50)

    local speedTitle = display.newText(sceneGroup, "Speed (mm/s): ", display.contentCenterX-20, 150, native.SystemFont, 40)
    speedTitle.anchorX = 1

    speed = native.newTextField(display.contentCenterX+250, 150, 100, 35)
    speed.text = 10
    speed.anchorX = 0
    sceneGroup:insert(speed)

    local startDelayTitle = display.newText(sceneGroup, "Start Delay (ms): ", display.contentCenterX-20, 225, native.SystemFont, 40)
    startDelayTitle.anchorX = 1

    startDelay = native.newTextField(display.contentCenterX+250, 225, 100, 35)
    startDelay.text = 500
    startDelay.anchorX = 0
    sceneGroup:insert(startDelay)

    local movtTypeTitle = display.newText(sceneGroup, "Mov't Type: ", display.contentCenterX-20, 350, native.SystemFont, 40)
    movtTypeTitle.anchorX = 1

    movtType = widget.newPickerWheel({
        x = display.contentCenterX+300,
        y = 350,
        fontSize = 33,
        width = 200,
        rowHeight = 30,
        style = "resizable",
        columns = {{
            align = "center",
            width = 200,
            labelPadding = 10,
            startIndex = 1,
            labels = movtAvailable
        }}
    })
    sceneGroup:insert(movtType)

    local goBackButton = display.newText(sceneGroup, "Save Settings", display.contentCenterX, 700, native.SystemFont, 45)
    goBackButton:addEventListener("tap", exportSettings)

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
        composer.removeScene( 'animation-settings' )
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
