
local composer = require( "composer" )

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------
local widget = require( "widget" )

local taskSettings

local animatedTarget
local shrinkingTarget
local targetWidth
local delay
local numTargets
local targetDistance
local hapticsOnMiss

local animatedTargetOptions
local shrinkingTargetOptions

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


local function setupSession()
  -- export task settings
  taskSettings = {
      delay = delay.text,
      width = targetWidth.text,
      targets = numTargets.text,
      distance = targetDistance.text,
      haptics = hapticsOnMiss.isOn,
      animated = animatedTarget.isOn,
      shrinking = shrinkingTarget.isOn
  }
  --table.foreach(taskSettings, print) -- debug
  composer.setVariable("taskSettings", taskSettings)
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

  local delayTitle = display.newText(sceneGroup, "Presentation Delay (ms): ", display.contentCenterX-20, 150, native.SystemFont, 40)
  delayTitle.anchorX = 1

  delay = native.newTextField(display.contentCenterX+250, 150, 100, 35)
  delay.text = 500
  delay.anchorX = 0
  sceneGroup:insert(delay)

  local numTargetsTitle = display.newText(sceneGroup, "Number of Targets: ", display.contentCenterX-20, 225, native.SystemFont, 40)
  numTargetsTitle.anchorX = 1

  numTargets = native.newTextField(display.contentCenterX+250, 225, 100, 35)
  numTargets.text = 2
  numTargets.anchorX = 0
  sceneGroup:insert(numTargets)

  targetDistanceTitle = display.newText(sceneGroup, "Min Target Distance (mm): ", display.contentCenterX-20, 300, native.SystemFont, 40)
  targetDistanceTitle.anchorX = 1

  targetDistance = native.newTextField(display.contentCenterX+250, 300, 100, 35)
  targetDistance.text = 20
  targetDistance.anchorX = 0
  sceneGroup:insert(targetDistance)

  local targetWidthTitle = display.newText(sceneGroup, "Target Width (mm): ", display.contentCenterX-20, 375, native.SystemFont, 40)
  targetWidthTitle.anchorX = 1

  targetWidth = native.newTextField(display.contentCenterX+250, 375, 100, 35)
  targetWidth.text = 5
  targetWidth.anchorX = 0
  sceneGroup:insert(targetWidth)

  local animatedTargetTitle = display.newText(sceneGroup, "Animated Target: ", display.contentCenterX-20, 450, native.SystemFont, 40)
  animatedTargetTitle.anchorX = 1

  animatedTarget = widget.newSwitch({
      x = display.contentCenterX+295, 
      y = 450,
      style = "checkbox",
      id = "animatedTargetCheckbox",
      onPress = onAnimatedTargetSwitchPress
  })
  sceneGroup:insert(animatedTarget)

  local shrinkingTargetTitle = display.newText(sceneGroup, "Shrinking Target: ", display.contentCenterX-20, 525, native.SystemFont, 40)
  shrinkingTargetTitle.anchorX = 1

  shrinkingTarget = widget.newSwitch({
      x = display.contentCenterX+295, 
      y = 525,
      style = "checkbox",
      id = "shrinkingTargetCheckbox",
      onPress = onShrinkingTargetSwitchPress
  })
  sceneGroup:insert(shrinkingTarget)

  local hapticsOnMissTitle = display.newText(sceneGroup, "Vibrate on Miss: ", display.contentCenterX-20, 600, native.SystemFont, 40)
  hapticsOnMissTitle.anchorX = 1 

  hapticsOnMiss = widget.newSwitch({
      x = display.contentCenterX+295, 
      y = 600,
      style = "checkbox",
      id = "shrinkingTargetCheckbox",
      initialSwitchState = true,
  })
  sceneGroup:insert(hapticsOnMiss)

  local setupSessionButton = display.newText(sceneGroup, "Setup Session", display.contentCenterX, 700, native.SystemFont, 45)
  setupSessionButton:addEventListener("tap", setupSession)
end


-- show()
function scene:show( event )

	local sceneGroup = self.view
	local phase = event.phase

	if ( phase == "will" ) then
    -- publish taskSettings table
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
    composer.removeScene("settings")
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
