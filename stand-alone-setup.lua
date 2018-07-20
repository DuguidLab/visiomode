
local composer = require( "composer" )

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------
local widget = require( "widget" )

local animatedTarget
local shrinkingTarget
local targetWidth
local delay
local numTargets
local targetDistance
local hapticsOnMiss

local animatedTargetOptions
local shrinkingTargetOptions

local startTaskButton
local goBackButton

-- event handlers 
local function onAnimatedTargetSwitchPress( event )
    local switch = event.target

    if (switch.isOn) then
        animatedTargetOptions.alpha = 1
    else 
        animatedTargetOptions.alpha = 0
    end
end


local function onShrinkingTargetSwitchPress( event )
    local switch = event.target

    if (switch.isOn) then
        shrinkingTargetOptions.alpha = 1
    else 
        shrinkingTargetOptions.alpha = 0
    end
end


local function gotoMenu()
    composer.gotoScene("menu")
end


local function gotoAntimationOptions()
    composer.gotoScene("animation-settings")
end


local function gotoShrinkingOptions()
    composer.gotoScene("shrinking-settings")
end


local function startTask()
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

    local title = display.newText(sceneGroup, "Stand-Alone Task Setup", display.contentCenterX, 70, native.SystemFont, 50)
    
    delayTitle = display.newText(sceneGroup, "Presentation Delay (ms): ", display.contentCenterX-20, 150, native.SystemFont, 40)
    delayTitle.anchorX = 1
    delayField = native.newTextField(display.contentCenterX+250, 150, 100, 35)
    delayField.text = 500
    delayField.anchorX = 0
    sceneGroup:insert(delayField)

    numTargetsTitle = display.newText(sceneGroup, "Number of Targets: ", display.contentCenterX-20, 225, native.SystemFont, 40)
    numTargetsTitle.anchorX = 1
    numTargetsField = native.newTextField(display.contentCenterX+250, 225, 100, 35)
    numTargetsField.text = 2
    numTargetsField.anchorX = 0
    sceneGroup:insert(numTargetsField)

    targetDistanceTitle = display.newText(sceneGroup, "Min Target Distance (mm): ", display.contentCenterX-20, 300, native.SystemFont, 40)
    targetDistanceTitle.anchorX = 1
    targetDistanceField = native.newTextField(display.contentCenterX+250, 300, 100, 35)
    targetDistanceField.text = 1000
    targetDistanceField.anchorX = 0
    sceneGroup:insert(targetDistanceField)

    targetWidthTitle = display.newText(sceneGroup, "Target Width (px): ", display.contentCenterX-20, 375, native.SystemFont, 40)
    targetWidthTitle.anchorX = 1
    targetWidthField = native.newTextField(display.contentCenterX+250, 375, 100, 35)
    targetWidthField.text = 80
    targetWidthField.anchorX = 0
    sceneGroup:insert(targetWidthField)

    animatedTargetTitle = display.newText(sceneGroup, "Animated Target: ", display.contentCenterX-20, 450, native.SystemFont, 40)
    animatedTargetTitle.anchorX = 1
    animatedTargetField = widget.newSwitch({
        x = display.contentCenterX+295, 
        y = 450,
        style = "checkbox",
        id = "animatedTargetCheckbox",
        onPress = onAnimatedTargetSwitchPress
    })
    sceneGroup:insert(animatedTargetField)
    animatedTargetOptions = display.newText(sceneGroup, "Configure...", display.contentCenterX+450, 450, native.SystemFont, 35)
    animatedTargetOptions.alpha = 0
    animatedTargetOptions:addEventListener("tap", gotoAntimationOptions)

    shrinkingTargetTitle = display.newText(sceneGroup, "Shrinking Target: ", display.contentCenterX-20, 525, native.SystemFont, 40)
    shrinkingTargetTitle.anchorX = 1
    shrinkingTargetField = widget.newSwitch({
        x = display.contentCenterX+295, 
        y = 525,
        style = "checkbox",
        id = "shrinkingTargetCheckbox",
        onPress = onShrinkingTargetSwitchPress
    })
    sceneGroup:insert(shrinkingTargetField)
    shrinkingTargetOptions = display.newText(sceneGroup, "Configure...", display.contentCenterX+450, 525, native.SystemFont, 35)
    shrinkingTargetOptions.alpha = 0
    shrinkingTargetOptions:addEventListener("tap", gotoShrinkingOptions)

    hapticsOnMissTitle = display.newText(sceneGroup, "Vibrate on Miss: ", display.contentCenterX-20, 600, native.SystemFont, 40)
    hapticsOnMissTitle.anchorX = 1 
    hapticsOnMissField = widget.newSwitch({
        x = display.contentCenterX+295, 
        y = 600,
        style = "checkbox",
        id = "shrinkingTargetCheckbox",
    })
    sceneGroup:insert(hapticsOnMissField)
 
    startTaskButton = display.newText(sceneGroup, "Start Task", display.contentCenterX, 700, native.SystemFont, 45)
    startTaskButton:addEventListener("tap", startTask)
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
        composer.removeScene("stand-alone-setup")
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
