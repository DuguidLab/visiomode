
local composer = require( "composer" )

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------


-- initialise variables
local target
local bounds
local hits
local misses

local taskSettings

local numTargets
local targetDistance  -- mm
local delay
local horizontalWidth
local vibrateOnMiss

local pixelMilliMeter = 0.2645833  -- factor for converting pixels to mm


local function getTaskSettings()

    taskSettings = composer.getVariable("taskSettings")
    table.foreach(taskSettings, print)

    -- set settings vars
    numTargets = taskSettings.targets
    delay = taskSettings.delay
    vibrateOnMiss = taskSettings.haptics

    -- convert mm to pix
    horizontalWidth = math.floor(taskSettings.width / pixelMilliMeter)
    targetDistance = math.floor(taskSettings.distance / pixelMilliMeter) + math.floor(horizontalWidth / 2)
end


local function setTargetBounds()
    
    bounds = {}
    iter = 1  -- second counter for for loop
    -- set bounds
    if (numTargets % 2 == 0) then
        -- slits placed center-out
        for i = 1, numTargets, 2 do
            table.insert(bounds, display.contentCenterX + ((targetDistance / 2) * iter))
            table.insert(bounds, display.contentCenterX - ((targetDistance / 2) * iter))
            iter = iter + 1
        end
    else
        -- slits placed center-surround
        table.insert(bounds, display.contentCenterX)
        for i = 1, numTargets, 3 do
            table.insert(bounds, display.contentCenterX + (targetDistance * iter))
            table.insert(bounds, display.contentCenterX - (targetDistance * iter))
        iter = iter + 1
        end
    end

    -- inspect bounds table
    print(table.foreach(bounds, print))
    print(targetDistance)
    print(display.contentCenterX)
end


local function restoreTarget()
    target.x = bounds[math.random(#bounds)]
    target.alpha = 1
end


local function onTargetHit(event)
    local target = event.target
    local phase = event.phase

    if ("began" == phase) then

    elseif ("moved" == phase) then

    elseif ("ended" == phase) then
        -- move target to a new random pos
        target.alpha = 0
        print("hit")
        timer.performWithDelay(delay, restoreTarget)
    end

    return true
end


local function onTargetMiss(event)
    local phase = event.phase

    if ("began" == phase) then

    elseif ("moved" == phase) then

    elseif ("ended" == phase) then
        if (target.alpha == 1) then
            print("miss")
            -- vibrate if haptics enabled
            if (vibrateOnMiss) then
                system.vibrate()
            end
        elseif (target.alpha == 0) then
            print("overexcited")
        end
    end

    return true
end


-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create( event )

    getTaskSettings()

    -- set up task scene
	local sceneGroup = self.view

    local background = display.newRect(display.contentCenterX, display.contentCenterY, display.contentWidth, display.contentHeight)
    background.fill = {0, 0, 0}
    background:toBack()

    setTargetBounds()
    target = display.newRect(sceneGroup, bounds[math.random(#bounds)], display.contentCenterY, horizontalWidth, display.contentHeight)
    target.fill = { 1, 1, 1 }

    background:addEventListener("touch", onTargetMiss)
    target:addEventListener("touch", onTargetHit)
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
