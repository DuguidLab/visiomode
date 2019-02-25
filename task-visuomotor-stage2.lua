local composer = require( "composer" )

local scene = composer.newScene()

local json = require("json")

-- initialise variables
local session

local target
local bounds
local hits
local misses
local precued
local corrections
local correction_trial -- indicateif a trial is a correction so as to not be counted

local start

local taskSettings
local sessionSettings
local sessionTimer

local iti_timer

local startTime
local hitTime
local missTime
local precueTime

local targetDistance  -- mm
local horizontalWidth

-- RPi comm buffer
local buffer

-- TODO figure out DPI at runtime!
local pixelMilliMeter = 0.123902439  -- factor for converting pixels to mm 


local function getTaskSettings()
    local taskSettings = composer.getVariable("taskSettings")
    table.foreach(taskSettings, print)
    return taskSettings
end


local function getSessionSettings()
    local sessionSettings = composer.getVariable("sessionSettings")
    table.foreach(sessionSettings, print)
    return sessionSettings
end


local function restoreTargets()
    local target_idx = math.random(#bounds)
    print(target_idx)
    local distractor_idx = 3 - target_idx
    target.x = bounds[target_idx]
    target.alpha = 1
    distractor.x = bounds[distractor_idx]
    distractor.alpha = 1
end


local function restoreTargetsSamePos()
    target.alpha = 1
    distractor.alpha = 1
end


local function getTime()
    local _,msec = math.modf(os.clock())
    if msec==0 then
        msec='000'
    else 
        msec=tostring(msec):sub(3,5)
    end

    local time=os.date('%Y-%m-%dT%H:%M:%S.',os.time())
    return time .. msec
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
        distractor.alpha = 0
        local hit = {
            timestamp = hitTime - startTime,
            x_distance = event.x - event.xStart,
            y_distance = event.y - event.yStart,
            x = event.x, y = event.y,
            duration = now - hitTime,
            touch_force = event.pressure
        }
        if correction_trial then
            table.insert(corrections, hit)
            print("corrected")
            correction_trial = false
        else
            table.insert(hits, hit)
            print("hit")
        end
        if sessionSettings.sessionType == 'rpi' then
            composer.setVariable('buffer', {'reward:' .. getTime()})
        end

        iti_timer = timer.performWithDelay(taskSettings.delay, restoreTargets)
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
        local miss = {
            timestamp = missTime - startTime,
            x_distance = event.x - event.xStart,
            y_distance = event.y - event.yStart,
            x = event.x,
            y = event.y,
            duration = now - missTime,
            touch_force = event.pressure
        }
        target.alpha = 0
        distractor.alpha = 0

        if correction_trial then
            table.insert(corrections, miss)
            print("still correcting")
        else
            table.insert(misses, miss)
            print("miss")
            correction_trial = true -- next trial should be a correction trial
        end

        iti_timer = timer.performWithDelay(taskSettings.delay, restoreTargetsSamePos)

    end

    return true
end


local function onPrecued(event)
    local phase = event.phase

    if ("began" == phase) then
        missTime = os.clock()
    elseif ("moved" == phase) then

    elseif ("ended" == phase) then
        local now = os.clock()
        local prec = {
            timestamp = missTime - startTime,
            x_distance = event.x - event.xStart,
            y_distance = event.y - event.yStart,
            x = event.x, y = event.y,
            duration = now - missTime,
            touch_force = event.pressure
        }
        table.insert(precued, prec)
        print("precued")
    end

    return true

end


local function saveSession()
    local filePath = system.pathForFile("session-" .. os.date('%Y%m%d_%H%M%S') ..  ".json", system.DocumentsDirectory)
    local file = io.open(filePath, "w")

    session = {
        timestamp = os.date('%Y-%m-%d_%H:%M:%S'),
        start = start,
        hits = hits,
        misses = misses,
        precued = precued,
        corrections = corrections
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
    taskSettings = getTaskSettings()
    sessionSettings = getSessionSettings()

    start = getTime()

    -- init tables for hits / misses
    hits = {}
    misses = {}
    precued = {}
    corrections = {}
    correction_trial = false
    session = {}

    -- set up task scene
    local sceneGroup = self.view

    local background = display.newRect(sceneGroup, display.contentCenterX, display.contentCenterY, display.contentHeight, display.contentWidth)
    background.fill = {0, 0, 0}
    background:toBack()

    -- offset to move everything left or right
    local offset = -25

    print(display.actualContentWidth)
    -- local dividerWidth 5 / pixelMilliMeter  -- 5 mm to pixels
    local dividerWidth = 35
    local divider = display.newRect(sceneGroup, (display.actualContentWidth * 0.5) + display.screenOriginX + offset, display.contentCenterY, dividerWidth, display.contentHeight)
    divider.fill= { 0.5, 0.5, 0.5 }


     -- set up bounds (x positions)
    bounds = {
        (display.actualContentWidth * 0.25) + display.screenOriginX  - (dividerWidth / 2) + offset,
        (display.actualContentWidth * 0.75) + display.screenOriginX + (dividerWidth / 2) + offset
    }

    local width = 665
    target = display.newImageRect(sceneGroup, 'assets/stage2_target.jpg', width, display.contentHeight)
    target.y = display.contentCenterY

    distractor = display.newImageRect(sceneGroup, 'assets/stage2_distractor.jpg', width, display.contentHeight)
    distractor.y = display.contentCenterY

    restoreTargets()

    background:addEventListener("touch", onPrecued)
    target:addEventListener("touch", onTargetHit)
    distractor:addEventListener("touch", onTargetMiss)
end


-- show()
function scene:show( event )

    local sceneGroup = self.view
    local phase = event.phase

    if ( phase == "will" ) then

    elseif ( phase == "did" ) then
        if (sessionSettings.duration > 0) then
          -- gotta convert min to msec
            sessionTimer = timer.performWithDelay(sessionSettings.duration * 60000, sessionEnd, 1)
        end
    end
end


-- hide()
function scene:hide( event )

    local sceneGroup = self.view
    local phase = event.phase

    if ( phase == "will" ) then
        timer.cancel(sessionTimer)
    elseif ( phase == "did" ) then
        composer.removeScene("task-visuomotor-stage2")
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
