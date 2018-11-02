
local composer = require( "composer" )

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------
local json = require("json")

-- initialise variables
local session

local target
local bounds
local hits
local misses
local precued

local taskSettings
local sessionSettings
local animationSettings
local shrinkingSettings
local sessionTimer

local startTime
local hitTime
local missTime
local precueTime

local targetDistance  -- mm
local horizontalWidth

-- RPi comm buffer
local buffer

-- start physics engine (needed for animation)
physics.start()
physics.setGravity( 0, 0 )


-- TODO figure out DPI at runtime!
local pixelMilliMeter = 0.2645833  -- factor for converting pixels to mm 


local function getSessionSettings()
    local sessionSettings = composer.getVariable("sessionSettings")
    return sessionSettings
end

local function setTargetBounds()
  bounds = {}
  iter = 1  -- second counter for for loop
  -- set bounds
  if (taskSettings.targets % 2 == 0) then
      -- slits placed center-out
      for i = 1, taskSettings.targets, 2 do
          table.insert(bounds, display.contentCenterX + ((targetDistance / 2) * iter))
          table.insert(bounds, display.contentCenterX - ((targetDistance / 2) * iter))
          iter = iter + 1
      end
  else
      -- slits placed center-surround
      table.insert(bounds, display.contentCenterX)
      for i = 1, taskSettings.targets, 3 do
          table.insert(bounds, display.contentCenterX + (targetDistance * iter))
          table.insert(bounds, display.contentCenterX - (targetDistance * iter))
      iter = iter + 1
      end
  end

  -- inspect bounds table
  print(table.foreach(bounds, print))
  print(targetDistance)
end


local function restoreTarget(newX)
    if not type(newX) == 'number' then
        newX = bounds[math.random(#bounds)]
    end
    target.x = newX
    target.alpha = 1
end


local function onTargetHit(event)
    local target = event.target
    local phase = event.phase

    if ("began" == phase) then
        hitTime = os.clock()
    elseif ("moved" == phase) then
        return true
    elseif ("ended" == phase) then
        local now = os.clock()
        target.alpha = 0

        local hit = {
            timestamp = hitTime - startTime,
            x_distance = math.abs(event.x - event.xStart),
            y_distance = math.abs(event.y - event.yStart),
            touch_coords = {x = event.x, y = event.y},
            duration = now - hitTime,
            touch_force = event.pressure
        }

        table.insert(hits, hit)
        print("hit")
        if sessionSettings.sessionType == 'rpi' then
            composer.setVariable('buffer', {'reward:' .. taskSettings.delay})
        end

        if ( animationSettings.movtType == 'on-touch' ) then 
            animateOnTouch()
        else
            timer.performWithDelay(taskSettings.delay, restoreTarget)
        end
    end

    return true
end


local function onTargetMiss(event)
    local phase = event.phase

    if ("began" == phase) then
        missTime = os.clock()
    elseif ("moved" == phase) then

    elseif ("ended" == phase) then
        local now = os.clock()
        if (target.alpha == 1) then
            local miss = {
                timestamp = missTime - startTime,
                x_distance = math.abs(event.x - event.xStart),
                y_distance = math.abs(event.y - event.yStart),
                touch_coords = {x = event.x, y = event.y},
                duration = now - missTime,
                touch_force = event.pressure
            }

            table.insert(misses, miss)
            print("miss")

            -- vibrate if haptics enabled
            if (taskSettings.haptics) then
                system.vibrate()
            end
        elseif (target.alpha == 0) then
            local prec = {
                timestamp = missTime - startTime,
                x_distance = math.abs(event.x - event.xStart),
                y_distance = math.abs(event.y - event.yStart),
                touch_coords = {x = event.x, y = event.y},
                duration = now - missTime,
                touch_force = event.pressure
            }
            table.insert(precued, prec)
            print("precued")
        end
    end

    return true
end


local function saveSession()
    local filePath = system.pathForFile("session-" .. os.date('%Y%m%d_%H%M%S') ..  ".json", system.DocumentsDirectory)
    local file = io.open(filePath, "w")

    session = {
        timestamp = os.date('%Y-%m-%d_%H:%M:%S'),
        hits = hits,
        misses = misses,
        precued = precued
    }

    if file then
        file:write(json.encode(session))
        io.close(file)
    end
end


local function streamSession()
    -- Stream session data back to RPi controller
    if sessionSettings.sessionType == 'rpi' then
        print('streaming session data to rpi...')
        composer.setVariable(
            'buffer', {'session:' .. os.date('%Y%m%d_%H%M%S') .. ':' .. json.encode(session)}
        )
    end
end


local function sessionEnd()
    saveSession()
    streamSession()
    composer.setVariable("lastSession", session)
    composer.gotoScene("last-session-summary")
end


-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create( event )
    -- set msec start time
    startTime = os.clock()

    -- get settings
    sessionSettings = getSessionSettings()

    -- init tables for hits / misses
    hits = {}
    misses = {}
    precued = {}

    -- set up task scene
    local sceneGroup = self.view

    local background = display.newRect( display.contentCenterX, display.contentCenterY, display.contentWidth, display.contentHeight )
    background.fill = {0, 0, 0}
    background:toBack()

    --setTargetBounds()
    target = display.newRect( sceneGroup, bounds[math.random(#bounds)], display.contentCenterY, horizontalWidth, display.contentHeight )
    target.fill = { 1, 1, 0 }
    physics.addBody( target, "dynamic", { radius = horizontalWidth, bounce=1.0 } )

    distractor = display.newRect( sceneGroup, bounds[math.random(#bounds)], display.contentCenterY, horizontalWidth, display.contentHeight )
    distractor.fill = { 1, 0, 1 }
    physics.addBody(distractor, "dynamic", { radius = horizontalWidth, bounce=1.0 })

    if taskSettings.animated then
        animateTarget(sceneGroup)
    end

    background:addEventListener("touch", onTargetMiss)
    target:addEventListener("touch", onTargetHit)
end


-- show()
function scene:show( event )

    local sceneGroup = self.view
    local phase = event.phase

    if ( phase == "will" ) then

    elseif ( phase == "did" ) then
        if (sessionSettings.duration > 0) then
          -- gotta convert min to msec
            sessionTimer = timer.performWithDelay( sessionSettings.duration * 60000, sessionEnd, 1 )
        end
    end
end


-- hide()
function scene:hide( event )

    local sceneGroup = self.view
    local phase = event.phase

    if ( phase == "will" ) then
        timer.cancel( sessionTimer )
        saveSession()
    elseif ( phase == "did" ) then
        physics.pause()
        composer.removeScene( "task" )
    end
end


-- destroy()
function scene:destroy( event )

    local sceneGroup = self.view

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
