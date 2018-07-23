
local composer = require( "composer" )

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------

local widget = require('widget')

local sessionTime
local showEndScreen
local endTone
local saveSessionData


local function startSession()
    -- export session settings
    sessionSettings = {
        sessionType = "stand-alone",
        duration = sessionTime.text,
        showResults = showEndScreen.isOn,
        playToneAtEnd = endTone.isOn,
        saveSession = saveSessionData.isOn
    }
    composer.setVariable("sessionSettings", sessionSettings)

    composer.gotoScene("task")
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

    local title = display.newText(sceneGroup, "Stand-Alone Session Setup", display.contentCenterX, 70, native.SystemFont, 50)
    
    local sessionTimeTitle = display.newText(sceneGroup, "Session Duration (min): ", display.contentCenterX-20, 150, native.SystemFont, 40)
    sessionTimeTitle.anchorX = 1
    
    sessionTime = native.newTextField(display.contentCenterX+250, 150, 100, 35)
    sessionTime.text = 30
    sessionTime.anchorX = 0
    sceneGroup:insert(sessionTime)

    local showEndScreenTitle = display.newText(sceneGroup, "Show Results at End: ", display.contentCenterX-20, 225, native.SystemFont, 40)
    showEndScreenTitle.anchorX = 1

    showEndScreen = widget.newSwitch({
        x= display.contentCenterX+295,
        y = 225,
        style = "checkbox",
        id = "showEndScreenCheckbox",
        initialSwitchState = true
    })
    sceneGroup:insert(showEndScreen)

    local endToneTitle = display.newText(sceneGroup, "Tone at End: ", display.contentCenterX-20, 300, native.SystemFont, 40)
    endToneTitle.anchorX = 1

    endTone = widget.newSwitch({
        x = display.contentCenterX+295,
        y = 300,
        style = "checkbox",
        id = "endToneCheckbox"
    })
    sceneGroup:insert(endTone)

    local saveSessionDataTitle = display.newText(sceneGroup, "Save Session Data: ", display.contentCenterX-20, 375, native.SystemFont, 40)
    saveSessionDataTitle.anchorX = 1

    saveSessionData = widget.newSwitch({
        x = display.contentCenterX+295,
        y = 375, 
        style = "checkbox",
        id = "saveSessionDataCheckbox",
        initialSwitchState = true
    })
    sceneGroup:insert(saveSessionData)

    local startSessionButton = display.newText(sceneGroup, "Start Session", display.contentCenterX, 700, native.SystemFont, 45)
    startSessionButton:addEventListener("tap", startSession)

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

	elseif ( phase == "did" ) then
        composer.removeScene("stand-alone-session-setup")
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
